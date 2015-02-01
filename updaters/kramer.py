from catalog.models import Updater
from catalog.models import Distributor
from catalog.models import Stock
from catalog.models import Currency
from catalog.models import Unit
from catalog.models import CategorySynonym
from catalog.models import VendorSynonym
from catalog.models import Category
from catalog.models import Vendor
from catalog.models import Product
from catalog.models import Party
from catalog.models import PriceType
from catalog.models import Price


class Runner:

	def __init__(self):

		# Инициируем переменные
		self.name = 'Kramer'
		self.alias = 'kramer'

		# Получаем необходимые объекты
		self.distributor = Distributor.objects.take(alias=self.alias, name=self.name)
		self.updater = Updater.objects.take(alias=self.alias, name=self.name, distributor=self.distributor)
		self.factory = Stock.objects.take(alias=self.alias+'-factory', name=self.name+': завод', delivery_time_min = 10, delivery_time_max = 40, distributor=self.distributor)
		self.vendor = Vendor.objects.take(alias=self.alias, name=self.name)
		self.default_unit = Unit.objects.take(alias='pcs', name='шт.')
		self.rrp = PriceType.objects.take(alias='RRP', name='Рекомендованная розничная цена')
		self.rub = Currency.objects.take(alias='RUB', name='р.', full_name='Российский рубль', rate=1, quantity=1)
		self.usd = Currency.objects.take(alias='USD', name='$', full_name='Доллар США', rate=60, quantity=1)

		# Удаляем неактуальные партии
		Party.objects.clear(stock=self.factory)

		# Фильтры ссылок
		self.devices_url = "http://www.kramer.ru/Useful_files/Kramer-RUS-List-Price-"
		self.cables_url = "http://www.kramer.ru/Useful_files/Kramer-Cable-List-Price-"

	def run(self):

		import lxml.html
		import requests

		# Создаем сессию
		s = requests.Session()

		# Получаем куки
		url = 'http://kramer.ru/'
		r = s.get(url)
		cookies = r.cookies

		# Авторизуемся
		url = 'http://kramer.ru/'
		payload = {'dealer_login': self.updater.login, 'dealer_pass': self.updater.password}
		r = s.post(url, cookies=cookies, data=payload, allow_redirects=True)
		cookies = r.cookies

		# Переходим на закрытую часть
		url = 'http://kramer.ru/closed/files/'
		r = s.get(url, cookies=cookies, allow_redirects=True)
		tree = lxml.html.fromstring(r.text)

		# Ещем ссылки
		urls = tree.xpath('//a/@href')
		ok = 0
		for url in urls:
			if self.devices_url in url:
				xls_data = self.getXLS(request = s.get(url, cookies=cookies, allow_redirects=True))
				self.parseDevices(xls_data)
				ok += 1
			elif self.cables_url in url:
				xls_data = self.getXLS(request = s.get(url, cookies=cookies, allow_redirects=True))
				self.parseCables(xls_data)
				ok += 1

		if ok < 2:
			print("Не получилось загрузить прайс-листы.")
			print("Проверьте параметры доступа.")
			return False

		return True

	def getXLS(self, request):

		from io import BytesIO
		from zipfile import ZipFile

		zip_data = ZipFile(BytesIO(request.content))
		xls_data = zip_data.open(zip_data.namelist()[0])

		print("Получен прайс-лист: " + zip_data.namelist()[0])

		return xls_data

	def parseDevices(self, xls_data):

		import xlrd

		# Номера строк и столбцов
		num = {'header': 4}

		# Распознаваемые слова
		word = {
			'group': 'ГРУППА',
			'article': 'P/N',
			'model': 'Модель',
			'size': 'Размер',
			'name': 'Описание',
			'price': 'Цена, $',
			'dop': 'Примечание',
			'group_name': '',
			'category_name': ''}

		book = xlrd.open_workbook(file_contents=xls_data.read())
		sheet = book.sheet_by_index(0)
		for row_num in range(sheet.nrows):
			row = sheet.row_values(row_num)

			# Пустые строки
			if row_num < num['header']:
				continue

			# Заголовок таблицы
			elif row_num == num['header']:
				for cel_num, cel in enumerate(row):
					if   str(cel).strip() == word['article']:  num['article'] = cel_num
					elif str(cel).strip() == word['model']:  num['model'] = cel_num
					elif str(cel).strip() == word['size']:   num['size'] = cel_num
					elif str(cel).strip() == word['name']:   num['name'] = cel_num
					elif str(cel).strip() == word['price']:  num['price'] = cel_num
					elif str(cel).strip() == word['dop']:    num['dop'] = cel_num

				# Проверяем, все ли столбцы распознались
				if not num['article'] == 0 or not num['model'] or not num['size'] or not num['name'] or not num['price'] or not num['dop']:
					print("Ошибка структуры данных: не все столбцы опознаны.")
					return False
				else: print("Структура данных без изменений.")

			# Категория
			elif row[num['name']] and not row[num['article']] and not row[num['price']]:
				if word['group'] in row[num['name']]: word['group_name'] = row[num['name']]
				else: word['category_name'] = row[num['name']]
				category_synonym = CategorySynonym.objects.take(name="Devices: %s %s" % (word['group_name'], word['category_name']), updater=self.updater, distributor=self.distributor)

			# Товар
			elif row[num['name']] and row[num['article']] and row[num['price']]:

				# Определяем имя
				name = "{} {} {}".format(self.vendor.name, row[num['model']], row[num['name']])
				if row[num['size']]: name += " ( размер: {})".format(str(row[num['size']]))

				# Определяем артикул
				article=row[num['article']]

				# Получаем объект товара
				product = Product.objects.take(article=article, vendor=self.vendor, name=name, category = category_synonym.category, unit = self.default_unit)

				# Указываем категорию
				if not product.category and category_synonym.category:
					product.category = category_synonym.category
					product.save()

				# Добавляем партии
				price = self.fixPrice(row[num['price']])
				party = Party.objects.make(product=product, stock=self.factory, price = price, price_type = self.rrp, currency = self.usd, quantity = -1, unit = self.default_unit)
				print(product.article + ' = ' + str(party.price) + ' ' + party.currency.alias + ' ' + party.price_type.alias)

		print("Обработка прайс-листа оборудования завершена.")
		return True

	def parseCables(self, xls_data):

		import xlrd

		# Номера строк и столбцов
		num = {'header': 4}

		# Распознаваемые слова
		word = {
			'article': 'Part Number',
			'model': 'Модель',
			'name': 'Описание',
			'size': 'Метры',
			'price': 'Цена,     $',
			'dop': 'Примечание',
			'category_name': ''}

		book = xlrd.open_workbook(file_contents=xls_data.read())
		sheet = book.sheet_by_index(0)
		for row_num in range(sheet.nrows):
			row = sheet.row_values(row_num)

			# Пустые строки
			if row_num < num['header']:
				continue

			# Заголовок таблицы
			elif row_num == num['header']:
				for cel_num, cel in enumerate(row):
					if   str(cel).strip() == word['article']: num['article'] = cel_num
					elif str(cel).strip() == word['model']: num['model'] = cel_num
					elif str(cel).strip() == word['name']:  num['name'] = cel_num
					elif str(cel).strip() == word['size']:  num['size'] = cel_num
					elif str(cel).strip() == word['price']: num['price'] = cel_num
					elif str(cel).strip() == word['dop']:   num['dop'] = cel_num

				# Проверяем, все ли столбцы распознались
				if not num['article'] or not num['model'] or not num['name'] or not num['size'] or not num['price'] or not num['dop']:
					print("Ошибка структуры данных: не все столбцы опознаны.")
					return False
				else: print("Структура данных без изменений.")

			# Категория
			elif row[num['name']] and not row[num['article']] and not row[num['price']]:
				word['category_name'] = row[num['name']]
				category_synonym = CategorySynonym.objects.take(name="Cables: %s" % (word['category_name']), updater=self.updater, distributor=self.distributor)

			# Товар
			elif row[num['name']] and row[num['article']] and row[num['price']]:

				# Определяем имя
				name = self.vendor.name + ' ' + str(row[num['model']]) + ' ' + str(row[num['name']])
				if row[num['size']]: name += ' (длина: ' + str(row[num['size']]).replace('.', ',') + ' м.)'

				# Определяем артикул
				article=row[num['article']]

				# Получаем объект товара
				product = Product.objects.take(article=article, vendor=self.vendor, name=name, category = category_synonym.category, unit = self.default_unit)

				# Указываем категорию
				if not product.category and category_synonym.category:
					product.category = category_synonym.category
					product.save()

				# Добавляем партии
				price = self.fixPrice(row[num['price']])
				party = Party.objects.make(product=product, stock=self.factory, price = price, price_type = self.rrp, currency = self.usd, quantity = -1, unit = self.default_unit)
				print(product.article + ' = ' + str(party.price) + ' ' + party.currency.alias + ' ' + party.price_type.alias)

		print("Обработка прайс-листа материалов завершена.")
		return True

	def fixPrice(self, price):
		if price in ('CALL', '?'): price = None
		else: price = float(price)
		return price
