import sys
import time
from utils import string_to_list, list_to_string, print_update, TIME_SLEEP, DAYS_MAX, BATCH_SIZE, YELLOW_ALERT_LINE, RED_ALERT_LINE, broker_connection
import os

NUM_PRODUCTS = 5

class Line:

    def __init__(self, line_id, factory_id):

        self.parts_buffer = [0] * 100
        self.line_id = line_id
        self.factory_id = factory_id
        _, self.client = broker_connection("line-" + line_id + "-" + factory_id, self.on_message)
        self.products_necessary_parts = self.read_products_necessary_parts()
        self.entity_name = 'line' + line_id + "-" + factory_id
        self.waitingOrder = False

    def on_message(self, ch, method, properties, message):

        msg = message.decode()
        print(msg)
        command = msg.split("/")
        # print(command)

        if command[0] == 'receive_order':
            self.receive_order(command[1], command[2], command[3], command[4]) # "receive_order" + '/' + '%d/%d/%d/%d' %(line_number, factory_id, product_index, products_per_line)
        elif command[0] == 'receive_parts':
            self.receive_parts(command[1], command[2], string_to_list(command[3])) # "receive_parts" + "/" + line_id + "/" + factory_id + "/" + list_to_string(parts_to_send) 

    def read_products_necessary_parts(self):
        
        necessary_parts = []
        with open("src/products_and_parts.txt", 'r') as file:
            
            for i in range(NUM_PRODUCTS):
                products_parts = string_to_list(file.readline())
                necessary_parts.append(products_parts)

        return necessary_parts

    def receive_parts(self, line_id, factory_id, parts_received):
        
        print('line_id', line_id, 'factory_id' ,factory_id)
        if self.line_id != line_id or self.factory_id != factory_id:
            return

        for i, _ in enumerate(self.parts_buffer):
            self.parts_buffer[i] += parts_received[i]

        self.waitingOrder = False
        print_update("received parts! updated parts buffer " + str(self.parts_buffer), self.entity_name)

    def check_parts(self):

        parts_to_be_ordered = [0] * 100
        status = 'GREEN'
        for i, part_amount in enumerate(self.parts_buffer):
            if part_amount < RED_ALERT_LINE:
                status = 'RED'
                parts_to_be_ordered[i] = 1
            elif part_amount < YELLOW_ALERT_LINE:
                status = 'YELLOW'
        

        # print('parts buffer on line', self.line_id, ':', self.parts_buffer)
        msg = 'parts buffer status on line %s:%s and buffer = %s' %(str(self.line_id), status, str(self.parts_buffer))
        print_update(msg, self.entity_name)

        if parts_to_be_ordered.count(1) > 0 and self.waitingOrder == False:
            self.order_parts(parts_to_be_ordered)
            
    def order_parts(self, parts_to_be_ordered):

        # print("ordering parts in line %s" %(str(self.line_id)))
        order = ""
        for part_number, part_need in enumerate(parts_to_be_ordered):
            if part_need:
                order += str(1) + ";"  
            else:
                order += str(0) + ';'  
     
        # remove ; at the end
        order = "send_parts" + "/" + self.line_id + "/" + self.factory_id + "/" + order[:-1]

        # send order
        # print("chegou aqui")
        self.client.basic_publish(exchange='', routing_key='warehouse', body=order)
        # print("aqui nao")
        self.waitingOrder = True

    def receive_order(self, line_index, factory_id, product_index, order):
        
        if line_index != self.line_id or factory_id != self.factory_id:
            return

        parts_decremented = [False] * 100

        # basic kit
        for i in range(43):
            if (self.parts_buffer[i] - int(order)) <= 0:
                self.line_broke()
                return
            parts_decremented[i] = True

        # variable kit
        for part in self.products_necessary_parts[int(product_index)]:
            if (self.parts_buffer[part-1] - int(order)) < 0:
                self.line_broke()
                return
            parts_decremented[part-1] = True

        # product_index, line_id, factory_id, products
        message = 'receive_products' + '/' + product_index + '/' + self.line_id + "/" + self.factory_id + "/" + order
        self.client.basic_publish(exchange='', routing_key='product_stock', body=message)
        
        self.decrement_parts(parts_decremented, order)
        msg = "order of product " + str(int(product_index) + 1) + " sent"
        # print("order sent\n\n")
        print_update(msg, self.entity_name)
        print_update("updated parts buffer " + str(self.parts_buffer), self.entity_name)


    def line_broke(self):

        # print("line ", self.line_id, " broke: lack of part stock")
        msg = ("line " + str(self.line_id) + " broke: lack of part stock").upper()
        print_update(msg, self.entity_name)

    def decrement_parts(self, parts_decremented, order):

        for part_number, part_decremented in enumerate(parts_decremented):
            if part_decremented:
                self.parts_buffer[part_number] -= int(order)

def main(line_id, factory_id):

    line = Line(line_id, factory_id)
    days = 0

    while days <= DAYS_MAX:

        days += 1
        print_update("day " + str(days), 'line' + line_id + "-" + factory_id)
        line.check_parts()
        time.sleep(TIME_SLEEP)

if __name__ == '__main__':

    time.sleep(3)

    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    
    line_id = sys.argv[1]
    factory_id = sys.argv[2]
    main(line_id, factory_id)