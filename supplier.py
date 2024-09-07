import paho.mqtt.client as mqtt
import sys
import time
from utils import string_to_list, list_to_string, print_update, BATCH_SIZE, TIME_SLEEP, DAYS_MAX, PARTS_TO_SEND_AMOUNT_SUPPLIER, broker_connection
import os

# PARTS_TO_SEND_AMOUNT_SUPPLIER = 12 * BATCH_SIZE

class Supplier:

    def __init__(self):
        _, self.client = broker_connection("supplier", self.on_message)
        self.waitingOrder = False
        self.entity_name = 'supplier'

    def on_message(self, ch, method, properties, message):

        msg = message.decode()

        command = msg.split("/")
        # print(command)

        if command[0] == 'send_parts':
            self.send_parts(string_to_list(command[1]))

    # parts_ordered: bool vector[100]
    def send_parts(self, parts_ordered):
        
        parts_to_send = [0] * 100
        for part_number, part_need in enumerate(parts_ordered):
            if part_need:
                parts_to_send[part_number] = PARTS_TO_SEND_AMOUNT_SUPPLIER
        
        result = "receive_parts" + "/" + list_to_string(parts_to_send) 
        print_update("enviando: " + list_to_string(parts_to_send), self.entity_name)
        # print("enviando \n\n\n", list_to_string(parts_to_send))
        
        self.client.basic_publish(exchange='', routing_key='warehouse', body=result)


def main():

    line = Supplier()

    days = 0

    while days <= DAYS_MAX:

        print_update('day ' + str(days), "supplier")
        days += 1

        time.sleep(TIME_SLEEP)

if __name__ == '__main__':
    time.sleep(3)

    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

    main()