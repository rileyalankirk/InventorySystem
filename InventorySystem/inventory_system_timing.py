"""A program to time a inventory system service.

Author: Riley Kirkpatrick
"""


import argparse
import grpc
import inventory_system_pb2 as inventory_system
import inventory_system_pb2_grpc as inventory_system_grpc
import numpy as np
import os
import random
import time
from inventory_system import get_dbsession, reset_db
from os import path

NUMBER_OF_TIMING_RUNS = 1
UNIQUE_PRODUCTS_PER_ORDER = 10
NUMBER_OF_PRODUCTS = 500 # Should be multiple of UNIQUE_PRODUCTS_PER_ORDER for simplicity
NUMBER_OF_ORDERS = NUMBER_OF_PRODUCTS // UNIQUE_PRODUCTS_PER_ORDER


def prepare_database_for_timing(stub):
    # Empty the database
    stub.ClearDatabase(inventory_system.Empty())

    # Add products to the database
    products = [inventory_system.Product(name='Product' + str(i), description='A product that carries the number ' + str(i),
                        manufacturer='Riley Kirkpatrick', wholesale_cost=i, sale_cost=i/2.5, amount=i)
                        for i in range(NUMBER_OF_PRODUCTS)]
    product_ids = stub.AddProducts(inventory_system.Products(products=products)).ids

    # Add orders to the database
    date = inventory_system.Date(year=2020, month=4, day=20)
    orders = []
    for i in range(NUMBER_OF_ORDERS):
        # Since amount=i//2, Product0 and Product1 should not be added to the first order
        products = [inventory_system.Product(name='Product' + str(i), amount=i//2) for i in range(i*UNIQUE_PRODUCTS_PER_ORDER, (i+1)*UNIQUE_PRODUCTS_PER_ORDER)]
        orders.append(inventory_system.Order(destination=str(i) + ' Main St, Bethlehem, PA 18018', date=date,
                                             products=products, is_paid=i % 2 == 0, is_shipped=i % 2 != 0))
    
    return product_ids, stub.CreateOrders(inventory_system.Orders(orders=orders)).ids

def run_timing(stub, number_of_run=None):
    # The number of the timing run
    run_number = ''
    if not number_of_run is None:
        run_number = ' (%s)' % number_of_run

    grpc_times = []
    product_ids, order_ids = prepare_database_for_timing(stub)

    # Timing for GetProductsByID
    start_time = time.monotonic() # The start of the timing

    products = stub.GetProductsByID(inventory_system.IDs(ids=product_ids)).products

    grpc_times.append(time.monotonic() - start_time)
    print('Finished timing GetProductsByID%s...' % run_number)


    # Timing for GetProductsByName
    start_time = time.monotonic() # The start of the timing

    names = ['Product' + str(i) for i in range(NUMBER_OF_PRODUCTS)]
    products = stub.GetProductsByName(inventory_system.Names(names=names)).products

    grpc_times.append(time.monotonic() - start_time)
    print('Finished timing GetProductsByName%s...' % run_number)


    # Timing for GetProductsByManufacturer
    start_time = time.monotonic() # The start of the timing

    products = stub.GetProductsByManufacturer(inventory_system.Manufacturer(manufacturer='Riley Kirkpatrick')).products

    grpc_times.append(time.monotonic() - start_time)
    print('Finished timing GetProductsByManufacturer%s...' % run_number)


    # Timing for GetOrdersByID
    start_time = time.monotonic() # The start of the timing

    orders = stub.GetOrdersByID(inventory_system.IDs(ids=order_ids)).orders

    grpc_times.append(time.monotonic() - start_time)
    print('Finished timing GetOrdersByID%s...' % run_number)
    

    # Timing for GetOrdersByStatus
    start_time = time.monotonic() # The start of the timing

    orders = stub.GetOrdersByStatus(inventory_system.OrderStatus(paid=False, shipped=False)).orders
    orders = stub.GetOrdersByStatus(inventory_system.OrderStatus(paid=False, shipped=True)).orders
    orders = stub.GetOrdersByStatus(inventory_system.OrderStatus(paid=True, shipped=False)).orders
    orders = stub.GetOrdersByStatus(inventory_system.OrderStatus(paid=True, shipped=True)).orders

    grpc_times.append(time.monotonic() - start_time)
    print('Finished timing GetOrdersByStatus%s...' % run_number)


    # Timing for GetProductsInStock
    start_time = time.monotonic() # The start of the timing

    products = stub.GetProductsInStock(inventory_system.Empty()).products

    grpc_times.append(time.monotonic() - start_time)
    print('Finished timing GetProductsInStock%s...' % run_number)


    # Timing for UpdateProducts
    start_time = time.monotonic() # The start of the timing
    
    products = [inventory_system.Product(id=id, wholesale_cost=random.random()*10000, sale_cost=random.random()*2500,
                                            amount=int(random.random()*100)) for id in product_ids]
    stub.UpdateProducts(inventory_system.Products(products=products))

    grpc_times.append(time.monotonic() - start_time)
    print('Finished timing UpdateProducts%s...' % run_number)


    # Timing for UpdateOrders
    _, order_ids = prepare_database_for_timing(stub)
    start_time = time.monotonic() # The start of the timing

    products = [inventory_system.Product(name='Product' + str(i), amount=1) for i in range(2*NUMBER_OF_ORDERS, 2*NUMBER_OF_ORDERS+1)]
    orders = [inventory_system.Order(id=id, is_paid=random.random() > 0.5, is_shipped=random.random() <= 0.5, products=products) for id in order_ids]
    stub.UpdateOrders(inventory_system.Orders(orders=orders))

    grpc_times.append(time.monotonic() - start_time)
    print('Finished timing UpdateOrders%s...' % run_number)


    # Timing for AddProducts
    prepare_database_for_timing(stub)
    start_time = time.monotonic() # The start of the timing

    products = [inventory_system.Product(name=str(i), description='A product of the number ' + str(i),
                            manufacturer='Toys R Us', wholesale_cost=i, sale_cost=i/2.5, amount=100)
                            for i in range(NUMBER_OF_PRODUCTS)]
    ids = stub.AddProducts(inventory_system.Products(products=products)).ids

    grpc_times.append(time.monotonic() - start_time)
    print('Finished timing AddProducts%s...' % run_number)


    # Timing for CreateOrders
    prepare_database_for_timing(stub)
    start_time = time.monotonic() # The start of the timing

    date = inventory_system.Date(year=2020, month=4, day=20)
    orders = []
    for i in range(NUMBER_OF_ORDERS):
        products = [inventory_system.Product(name='Product' + str(i), amount=1) for i in range(2*NUMBER_OF_ORDERS, 2*NUMBER_OF_ORDERS+1)]
        orders.append(inventory_system.Order(destination="Elmo's World", date=date, products=products,
                                                is_paid=i % 2 == 0, is_shipped=i % 2 != 0))
    ids = stub.CreateOrders(inventory_system.Orders(orders=orders)).ids

    grpc_times.append(time.monotonic() - start_time)
    print('Finished timing CreateOrders%s...\n\n' % run_number)

    return grpc_times

def main():
    parser = argparse.ArgumentParser(prog='inventory_system_timing', description='Runs a client that times interactions'
                                                                                 ' with an inventory system')
    parser.add_argument('ip', help='The IP of the server running the inventory system')
    parser.add_argument('-p', '--port', default='1337', help='The port of the server running the inventory system')
    args = parser.parse_args()

    with grpc.insecure_channel(args.ip + ':' + args.port) as channel:
        stub = inventory_system_grpc.InventorySystemStub(channel)
        
        grpc_times = [run_timing(stub, i + 1) for i in range(NUMBER_OF_TIMING_RUNS)]
        sum_of_times = np.sum(grpc_times, axis=0)


        print('GetProductsByID Time:', sum_of_times[0])
        print('GetProductsByName Time:', sum_of_times[1])
        print('GetProductsByManufacturer Time:', sum_of_times[2])
        print('GetOrdersByID Time:', sum_of_times[3])
        print('GetOrdersByStatus Time:', sum_of_times[4])
        print('GetProductsInStock Time:', sum_of_times[5])
        print('UpdateProducts Time:', sum_of_times[6])
        print('UpdateOrders Time:', sum_of_times[7])
        print('AddProducts Time:', sum_of_times[8])
        print('CreateOrders Time:', sum_of_times[9])
        print('Total Time:', sum(sum_of_times))


if __name__ == '__main__':
    main()
