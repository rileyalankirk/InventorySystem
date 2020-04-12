"""Client for connecting to an gRPC service to interact with an inventory system.

Author: Riley Kirkpatrick
"""


import argparse
import grpc
import sys
import inventory_system_pb2 as inventory_system
import inventory_system_pb2_grpc as inventory_system_grpc
from inventory_system import add_parsers_and_subparsers, get_date_and_products, products_from_arg_list,\
                             string_to_date, get_products_to_add, get_products_to_update

def to_inventory_system_products(products):
    """Converts a list of products to a list of inventory_system.Product objects.
    """
    _products = []
    for product in products:
        _products.append(inventory_system.Product(id=product.id, name=product.name, description=product.description,
                                                  manufacturer=product.manufacturer, wholesale_cost=product.wholesale_cost,
                                                  sale_cost=product.sale_cost, amount=product.amount))
    return _products

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
                    for product in products.products:
                        print(product)
                else:
                    print('There are no products of the given names.')
            elif args.command == 'get-products-by-manufacturer':
                products = stub.GetProductsByManufacturer(inventory_system.Manufacturer(manufacturer=args.manufacturer))
                for product in products.products: print(product)
            elif args.command == 'get-order':
                order = stub.GetOrder(inventory_system.ID(id=args.id))
                print(order)
            elif args.command == 'get-orders':
                orders = stub.GetOrders(inventory_system.OrderStatus(paid=args.paid, shipped=args.shipped))
                for order in orders.orders: print(order)
            elif args.command == 'add-products':
                products = to_inventory_system_products(get_products_to_add(args.products))
                ids = stub.AddProducts(inventory_system.Products(products=products))
                if len(ids.ids) > 0:
                    print('Product IDs:')
                    for id in ids.ids:
                        print(id)
                else:
                    print('Product creation was not successful. It may already exist. Try the get-product-by-* commands.')
            elif args.command == 'update-products':
                products = to_inventory_system_products(get_products_to_update(args.products))
                stub.UpdateProducts(inventory_system.Products(products=products))
            elif args.command == 'create-order':
                date, products = get_date_and_products(args.date, args.products)
                if date is None:
                    print('Order creation was not successful. It may already exist. Try the get-order command.')

                order_id = stub.CreateOrder(inventory_system.Order(destination=args.destination,
                                            date=date, is_paid=args.is_paid, is_shipped=args.is_shipped,
                                            products=products))
                if order_id.id != '':
                    print('Order ID:', order_id.id)
                else:
                    print('Order creation was not successful. It may already exist. Try the get-order command.')
            elif args.command == 'update-order':
                date, products = '', []
                if args.date != '':
                    date = string_to_date(args.date)
                    if not date is None:
                        date = inventory_system.Date(year=date.month, month=date.month, day=date.day)
                else:
                    date = inventory_system.Date(month=-1, day=-1, year=-1)
                if len(args.products) > 0:
                    products = products_from_arg_list(args.products)
                    if not products is None:
                        products = [inventory_system.Product(id=product.id, name=product.name, amount=product.amount) for product in products]
                if date is None or products is None:
                    return
                order_id = stub.UpdateOrder(inventory_system.Order(id=args.id, destination=args.destination,
                                            date=date, is_paid=args.is_paid, is_shipped=args.is_shipped,
                                            products=products))
        except grpc.RpcError as e:
            print(e.details())


if __name__ == '__main__':
    main()