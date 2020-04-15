"""This program implements a gRPC service to interact with an inventory system. Clients may retrieve,
add, and update both products and orders in the system.

Author: Riley Kirkpatrick
"""

import argparse
import grpc
import inventory_system
import inventory_system_pb2
import inventory_system_pb2_grpc
import os
import sys
import uuid
from concurrent import futures
from os import path


class InventorySystem(inventory_system_pb2_grpc.InventorySystemServicer):
  """A service that allows you to keep track of an inventory of products and the orders for those products
  """

  def __init__(self, database_path):
    # Creates the database if it does not exist
    if not path.exists(database_path):
      inventory_system.create_inventory_system_db(database_path)
    # Creates the connection to the database
    self.database = inventory_system.get_dbsession(database_path)

  def to_inventory_system_product(self, product):
    """Convert a product object to an inventory_system.Product object
    """
    return inventory_system_pb2.Product(id=product.id, name=product.name, description=product.description,
                                    manufacturer=product.manufacturer, wholesale_cost=product.wholesale_cost,
                                    sale_cost=product.sale_cost, amount=product.amount)
  
  def to_inventory_system_order(self, order):
    date = inventory_system_pb2.Date(year=order.date.year, month=order.date.month, day=order.date.day)
    products = [inventory_system_pb2.Product(id=product.id, name=product.name, amount=product.amount) for product in order.products]
    return inventory_system_pb2.Order(id=order.id, destination=order.destination, date=date, is_paid=order.is_paid,
                                  is_shipped=order.is_shipped, products=products)

  def set_status_code_not_found(self, context, details=''):
    """Sets the status code if a product or order is not found
    """
    context.set_code(grpc.StatusCode.NOT_FOUND)
    context.set_details(details)

  def GetProductsByID(self, request, context):
    """Gets products by their IDs
    """
    products = inventory_system.GetProductsByID(self.database, request.ids)
    if len(products) == 0:
      self.set_status_code_not_found(context, 'No products were found for the given IDs ' + str(request.ids))
    return inventory_system_pb2.Products(products=[self.to_inventory_system_product(product) for product in products])

  def GetProductsByName(self, request, context):
    """Gets a product by its name 
    """
    products = inventory_system.GetProductsByName(self.database, request.names)
    if len(products) == 0:
      self.set_status_code_not_found(context, 'No products were found for the given names ' + str(request.names))
    return inventory_system_pb2.Products(products=[self.to_inventory_system_product(product) for product in products])

  def GetProductsByManufacturer(self, request, context):
    """Retrieves all products from a given manufacturer 
    """
    products = inventory_system.GetProductsByManufacturer(self.database, request.manufacturer)
    if len(products) == 0:
      self.set_status_code_not_found(context, 'No products were found for the manufacturer ' + str(request.manufacturer))
    return inventory_system_pb2.Products(products=[self.to_inventory_system_product(product) for product in products])

  def AddProducts(self, request, context):
    """Adds new products that do not have the same names as previous products and the IDs are
    assigned by the server; returns the IDs of the products if they were added successfully
    otherwise empty list 
    """
    return inventory_system_pb2.IDs(ids=inventory_system.AddProducts(self.database, request.products))

  def UpdateProducts(self, request, context):
    """Updates products (name and ID cannot be updated)
    """
    inventory_system.UpdateProducts(self.database, request.products)
    return inventory_system_pb2.Empty()

  def GetProductsInStock(self, request, context):
    """Retrieves all products that are in stock  
    """
    return inventory_system_pb2.Products(products=[self.to_inventory_system_product(product)
                                                   for product in inventory_system.GetProductsInStock(self.database)])

  def GetOrdersByID(self, request, context):
    """Gets an order by its ID 
    """
    orders = inventory_system.GetOrdersByID(self.database, request.ids)
    if len(orders) == 0:
      self.set_status_code_not_found(context, 'No orders were found for the ids ' + str(request.ids))
    return inventory_system_pb2.Orders(orders=[self.to_inventory_system_order(order) for order in orders])

  def CreateOrders(self, request, context):
    """Creates orders if there is enough product in stock with IDs assigned by the server;
    returns the IDs of the orders if they were added successfully otherwise empty list
    """
    ids = inventory_system.CreateOrders(self.database, request.orders)
    if len(ids) == 0:
      self.set_status_code_not_found(context, 'Failed to create all orders.')
    return inventory_system_pb2.IDs(ids=ids)

  def UpdateOrders(self, request, context):
    """Update orders (ID cannot be updated) and if there is not enough product the order is not updated
    """
    inventory_system.UpdateOrders(self.database, request.orders)
    return inventory_system_pb2.Empty()

  def GetOrdersByStatus(self, request, context):
    """Retrieves all orders that are unshipped, unpaid, or both  
    """
    orders = inventory_system.GetOrdersByStatus(self.database, request)
    if len(orders) == 0:
      self.set_status_code_not_found(context, 'No orders were found satisfying is_paid=' + str(request.paid) +
                                         ' and/or is_shipped=' + str(request.shipped))
    return inventory_system_pb2.Orders(orders=[self.to_inventory_system_order(order) for order in orders])
  
  def ClearDatabase(self, request, context):
    """Clears inventory system database
    """
    inventory_system.reset_db(self.database)
    return inventory_system_pb2.Empty()


def main():
  parser = argparse.ArgumentParser(prog='inventory_system_service',
                                   description='Runs a server that allows clients to interact'
                                               'with an inventory system')
  parser.add_argument('-p', '--port', default='1337', help='The port the server runs on.')
  parser.add_argument('-db', '--database_path', default='inventory_system.db', help='The file that the database is stored in.')
  args = parser.parse_args()

  # Must be one worker since the database must be accessed within one thread
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
  inv_system = InventorySystem(args.database_path)
  inventory_system_pb2_grpc.add_InventorySystemServicer_to_server(inv_system, server)
  server.add_insecure_port('[::]:' + args.port)
  server.start()
  try:
    server.wait_for_termination()
  except KeyboardInterrupt:
    # No need to save or close the database since it is already handled
    # Pass so that the program terminates quietly
    pass


if __name__ == '__main__':
    main()