"""Client for connecting to an gRPC service to interact with an inventory system.

Author: Riley Kirkpatrick
"""


import argparse
import grpc
import sys
import inventory_system_pb2 as inventory_system
import inventory_system_pb2_grpc as inventory_system_grpc
from inventory_system import add_parsers_and_subparsers, get_date_and_products, products_from_arg_list,\
                             string_to_date, get_products_to_add, get_products_to_update, get_orders_to_update,\
                             get_orders_to_create

def to_inventory_system_products(products):
    """Converts a list of products to a list of inventory_system.Product objects.
    """
    _products = []
    for product in products:
        _products.append(inventory_system.Product(id=product.id, name=product.name, description=product.description,
                                                  manufacturer=product.manufacturer, wholesale_cost=product.wholesale_cost,
                                                  sale_cost=product.sale_cost, amount=product.amount))
    return _products

def to_inventory_system_orders(orders):
    """Converts a list of orders to a list of inventory_system.Order objects.
    """
    _orders = []
    for order in orders:
        if order.date == '':
            order.date = inventory_system.Date(month=-1, day=-1, year=-1)
        products = [inventory_system.Product(id=product.id, name=product.name, amount=product.amount) for product in order.products]
        _orders.append(inventory_system.Order(id=order.id, destination=order.destination, date=order.date,
                                              is_paid=order.is_paid, is_shipped=order.is_shipped, products=products))
    return _orders

def main():
    # Create an argument parser with a required ip argument and subparsers for each function that
    # interacts with the inventory system
    parser = argparse.ArgumentParser(prog='inventory_system_service', description='Runs a client'
                                                   'that that interacts with an inventory system')
    add_parsers_and_subparsers(parser)
    args = parser.parse_args()

     # If no arguments were supplied, print the usage message for the program
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        return

    with grpc.insecure_channel(args.ip + ':' + args.port) as channel:
        stub = inventory_system_grpc.InventorySystemStub(channel)
        try:
            # Run the command that is passed as an argument to the program
            if args.command == 'get-products-in-stock':
                products = stub.GetProductsInStock(inventory_system.Empty())
                if len(products.products) > 0:
                    for product in products.products:
                        print(product)
                else:
                    print('There are no products in stock.')
            elif args.command == 'get-products-by-id':
                products = stub.GetProductsByID(inventory_system.IDs(ids=args.ids))
                if len(products.products) > 0:
                    for product in products.products:
                        print(product)
                else:
                    print('There are no products of the given IDs.')
            elif args.command == 'get-products-by-name':
                products = stub.GetProductsByName(inventory_system.Names(names=args.names))
                if len(products.products) > 0:
                    for product in products.products: print(product)
                else:
                    print('There are no products of the given names.')
            elif args.command == 'get-products-by-manufacturer':
                products = stub.GetProductsByManufacturer(inventory_system.Manufacturer(manufacturer=args.manufacturer))
                if len(products.products) > 0:
                    for product in products.products: print(product)
                else:
                    print('There are no products with the given manufacturer.')
            elif args.command == 'get-orders-by-id':
                orders = stub.GetOrdersByID(inventory_system.IDs(ids=args.ids))
                if len(orders.orders) > 0:
                    for order in orders.orders: print(order)
                else:
                    print('There are no orders with the given IDs.')
            elif args.command == 'get-orders-by-status':
                orders = stub.GetOrdersByStatus(inventory_system.OrderStatus(paid=args.paid, shipped=args.shipped))
                if len(order.orders) > 0:
                    for order in orders.orders: print(order)
                else:
                    print('There are no orders with the given status.')
            elif args.command == 'add-products':
                products = to_inventory_system_products(get_products_to_add(args.products))
                ids = stub.AddProducts(inventory_system.Products(products=products))
                if len(ids.ids) > 0:
                    print('Product IDs:')
                    for id in ids.ids: print(id)
                else:
                    print('Product creation was not successful. It may already exist. Try the get-products-by-* commands.')
            elif args.command == 'update-products':
                products = to_inventory_system_products(get_products_to_update(args.products))
                stub.UpdateProducts(inventory_system.Products(products=products))
            elif args.command == 'create-orders':
                orders = to_inventory_system_orders(get_orders_to_create(args.orders))
                ids = stub.CreateOrders(inventory_system.orders(orders=orders))
                
                if len(ids.ids) == 0:
                    print('Order creation was not successful. They may already exist. Try the get-orders command.')
                else:
                    print('Order IDs:', ids.ids)
                    for id in ids.ids: print(id)
            elif args.command == 'update-orders':
                orders = to_inventory_system_orders(get_orders_to_update(args.orders))
                stub.UpdateOrders(inventory_system.Orders(orders=orders))
        except grpc.RpcError as e:
            print(e.details())


if __name__ == '__main__':
    main()