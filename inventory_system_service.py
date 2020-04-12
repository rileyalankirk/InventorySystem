"""This program implements a gRPC service to interact with an inventory system. Clients may retrieve,
add, and update both products and orders in the system.

Author: Riley Kirkpatrick
"""

# GetOrders

import argparse
import grpc
import inventory_system_pb2 as inventory_system
import inventory_system_pb2_grpc as inventory_system_grpc
import os
import sys
import uuid
from concurrent import futures
from inventory_system import create_inventory_system_db, get_dbsession, reset_db, get_product_by_id, get_product_by_name,\
                             get_products_by_manufacturer, add_product, update_product, get_products_in_stock,\
                             get_order, create_order, get_orders, update_order
from os import path


class InventorySystem(inventory_system_grpc.InventorySystemServicer):
  """A service that allows you to keep track of an inventory of products and the orders for those products
  """

  def __init__(self, database_path):
    if not path.exists(database_path):
      create_inventory_system_db(database_path)
    self.database = get_dbsession(database_path)

  def to_inventory_system_product(self, product):
    """Convert a product object to an inventory_system.Product object
    """
    return inventory_system.Product(id=product.id, name=product.name, description=product.description,
                                    manufacturer=product.manufacturer, wholesale_cost=product.wholesale_cost,
                                    sale_cost=product.sale_cost, amount=product.amount)
  
  def to_inventory_system_order(self, order):
    date = inventory_system.Date(year=order.date.year, month=order.date.month, day=order.date.day)
    products = [inventory_system.Product(id=product.id, name=product.name, amount=product.amount) for product in order.products]
    return inventory_system.Order(id=order.id, destination=order.destination, date=date, is_paid=order.is_paid,
                                  is_shipped=order.is_shipped, products=products)

  def __get_product_by(self, context, product=None, error=''):
    if error != '':
      context.set_code(grpc.StatusCode.NOT_FOUND)
      context.set_details(error)
      return inventory_system.Product()
    return self.to_inventory_system_product(product)

  def GetProductByID(self, request, context):
    """Gets a product by its ID 
    """
    product = get_product_by_id(self.database, request.id)
    error = ''
    if product is None:
      error = 'No product was found for the id ' + request.id
    return self.__get_product_by(context, product, error)

  def GetProductByName(self, request, context):
    """Gets a product by its name 
    """
    product = get_product_by_name(self.database, request.name)
    error = ''
    if product is None:
      error = 'No product was found for the name ' + request.name
    return self.__get_product_by(context, product, error)

  def GetProductsByManufacturer(self, request, context):
    """Retrieves all products from a given manufacturer 
    """
    products = get_products_by_manufacturer(self.database, request.manufacturer)
    error = ''
    if products is None:
      context.set_code(grpc.StatusCode.NOT_FOUND)
      context.set_details('No products were found for the manufacturer ' + request.manufacturer)
    return inventory_system.Products(products=[self.to_inventory_system_product(product) for product in products])

  def AddProduct(self, request, context):
    """Adds a new product that does not have the same name as previous products and the ID is
    assigned by the server; returns the ID of the product if it was added successfully
    otherwise empty string 
    """
    return inventory_system.ID(id=add_product(self.database, request))

  def UpdateProduct(self, request, context):
    """Update products (name and ID cannot be updated)
    """
    update_product(self.database, request)
    return inventory_system.Empty()

  def GetProductsInStock(self, request, context):
    """Retrieves all products that are in stock  
    """
    return inventory_system.Products(products=[self.to_inventory_system_product(product) for product in get_products_in_stock(self.database)])

  def GetOrder(self, request, context):
    """Gets an order by its ID 
    """
    order = get_order(self.database, request.id)
    if order is None:
      context.set_code(grpc.StatusCode.NOT_FOUND)
      context.set_details('No order was found for the id ' + request.id)
    return self.to_inventory_system_order(order)

  def CreateOrder(self, request, context):
    """Creates an order if there is enough product in stock with an ID assigned by the server;
    returns the ID of the product if it was added successfully otherwise empty string
    """
    id = create_order(self.database, request)
    return inventory_system.ID(id=id)

  def UpdateOrder(self, request, context):
    """Update orders (ID cannot be updated) and if there is not enough product the order is not updated
    """
    update_order(self.database, request)
    return inventory_system.Empty()

  def GetOrders(self, request, context):
    """Retrieves all orders that are unshipped, unpaid, or both  
    """
    orders = get_orders(self.database, request)
    if len(orders) == 0:
      context.set_code(grpc.StatusCode.NOT_FOUND)
      context.set_details('No orders were found satisfying is_paid=' + str(request.paid) +
                          ' and/or is_shipped=' + str(request.shipped))
    return inventory_system.Orders(orders=[self.to_inventory_system_order(order) for order in orders])
  
  def ClearDatabase(self, request, context):
    """Clears inventory system database
    """
    reset_db(self.database)
    return inventory_system.Empty()


def main():
  parser = argparse.ArgumentParser(prog='inventory_system_service',
                                   description='Runs a server that allows clients to interact'
                                               'with an inventory system')
  parser.add_argument('-p', '--port', default='1337', help='The port the server runs on.')
  parser.add_argument('-db', '--database_path', default='inventory_system.db', help='The file that the database is stored in.')
  args = parser.parse_args()

  # Must be one worker since the database can only be accessed within one thread
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))

  inv_system = InventorySystem(args.database_path)
  inventory_system_grpc.add_InventorySystemServicer_to_server(inv_system, server)
  server.add_insecure_port('[::]:' + args.port)
  server.start()
  try:
    server.wait_for_termination()
  except KeyboardInterrupt:
    # No need to save or close the database since it is already handled
    pass


if __name__ == '__main__':
    main()