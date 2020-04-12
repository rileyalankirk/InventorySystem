"""Client for connecting to an gRPC service to interact with an inventory system.

Author: Riley Kirkpatrick
"""


import argparse
import grpc
import sys
import inventory_system_pb2 as inventory_system
import inventory_system_pb2_grpc as inventory_system_grpc
from inventory_system import add_parsers_and_subparsers, get_date_and_products, products_from_arg_list, string_to_date


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
                message = ''
                for product in products: message += str(product) + '\n'
                if message == '':
                    print('There are no products in stock.')
                else:
                    print(message)
            elif args.command == 'get-product-by-id':
                product = stub.GetProductByID(inventory_system.ID(id=args.id))
                print(product)
            elif args.command == 'get-product-by-name':
                product = stub.GetProductByName(inventory_system.Name(name=args.name))
                print(product)
            elif args.command == 'get-products-by-manufacturer':
                products = stub.GetProductsByManufacturer(inventory_system.Manufacturer(manufacturer=args.manufacturer))
                for product in products: print(product)
            elif args.command == 'get-order':
                order = stub.GetOrder(inventory_system.ID(id=args.id))
                print(order)
            elif args.command == 'get-orders':
                orders = stub.GetOrders(inventory_system.OrderStatus(paid=args.paid, shipped=args.shipped))
                for order in orders: print(order)
            elif args.command == 'add-product':
                product_id = stub.AddProduct(inventory_system.Product(name=args.name, description=args.description,
                                            manufacturer=args.manufacturer, wholesale_cost=args.wholesale_cost,
                                            sale_cost=args.sale_cost, amount=args.amount))
                if product_id.id != '':
                    print('Product ID:', product_id.id)
                else:
                    print('Product creation was not successful. It may already exist. Try the get-product-by-* commands.')
            elif args.command == 'update-product':
                return_val = stub.UpdateProduct(inventory_system.Product(id=args.id, name=args.name, description=args.description,
                                            manufacturer=args.manufacturer, wholesale_cost=args.wholesale_cost,
                                            sale_cost=args.sale_cost, amount=args.amount))
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