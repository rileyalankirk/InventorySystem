"""Helper functions for accessing and updating the inventory system database 

Author: Riley Kirkpatrick
"""

import uuid
from sqlalchemy import create_engine, Boolean, Column, Float, Integer, PickleType, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# ----------======================---------- Database Functions and Classes ----------======================----------





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
  # Create an engine that stores data in the database path
  engine = create_engine('sqlite:///' + database_path)
  # Create all tables in the engine
  InventoryBase.metadata.create_all(engine)

def get_dbsession(database_path):
  # Create a DBSession instance
  engine = create_engine('sqlite:///' + database_path)
  InventoryBase.metadata.bind = engine
  DBSession = sessionmaker(bind=engine)
  return DBSession()

def query_db(database, query, filter=None):
  query = database.query(query)
  if filter is None:
    return query.all()
  return query.filter(filter).all()

def add_db(database, row):
  database.add(row)
  database.flush()

def update_db(database, query, values, filter=None):
  if filter is None:
    database.query(query).update(values)
  else:
    database.query(query).filter(filter).update(values)

def save_db(database):
  # The parameter database must be an instance of DBSession
  database.commit()

def reset_db(database):
  database.query(Product).delete()
  database.query(Order).delete()
  save_db(database)





# ----------==================---------- Inventory System Functions and Classes ----------==================----------





class OrderDate():
  """A class for creating dates for an order that will then be stored in the database as a PickleType.
  """

  def __init__(self, month, day, year):
    self.month = month
    self.day = day
    self.year = year

class OrderProduct():
  """A class for creating products for an order that will then be stored in the database as a PickleType.
  """

  def __init__(self, id, name, amount):
    self.id = id
    self.name = name
    self.amount = amount


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
  # Converts a list of inventory_system.Product objects to type OrderProduct
  products = []
  for product in requested_products:
    product = get_order_product(database, product, query=True)
    if not product is None and product.amount > 0:
      products.append(product)
  return products

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

def remove_products_from_order(database, removed_products):
    """Adds the products removed from an order back into stock
    """
    for product in removed_products:
      product_in_db = query_db(database, Product, (Product.name==product.name or Product.id==product.id))
      if len(product_in_db) > 0:
        update_db(database, Product, {Product.amount:(product_in_db[0].amount + product.amount)},
                  (Product.name==product.name or Product.id==product.id))

def add_products_to_order(database, added_products):
    """Removes the products added to an order from stock
    """
    for product in added_products:
      product_in_db = query_db(database, Product, (Product.name==product.name or Product.id==product.id))
      if len(product_in_db) > 0:
        update_db(database, Product, {Product.amount:(product_in_db[0].amount - product.amount)},
                  (Product.name==product.name or Product.id==product.id))

def get_order_products(database, id):
    """Retrieves all products in an order with the ID of the product as a key to the amount of the product. 
    """
    order = query_db(database, Order, Order.id==id)
    if len(order) > 0:
      return {product.id: product.amount for product in order[0].products}
    return {}

def get_product_by_filter(database, filter):
  """Returns a Product object based on a filter or None if the product is not found.
  """
  product = query_db(database, Product, filter)
  if len(product) == 0:
    return None
  return product

def get_product_by_id(database, id):
  """Returns a Product object of a given ID or None if the product is not found.
  """
  product = get_product_by_filter(database, (Product.id==id))
  if len(product) == 1:
    return product[0]
  return None

def get_product_by_name(database, name):
  """Returns a Product object of a given name or None if the product is not found.
  """
  product = get_product_by_filter(database, (Product.name==name))
  if len(product) == 1:
    return product[0]
  return None

def get_products_by_manufacturer(database, manufacturer):
  """Returns a Product object of a given name or None if the product is not found.
  """
  return get_product_by_filter(database, (Product.manufacturer==manufacturer))

def add_product(database, product):
  """Adds a product to the database and returns its ID or an empty string if the add fails.
  """
  try:
    id = str(uuid.uuid4())
    # Check that no other product has the same name
    if len(query_db(database, Product, Product.name==product.name)) == 0:
      add_db(database, Product(id=id, name=product.name, description=product.description,
              manufacturer=product.manufacturer, wholesale_cost=product.wholesale_cost,
              sale_cost=product.sale_cost, amount=product.amount))
      save_db(database)
      return id
    return ''
  except KeyboardInterrupt:
    # Save the database if there is a KeyboardInterrupt
    save_db(database)
    database.close()
    # Allow the interrupt to propagate up 
    raise KeyboardInterrupt

def update_product(database, product):
  """Updates a product based on the passed product.
  """
  try:
    # Update a product's description
    if product.description != '':
      update_db(database, Product, {Product.description:product.description},
                (Product.name==product.name or Product.id==product.id))
    # Update a product's manufacturer
    if product.manufacturer != '':
      update_db(database, Product, {Product.manufacturer:product.manufacturer},
                (Product.name==product.name or Product.id==product.id))
    # Update a product's wholesale_cost
    if product.wholesale_cost >= 0:
      update_db(database, Product, {Product.wholesale_cost:product.wholesale_cost},
                (Product.name==product.name or Product.id==product.id))
    # Update a product's sale_cost
    if product.sale_cost >= 0:
      update_db(database, Product, {Product.sale_cost:product.sale_cost},
                (Product.name==product.name or Product.id==product.id))
    # Update a product's amount
    if product.amount >= 0:
      update_db(database, Product, {Product.amount:product.amount},
                (Product.name==product.name or Product.id==product.id))
    save_db(database)
  except KeyboardInterrupt:
    # Save the database if there is a KeyboardInterrupt
    save_db(database)
    database.close()
    # Allow the interrupt to propagate up 
    raise KeyboardInterrupt

def get_products_in_stock(database):
  """Returns a list of products in stock.
  """
  return query_db(database, Product, Product.amount > 0)

def get_order(database, id):
  """Gets an order by ID or returns None if not found.
  """
  order = query_db(database, Order, Order.id==id)
  if len(order) == 0:
    return None
  return order[0]

def create_order(database, order):
  """Adds an order to the database and returns the ID or an empty string if the add fails.
  """
  try:
    id = str(uuid.uuid4())
    date = OrderDate(month=order.date.month, day=order.date.day, year=order.date.year)
    products = []
    if check_product_available(database, order.products):
      products = get_products_new_order(database, order.products)

    if len(products) > 0:
      # Update how much product is available
      add_products_to_order(database, products)
      add_db(database, Order(id=id, destination=order.destination, date=date, products=products,
              is_paid=order.is_paid, is_shipped=order.is_shipped))
      save_db(database)
      return id
    return ''
  except KeyboardInterrupt:
    # Save the database if there is a KeyboardInterrupt
    save_db(database)
    database.close()
    # Allow the interrupt to propagate up 
    raise KeyboardInterrupt

def update_order(database, order):
  """Updates an order based on the passed order.
  """
  try:
    # Update an order's destination
    if order.destination != '':
      update_db(database, Order, {Order.destination:order.destination}, Order.id==order.id)
    # Update an order's date
    year = 0 <= order.date.year <= 9999
    month = 1 <= order.date.month <= 12
    day = 1 <= order.date.day <= 31
    if year and month and day:
      date = OrderDate(month=order.date.month, day=order.date.day, year=order.date.year)
      update_db(database, Order, {Order.date:date}, Order.id==order.id)
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
        update_db(database, Order, {Order.products:new_products}, Order.id==order.id)

    # Update whether an order has been paid for or not
    if order.is_paid:
      update_db(database, Order, {Order.is_paid:order.is_paid}, Order.id==order.id)
    # Update whether an order has been shipped for or not
    if order.is_shipped:
      update_db(database, Order, {Order.is_shipped:order.is_shipped}, Order.id==order.id)
    save_db(database)
  except KeyboardInterrupt:
    # Save the database if there is a KeyboardInterrupt
    save_db(database)
    database.close()
    # Allow the interrupt to propagate up 
    raise KeyboardInterrupt

def get_orders(database, order_status):
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





# ----------=====================---------- Inventory System Client Functions ----------=====================----------





def add_parsers_and_subparsers(parser):
  parser.add_argument('ip', help='The IP of the server running the inventory system')
  parser.add_argument('--port', default='1337', help='The IP of the server running the inventory system')
  subparsers = parser.add_subparsers(dest='command', help='The command you want to run')

  # Create a parser for GetProductsInStock which has no additional arguments
  subparsers.add_parser('get-products-in-stock', help='get-products-in-stock help')


  # Create a parser for GetProductByID, GetProductByName, GetProductsByManufacturer, and GetOrder
  # which each have a single argument
  getProdByIDParse = subparsers.add_parser('get-product-by-id', help='get-product-by-id help')
  getProdByIDParse.add_argument('id', help='The ID of the product being retrieved')

  getProdByNameParse = subparsers.add_parser('get-product-by-name', help='get-product-by-name help')
  getProdByNameParse.add_argument('name', help='The name of the product being retrieved')

  getProdsByManParse = subparsers.add_parser('get-products-by-manufacturer', help='get-products-by-manufacturer help')
  getProdsByManParse.add_argument('manufacturer', help='The manufacturer of the products being retrieved')

  getOrderParse = subparsers.add_parser('get-order', help='get-order help')
  getOrderParse.add_argument('id', help='The ID of the order being retrieved')


  # Create a parser for GetOrders with arguments for the status of the orders being retrieved
  getOrdersParse = subparsers.add_parser('get-orders', help='get-orders help')
  getOrdersParse.add_argument('-p', '--paid', type=bool, help='Whether the retrieved orders are paid or not, type an empty'
                                                              'string for false and any other string for true')
  getOrdersParse.add_argument('-a', '--shipped', type=bool, help='Whether the retrieved orders are shipped or not, type an'
                                                                  'empty string for false and any other string for true')


  # Create a parser for AddProduct and UpdateProduct which each have arguments for a product
  addProductParse = subparsers.add_parser('add-product', help='add-product help')
  addProductParse.add_argument('name', help='The name of the product being added')
  addProductParse.add_argument('-d', '--description', default='',
                                help='The description of the product being added')
  addProductParse.add_argument('-m', '--manufacturer', default='',
                                help='The manufacturer of the product being added')
  addProductParse.add_argument('-w', '--wholesale_cost', default=0.0, type=float,
                                help='The wholesale cost of the product being added')
  addProductParse.add_argument('-s', '--sale_cost', default = 0.0, type=float,
                                help='The sale cost of the product being added')
  addProductParse.add_argument('-a', '--amount', default=0, type=int,
                                help='The amount available of the product being added')

  updateProductParse = subparsers.add_parser('update-product', help='update-product help')
  # At least one of name and ID should be passed; nothing will happen if neither is passed
  updateProductParse.add_argument('-i', '--id', default='', help='The id of the product being updated')
  updateProductParse.add_argument('-n', '--name', default='', help='The name of the product being updated')
  updateProductParse.add_argument('-d', '--description', default='', help='The new description'
                                                                          ' of the product')
  updateProductParse.add_argument('-m', '--manufacturer', default='', help='The new manufacturer'
                                                                            ' of the product')
  updateProductParse.add_argument('-w', '--wholesale_cost', default=-1.0, type=float,
                                  help='The new wholesale cost of the product')
  updateProductParse.add_argument('-s', '--sale_cost', default=-1.0, type=float,
                                  help='The new sale cost of the product')
  updateProductParse.add_argument('-a', '--amount', default=-1, type=int,
                                  help='The new amount available of the product')


  # Create a parser for CreateOrder and UpdateOrder which each have arguments for a order
  createOrderParse = subparsers.add_parser('create-order', help='create-order help')
  createOrderParse.add_argument('destination', help='The destination of the order being created')
  createOrderParse.add_argument('date', help='The date the order was placed (MM/DD/YYYY)')
  createOrderParse.add_argument('-p', '--is_paid', default=False, type=bool,
                                help='Whether the order is paid for or not, type anything for a value of True')
  createOrderParse.add_argument('-s', '--is_shipped', default=False, type=bool,
                                help='Whether the order is shipped or not, type anything for a value of True')
  createOrderParse.add_argument('products', nargs='+', help='The products being ordered and their'
                                                            ' amounts (id,name,amount)')

  updateOrderParse = subparsers.add_parser('update-order', help='update-order help')
  updateOrderParse.add_argument('id', help='The id of the order being updated')
  updateOrderParse.add_argument('-dest', '--destination', default='', help='The new destination of '
                                                                          'the order being created')
  updateOrderParse.add_argument('-d', '--date', default='', help='The date the order was placed '
                                                                '(MM/DD/YYYY) - requires both / '
                                                                'even if a value is left empty')
  updateOrderParse.add_argument('-paid', '--is_paid', default=False, type=bool,
                                help='Whether the order is paid for or not, type anything for a value of True')
  updateOrderParse.add_argument('-s', '--is_shipped', default=False, type=bool,
                                help='Whether the order is shipped or not, type anything for a value of True')
  updateOrderParse.add_argument('-p', '--products', default=[], nargs='+', help='The products being ordered and their '
                                                                                  'amounts (id,name,amount) - only id or'
                                                                                  ' name required, but both commas are'
                                                                                  ' required')

def string_to_date(string):
  date = string.split('/')
  try:
      # If there were not 2 /, then raise an exception
      if len(date) != 3:
          raise Exception
      # Remove whitespace from each value and then convert it to an integer
      date = [_ for _ in map(int, map(str.strip, date))]
  except:
    print('Date was not of the correct form:\n'
          '\tExpected: (MM/DD/YYYY) such that 1 ≤ MM ≤ 12, 1 ≤ DD ≤ 31, 0 ≤ YYYY ≤ 9999'
          ' - requires both / even if a value is left empty',
          '\n\tRecieved:', string)
    return None
  return OrderDate(month=date[0], day=date[1], year=date[2])

def products_from_arg_list(arg_list):
  products = []
  _product = '' # Used if an exception occurs (so that the user knows the first product that failed)
  try:
    for product in arg_list:
      _product = product
      product = [_ for _ in map(str.strip, product.split(','))]
      # If there were not two commas, then raise an exception
      if len(product) != 3:
          raise Exception
      product[2] = int(product[2])
      products.append(OrderProduct(id=product[0], name=product[1], amount=product[2]))
  except:
    print('At least one product was not of the correct form:\n\tExpected: (id,name,amount)'
          '- only id or name required, but both commas are required',
          '\n\tRecieved:', _product)
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





# ----------====================---------- ----------===============---------- ----------====================----------
