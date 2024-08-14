import paho.mqtt.client as mqtt
import time
import sys
from utils import list_to_string, string_to_list

BROKER_ADDRESS = 'localhost'

class Factory:

    def __init__(self, fabric_type, lines_number, batch_size, client):
        self.fabric_type  = fabric_type
        self.lines_number = lines_number
        self.batch_size   = batch_size
        self.client = self.broker_connection()

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
        
        print("factory is aware that product stock has amount = ", product_buffer_on_stock)

    def make_daily_batch(self, batch_size):

        products_per_line = batch_size // self.lines_number
        extra = batch_size - products_per_line * self.lines_number

        # supondo 1 tipo de produto
        for i in range(self.lines_number):
            if extra > 0:
                # fazer pedido de (products_per_line) p1 + 1
                self.order_to_line(i, products_per_line + 1)
                extra -= 1
            else:
                # fazer pedido de (products_per_line) p1
                self.order_to_line(i, products_per_line)

    def order_to_line(self, line_number, products_per_line):

        print('ordering %d products to line %d' %(products_per_line, line_number))
        message = "receive_order" + '/' + '%d/%d' %(line_number, products_per_line)
        self.client.publish('line', message)

def main(fabric_type, lines_number, batch_size):

    factory = Factory(fabric_type, lines_number, batch_size)
    days = 0
    while True:
        
        days += 1
        print('day:', days)
        factory.make_daily_batch()
        time.sleep(3) # 1 segundo = 1 dia

if __name__ == '__main__':

    fabric_type  = sys.argv[1]
    lines_number = sys.argv[2]
    batch_size   = sys.argv[3]
    main(fabric_type, lines_number, batch_size)