import paho.mqtt.client as mqtt
import sys
import time
from utils import list_to_string, string_to_list, print_update, BATCH_SIZE, TIME_SLEEP, DAYS_MAX, YELLOW_ALERT_WAREHOUSE, RED_ALERT_WAREHOUSE, PARTS_TO_SEND_AMOUNT_WAREHOUSE, broker_connection
import os

# BATCH_SIZE = 48
# PARTS_THRESHOLD = BATCH_SIZE * 3
# PARTS_TO_SEND_AMOUNT_WAREHOUSE = 4 * BATCH_SIZE
# BROKER_ADDRESS = 'localhost'

class Warehouse:

    def __init__(self):
        self.parts_buffer = [0] * 100
        _, self.client = broker_connection("warehouse", self.on_message)
        self.waitingOrder = False
        self.entity_name = 'warehouse'

    def on_message(self, ch, method, properties, message):

        msg = message.decode()

        command = msg.split("/")
        print(command)

        if command[0] == 'send_parts':
            self.send_parts(command[1], command[2], string_to_list(command[3]))
        elif command[0] == 'receive_parts':
            self.receive_parts(string_to_list(command[1]))
            
    def receive_parts(self, parts_received):
    
        for i, _ in enumerate(self.parts_buffer):
            self.parts_buffer[i] += parts_received[i]

        self.waitingOrder = False

    def send_parts(self, line_id, factory_id, parts_ordered):
        
        parts_to_send = [0] * 100
        parts_index_sent = [False] * 100
        for part_number, part_need in enumerate(parts_ordered):
            if part_need:
                if self.parts_buffer[part_number] - PARTS_TO_SEND_AMOUNT_WAREHOUSE < 0: # erro aqui 
                    self.warehouse_broke()  
                    return
                parts_to_send[part_number] = PARTS_TO_SEND_AMOUNT_WAREHOUSE
                parts_index_sent[part_number] = True
        
        result = "receive_parts" + "/" + line_id + "/" + factory_id + "/" + list_to_string(parts_to_send) 
        # print("enviando \n\n\n", list_to_string(parts_to_send))
        self.client.basic_publish(exchange='', routing_key='line-' + str(line_id) + "-" + str(factory_id), body=result)

        self.decrement_parts(parts_index_sent)

    def warehouse_broke(self):

        msg = ("warehouse is broke: lack of stock").upper()
        print_update(msg, self.entity_name)
        # print("warehouse is broke: lack of stock")

    def decrement_parts(self, parts_index_sent):

        for part_number, part_sent in enumerate(parts_index_sent):
            if part_sent:
                self.parts_buffer[part_number] -= PARTS_TO_SEND_AMOUNT_WAREHOUSE

    def check_parts(self):

        parts_to_be_ordered = [0] * 100
        status = 'GREEN'
        for i, part_amount in enumerate(self.parts_buffer):
            if part_amount < RED_ALERT_WAREHOUSE:
                status = 'RED'
                parts_to_be_ordered[i] = 1
            elif part_amount < YELLOW_ALERT_WAREHOUSE:
                status = 'YELLOW'
        
        # print('parts buffer on warehouse:', self.parts_buffer)
        # print('parts buffer status on warehouse: %s and buffer = %s' %(status, str(self.parts_buffer)))
        msg = 'parts buffer status on warehouse: %s and buffer = %s' %(status, str(self.parts_buffer))
        print_update(msg, self.entity_name)

        if parts_to_be_ordered.count(1) > 0 and self.waitingOrder == False:
            self.order_parts(parts_to_be_ordered)
    
    def order_parts(self, parts_to_be_ordered):

        # print("ordering parts in warehouse")
        order = ""
        for part_number, part_need in enumerate(parts_to_be_ordered):
            if part_need:
                order += str(1) + ";"  
            else:
                order += str(0) + ";"  
     
        # remove ; at the end
        order = "send_parts" + "/" + order[:-1]

        # send order
        self.client.basic_publish(exchange='', routing_key='supplier', body=order)
        self.waitingOrder = True

    def receive_part(self):
        pass

    def make_products():
        pass

def main():

    warehouse = Warehouse()
    days = 0

    while days <= DAYS_MAX:

        days += 1
        print_update('day '+str(days), "warehouse")
        warehouse.check_parts()
        time.sleep(TIME_SLEEP)

if __name__ == '__main__':

    time.sleep(3)

    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

    main()