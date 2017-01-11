import uuid
from django.db import models
from django.utils import timezone


class DistributorManager(models.Manager):


	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
		return result


	def take(self, *args, **kwargs):

		alias = str(kwargs.get('alias', '')).strip()
		name  = str(kwargs.get('name', '')).strip()

		if not alias:
			return None

		try:
			result = self.get(alias = alias)

		except Distributor.DoesNotExist:

			if not name:
				return None

			result = Distributor(
				alias    = alias,
				name     = name)
			result.save()

		return result


class Distributor(models.Model):

	id          = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)

	name        = models.TextField(db_index = True)
	alias       = models.TextField(unique = True)
	description = models.TextField(null = True, default = '')

	state       = models.BooleanField(default = True, db_index = True)
	created     = models.DateTimeField(default = timezone.now, db_index = True)
	modified    = models.DateTimeField(default = timezone.now, db_index = True)

	objects     = DistributorManager()


	def get_dicted(self):

		result = {}

		result['id']          = str(self.id)
		result['name']        = self.name
		result['alias']       = self.alias
		result['description'] = self.description
		result['state']       = self.state
		result['created']     = str(self.created)
		result['modified']    = str(self.modified)

		return result


	def __str__(self):
		return self.name


	class Meta:
		ordering = ['name']


class UpdaterManager(models.Manager):


	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
		return result


	def take(self, alias, name, distributor = None):

		try:
			updater = self.get(alias = alias)
		except Updater.DoesNotExist:
			updater = Updater(
				alias       = alias,
				name        = name,
				distributor = distributor)
			updater.save()
		return updater


class Updater(models.Model):

	id          = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
	distributor = models.ForeignKey(Distributor, related_name = '+', null = True, default = None)

	name        = models.TextField(db_index = True)
	alias       = models.TextField(unique = True)
	login       = models.TextField(null = True, default = '')
	password    = models.TextField(null = True, default = '')
	updated     = models.DateTimeField(default = timezone.now)

	state       = models.BooleanField(default = True, db_index = True)
	created     = models.DateTimeField(default = timezone.now, db_index = True)
	modified    = models.DateTimeField(default = timezone.now, db_index = True)

	objects     = UpdaterManager()


	def get_dicted(self):

		result = {}

		result['id']       = str(self.id)
		result['name']     = self.name
		result['alias']    = self.alias
		result['login']    = self.login
		result['password'] = self.password
		result['state']    = self.state
		result['updated']  = str(self.updated)
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)

		try:
			result['distributor'] = self.distributor.get_dicted()
		except Exception:
			result['distributor'] = None

		return result


	def __str__(self):
		return self.name


	class Meta:
		ordering = ['name']


class StockManager(models.Manager):


	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
		return result


	def take(self, alias, name, delivery_time_min = 10, delivery_time_max = 20,
			distributor=None):

		try:
			stock = self.get(alias = alias)
		except Stock.DoesNotExist:
			stock = Stock(
				alias             = alias,
				name              = name,
				delivery_time_min = delivery_time_min,
				delivery_time_max = delivery_time_max,
				distributor       = distributor)
			stock.save()
		return stock


class Stock(models.Model):

	id                = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
	distributor       = models.ForeignKey(Distributor, related_name = '+', null = True, default = None)

	name              = models.TextField(db_index = True)
	alias             = models.TextField(unique = True)
	description       = models.TextField(null = True, default = '')
	delivery_time_min = models.BigIntegerField(db_index = True)
	delivery_time_max = models.BigIntegerField(db_index = True)
	state             = models.BooleanField(default = True, db_index = True)
	created           = models.DateTimeField(default = timezone.now, db_index = True)
	modified          = models.DateTimeField(default = timezone.now, db_index = True)

	objects           = StockManager()


	def get_dicted(self):

		result = {}

		result['id']                = str(self.id)
		result['name']              = self.name
		result['alias']             = self.alias
		result['delivery_time_min'] = self.delivery_time_min
		result['delivery_time_max'] = self.delivery_time_max
		result['state']             = self.state
		result['created']           = str(self.created)
		result['modified']          = str(self.modified)

		try:
			result['distributor'] = self.distributor.get_dicted()
		except Exception:
			result['distributor'] = None

		return result


	def __str__(self):
		return self.name


	class Meta:
		ordering = ['name']


class CategoryManager(models.Manager):


	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
		return result


	def getCategoryTree(self, tree, parent = None):
		"Функция: дерево категорий (используется рекурсия)."

		# Получаем список дочерних категорий
		categories = self.filter(parent = parent).order_by('order')

		# Проходим по списку категорий с рекурсивным погружением
		for category in categories:
			tree.append(category)
			tree = self.getCategoryTree(tree, category)

		return tree


	def getCategoryHTMLTree(self, root, parent = None, first = None):
		"Функция: дерево категорий (используется рекурсия)."

		# Импортируем
		from lxml import etree

		# Получаем список дочерних категорий
		categories = self.filter(parent = parent).filter(state = True).order_by('order')

		# Проходим по списку категорий с рекурсивным погружением
		if len(categories):
			ul = etree.SubElement(root, "ul")
			ul.attrib['class'] = 'no-bullet'
			if first:
				li = etree.SubElement(ul, "li")
				i = etree.SubElement(li, "i")
				i.text = ''
				i.attrib['class'] = 'fa fa-circle-thin'
				a = etree.SubElement(li, "a")
				a.attrib['data-do'] = 'filter-products-select-category'
				a.attrib['data-id'] = ''
				a.attrib['class'] = 'tm-li-category-name'
				a.text = 'Все категории'

			for category in categories:
				li = etree.SubElement(ul, "li")

				# Если есть дочерние
				childs = self.filter(parent=category).filter(state=True).order_by('order')
				if len(childs):
					li.attrib['class'] = 'closed'
					i = etree.SubElement(li, "i")
					i.attrib['data-do'] = 'switch-li-status'
					i.attrib['data-state'] = 'closed'
					i.text = ''
					i.attrib['class'] = 'fa fa-plus-square-o'
				else:
					i = etree.SubElement(li, "i")
					i.text = ''
					i.attrib['class'] = 'fa fa-circle-thin'
				a = etree.SubElement(li, "a")
				a.attrib['data-do'] = 'filter-products-select-category'
				a.attrib['data-id'] = str(category.id)
				a.attrib['class'] = 'tm-li-category-name'
				a.text = category.name
				self.getCategoryHTMLTree(li, category)

		# Возвращаем результат
		return root


class Category(models.Model):

	id          = models.BigAutoField(primary_key = True)
	parent      = models.ForeignKey('self', related_name = '+', null = True, default = None)

	name        = models.TextField(db_index = True)
	alias       = models.TextField(null = True, default = '', db_index = True)
	description = models.TextField(null = True, default = '')
	level       = models.BigIntegerField(default = 0, db_index = True)
	order       = models.BigIntegerField(default = 999999, db_index = True)
	path        = models.TextField(null = True, default = '', db_index = True)

	state       = models.BooleanField(default = True, db_index = True)
	created     = models.DateTimeField(default = timezone.now, db_index = True)
	modified    = models.DateTimeField(default = timezone.now, db_index = True)

	objects     = CategoryManager()


	def get_dicted(self):

		result = {}

		result['id']           = str(self.id)
		result['name']         = self.name
		result['name_leveled'] = '— ' * self.level + self.name
		result['alias']        = self.alias
		result['description']  = self.description
		result['level']        = self.level
		result['order']        = self.order
		result['path']         = self.path
		result['state']        = self.state
		result['created']      = str(self.created)
		result['modified']     = str(self.modified)

		try:
			result['parent'] = self.parent.get_dicted()
		except Exception:
			result['parent'] = None

		return result


	def __str__(self):
		return self.name


	class Meta:
		ordering = ['order']


class VendorManager(models.Manager):


	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
		return result


	def take(self, alias, name):
		try:
			vendor = self.get(alias=alias)
		except Vendor.DoesNotExist:
			vendor = Vendor(
				alias = alias,
				name  = name)
			vendor.save()
		return vendor


class Vendor(models.Model):

	id          = models.BigAutoField(primary_key = True)

	name        = models.TextField(unique = True)
	alias       = models.TextField(unique = True)
	description = models.TextField(null = True, default = '')

	state       = models.BooleanField(default = True, db_index = True)
	created     = models.DateTimeField(default = timezone.now, db_index = True)
	modified    = models.DateTimeField(default = timezone.now, db_index = True)

	objects     = VendorManager()


	def get_dicted(self):

		result = {}

		result['id']          = str(self.id)
		result['name']        = self.name
		result['alias']       = self.alias
		result['description'] = self.description
		result['state']       = self.state
		result['created']     = str(self.created)
		result['modified']    = str(self.modified)

		return result


	def __str__(self):
		return self.name


	class Meta:
		ordering = ['name']


class UnitManager(models.Manager):


	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
		return result


	def take(self, alias, name):
		try:
			unit = self.get(alias=alias)
		except Unit.DoesNotExist:
			unit = Unit(
				alias = alias,
				name  = name)
			unit.save()
		return unit


class Unit(models.Model):

	id             = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)

	name           = models.TextField(db_index = True)
	name_short     = models.TextField(null = True, default = '', db_index = True)
	name_short_xml = models.TextField(null = True, default = '')
	alias          = models.TextField(unique = True)

	state          = models.BooleanField(default = True, db_index = True)
	created        = models.DateTimeField(default = timezone.now, db_index = True)
	modified       = models.DateTimeField(default = timezone.now, db_index = True)

	objects  = UnitManager()


	def get_dicted(self):

		result = {}

		result['id']             = str(self.id)
		result['name']           = self.name
		result['name_short']     = self.name_short
		result['name_short_xml'] = self.name_short_xml
		result['alias']          = self.alias
		result['state']          = self.state
		result['created']        = str(self.created)
		result['modified']       = str(self.modified)

		return result


	def __str__(self):
		return self.name


	class Meta:
		ordering = ['name']


class PriceTypeManager(models.Manager):


	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
		return result


	def take(self, alias, name):
		try:
			price_type = self.get(alias=alias)
		except PriceType.DoesNotExist:
			price_type = PriceType(
				alias = alias,
				name  = name)
			price_type.save()
		return price_type


class PriceType(models.Model):

	id         = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)

	name       = models.TextField(db_index = True)
	alias      = models.TextField(unique = True)
	multiplier = models.DecimalField(max_digits = 10, decimal_places = 4, default = 1.0, db_index = True)

	state      = models.BooleanField(default = True, db_index = True)
	created    = models.DateTimeField(default = timezone.now, db_index = True)
	modified   = models.DateTimeField(default = timezone.now, db_index = True)

	objects    = PriceTypeManager()

	def get_dicted(self):

		result = {}

		result['id']         = str(self.id)
		result['name']       = self.name
		result['alias']      = self.alias
		result['state']      = self.state
		result['multiplier'] = str(self.multiplier)
		result['created']    = str(self.created)
		result['modified']   = str(self.modified)

		return result

	def __str__(self):
		return self.name


	class Meta:
		ordering = ['name']


class CurrencyManager(models.Manager):


	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
		return result


	def take(self, alias, name, full_name, rate = 1, quantity = 1):
		try:
			currency = self.get(alias = alias)
		except Currency.DoesNotExist:
			currency = Currency(
				alias     = alias,
				name      = name,
				full_name = full_name,
				rate      = rate,
				quantity  = quantity)
			currency.save()

		return currency


class Currency(models.Model):

	id        = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)

	name      = models.TextField(db_index = True)
	full_name = models.TextField(db_index = True)
	alias     = models.TextField(unique = True)
	rate      = models.DecimalField(max_digits = 10, decimal_places = 4, db_index = True)
	quantity  = models.DecimalField(max_digits = 10, decimal_places = 3, db_index = True)

	state     = models.BooleanField(default = True, db_index = True)
	created   = models.DateTimeField(default = timezone.now, db_index = True)
	modified  = models.DateTimeField(default = timezone.now, db_index = True)

	objects   = CurrencyManager()


	def get_dicted(self):

		result = {}

		result['id']        = str(self.id)
		result['name']      = self.name
		result['full_name'] = self.full_name
		result['alias']     = self.alias
		result['rate']      = str(self.rate)
		result['quantity']  = str(self.quantity)
		result['state']     = self.state
		result['created']   = str(self.created)
		result['modified']  = str(self.modified)

		return result


	def __str__(self):
		return self.name


	class Meta:
		ordering = ['alias']


class Price(models.Model):

	id         = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
	price_type = models.ForeignKey(PriceType, related_name = '+', null = True, default = None)
	currency   = models.ForeignKey(Currency,  related_name = '+', null = True, default = None)

	price      = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, default = None, db_index = True)
	fixed      = models.BooleanField(default = False, db_index = True)

	state      = models.BooleanField(default = True, db_index = True)
	created    = models.DateTimeField(default = timezone.now, db_index = True)
	modified   = models.DateTimeField(default = timezone.now, db_index = True)


	def get_dicted(self):

		result = {}

		result['id']       = str(self.id)
		result['price']    = str(self.price)
		result['fixed']    = self.fixed
		result['state']    = self.state
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)

		try:
			result['price_type'] = self.price_type.get_dicted()
		except Exception:
			result['price_type'] = None

		try:
			result['currency'] = self.currency.get_dicted()
		except Exception:
			result['currency'] = None

		result['price_str'] = self._get_price_str()
		result['price_xml'] = self._get_price_xml()

		return result


	def _get_price_str(self):

		try:
			price    = self.price
			currency = self.currency
		except Exception:
			return ''

		if price:
			price = '{:,}'.format(round(price, 2))
			price = price.replace(',', ' ')
			price = price.replace('.', ',')
			price = price + ' ' + currency.name
		else:
			return ''

		return price

	price_str = property(_get_price_str)


	def _get_price_xml(self):

		try:
			price    = self.price
			currency = self.currency
		except:
			return ''

		if price:
			price = '{:,}'.format(round(price, 2))
			price = price.replace(',', '&nbsp;')
			price = price.replace('.', ',')
			price = price + '&nbsp;' + currency.name
		else:
			return '<i class="fa fa-phone"></i>'

		return price

	price_xml = property(_get_price_xml)


	class Meta:
		ordering = ['-created']


class Quantity(models.Model):

	id         = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
	unit       = models.ForeignKey(Unit, related_name = '+', null = True, default = None)

	on_stock   = models.BigIntegerField(null = True, default = 0, db_index = True)
	on_transit = models.BigIntegerField(null = True, default = 0, db_index = True)
	on_factory = models.BigIntegerField(null = True, default = 0, db_index = True)
	fixed      = models.BooleanField(default = False, db_index = True)

	state      = models.BooleanField(default = True, db_index = True)
	created    = models.DateTimeField(default = timezone.now, db_index = True)
	modified   = models.DateTimeField(default = timezone.now, db_index = True)


	def get_dicted(self):

		result = {}

		result['id']         = str(self.id)
		result['on_stock']   = self.on_stock
		result['on_transit'] = self.on_transit
		result['on_factory'] = self.on_factory
		result['fixed']      = self.fixed
		result['state']      = self.state
		result['created']    = str(self.created)
		result['modified']   = str(self.modified)

		try:
			result['unit'] = self.unit.get_dicted()
		except Exception:
			result['unit'] = None

		return result


	def _get_on_stock_xml(self):

		try:

			if self.on_stock == -1:
				quantity = '&infin;'
			elif self.on_stock:
				quantity = str(self.on_stock)
			elif self.on_stock is None:
				quantity = '?'
			else:
				quantity = ''
		except:
			quantity = ''

		return quantity


	def _get_on_transit_xml(self):

		try:

			if self.on_transit == -1:
				quantity = '&infin;'
			elif self.on_transit:
				quantity = str(self.on_transit)
			elif self.on_transit is None:
				quantity = '?'
			else:
				quantity = ''
				
		except Exception:
			quantity = ''

		return quantity


	def _get_on_factory_xml(self):

		try:

			if self.on_factory == -1:
				quantity = '&infin;'
			elif self.on_factory:
				quantity = str(self.on_factory)
			elif self.on_factory is None:
				quantity = '?'
			else:
				quantity = ''
		except Exception:
			quantity = ''

		return quantity


	on_stock_xml   = property(_get_on_stock_xml)
	on_transit_xml = property(_get_on_transit_xml)
	on_factory_xml = property(_get_on_factory_xml)


	class Meta:
		ordering = ['-created']


class ProductManager(models.Manager):


	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
		return result


	def take(self, article, vendor, name, category = None, unit = None,
			description = None):

		# TODO NEED Refactoring
		name = str(name).strip()
		name = name.replace("\u00AD", "")
		name = name.replace("™", "")
		name = name.replace("®", "")

		article = str(article).strip()
		article = article.replace("\u00AD", "")
		article = article.replace("™", "")
		article = article.replace("®", "")
		article = article

		try:
			product = self.get(article = article, vendor = vendor)
			if not product.category and category:
				product.category = category
				product.modified = timezone.now()
				product.save()
			if not product.description and description:
				product.description = description
				product.modified    = timezone.now()
				product.save()
		except Product.DoesNotExist:
			product = Product(
				name        = name,
				article     = article,
				vendor      = vendor,
				category    = category,
				unit        = unit)
			product.save()
		except Product.MultipleObjectsReturned:
			print("MultipleObjectsReturned: {} {}".format(vendor, article))
			products = self.filter(article = article, vendor = vendor)
			product  = products[0]

		if product.duble:
			product = self.get(id = product.duble)

		print('{} {}'.format(
			product.vendor,
			product.article))

		return product


class Product(models.Model):

	id          = models.BigAutoField(primary_key = True)
	vendor      = models.ForeignKey(Vendor,   related_name = '+')
	category    = models.ForeignKey(Category, related_name = '+', null = True, default = None)
	unit        = models.ForeignKey(Unit,     related_name = '+', null = True, default = None)
	duble       = models.ForeignKey('self',   related_name = '+', null = True, default = None)
	price       = models.ForeignKey(Price,    related_name = '+', null = True, default = None)
	quantity    = models.ForeignKey(Quantity, related_name = '+', null = True, default = None)

	name        = models.TextField(db_index = True)
	article     = models.TextField(db_index = True)
	description = models.TextField(null = True, default = '')
	edited      = models.BooleanField(default = False, db_index = True)
	for_export  = models.BooleanField(default = False, db_index = True)

	state       = models.BooleanField(default = True, db_index = True)
	created     = models.DateTimeField(default = timezone.now, db_index = True)
	modified    = models.DateTimeField(default = timezone.now, db_index = True)

	objects     = ProductManager()


	def get_dicted(self):

		result = {}

		result['id']          = str(self.id)
		result['name']        = self.name
		result['article']     = self.article
		result['description'] = self.description
		result['edited']      = self.edited
		result['for_export']  = self.for_export
		result['state']       = self.state
		result['created']     = str(self.created)
		result['modified']    = str(self.modified)

		try:
			result['vendor'] = self.vendor.get_dicted()
		except Exception:
			result['vendor'] = None

		try:
			result['category'] = self.category.get_dicted()
		except Exception:
			result['category'] = None

		try:
			result['unit'] = self.unit.get_dicted()
		except Exception:
			result['unit'] = None

		try:
			result['duble'] = self.duble.get_dicted()
		except Exception:
			result['duble'] = None

		try:
			result['price'] = self.price.get_dicted()
		except Exception:
			result['price'] = None

		try:
			result['quantity'] = self.quantity.get_dicted()
		except Exception:
			result['quantity'] = None

		return result


	def __str__(self):
		return self.name


	# TODO Need rafactoring
	def recalculate(self):

		# Определяем переменные
		rp = PriceType.objects.take(
			alias = 'RP',
			name  = 'Розничная цена')

		rub = Currency.objects.take(
			alias     = 'RUB',
			name      = 'р.',
			full_name = 'Российский рубль',
			rate      = 1,
			quantity  = 1)

		# Получаем объекты количества и цены
		if self.quantity is None:
			quantity = Quantity()
			quantity.save()
			self.quantity = quantity
			self.save()

		if self.price is None:
			price = Price()
			price.save()
			self.price = price
			self.save()

		# Вычисляем количество товара
		quantities = {
			'stock'   : [0],
			'transit' : [0],
			'factory' : [0]}

		undef = {
			'stock'   : None,
			'transit' : None,
			'factory' : None}

		prices = []
		prices_null = []

		# Проходим по всем партиям продукта
		for party in Party.objects.filter(product = self, stock__state = True, stock__distributor__state = True):

			if party.quantity:

				if 'stock' in party.stock.alias:
					quantities['stock'].append(party.quantity)
					undef['stock'] = False
				elif 'transit' in party.stock.alias:
					quantities['transit'].append(party.quantity)
					undef['transit'] = False
				elif 'factory' in party.stock.alias \
						or 'delivery' in party.stock.alias \
						or 'order' in party.stock.alias:
					quantities['factory'].append(party.quantity)
					undef['factory'] = False

			elif party.quantity is None:

				if 'stock' in party.stock.alias and undef['stock'] is None:
					undef['stock'] = True
				elif 'transit' in party.stock.alias and undef['transit'] is None:
					undef['transit'] = True
				elif ('factory' in party.stock.alias \
						or 'delivery' in party.stock.alias \
						or 'order' in party.stock.alias) \
						and undef['transit'] is None:
					undef['factory'] = True

			if party.quantity != 0:

				if party.price and party.currency and party.price_type:
					prices.append(party.price * party.currency.rate * party.price_type.multiplier / party.currency.quantity)

			else:

				if party.price and party.currency and party.price_type:
					prices_null.append(party.price * party.currency.rate * party.price_type.multiplier / party.currency.quantity)

		# Записываем информацию в базу
		if -1 in quantities['stock']:
			self.quantity.on_stock = -1
		elif undef['stock']:
			self.quantity.on_stock = None
		else:
			self.quantity.on_stock = sum(quantities['stock'])

		if -1 in quantities['transit']:
			self.quantity.on_transit = -1
		elif undef['transit']:
			self.quantity.on_transit = None
		else:
			self.quantity.on_transit = sum(quantities['transit'])

		if -1 in quantities['factory']:
			self.quantity.on_factory = -1
		elif undef['factory']:
			self.quantity.on_factory = None
		else:
			self.quantity.on_factory = sum(quantities['factory'])

		self.quantity.modified = timezone.now()
		self.quantity.save()

		if len(prices):
			self.price.price      = min(prices)
			self.price.price_type = rp
			self.price.currency   = rub
		elif len(prices_null):
			self.price.price      = min(prices_null)
			self.price.price_type = rp
			self.price.currency   = rub
		else:
			self.price.price      = None
			self.price.price_type = rp
			self.price.currency   = rub

		self.price.modified = timezone.now()
		self.price.save()


	def get_parameter_to_product(self, parameter_alias):

		try:
			parameter = Parameter.objects.get(alias = parameter_alias)
		except Exception:
			return None

		try:
			parameter_to_product = ParameterToProduct.objects.get(
				product = self,
				parameter = parameter)
		except Exception:
			parameter_to_product = ParameterToProduct(
				product   = self,
				parameter = parameter)
			parameter_to_product.save()

		return parameter_to_product


	class Meta:
		ordering = ['name']


class PartyManager(models.Manager):


	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
		return result


	def make(self, product, stock, article = None,
			price = None, price_type = None, currency = None,
			price_out = None, price_type_out = None, currency_out = None,
			quantity = None, unit = None, product_name = '', time = None):

		if time:
			Party.objects.filter(product = product, stock = stock, created__lt = time).delete()

		party = Party(
			product        = product,
			stock          = stock,
			article        = article,
			price          = price,
			price_type     = price_type,
			currency       = currency,
			price_out      = price_out,
			price_type_out = price_type_out,
			currency_out   = currency,
			quantity       = quantity,
			unit           = unit,
			product_name   = product_name)
		party.save()

		print('{} {} = {}; {} on {}'.format(
			party.product.vendor.name,
			party.product.article,
			party.price_str,
			party.quantity,
			party.stock.alias))

		party.product.recalculate()

		return party


	def clear(self, stock, time = None):
		if time:
			Party.objects.filter(stock = stock, created__lt = time).delete()
		else:
			Party.objects.filter(stock = stock).delete()
		return True


class Party(models.Model):

	id             = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
	product        = models.ForeignKey(Product,   related_name = '+')
	stock          = models.ForeignKey(Stock,     related_name = '+')
	price_type     = models.ForeignKey(PriceType, related_name = '+', null = True, default = None)
	currency       = models.ForeignKey(Currency,  related_name = '+', null = True, default = None)
	price_type_out = models.ForeignKey(PriceType, related_name = '+', null = True, default = None)
	currency_out   = models.ForeignKey(Currency,  related_name = '+', null = True, default = None)
	unit           = models.ForeignKey(Unit,      related_name = '+', null = True, default = None)

	article        = models.TextField(null = True, default = None, db_index = True) # Артикул поставщика
	price          = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, default = None, db_index = True)
	price_out      = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, default = None, db_index = True)
	quantity       = models.BigIntegerField(null = True, default = None, db_index = True)
	product_name   = models.TextField(null = True, default = None)

	state          = models.BooleanField(default = True, db_index = True)
	created        = models.DateTimeField(default = timezone.now, db_index = True)
	modified       = models.DateTimeField(default = timezone.now, db_index = True)

	objects        = PartyManager()


	def get_dicted(self):

		result = {}

		result['id']           = str(self.id)
		result['article']      = self.article
		result['price']        = str(self.price)
		result['price_out']    = self.price_out
		result['quantity']     = self.description
		result['comment']      = self.comment
		result['product_name'] = self.comment
		result['state']        = self.state
		result['created']      = str(self.created)
		result['modified']     = str(self.modified)

		try:
			result['product'] = self.product.get_dicted()
		except Exception:
			result['product'] = None

		try:
			result['stock'] = self.stock.get_dicted()
		except Exception:
			result['stock'] = None

		try:
			result['price_type'] = self.price_type.get_dicted()
		except Exception:
			result['price_type'] = None

		try:
			result['currency'] = self.currency.get_dicted()
		except Exception:
			result['currency'] = None

		try:
			result['price_type_out'] = self.price_type_out.get_dicted()
		except Exception:
			result['price_type_out'] = None

		try:
			result['currency_out'] = self.currency_out.get_dicted()
		except Exception:
			result['currency_out'] = None

		try:
			result['unit'] = self.unit.get_dicted()
		except Exception:
			result['unit'] = None

		result['price_str']     = self._get_price_str()
		result['price_xml']     = self._get_price_xml()
		result['price_out_str'] = self._get_price_out_str()
		result['price_out_xml'] = self._get_price_out_xml()

		return result


	def _get_price_str(self):

		try:
			price = self.price
			currency = self.currency
		except: return ''

		if price:
			price = '{:,}'.format(round(price, 2))
			price = price.replace(',', ' ')
			price = price.replace('.', ',')
			price = price + ' ' + currency.name
		else: return ''

		return price

	price_str = property(_get_price_str)


	def _get_price_xml(self):

		try:
			price = self.price
			currency = self.currency
		except: return ''

		if price:
			price = '{:,}'.format(round(price, 2))
			price = price.replace(',', '&nbsp;')
			price = price.replace('.', ',')
			price = price + '&nbsp;' + currency.name
		else: return ''

		return price

	price_xml = property(_get_price_xml)


	def _get_price_out_str(self):
		try:
			price = self.price_out * self.currency_out.rate / self.currency_out.quantity
		except:
			try:
				price = self.price * self.price_type.multiplier * self.currency.rate / self.currency.quantity
			except: return ''

		currency = Currency.objects.take(
			alias     = 'RUB',
			name      = 'р.',
			full_name = 'Российский рубль',
			rate      = 1,
			quantity  = 1)

		if price:
			price = '{:,}'.format(round(price, 2))
			price = price.replace(',', '&nbsp;')
			price = price.replace('.', ',')
			price = price + '&nbsp;' + currency.name
		else: return ''

		return price

	price_out_str = property(_get_price_out_str)


	class Meta:
		ordering = ['-created']


class PartyHystory(models.Model):

	id             = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
	product        = models.ForeignKey(Product,   related_name = '+')
	stock          = models.ForeignKey(Stock,     related_name = '+')
	price_type     = models.ForeignKey(PriceType, related_name = '+', null = True, default = None)
	currency       = models.ForeignKey(Currency,  related_name = '+', null = True, default = None)
	price_type_out = models.ForeignKey(PriceType, related_name = '+', null = True, default = None)
	currency_out   = models.ForeignKey(Currency,  related_name = '+', null = True, default = None)

	price          = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, default = None)
	price_out      = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, default = None)
	quantity       = models.BigIntegerField(null = True, default = None)
	unit           = models.ForeignKey(Unit, null = True, default = None, db_index = True)
	date           = models.DateField(db_index = True)


	def get_dicted(self):

		result = {}

		result['id']        = str(self.id)
		result['article']   = self.article
		result['price']     = str(self.price)
		result['price_out'] = self.price_out
		result['quantity']  = self.description
		result['comment']   = self.comment
		result['date']      = str(self.date)

		try:    result['product']        = self.product.get_dicted()
		except: result['product']        = None

		try:    result['stock']          = self.stock.get_dicted()
		except: result['stock']          = None

		try:    result['price_type']     = self.price_type.get_dicted()
		except: result['price_type']     = None

		try:    result['currency']       = self.currency.get_dicted()
		except: result['currency']       = None

		try:    result['price_type_out'] = self.price_type_out.get_dicted()
		except: result['price_type_out'] = None

		try:    result['currency_out']   = self.currency_out.get_dicted()
		except: result['currency_out']   = None

		try:    result['unit']           = self.unit.get_dicted()
		except: result['unit']           = None

		return result

	class Meta:
		ordering = ['-date']


class PriceHystory(models.Model):

	id         = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
	product    = models.ForeignKey(Product)
	price_type = models.ForeignKey(PriceType, null = True, default = None)
	currency   = models.ForeignKey(Currency, null = True, default = None)

	price      = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, default = None)
	date       = models.DateField(db_index = True)


	def get_dicted(self):

		result = {}

		result['id']    = str(self.id)
		result['price'] = str(self.price)
		result['date']  = str(self.date)

		try:    result['product']    = self.product.get_dicted()
		except: result['product']    = None

		try:    result['price_type'] = self.price_type.get_dicted()
		except: result['price_type'] = None

		try:    result['currency']   = self.currency.get_dicted()
		except: result['currency']   = None

		return result


	class Meta:
		ordering = ['-date']


class QuantityHystory(models.Model):

	id         = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
	product    = models.ForeignKey(Product, related_name = '+')
	unit       = models.ForeignKey(Unit,    related_name = '+', null = True, default = None)

	on_stock   = models.BigIntegerField(null = True, default = None)
	on_transit = models.BigIntegerField(null = True, default = None)
	on_factory = models.BigIntegerField(null = True, default = None)

	date       = models.DateField()


	def get_dicted(self):

		result = {}

		result['id']         = str(self.id)
		result['on_stock']   = self.on_stock
		result['on_transit'] = self.on_transit
		result['on_factory'] = self.on_factory
		result['date']       = str(self.date)

		try:    result['product'] = self.product.get_dicted()
		except: result['product'] = None

		try:    result['unit']    = self.unit.get_dicted()
		except: result['unit']    = None

		return result

	class Meta:
		ordering = ['-date']


class ParameterTypeManager(models.Manager):

	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
		return result


class ParameterType(models.Model):

	id        = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)

	name      = models.TextField(unique = True)
	alias     = models.TextField(unique = True)
	order     = models.BigIntegerField(default = 0, db_index = True)

	state     = models.BooleanField(default = True, db_index = True)
	created   = models.DateTimeField(default = timezone.now, db_index = True)
	modified  = models.DateTimeField(default = timezone.now, db_index = True)

	objects   = ParameterTypeManager()

	def get_dicted(self):

		result = {}

		result['id']       = str(self.id)
		result['name']     = self.name
		result['alias']    = self.alias
		result['order']    = self.order
		result['state']    = self.state
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)

		return result

	def __str__(self):
		return self.alias

	class Meta:
		ordering = ['name']


class ParameterManager(models.Manager):

	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
		return result


class Parameter(models.Model):

	id            = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
	parametertype = models.ForeignKey(ParameterType, related_name = '+', null = True, default = None)
	unit          = models.ForeignKey(Unit,          related_name = '+', null = True, default = None)

	name          = models.TextField(unique = True)
	alias         = models.TextField(unique = True)
	order         = models.BigIntegerField(default = 0, db_index = True)

	state         = models.BooleanField(default = True, db_index = True)
	created       = models.DateTimeField(default = timezone.now, db_index = True)
	modified      = models.DateTimeField(default = timezone.now, db_index = True)

	objects        = ParameterManager()

	def get_dicted(self):

		result = {}

		result['id']       = str(self.id)
		result['name']     = self.name
		result['alias']    = self.alias
		result['order']    = self.order
		result['state']    = self.state
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)

		try:
			result['parametertype'] = self.parametertype.get_dicted()
		except Exception:
			result['parametertype'] = None

		return result

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['order', 'name']


class ParameterValueManager(models.Manager):

	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
		return result


class ParameterValue(models.Model):

	id          = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
	parameter   = models.ForeignKey(Parameter, related_name = '+')

	name        = models.TextField(db_index = True)
	order       = models.BigIntegerField(db_index = True)

	state       = models.BooleanField(default = True, db_index = True)
	created     = models.DateTimeField(default = timezone.now, db_index = True)
	modified    = models.DateTimeField(default = timezone.now, db_index = True)

	objects      = ParameterValueManager()

	def get_dicted(self):

		result = {}

		result['id']           = str(self.id)
		result['name']         = self.name
		result['order']        = self.order
		result['state']        = self.state
		result['created']      = str(self.created)
		result['modified']     = str(self.modified)

		try:
			result['parameter'] = self.parameter.get_dicted()
		except Exception:
			result['parameter'] = None

		return result

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['order', 'name']


class ParameterValueSynonymManager(models.Manager):


	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
		return result


	def take(self, name, updater = None, parameter = None):

		name = name.strip()

		try:
			value_synonym = self.get(
				name        = name,
				updater     = updater)
		except ParameterValueSynonym.DoesNotExist:
			value_synonym = ParameterValueSynonym(
				name        = name,
				updater     = updater,
				parameter   = parameter)
			value_synonym.save()

		return value_synonym


class ParameterValueSynonym(models.Model):

	id             = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
	updater        = models.ForeignKey(Updater,        related_name = '+', null = True, default = None)
	parameter      = models.ForeignKey(Parameter,      related_name = '+', null = True, default = None)
	parametervalue = models.ForeignKey(ParameterValue, related_name = '+', null = True, default = None)

	name           = models.TextField()

	state          = models.BooleanField(default = True, db_index = True)
	created        = models.DateTimeField(default = timezone.now, db_index = True)
	modified       = models.DateTimeField(default = timezone.now, db_index = True)

	objects        = ParameterValueSynonymManager()

	def get_dicted(self):

		result = {}

		result['id']       = str(self.id)
		result['name']     = self.name
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)

		try:
			result['updater'] = self.updater.get_dicted()
		except Exception:
			result['updater'] = None

		try:
			result['parameter'] = self.parameter.get_dicted()
		except Exception:
			result['parameter'] = None

		try:
			result['parametervalue'] = self.parametervalue.get_dicted()
		except Exception:
			result['parametervalue'] = None

		return result

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']


class ParameterToProductManager(models.Manager):

	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
		return result

	def take(self, parameter, product):

		try:
			parameter_to_product = self.get(
				parameter = parameter,
				product   = product)
		except ParameterToProduct.DoesNotExist:
			parameter_to_product = ParameterToProduct(
				parameter = parameter,
				product   = product)
			parameter_to_product.save()

		return parameter_to_product


class ParameterToProduct(models.Model):

	id            = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
	parameter     = models.ForeignKey(Parameter,      related_name = '+')
	product       = models.ForeignKey(Product,        related_name = '+')
	value_list    = models.ForeignKey(ParameterValue, related_name = '+', null = True, default = None)

	value_text    = models.TextField(null = True, default = None, db_index = True)
	value_integer = models.BigIntegerField(null = True, default = None, db_index = True)
	value_decimal = models.DecimalField(max_digits = 20, decimal_places = 2, null = True, default = None, db_index = True)

	state         = models.BooleanField(default = True, db_index = True)
	created       = models.DateTimeField(default = timezone.now, db_index = True)
	modified      = models.DateTimeField(default = timezone.now, db_index = True)

	objects       = ParameterToProductManager()

	def get_dicted(self):

		result = {}

		result['id']            = str(self.id)
		result['value_text']    = self.value_text
		result['value_integer'] = self.value_integer
		result['value_decimal'] = str(self.value_decimal)
		result['state']         = self.state
		result['created']       = str(self.created)
		result['modified']      = str(self.modified)

		try:    result['parameter']       = self.parameter.get_dicted()
		except: result['parameter']       = None

		try:    result['product']         = self.product.get_dicted()
		except: result['product']         = None

		try:    result['value_list']      = self.value_list.get_dicted()
		except: result['value_list']      = None

		try:    result['parameter_value'] = self.parameter_value.get_dicted()
		except: result['parameter_value'] = None

		return result


	def __str__(self):

		return '{} {} - {}'.format(
			self.product.vendor.name,
			self.product.article,
			self.parameter.name)


	def set_value(self, value, updater = None, distributor = None):

		print('set_value: {}'.format(value))

		if self.parameter.parametertype is None:

			print('self.parameter.parametertype is None')

			return False

		if self.parameter.parametertype.alias == 'text':

			print('self.parameter.parametertype.alias == "text"')

			self.value_text   = value.strip()
			self.save()

		elif self.parameter.parametertype.alias == 'months':

			if str(type(value)) in ("<class 'str'>", "<class 'int'>"):

				value = str(value)

				x = 1
				r = 1

				if 'год' in value or 'лет' in value or 'Y' in value:
					x = 12
					value = value.replace('Y', '')
				elif 'дней' in value:
					r = 30

				try:
					self.value_integer = int(value.strip().split(' ')[0]) * x // r
					self.save()
				except Exception:
					print('Не смог обработать значение: {}.'.format(value))
					return False

		elif self.parameter.parametertype.alias == 'list':

			print('self.parameter.parametertype.alias == "list"')

			value_synonym = ParameterValueSynonym.objects.take(
				name        = value,
				updater     = updater,
				parameter   = self.parameter)

			if value_synonym.parametervalue:
				self.value_list = value_synonym.parametervalue
			else:
				print('Значение не проверено: {}.'.format(value))

		else:

			print('Неизвестный тип данных!!!')
			print('Ошибка! {} = {}'.format(self, value))
			return False

		print("{} = {}".format(self, self.parameter_value_xml))


	def _get_parameter_name_xml(self):

		return self.parameter.name

	parameter_name_xml = property(_get_parameter_name_xml)


	def _get_parameter_value_xml(self):

		if self.value_text:
			value = self.value_text
		elif self.value_integer:
			value = '{:,}'.format(self.value_integer).replace(',', ' ')
		elif self.value_decimal:
			value = '{:,}'.format(self.value_decimal).replace(',', ' ').replace('.', ',')
		elif self.value_list:
			value = self.value_list.name
		else:
			return ''

		if self.parameter.unit:
			value = '{} {}'.format(value, self.parameter.unit.name_short_xml)

		return value

	parameter_value_xml = property(_get_parameter_value_xml)


	class Meta:
		ordering = ['created']
		db_table = 'catalog_parameter_to_product'



class ParameterToCategory(models.Model):

	id        = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
	parameter = models.ForeignKey(Parameter, related_name = '+')
	category  = models.ForeignKey(Category,  related_name = '+')

	order     = models.BigIntegerField(db_index = True)

	state     = models.BooleanField(default = True, db_index = True)
	created   = models.DateTimeField(default = timezone.now, db_index = True)
	modified  = models.DateTimeField(default = timezone.now, db_index = True)

	def get_dicted(self):

		result = {}

		result['id']       = str(self.id)
		result['order']    = self.order
		result['state']    = self.state
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)

		try:    result['parameter']       = self.parameter.get_dicted()
		except: result['parameter']       = None

		try:    result['category']        = self.category.get_dicted()
		except: result['category']        = None

		try:    result['value_list']      = self.value_list.get_dicted()
		except: result['value_list']      = None

		try:    result['parameter_value'] = self.parameter_value.get_dicted()
		except: result['parameter_value'] = None

		return result

	class Meta:
		ordering = ['created']
		db_table = 'catalog_parameter_to_category'


class ParameterSynonymManager(models.Manager):

	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
		return result

	def take(self, name, updater = None, parameter = None):
		name = str(name).strip()
		try:
			parameter_synonym = self.get(
				name        = name,
				updater     = updater)
		except ParameterSynonym.DoesNotExist:
			parameter_synonym = ParameterSynonym(
				name        = name,
				updater     = updater,
				parameter   = parameter)
			parameter_synonym.save()
		return parameter_synonym


class ParameterSynonym(models.Model):

	id          = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
	updater     = models.ForeignKey(Updater,   related_name = '+', null = True, default = None)
	parameter   = models.ForeignKey(Parameter, related_name = '+', null = True, default = None)

	name        = models.TextField(db_index = True)

	state       = models.BooleanField(default = True, db_index = True)
	created     = models.DateTimeField(default = timezone.now, db_index = True)
	modified    = models.DateTimeField(default = timezone.now, db_index = True)

	objects     = ParameterSynonymManager()

	def get_dicted(self):

		result = {}

		result['id']       = str(self.id)
		result['name']     = self.name
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)

		try:
			result['updater'] = self.updater.get_dicted()
		except Exception:
			result['updater']     = None

		try:
			result['parameter'] = self.parameter.get_dicted()
		except Exception:
			result['parameter'] = None

		return result


	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']


class CategorySynonymManager(models.Manager):

	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
		return result

	def take(self, name, updater = None, category = None):
		name = str(name).strip()
		try:
			categorySynonym = self.get(
				name        = name,
				updater     = updater)
		except CategorySynonym.DoesNotExist:
			categorySynonym = CategorySynonym(
				name        = name,
				updater     = updater,
				category    = category)
			categorySynonym.save()
		return categorySynonym


class CategorySynonym(models.Model):

	id          = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
	updater     = models.ForeignKey(Updater,  related_name = '+', null = True, default = None)
	category    = models.ForeignKey(Category, related_name = '+', null = True, default = None)

	name        = models.TextField(db_index = True)

	state       = models.BooleanField(default = True, db_index = True)
	created     = models.DateTimeField(default = timezone.now, db_index = True)
	modified    = models.DateTimeField(default = timezone.now, db_index = True)

	objects     = CategorySynonymManager()

	def get_dicted(self):

		result = {}

		result['id']       = str(self.id)
		result['name']     = self.name
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)

		try:
			result['updater'] = self.updater.get_dicted()
		except Exception:
			result['updater']     = None

		try:
			result['category'] = self.category.get_dicted()
		except Exception:
			result['category'] = None

		return result


	def __str__(self):
		return self.name


	class Meta:
		ordering = ['name']


class VendorSynonymManager(models.Manager):


	def get_all_dicted(self):
		result = []
		for o in self.all():
			result.append(o.get_dicted())
		return result


	def take(self, name, updater = None, vendor = None):
		name = str(name).strip()
		try:
			vendorSynonym = self.get(
				name        = name,
				updater     = updater)
		except VendorSynonym.DoesNotExist:
			vendorSynonym = VendorSynonym(
				name        = name,
				updater     = updater,
				vendor      = vendor)
			vendorSynonym.save()
		return vendorSynonym


class VendorSynonym(models.Model):

	id          = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
	updater     = models.ForeignKey(Updater, related_name = '+', null = True, default = None)
	vendor      = models.ForeignKey(Vendor,  related_name = '+', null = True, default = None)

	name        = models.TextField(db_index = True)

	state       = models.BooleanField(default = True, db_index = True)
	created     = models.DateTimeField(default = timezone.now, db_index = True)
	modified    = models.DateTimeField(default = timezone.now, db_index = True)

	objects     = VendorSynonymManager()


	def get_dicted(self):

		result = {}

		result['id']       = str(self.id)
		result['name']     = self.name
		result['created']  = str(self.created)
		result['modified'] = str(self.modified)

		try:
			result['updater'] = self.updater.get_dicted()
		except Exception:
			result['updater'] = None

		try:
			result['vendor'] = self.vendor.get_dicted()
		except Exception:
			result['vendor'] = None

		return result


	def __str__(self):
		return self.name


	class Meta:
		ordering = ['name']



class ProductPhotoManager(models.Manager):


	def load(self, *args, **kwargs):

		# Библиотеки. необходимые для загрузки данных в память
		import requests
#		from io import BytesIO
		from django.conf import settings

		# Инициализация переменных
		product = kwargs.get('product', None)
		source  = str(kwargs.get('source', '')).strip()

		# Если указаны продукт и источник изображения
		if product and source:

			# Получаем объект с базы, или создаём его
			try:
				photo = self.get(product = product, source = source)
			except Exception:
				photo = ProductPhoto(product = product, source = source)

			# Если изображение ещё не загружено
			if not photo.patch:
				r = requests.get(source)
#				print(type(r.content))
#				print(photo.id)

				# Получаем разрешение файла
				s = source.split('.')
				ext = s[len(s) - 1].lower()
#				print(ext)

				photo.src = '{media_url}catalog/photos/{id}.{ext}'.format(
					media_url = settings.MEDIA_URL,
					id        = photo.id,
					ext       = ext)
				photo.patch = '{media_dir}catalog/photos/{id}.{ext}'.format(
					media_dir = settings.MEDIA_DIR,
					id        = photo.id,
					ext       = ext)

#				print(photo.src)
#				print(photo.patch)

				# Записывваем фото на диск
				f = open(photo.patch, 'wb')
				f.write(r.content)
				f.close()

				# Записываем изменения в память
				photo.save()

			print('ProductPhoto {} {}: {}'.format(
				product.vendor.name,
				product.article,
				source))


class ProductPhoto(models.Model):

	id           = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
	product      = models.ForeignKey(Product, related_name = '+', null = True, default = None)
	trumb        = models.ForeignKey('self',  related_name = '+', null = True, default = None)

	name         = models.TextField(null = True, default = '', db_index = True)
	patch        = models.TextField(null = True, default = '')
	src          = models.TextField(null = True, default = '')
	description  = models.TextField(null = True, default = '')
	source       = models.TextField(null = True, default = '')
	hash_md5     = models.TextField(null = True, default = None, db_index = True)

	state        = models.BooleanField(default = True, db_index = True)
	created      = models.DateTimeField(default = timezone.now, db_index = True)
	modified     = models.DateTimeField(default = timezone.now, db_index = True)

	objects = ProductPhotoManager()

	def __str__(self):
		return self.title

	class Meta:
		ordering = ['-created']


models = {
	'distributor'           : Distributor,
	'updater'               : Updater,
	'stock'                 : Stock,
	'category'              : Category,
	'vendor'                : Vendor,
	'unit'                  : Unit,
	'pricetype'             : PriceType,
	'currency'              : Currency,
	'price'                 : Price,
	'quantity'              : Quantity,
	'product'               : Product,
	'party'                 : Party,
	'partyhystory'          : PartyHystory,
	'pricehystory'          : PriceHystory,
	'quantityhystory'       : QuantityHystory,
	'parametertype'         : ParameterType,
	'parameter'             : Parameter,
	'parametervalue'        : ParameterValue,
	'parametervaluesynonym' : ParameterValueSynonym,
	'parametertoproduct'    : ParameterToProduct,
	'parametertocategory'   : ParameterToCategory,
	'parametersynonym'      : ParameterSynonym,
	'categorysynonym'       : CategorySynonym,
	'vendorsynonym'         : VendorSynonym,
	'productphoto'          : ProductPhoto}
