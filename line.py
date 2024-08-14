import paho.mqtt.client as mqtt
import sys
import time
from utils import string_to_list, list_to_string

PARTS_THRESHOLD = 10
NUM_PRODUCTS = 5

class Line:

    def __init__(self, line_id):

        self.parts_buffer = [1] * 100
        self.line_id = line_id
        self.client = self.broker_connection()
        self.products_necessary_parts = self.read_products_necessary_parts()

    def broker_connection(self):

        # configurate MQTT client
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        # conect to broker
        broker_address="localhost"
        client.connect(broker_address)

        # keep client running
        client.loop_start()

        return client
    
    def on_connect(self, client, userdata, flags, rc):

        if rc == 0:
            print("client connected.")
            client.subscribe("line")

    def on_message(self, client, userdata, message):

        msg = str(message.payload.decode("utf-8"))

        command = msg.split("/")
        print(command)

        if command[0] == 'receive_order':
            self.receive_order(string_to_list(command[2]))
        elif command[0] == 'receive_parts':
            self.receive_parts(string_to_list(command[2])) # "receive_parts" + "/" + line_id + "/" + list_to_string(parts_to_send) 

    def read_products_necessary_parts(self):
        
        necessary_parts = []
        with open("products_and_parts.txt", 'r') as file:
            
            for i in range(NUM_PRODUCTS):
                products_parts = string_to_list(file.readline())
                necessary_parts.append(products_parts)
                print(products_parts)

        return necessary_parts

    def receive_parts(self, parts_received):

        for i, _ in enumerate(self.parts_buffer):
            self.parts_buffer[i] += parts_received[i]

    def check_parts(self):

        parts_to_be_ordered = [0] * 100
        status = 'GREEN'
        for i, part_amount in enumerate(self.parts_buffer):
            if part_amount < PARTS_THRESHOLD:
                status = 'RED'
                parts_to_be_ordered[i] = 1
            elif part_amount < PARTS_THRESHOLD * 2:
                status = 'YELLOW'
        
        print('parts buffer on line', self.line_id, ':', self.parts_buffer)
        print('parts buffer status on line %s:%s' %(str(self.line_id), status))

        if parts_to_be_ordered.count(1) > 0:
            self.order_parts(parts_to_be_ordered)
            
    def order_parts(self, parts_to_be_ordered):

        print("ordering parts in line %s" %(str(self.line_id)))
        order = ""
        for part_number, part_need in enumerate(parts_to_be_ordered):
            if part_need:
                order += str(1) + ";"    
     
        # remove ; at the end
        order = "send_parts" + "/" + self.line_id + "/" + order[:-1]

        # send order
        self.client.publish("warehouse", order)

    def receive_order(self, order):
        
        products = []
        for i in range(NUM_PRODUCTS):
            for part in self.products_necessary_parts[i]:
                self.parts_buffer[part - 1] -= order[i] # potential break
                if (self.parts_buffer - 1) <= 0:
                    self.line_broke()
    
            products.append(order[i])

        message = 'receive_products' + list_to_string(products)
        self.client.publish("product_stock", message)

    def line_broke(self):

        print("line ", self.line_id, " broke: lack of part stock")

def main(line_id):

    line = Line(line_id)
    days = 0

    while True:

        days += 1
        print("day", days)
        line.check_parts()
        time.sleep(3)

if __name__ == '__main__':
    
    line_id = sys.argv[1]
    main(line_id)