import paho.mqtt.client as mqtt
import time
import sys
from utils import list_to_string, string_to_list, print_update, BATCH_SIZE, TIME_SLEEP, DAYS_MAX, RED_ALERT_PRODUCT_STOCK, PRODUCTS_N, broker_connection
import os

class Factory:

    def __init__(self, fabric_type, factory_id, lines_number, batch_size):
        self.fabric_type  = fabric_type
        self.factory_id = factory_id
        self.lines_number = lines_number
        self.batch_size   = batch_size
        self.entity_name = 'factory' + '-' + fabric_type
        self.last_stock_status = None
        self.products_most_needed = []
        _, self.client = broker_connection("factory-" + factory_id, self.on_message)

    def on_message(self, ch, method, properties, message):

        msg = message.decode()

        command = msg.split("/")

        if command[0] == 'update_factory':
            self.update_factory(string_to_list(command[1]))

    def check_status(self, product_buffer_on_stock):
        
        status = 'green'
        for amount in product_buffer_on_stock:
            if amount <= RED_ALERT_PRODUCT_STOCK:
                return 'red'
            elif amount <= RED_ALERT_PRODUCT_STOCK * 2:
                status = 'yellow'

        return status

    def update_factory(self, product_buffer_on_stock):

        products_most_needed = [0] * (self.lines_number - PRODUCTS_N)

        self.last_stock_status = self.check_status(product_buffer_on_stock)

        print_update("factory is aware that product stock has amount = " + str(product_buffer_on_stock) + " and status = " + self.last_stock_status, self.entity_name)

        for i in range(self.lines_number - PRODUCTS_N):
            lowest_quantity = None
            lowest_quantity_index = -1
            for j, quantitiy in enumerate(product_buffer_on_stock):
                if quantitiy != "checked" and (lowest_quantity == None or quantitiy < lowest_quantity):
                    lowest_quantity = quantitiy
                    lowest_quantity_index = j
            
            # print("trying to remove ", lowest_quantity_index)
            product_buffer_on_stock[lowest_quantity_index] = "checked"
            products_most_needed[i] = lowest_quantity_index

        self.products_most_needed = products_most_needed
    
    def order_daily_batch(self):

        if self.fabric_type == 'empurrada':
            # batch = [BATCH_SIZE] * self.lines_number
            batch_size = BATCH_SIZE
        # puxada
        elif self.last_stock_status == 'green': 
            # batch = [BATCH_SIZE//2] * self.lines_number
            batch_size = BATCH_SIZE // 2
        elif self.last_stock_status == 'yellow':
            # batch = [BATCH_SIZE] * self.lines_number
            batch_size = BATCH_SIZE
        else:
            # batch = [BATCH_SIZE * 2] * self.lines_number
            batch_size = BATCH_SIZE * 2
        # debug_list = [0] * self.lines_number

        for i in range(PRODUCTS_N):
            self.order_to_line(i, self.factory_id, i, batch_size)
            # debug_list.append(i)

        if self.products_most_needed:
            for i in range(self.lines_number - PRODUCTS_N):
                self.order_to_line(i + PRODUCTS_N, self.factory_id, self.products_most_needed[i], batch_size)
                # debug_list.append(self.products_most_needed[i])
        
        # print_update("ordering products: " + str(debug_list), self.entity_name)

    def order_to_line(self, line_number, factory_id, product_index, products_per_line):

        print_update('ordering %d products %d to line %d' %(products_per_line, product_index, line_number), self.entity_name)
        # print('ordering %d products to line %d' %(products_per_line, line_number))
        message = "receive_order" + '/' + '%d/%d/%d/%d' %(line_number, int(factory_id) , product_index, products_per_line)
        self.client.basic_publish(exchange='', routing_key='line-' + str(line_number) + "-" + str(factory_id), body=message)

def main(fabric_type, factory_id, lines_number, batch_size):

    factory = Factory(fabric_type, factory_id, lines_number, batch_size)
    days = 0
    while days <= DAYS_MAX:
        
        days += 1
        print_update('day '+str(days), 'factory' + '-' + fabric_type)
        
        factory.order_daily_batch()
        time.sleep(TIME_SLEEP) # 1 segundo = 1 dia

if __name__ == '__main__':

    time.sleep(3)

    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

    fabric_type  = sys.argv[1]
    if fabric_type != "puxada" and fabric_type != "empurrada":
        print("fabric type invalid")
    factory_id = sys.argv[2]
    
    lines_number = int(sys.argv[3])
    batch_size   = int(sys.argv[4])
    main(fabric_type, factory_id, lines_number, batch_size)