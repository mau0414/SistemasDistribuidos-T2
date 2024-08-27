import paho.mqtt.client as mqtt
import sys
import time
from utils import string_to_list, list_to_string, print_update, TIME_SLEEP, DAYS_MAX, BATCH_SIZE, YELLOW_ALERT_LINE, RED_ALERT_LINE

# BATCH_SIZE = 48
# PARTS_THRESHOLD = BATCH_SIZE * 3
NUM_PRODUCTS = 5

class Line:

    def __init__(self, line_id):

        self.parts_buffer = [0] * 100
        self.line_id = line_id
        self.client = self.broker_connection()
        self.products_necessary_parts = self.read_products_necessary_parts()
        self.entity_name = 'line' + line_id
        self.waitingOrder = False

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
        # print(command)

        if command[0] == 'receive_order':
            self.receive_order(command[1], command[2], command[3]) # "receive_order" + '/' + '%d/%d/%d' %(line_number, product_index, products_per_line)
        elif command[0] == 'receive_parts':
            self.receive_parts(command[1], string_to_list(command[2])) # "receive_parts" + "/" + line_id + "/" + list_to_string(parts_to_send) 

    def read_products_necessary_parts(self):
        
        necessary_parts = []
        with open("products_and_parts.txt", 'r') as file:
            
            for i in range(NUM_PRODUCTS):
                products_parts = string_to_list(file.readline())
                necessary_parts.append(products_parts)

        return necessary_parts

    def receive_parts(self, line_id, parts_received):

        if self.line_id != line_id:
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
            print('ENTROU AQUI UMA VEZZZ')
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
        order = "send_parts" + "/" + self.line_id + "/" + order[:-1]

        # send order
        self.client.publish("warehouse", order)
        self.waitingOrder = True

    def receive_order(self, line_index, product_index, order):
        
        if line_index != self.line_id:
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

        message = 'receive_products' + '/' + product_index + '/' + self.line_id + "/" + order
        self.client.publish("product_stock", message)
        
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

def main(line_id):

    line = Line(line_id)
    days = 0

    while days <= DAYS_MAX:

        days += 1
        print_update("day " + str(days), 'line' + str(line_id))
        line.check_parts()
        time.sleep(TIME_SLEEP)

if __name__ == '__main__':
    
    line_id = sys.argv[1]
    main(line_id)