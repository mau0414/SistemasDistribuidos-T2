import paho.mqtt.client as mqtt
import time
import sys
from utils import list_to_string, string_to_list, print_update, BROKER_ADDRESS, TIME_SLEEP, DAYS_MAX


class Factory:

    def __init__(self, fabric_type, lines_number, batch_size):
        self.fabric_type  = fabric_type
        self.lines_number = lines_number
        self.batch_size   = batch_size
        self.client = self.broker_connection()
        self.entity_name = 'factory' + '-' + fabric_type

    def broker_connection(self):
        # Configura o cliente MQTT
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        # Conecta ao broker MQTT (substitua com o endereço do seu broker)
        client.connect(BROKER_ADDRESS)


        # Mantém o cliente rodando
        client.loop_start()

        return client
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("client connected.")
            client.subscribe("factory")

    def on_message(self, client, userdata, message):

        msg = str(message.payload.decode("utf-8"))

        command = msg.split("/")

        if command[0] == 'update_factory':
            self.update_factory(string_to_list(command[1]))

    def update_factory(self, product_buffer_on_stock):
        
        print_update("factory is aware that product stock has amount = " + str(product_buffer_on_stock), self.entity_name)
        # print("factory is aware that product stock has amount = ", product_buffer_on_stock)

    def order_daily_batch(self, batch):

        for i in range(self.lines_number):
            self.order_to_line(i, i, batch[i])

    def order_to_line(self, line_number, product_index, products_per_line):

        print_update('ordering %d products to line %d' %(products_per_line, line_number), self.entity_name)
        # print('ordering %d products to line %d' %(products_per_line, line_number))
        message = "receive_order" + '/' + '%d/%d/%d' %(line_number, product_index, products_per_line)
        self.client.publish('line', message)

def main(fabric_type, lines_number, batch_size):

    factory = Factory(fabric_type, lines_number, batch_size)
    days = 0
    while days <= DAYS_MAX:
        
        days += 1
        print_update('day '+str(days), 'factory' + '-' + fabric_type)
        product_batch = [48, 48, 48, 48, 48]
        # product_batch = [20, 20, 20, 20, 20]
        factory.order_daily_batch(product_batch)
        time.sleep(TIME_SLEEP) # 1 segundo = 1 dia

if __name__ == '__main__':

    fabric_type  = sys.argv[1]
    lines_number = int(sys.argv[2])
    batch_size   = int(sys.argv[3])
    main(fabric_type, lines_number, batch_size)