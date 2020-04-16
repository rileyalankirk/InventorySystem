"""Test the inventory system client argparse.

Author: Riley Kirkpatrick
"""


import inventory_system


def add_products(products=[]):
    return inventory_system.get_products_to_add(products)

def update_products(products=[]):
    return inventory_system.get_products_to_update(products)

def create_orders(orders=[]):
    return inventory_system.get_orders_to_create(orders)

def update_orders(orders=[]):
    return inventory_system.get_orders_to_update(orders)

def main():
    # Test add_products argparser
    # Products: (name,description,manufacturer,wholesale_cost,sale_cost,amount)      --   Required: name
    assert(add_products() == [])
    assert(add_products([',description,manufacturer,wholesale_cost,sale_cost,amount',
                         ',description,manufacturer,wholesale_cost,sale_cost,amount',
                         ',description,manufacturer,wholesale_cost,sale_cost,amount']) == [])
                         
    for i in add_products(['name0', 'name1,', 'name2,,', 'name3,,,', 'name4,,,,', 'name5,,,,,', 'name0,,,,,,']):
        assert(i.name in ['name0', 'name1', 'name2', 'name3', 'name4', 'name5'])
        assert(i.description == '')
        assert(i.manufacturer == '')
        assert(i.wholesale_cost == 0.0)
        assert(i.sale_cost == 0.0)
        assert(i.amount == 0)

    for i in add_products(['name1,descr', 'name2,descr,', 'name3,descr,,', 'name4,descr,,,', 'name5,descr,,,,']):
        assert(i.name in ['name1', 'name2', 'name3', 'name4', 'name5'])
        assert(i.description == 'descr')
        assert(i.manufacturer == '')
        assert(i.wholesale_cost == 0.0)
        assert(i.sale_cost == 0.0)
        assert(i.amount == 0)
    
    for i in add_products(['name2,,manu', 'name3,,manu,', 'name4,,manu,,', 'name5,,manu,,,']):
        assert(i.name in ['name2', 'name3', 'name4', 'name5'])
        assert(i.description == '')
        assert(i.manufacturer == 'manu')
        assert(i.wholesale_cost == 0.0)
        assert(i.sale_cost == 0.0)
        assert(i.amount == 0)
    
    for i in add_products(['name3,,,1.1', 'name4,,,1.1,', 'name5,,,1.1,,']):
        assert(i.name in ['name3', 'name4', 'name5'])
        assert(i.description == '')
        assert(i.manufacturer == '')
        assert(i.wholesale_cost == 1.1)
        assert(i.sale_cost == 0.0)
        assert(i.amount == 0)
        
    for i in add_products(['name4,,,,1.2', 'name5,,,,1.2,']):
        assert(i.name in ['name4', 'name5'])
        assert(i.description == '')
        assert(i.manufacturer == '')
        assert(i.wholesale_cost == 0.0)
        assert(i.sale_cost == 1.2)
        assert(i.amount == 0)
    
    i =  add_products(['name5,,,,,5'])
    if len(i) == 1:
        i = i[0]
    else:
        assert(False)
    assert(i.name == 'name5')
    assert(i.description == '')
    assert(i.manufacturer == '')
    assert(i.wholesale_cost == 0.0)
    assert(i.sale_cost == 0)
    assert(i.amount == 5)

    # Test update_products argparser
    # Products: (id,name,description,manufacturer,wholesale_cost,sale_cost,amount)   --   Required: id OR name
    assert(update_products() == [])
    assert(update_products([',,description,manufacturer,wholesale_cost,sale_cost,amount',
                         ',,description,manufacturer,wholesale_cost,sale_cost,amount',
                         ',,description,manufacturer,wholesale_cost,sale_cost,amount']) == [])
    
    for i in update_products(['id0,', 'id1,,', 'id2,,,', 'id3,,,,', 'id4,,,,,', 'id5,,,,,,', 'id0,,,,,,,']):
        assert(i.id in ['id0', 'id1', 'id2', 'id3', 'id4', 'id5'])
        assert(i.name == '')
        assert(i.description == '')
        assert(i.manufacturer == '')
        assert(i.wholesale_cost == 0.0)
        assert(i.sale_cost == 0.0)
        assert(i.amount == 0)

    for i in update_products([',name0', ',name1,', ',name2,,', ',name3,,,', ',name4,,,,', ',name5,,,,,', ',name0,,,,,,']):
        assert(i.id == '')
        assert(i.name in ['name0', 'name1', 'name2', 'name3', 'name4', 'name5'])
        assert(i.description == '')
        assert(i.manufacturer == '')
        assert(i.wholesale_cost == 0.0)
        assert(i.sale_cost == 0.0)
        assert(i.amount == 0)

    for i in update_products([',name1,descr', ',name2,descr,', ',name3,descr,,', ',name4,descr,,,', ',name5,descr,,,,']):
        assert(i.id == '')
        assert(i.name in ['name1', 'name2', 'name3', 'name4', 'name5'])
        assert(i.description == 'descr')
        assert(i.manufacturer == '')
        assert(i.wholesale_cost == 0.0)
        assert(i.sale_cost == 0.0)
        assert(i.amount == 0)
    
    for i in update_products([',name2,,manu', ',name3,,manu,', ',name4,,manu,,', ',name5,,manu,,,']):
        assert(i.id == '')
        assert(i.name in ['name2', 'name3', 'name4', 'name5'])
        assert(i.description == '')
        assert(i.manufacturer == 'manu')
        assert(i.wholesale_cost == 0.0)
        assert(i.sale_cost == 0.0)
        assert(i.amount == 0)
    
    for i in update_products([',name3,,,1.1', ',name4,,,1.1,', ',name5,,,1.1,,']):
        assert(i.id == '')
        assert(i.name in ['name3', 'name4', 'name5'])
        assert(i.description == '')
        assert(i.manufacturer == '')
        assert(i.wholesale_cost == 1.1)
        assert(i.sale_cost == 0.0)
        assert(i.amount == 0)
        
    for i in update_products([',name4,,,,1.2', ',name5,,,,1.2,']):
        assert(i.id == '')
        assert(i.name in ['name4', 'name5'])
        assert(i.description == '')
        assert(i.manufacturer == '')
        assert(i.wholesale_cost == 0.0)
        assert(i.sale_cost == 1.2)
        assert(i.amount == 0)
    
    i =  update_products([',name5,,,,,5'])
    if len(i) == 1:
        i = i[0]
    else:
        assert(False)
    assert(i.id == '')
    assert(i.name == 'name5')
    assert(i.description == '')
    assert(i.manufacturer == '')
    assert(i.wholesale_cost == 0.0)
    assert(i.sale_cost == 0)
    assert(i.amount == 5)

    # Test create_orders argparser
    # Orders: (destination,date,is_paid,is_shipped,prod1,prod2,...,prodN)            --   Required: products (1+)
    # Products: (id;name;amount)                                                     --   Required: id OR name, amount
    # Date: (MM/DD/YYYY)
    assert(create_orders() == [])
    assert(create_orders(['destination,11/11/1111,is_paid,is_shipped', 'destination,11/11/1111,is_paid,is_shipped,',
                         'destination,11/11/1111,is_paid,is_shipped,,']) == [])
                         
    for i in create_orders([',,,,id0;name0;1', ',,,,id1;name1;1', ',,,,id2;name2;1', ',,,,id3;name3;1,id4;name4;1']):
        assert(i.destination == '')
        assert(i.date == '')
        assert(i.is_paid == False)
        assert(i.is_shipped == False)
        assert(len(i.products) > 0)

    for i in create_orders(['dest,,,,id0;name0;1', 'dest,,,,id1;name1;1', 'dest,,,,id2;name2;1', 'dest,,,,id3;name3;1,id4;name4;1']):
        assert(i.destination == 'dest')
        assert(i.date == '')
        assert(i.is_paid == False)
        assert(i.is_shipped == False)
        assert(len(i.products) > 0)
    
    for i in create_orders([',1/1/1,,,id0;name0;1', ',1/1/1,,,id1;name1;1', ',1/1/1,,,id2;name2;1', ',1/1/1,,,id3;name3;1,id4;name4;1']):
        assert(i.destination == '')
        assert(i.date.day == 1 and i.date.month == 1 and i.date.year == 1)
        assert(i.is_paid == False)
        assert(i.is_shipped == False)
        assert(len(i.products) > 0)
    
    for i in create_orders([',,t,,id0;name0;1', ',,t,,id1;name1;1', ',,t,,id2;name2;1', ',,t,,id3;name3;1,id4;name4;1']):
        assert(i.destination == '')
        assert(i.date == '')
        assert(i.is_paid == True)
        assert(i.is_shipped == False)
        assert(len(i.products) > 0)
    
    for i in create_orders([',,,t,id0;name0;1', ',,,t,id1;name1;1', ',,,t,id2;name2;1', ',,,t,id3;name3;1,id4;name4;1']):
        assert(i.destination == '')
        assert(i.date == '')
        assert(i.is_paid == False)
        assert(i.is_shipped == True)
        assert(len(i.products) > 0)

    # Test update_orders argparser
    # Orders: (id,destination,date,is_paid,is_shipped,prod1,prod2,...,prodN)            --   Required: id, products (1+)
    # Products: (id;name;amount)                                                     --   Required: id OR name, amount
    # Date: (MM/DD/YYYY)
    assert(update_orders() == [])
    assert(update_orders([',destination,11/11/1111,is_paid,is_shipped', ',destination,11/11/1111,is_paid,is_shipped,',
                         ',destination,11/11/1111,is_paid,is_shipped,,']) == [])           
                         
    for i in update_orders(['id0,,,,,id0;name0;1', 'id1,,,,,id1;name1;1', 'id2,,,,,id2;name2;1', 'id3,,,,,id3;name3;1,id4;name4;1']):
        assert(i.id in ['id0', 'id1', 'id2', 'id3'])
        assert(i.destination == '')
        assert(i.date == '')
        assert(i.is_paid == False)
        assert(i.is_shipped == False)
        assert(len(i.products) > 0)

    for i in update_orders(['id0,dest,,,,id0;name0;1', 'id1,dest,,,,id1;name1;1', 'id2,dest,,,,id2;name2;1', 'id3,dest,,,,id3;name3;1,id4;name4;1']):
        assert(i.id in ['id0', 'id1', 'id2', 'id3'])
        assert(i.destination == 'dest')
        assert(i.date == '')
        assert(i.is_paid == False)
        assert(i.is_shipped == False)
        assert(len(i.products) > 0)
    
    for i in update_orders(['id0,,1/1/1,,,id0;name0;1', 'id1,,1/1/1,,,id1;name1;1', 'id2,,1/1/1,,,id2;name2;1', 'id3,,1/1/1,,,id3;name3;1,id4;name4;1']):
        assert(i.id in ['id0', 'id1', 'id2', 'id3'])
        assert(i.destination == '')
        assert(i.date.day == 1 and i.date.month == 1 and i.date.year == 1)
        assert(i.is_paid == False)
        assert(i.is_shipped == False)
        assert(len(i.products) > 0)
    
    for i in update_orders(['id0,,,t,,id0;name0;1', 'id1,,,t,,id1;name1;1', 'id2,,,t,,id2;name2;1', 'id3,,,t,,id3;name3;1,id4;name4;1']):
        assert(i.id in ['id0', 'id1', 'id2', 'id3'])
        assert(i.destination == '')
        assert(i.date == '')
        assert(i.is_paid == True)
        assert(i.is_shipped == False)
        assert(len(i.products) > 0)
    
    for i in update_orders(['id0,,,,t,id0;name0;1', 'id1,,,,t,id1;name1;1', 'id2,,,,t,id2;name2;1', 'id3,,,,t,id3;name3;1,id4;name4;1']):
        assert(i.id in ['id0', 'id1', 'id2', 'id3'])
        assert(i.destination == '')
        assert(i.date == '')
        assert(i.is_paid == False)
        assert(i.is_shipped == True)
        assert(len(i.products) > 0)
    
    for i in update_orders([',,,,,id0;name0;1', ',,,,,id1;name1;1', ',,,,,id2;name2;1', ',,,,,id3;name3;1,id4;name4;1']):
        assert(i.id == '')
        assert(i.destination == '')
        assert(i.date == '')
        assert(i.is_paid == False)
        assert(i.is_shipped == False)
        assert(len(i.products) == 0)


if __name__ == '__main__':
    main()