"""Helper functions for accessing and updating the inventory system database 

Author: Riley Kirkpatrick
"""

import uuid
from sqlalchemy import create_engine, Boolean, Column, Float, Integer, PickleType, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ----------======================---------- <-<>-<>-<>-<>-<>-<>-<>-<>-<>-> ----------======================----------
# ----------======================---------- Database Functions and Classes ----------======================----------
# ----------======================---------- <-<>-<>-<>-<>-<>-<>-<>-<>-<>-> ----------======================----------





InventoryBase = declarative_base()


class Product(InventoryBase):
    __tablename__ = 'product'
    id = Column(String(36), nullable=False, primary_key=True)
    name = Column(String(50), nullable=False, primary_key=True)
    description = Column(String(250))
    manufacturer = Column(String(50))
    wholesale_cost = Column(Float)
    sale_cost = Column(Float)
    amount = Column(Integer)

class Order(InventoryBase):
    __tablename__ = 'order'
    id = Column(String(36), primary_key=True, nullable=False)
    destination = Column(String(50), nullable=False)
    date = Column(PickleType, nullable=False)
    is_paid = Column(Boolean)
    is_shipped = Column(Boolean)
    products = Column(PickleType, nullable=False)


def create_inventory_system_db(database_path):
  """Creates an inventory system database in the file at database_path
  """
  # Create an engine that stores data in the database path
  engine = create_engine('sqlite:///' + database_path)
  # Create all tables in the engine
  InventoryBase.metadata.create_all(engine)

def get_dbsession(database_path):
  """ Create a DBSession instance
  """
  engine = create_engine('sqlite:///' + database_path)
  InventoryBase.metadata.bind = engine
  DBSession = sessionmaker(bind=engine)
  return DBSession()

def query_db(database, query, filter=None):
  """Query a database with or without a filter and return all values of the query
  """
  if filter is None:
    return database.query(query).all()
  return database.query(query).filter(filter).all()

def add_db(database, values):
  """Add values to the database and flush the database
  """
  database.add_all(values)
  database.flush()

def update_db(database, query, values, filter=None):
  """Update rows in the database based on a query and possibly a filter
  """
  if filter is None:
    database.query(query).update(values, synchronize_session=False)
    #database.query(query).filter(filter).update({'status': status})
  else:
    database.query(query).filter(filter).update(values, synchronize_session=False)

def update_product_db(database, products):
  """Update product rows given a dict of tuple (id,name) for each product as keys to the new values,
  i.e., {(id,name):values,...}
  """
  for product in products:
    database.query(Product).filter(Product.id == product[0] or Product.name == product[1]).\
                                                update(products[product], synchronize_session=False)

def update_order_db(database, orders):
  """Update order rows given a dict of IDs mapped to the new values, i.e., {id:values,...}
  """
  for order in orders:
    database.query(Order).filter(Order.id == order).update(orders[order], synchronize_session=False)

def save_db(database):
  """Save the database
  """
  # The parameter database must be an instance of DBSession
  database.commit()

def reset_db(database):
  """Reset the database by removing all products and orders from it
  """
  database.query(Product).delete()
  database.query(Order).delete()
  save_db(database)




# ----------==================---------- <-<>-<>-<>-<>-<>-<><>-<>-<>-<>-<>-<>-> ----------==================----------
# ----------==================---------- Inventory System Functions and Classes ----------==================----------
# ----------==================---------- <-<>-<>-<>-<>-<>-<><>-<>-<>-<>-<>-<>-> ----------==================----------





class OrderDate():
  """A class for creating dates for an order that will then be stored in the database as a PickleType
  """

  def __init__(self, month, day, year):
    self.month = month
    self.day = day
    self.year = year

class OrderProduct():
  """A class for creating products for an order that will then be stored in the database as a PickleType
  """

  def __init__(self, id, name, amount):
    self.id = id
    self.name = name
    self.amount = amount

def GetProductsByID(database, ids):
  """Returns a Product object of a given ID or None if the product is not found.
  """
  return query_db(database, Product, (Product.id.in_(ids)))

def GetProductsByName(database, names):
  """Returns a Product object of a given name or None if the product is not found.
  """
  return query_db(database, Product, (Product.name.in_(names)))

def GetProductsByManufacturer(database, manufacturer):
  """Returns a Product object of a given name or None if the product is not found.
  """
  return query_db(database, Product, (Product.manufacturer==manufacturer))

def AddProducts(database, products):
  """Adds products to the database and returns their IDs or an empty list if the add fails.
  """
  try:
    ids = [str(uuid.uuid4()) for i in range(len(products))]
    products = [Product(id=ids[i], name=products[i].name, description=products[i].description,
                        manufacturer=products[i].manufacturer, wholesale_cost=products[i].wholesale_cost,
                        sale_cost=products[i].sale_cost, amount=products[i].amount) for i in range(len(products))]
    add_db(database, products)
    save_db(database)
    return ids
  except KeyboardInterrupt:
    # Save the database if there is a KeyboardInterrupt
    save_db(database)
    database.close()
    # Allow the interrupt to propagate up 
    raise KeyboardInterrupt
  except Exception as e:
    print('There was an issue adding products: ' + e)
    return []

def UpdateProducts(database, products):
  """Updates products based on the passed products.
  """
  try:
    # Creates a dictionary with tuple keys (product.id, product.name) that map to a dict value: the dict contains the
    # values of the product that are to be updated and calls update_product_db to update the database
    _products = {}
    for product in products:
      _products[(product.id, product.name)] = {}
      # Update a product's description
      if product.description != '':
        _products[(product.id, product.name)][Product.description] = product.description
      # Update a product's manufacturer
      if product.manufacturer != '':
        _products[(product.id, product.name)][Product.manufacturer] = product.manufacturer
      # Update a product's wholesale_cost
      if product.wholesale_cost >= 0:
        _products[(product.id, product.name)][Product.wholesale_cost] = product.wholesale_cost
      # Update a product's sale_cost
      if product.sale_cost >= 0:
        _products[(product.id, product.name)][Product.sale_cost] = product.sale_cost
      # Update a product's amount
      if product.amount >= 0:
        _products[(product.id, product.name)][Product.amount] = product.amount
    update_product_db(database, _products)
    save_db(database)
  except KeyboardInterrupt:
    # Save the database if there is a KeyboardInterrupt
    save_db(database)
    database.close()
    # Allow the interrupt to propagate up 
    raise KeyboardInterrupt

def GetProductsInStock(database):
  """Returns a list of products in stock.
  """
  return query_db(database, Product, Product.amount > 0)

def GetOrdersByID(database, ids):
  """Gets orders by their IDs or returns None if not found.
  """
  return query_db(database, Order, (Order.id.in_(ids)))

def check_product_available(database, added_products):
    """Checks all products added to an order to make sure there is enough in stock in the database. Returns True if
    there is enough stock and False otherwise.
    """
    for product in added_products:
      product_available = query_db(database, Product, (Product.id==product.id or Product.name==product.name))
      if len(product_available) > 0:
        if product_available[0].amount < product.amount:
          return False
    return True

def get_order_product(database, prod_for_id, prod_for_name=None, prod_for_amount=None, query=False):
  """Retrieves and returns a product based on the ID, name, and amount from the passed products.
  The passed products are dbProduct objects and are converted to a OrderProduct object. If a product
  for name or amount is not supplied, then the product for ID is used to get the name or amount.
  If query is True, then the product for ID is used to query the database for the product which then
  is used to create the OrderProduct object.
  """

  # Query will use prod_for_id to query the database for the ID and name if only one is supplied
  # The amount from prod_for_id is used for the amount
  if query:
    product = query_db(database, Product, (Product.id==prod_for_id.id or Product.name==prod_for_id.name))
    if len(product) > 0:
      product = product[0]
      return OrderProduct(id=product.id, name=product.name, amount=prod_for_id.amount)
    return None
  
  # If no products for name or amount retrieval is supplied, use the product supplied for the ID
  if prod_for_name is None:
    prod_for_name = prod_for_id
  if prod_for_amount is None:
    prod_for_amount = prod_for_id
  return OrderProduct(id=prod_for_id.id, name=prod_for_name.name, amount=prod_for_amount.amount)

def get_products_new_order(database, requested_products):
  """Converts a list of Product objects to type OrderProduct
  """
  products = []
  for product in requested_products:
    product = get_order_product(database, product, query=True)
    if not product is None and product.amount > 0:
      products.append(product)
  return products

def add_products_to_order(database, added_products):
    """Removes the products added to an order from stock
    """
    for product in added_products:
      product_in_db = query_db(database, Product, (Product.name==product.name or Product.id==product.id))
      if len(product_in_db) > 0:
        update_db(database, Product, {Product.amount:(product_in_db[0].amount - product.amount)},
                  (Product.name==product.name or Product.id==product.id))
  
def CreateOrders(database, orders):
  """Adds an order to the database and returns the ID or an empty string if the add fails.
  """
  try:

    _orders, ids = [], []
    dates = [OrderDate(month=orders[i].date.month, day=orders[i].date.day, year=orders[i].date.year) for i in range(len(orders))]
    
    for i in range(len(orders)):
      products = []
      if check_product_available(database, orders[i].products):
        products = get_products_new_order(database, orders[i].products)

      if len(products) > 0:
        # Update how much product is available
        add_products_to_order(database, products)
        id = str(uuid.uuid4())
        ids.append(id)
        _orders.append(Order(id=id, destination=orders[i].destination, date=dates[i], is_paid=orders[i].is_paid,
                           is_shipped=orders[i].is_shipped, products=products))
    add_db(database, _orders)
    save_db(database)
    return ids
  except KeyboardInterrupt:
    # Save the database if there is a KeyboardInterrupt
    save_db(database)
    database.close()
    # Allow the interrupt to propagate up 
    raise KeyboardInterrupt

def remove_products_from_order(database, removed_products):
    """Adds the products removed from an order back into stock
    """
    for product in removed_products:
      product_in_db = query_db(database, Product, (Product.name==product.name or Product.id==product.id))
      if len(product_in_db) > 0:
        update_db(database, Product, {Product.amount:(product_in_db[0].amount + product.amount)},
                  (Product.name==product.name or Product.id==product.id))

def get_order_products(database, id):
    """Retrieves all products in an order with the ID of the product as a key to the amount of the product. 
    """
    order = query_db(database, Order, Order.id==id)
    if len(order) > 0:
      return {product.id: product.amount for product in order[0].products}
    return {}

def UpdateOrders(database, orders):
  """Updates an order based on the passed order.
  """
  try:
    # Creates a dictionary with the order IDs as the keys that map to a dict value: the dict contains the
    # values of the order that are to be updated and calls update_order_db to update the database
    _orders = {}
    for order in orders:
      _orders[order.id] = {}
      # Update an order's destination
      if order.destination != '':
        _orders[order.id][Order.destination] = order.destination
      # Update an order's date
      year = 0 <= order.date.year <= 9999
      month = 1 <= order.date.month <= 12
      day = 1 <= order.date.day <= 31
      if year and month and day:
        _orders[order.id][Order.date] = OrderDate(month=order.date.month, day=order.date.day, year=order.date.year)
      # Update the products of an order (remove, add, or update the quantity of each product)
      if len(order.products) > 0:
        old_product_amounts = get_order_products(database, order.id)
        # Get products to add and remove
        added_products, removed_products = [], []
        for product in order.products:
          try:
            old_amount = old_product_amounts[product.id]
            if old_amount <= product.amount:
              added_products.append(OrderProduct(id=product.id, name=product.name, amount=(product.amount - old_amount)))
            else:
              removed_products.append(OrderProduct(id=product.id, name=product.name, amount=(old_amount - product.amount)))
          except KeyError:
            # If there is a KeyError, then the product is new to the order
            added_products.append(OrderProduct(id=product.id, name=product.name, amount=product.amount))
        if check_product_available(database, added_products):
          # Update the database
          add_products_to_order(database, added_products)
          remove_products_from_order(database, removed_products)
          new_products = [OrderProduct(id=product.id, name=product.name, amount=product.amount) for product in order.products]
          _orders[order.id][Order.products] = new_products

      # Update an order if it was paid for
      if order.is_paid:
        _orders[order.id][Order.is_paid] = order.is_paid
      # Update an order if it shipped
      if order.is_shipped:
        _orders[order.id][Order.is_shipped] = order.is_shipped
    update_order_db(database, _orders)
    save_db(database)
  except KeyboardInterrupt:
    # Save the database if there is a KeyboardInterrupt
    save_db(database)
    database.close()
    # Allow the interrupt to propagate up 
    raise KeyboardInterrupt

def GetOrdersByStatus(database, order_status):
  filter = None
  if order_status.shipped and order_status.paid:
    filter = (Order.is_shipped==True and Order.is_paid==True)
  elif order_status.shipped:
    filter = Order.is_shipped==True
  elif order_status.paid:
    filter = Order.is_paid==True
  else:
    filter = (Order.is_shipped==False and Order.is_paid==False)
  orders = query_db(database, Order, filter)
  return orders




# ----------=====================---------- <-<>-<>-<>-<>-<>-<>-<>-<>-<>-<>-> ----------=====================----------
# ----------=====================---------- Inventory System Client Functions ----------=====================----------
# ----------=====================---------- <-<>-<>-<>-<>-<>-<>-<>-<>-<>-<>-> ----------=====================----------





def add_parsers_and_subparsers(parser):
  parser.add_argument('ip', help='The IP of the server running the inventory system')
  parser.add_argument('--port', default='1337', help='The IP of the server running the inventory system')
  subparsers = parser.add_subparsers(dest='command', help='The command you want to run')

  # Create a parser for GetProductsInStock which has no additional arguments
  subparsers.add_parser('get-products-in-stock', help='get-products-in-stock help')


  # Create a parser for GetProductsByID, GetProductsByName, GetProductsByManufacturer, and GetOrder
  # which each have a single argument
  getProdByIDParse = subparsers.add_parser('get-products-by-id', help='get-products-by-id help')
  getProdByIDParse.add_argument('ids', nargs='+', help='The IDs of the products being retrieved')

  getProdByNameParse = subparsers.add_parser('get-products-by-name', help='get-products-by-name help')
  getProdByNameParse.add_argument('names', nargs='+', help='The names of the products being retrieved')

  getProdsByManParse = subparsers.add_parser('get-products-by-manufacturer', help='get-products-by-manufacturer help')
  getProdsByManParse.add_argument('manufacturer', help='The manufacturer of the products being retrieved')

  getOrderParse = subparsers.add_parser('get-orders-by-id', help='get-orders-by-id help')
  getOrderParse.add_argument('ids', nargs='+', help='The IDs of the orders being retrieved')


  # Create a parser for GetOrdersByStatus with arguments for the status of the orders being retrieved
  getOrdersParse = subparsers.add_parser('get-orders-by-status', help='get-orders-by-status help')
  getOrdersParse.add_argument('-p', '--paid', type=bool, help='Whether the retrieved orders are paid or not, type an empty'
                                                              'string for false and any other string for true')
  getOrdersParse.add_argument('-a', '--shipped', type=bool, help='Whether the retrieved orders are shipped or not, type an'
                                                                  'empty string for false and any other string for true')


  # Create a parser for AddProducts and UpdateProducts which each have arguments for products
  addProductParse = subparsers.add_parser('add-products', help='add-products help')
  addProductParse.add_argument('products', nargs='+', help='The products being added (name,description,manufacturer,'
                                                           'wholesale_cost,sale_cost,amount); only name is required')

  updateProductParse = subparsers.add_parser('update-products', help='update-products help')
  # At least one of name and ID should be passed; nothing will happen if neither is passed
  updateProductParse.add_argument('products', nargs='+', help='The products being updated (id,name,description,manufacturer,'
                                                           'wholesale_cost,sale_cost,amount); only id or name is required')


  # Create a parser for CreateOrder and UpdateOrder which each have arguments for a order
  createOrderParse = subparsers.add_parser('create-orders', help='create-orders help')
  createOrderParse.add_argument('orders', nargs='+', help='The orders being created (destination,date,is_paid,'
                                                           'is_shipped,product1,product2,...,productN); only '
                                                           'products is required. Products should be (id;name;amount) '
                                                           'and date should be of the form (MM/DD/YYYY).\nEx. (,2/2/1978'
                                                           ',,t,id_1;prod1;1,id_2;prod2;2)\nNote that for is_paid and is_shipped'
                                                           ' a non-empty string results in True and False otherwise.')

  updateOrderParse = subparsers.add_parser('update-orders', help='update-orders help')
  updateOrderParse.add_argument('orders', nargs='+', help='The orders being updated (id,destination,date,is_paid,'
                                                           'is_shipped,product1,product2,...,productN); only id '
                                                           'and products is required. Products should be (id;name;amount) '
                                                           'and date should be of the form (MM/DD/YYYY).\nEx. (id,,2/2/1978'
                                                           ',,t,id_1;prod1;1,id_2;prod2;2)\nNote that for is_paid and is_shipped'
                                                           ' a non-empty string results in True and False otherwise.')

def string_to_date(string):
  date = string.split('/')
  try:
      # If there were not 2 /, then raise an exception
      if len(date) != 3:
          raise Exception
      # Remove whitespace from each value and then convert it to an integer
      date = [_ for _ in map(int, map(str.strip, date))]
  except:
    return None
  return OrderDate(month=date[0], day=date[1], year=date[2])

def products_from_arg_list(arg_list, spl=','):
  products = []
  _product = '' # Used if an exception occurs (so that the user knows the first product that failed)
  try:
    for product in arg_list:
      _product = product
      product = [_ for _ in map(str.strip, product.split(spl))]
      # If there were not two commas, then raise an exception
      if len(product) != 3:
          raise Exception
      product[2] = int(product[2])
      # Check for duplicate products
      for __product in products:
        if __product.id == product[0] or __product.name == product[1]:
          continue
      products.append(OrderProduct(id=product[0], name=product[1], amount=product[2]))
  except:
    return None
  return products

def get_date_and_products(date, products):
  date = string_to_date(date)
  if date is None:
    return (None,)
  products = products_from_arg_list(products)
  if products is None:
    return (None,)
  return date, products

def is_int_or_float(string):
  # Checks if a string is a float or int
  values = string.split('.')
  for value in values:
    if not value.isdecimal():
      return False
  return True

def get_product_from_list(product, id=False):
  if len(product) >= 1 and (product[0] != '' or id):
    _product = {'name':product[0], 'description':'', 'manufacturer':'', 'wholesale_cost':0.0, 'sale_cost':0.0, 'amount':0}
    if len(product) >= 2:
      _product['description'] = product[1]
      if len(product) >= 3:
        _product['manufacturer'] = product[2]
        if len(product) >= 4:
          if is_int_or_float(product[3]):
            _product['wholesale_cost'] = float(product[3])
          if len(product) >= 5:
            if is_int_or_float(product[4]):
              _product['sale_cost'] = float(product[4])
            if len(product) >= 6 and is_int_or_float(product[5]):
              _product['amount'] = int(product[5])
    return _product

def get_products_to_add(products):
  _products = []
  for product in products:
    product = [value.strip() for value in product.split(',')]
    _product = get_product_from_list(product)
    if not _product is None:
      # Check for duplicate products
      for product in _products:
        if product.name == _product['name']:
          continue
      _products.append(Product(name=_product['name'], description=_product['description'],
                               manufacturer=_product['manufacturer'], wholesale_cost=_product['wholesale_cost'],
                               sale_cost=_product['sale_cost'], amount=_product['amount']))
  return _products

def get_products_to_update(products):
  _products = []
  for product in products:
    product = [value.strip() for value in product.split(',')]
    _product = None
    if len(product) > 1:
      _product = get_product_from_list(product[1:], id=product[0] != '')
    if product[0] != '' and _product is None:
      return
    if _product is None:
      _product = {'name':'', 'description':'', 'manufacturer':'', 'wholesale_cost':0.0, 'sale_cost':0.0, 'amount':0}
    else:
      _products.append(Product(id=product[0], name=_product['name'], description=_product['description'],
                               manufacturer=_product['manufacturer'], wholesale_cost=_product['wholesale_cost'],
                               sale_cost=_product['sale_cost'], amount=_product['amount']))
  return _products

def get_order_from_list(order):
  _order = {'destination':'', 'date':'', 'is_paid':False, 'is_shipped':False, 'products':[]}
  if len(order) > 0:
    _order['destination'] = order[0]
    if len(order) > 1:
      date = string_to_date(order[1])
      if not date is None:
        _order['date'] = date
      if len(order) > 2:
        _order['is_paid'] = len(order[2]) > 0
        if len(order) > 3:
          _order['is_shipped'] = len(order[3]) > 0
          if len(order) > 4:
            products = products_from_arg_list(order[4:], spl=';')
            if products is None:
              return
            _order['products'] = products
  if len(_order['products']) > 0:
    return _order

def get_orders_to_create(orders):
  _orders = []
  for order in orders:
    order = [value.strip() for value in order.split(',')]
    if len(order) <= 1:
      continue
    _order = get_order_from_list(order)
    # If there is no ID or no products then return
    if _order is None:
      continue
    _orders.append(Order(destination=_order['destination'], date=_order['date'],
                         is_paid=_order['is_paid'], is_shipped=_order['is_shipped'], products=_order['products']))
  return _orders

def get_orders_to_update(orders):
  _orders = []
  for order in orders:
    order = [value.strip() for value in order.split(',')]
    if len(order) <= 1:
      continue
    _order = get_order_from_list(order[1:])
    # If there is no ID or no products then return
    if order[0] == '' or _order is None:
      continue
    _order['id'] = order[0]
    _orders.append(Order(id=_order['id'], destination=_order['destination'], date=_order['date'],
                         is_paid=_order['is_paid'], is_shipped=_order['is_shipped'], products=_order['products']))
  return _orders




# ----------====================---------- <-<>-<>-<>-<>-<>-+-<>-<>-<>-<>-<>-> ----------====================----------
# ----------====================---------- ----------===============---------- ----------====================----------
# ----------====================---------- <-<>-<>-<>-<>-<>-+-<>-<>-<>-<>-<>-> ----------====================----------
