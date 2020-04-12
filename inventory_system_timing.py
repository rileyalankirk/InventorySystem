"""A program to time a inventory system service.

Author: Riley Kirkpatrick
"""


import argparse
import grpc
import inventory_system_pb2 as inventory_system
import inventory_system_pb2_grpc as inventory_system_grpc
import os
import random
import time
from inventory_system import get_dbsession, reset_db
from os import path

UNIQUE_PRODUCTS_PER_ORDER = 10
NUMBER_OF_PRODUCTS = 1000 # Should be multiple of UNIQUE_PRODUCTS_PER_ORDER for simplicity
NUMBER_OF_ORDERS = NUMBER_OF_PRODUCTS // UNIQUE_PRODUCTS_PER_ORDER


def prepare_database_for_timing(stub):
    stub.ClearDatabase(inventory_system.Empty())

    product_ids, order_ids = [], []

    # Add products to the database
    for i in range(NUMBER_OF_PRODUCTS):
        product = inventory_system.Product(name='Product' + str(i), description='A product that carries the number ' + str(i),
                          manufacturer='Riley Kirkpatrick', wholesale_cost=i, sale_cost=i/2.5, amount=i)
        product_ids.append(stub.AddProduct(product).id)

    # Add orders to the database
    date = inventory_system.Date(year=2020, month=4, day=20)
    for i in range(NUMBER_OF_ORDERS):
        is_paid, is_shipped = False, False
        if i % 2 == 0:
            is_paid = True
        else:
            is_shipped = True
        # Since amount=i//2, Product0 and Product1 should not be added to the first order
        products = [inventory_system.Product(name='Product' + str(i), amount=i//2) for i in range(i*UNIQUE_PRODUCTS_PER_ORDER, (i+1)*UNIQUE_PRODUCTS_PER_ORDER)]
        order = inventory_system.Order(destination=str(i) + ' Main St, Bethlehem, PA 18018', date=date, products=products,
                      is_paid=is_paid, is_shipped=is_shipped)
        order_ids.append(stub.CreateOrder(order).id)
    
    return product_ids, order_ids


def main():
    parser = argparse.ArgumentParser(prog='inventory_system_timing', description='Runs a client that times interactions'
                                                                                 ' with an inventory system')
    parser.add_argument('ip', help='The IP of the server running the inventory system')
    parser.add_argument('--port', default='1337', help='The IP of the server running the inventory system')
    args = parser.parse_args()

    with grpc.insecure_channel(args.ip + ':' + args.port) as channel:
        stub = inventory_system_grpc.InventorySystemStub(channel)
        
        grpc_times = []

        # Timing for GetProductByID
        product_ids, _ = prepare_database_for_timing(stub)
        start_time = time.monotonic() # The start of the timing

        for id in product_ids:
            product = stub.GetProductByID(inventory_system.ID(id=id))

        grpc_times.append(time.monotonic() - start_time)
        print('Finished timing GetProductByID...')


        # Timing for GetProductByName
        prepare_database_for_timing(stub)
        start_time = time.monotonic() # The start of the timing

        for i in range(NUMBER_OF_PRODUCTS):
            name = 'Product' + str(i)
            product = stub.GetProductByName(inventory_system.Name(name=name))

        grpc_times.append(time.monotonic() - start_time)
        print('Finished timing GetProductByName...')


        # Timing for GetProductsByManufacturer
        prepare_database_for_timing(stub)
        start_time = time.monotonic() # The start of the timing

        products = stub.GetProductsByManufacturer(inventory_system.Manufacturer(manufacturer='Riley Kirkpatrick'))

        grpc_times.append(time.monotonic() - start_time)
        print('Finished timing GetProductByManufacturer...')


        # Timing for GetOrder
        _, order_ids = prepare_database_for_timing(stub)
        start_time = time.monotonic() # The start of the timing

        for id in order_ids:
            order = stub.GetOrder(inventory_system.ID(id=id))

        grpc_times.append(time.monotonic() - start_time)
        print('Finished timing GetOrder...')
        

        # Timing for GetOrders
        prepare_database_for_timing(stub)
        start_time = time.monotonic() # The start of the timing

        stub.GetOrders(inventory_system.OrderStatus(paid=False, shipped=False))
        stub.GetOrders(inventory_system.OrderStatus(paid=False, shipped=True))
        stub.GetOrders(inventory_system.OrderStatus(paid=True, shipped=False))
        stub.GetOrders(inventory_system.OrderStatus(paid=True, shipped=True))

        grpc_times.append(time.monotonic() - start_time)
        print('Finished timing GetOrders...')


        # Timing for GetProductsInStock
        prepare_database_for_timing(stub)
        start_time = time.monotonic() # The start of the timing

        stub.GetProductsInStock(inventory_system.Empty())

        grpc_times.append(time.monotonic() - start_time)
        print('Finished timing GetProductsInStock...')


        # Timing for UpdateProduct
        product_ids, _ = prepare_database_for_timing(stub)
        start_time = time.monotonic() # The start of the timing

        for id in product_ids:
            value = random.random()*100
            stub.UpdateProduct(inventory_system.Product(id=id, wholesale_cost=value*100, sale_cost=value*25, amount=int(value)))

        grpc_times.append(time.monotonic() - start_time)
        print('Finished timing UpdateProduct...')


        # Timing for UpdateOrder
        _, order_ids = prepare_database_for_timing(stub)
        start_time = time.monotonic() # The start of the timing
        
        products = [inventory_system.Product(name='Product' + str(i), amount=1) for i in range(2*NUMBER_OF_ORDERS*UNIQUE_PRODUCTS_PER_ORDER, (2*NUMBER_OF_ORDERS+1)*UNIQUE_PRODUCTS_PER_ORDER)]
        for id in order_ids:
            boolean = random.random() > 0.5
            stub.UpdateOrder(inventory_system.Order(id=id, is_paid=boolean, is_shipped=not boolean, products=products))

        grpc_times.append(time.monotonic() - start_time)
        print('Finished timing UpdateOrder...')


        # Timing for AddProduct
        prepare_database_for_timing(stub)
        start_time = time.monotonic() # The start of the timing

        for i in range(NUMBER_OF_PRODUCTS):
            product = inventory_system.Product(name=str(i), description='A product of the number ' + str(i),
                                   manufacturer='Toys R Us', wholesale_cost=i, sale_cost=i/2.5, amount=100)
            stub.AddProduct(inventory_system.Product())

        grpc_times.append(time.monotonic() - start_time)
        print('Finished timing AddProduct...')


        # Timing for CreateOrder
        prepare_database_for_timing(stub)
        start_time = time.monotonic() # The start of the timing

        date = inventory_system.Date(year=2020, month=4, day=20)
        for i in range(NUMBER_OF_ORDERS):
            is_paid, is_shipped = False, False
            if i % 2 == 0:
                is_paid = True
            else:
                is_shipped = True
            products = [inventory_system.Product(name=str(i), amount=1) for i in range(i*UNIQUE_PRODUCTS_PER_ORDER, (i+1)*UNIQUE_PRODUCTS_PER_ORDER)]
            order = inventory_system.Order(destination="Elmo's World", date=date, products=products, is_paid=is_paid,
                               is_shipped=is_shipped)
            stub.CreateOrder(order)

        grpc_times.append(time.monotonic() - start_time)
        print('Finished timing CreateOrder...\n\n')

        print('GetProductByID Time:', grpc_times[0])
        print('GetProductByName Time:', grpc_times[1])
        print('GetProductsByManufacturer Time:', grpc_times[2])
        print('GetOrder Time:', grpc_times[3])
        print('GetOrders Time:', grpc_times[4])
        print('GetProductsInStock Time:', grpc_times[5])
        print('UpdateProduct Time:', grpc_times[6])
        print('UpdateOrder Time:', grpc_times[7])
        print('AddProduct Time:', grpc_times[8])
        print('CreateOrder Time:', grpc_times[9])
        print('Total Time:', sum(grpc_times))


if __name__ == '__main__':
    main()