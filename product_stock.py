import paho.mqtt.client as mqtt
import time
import random
from utils import list_to_string, string_to_list

PARTS_THRESHOLD = 20
NUM_PRODUCTS = 1

class ProductStock:

    def __init__(self):
        self.client = self.broker_connection()
        self.products_buffer = [0] * NUM_PRODUCTS

    def broker_connection(self):

        # Configura o cliente MQTT
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        # Conecta ao broker MQTT (substitua com o endereço do seu broker)
        broker_address="localhost"
        client.connect(broker_address)

        # Mantém o cliente rodando
        client.loop_start()

        return client

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("client connected.")
            client.subscribe("product_stock")

    def on_message(self, client, userdata, message):

        msg = str(message.payload.decode("utf-8"))

        command = msg.split("/")

        print(command)

        if command[0] == 'receive_products':
            self.receive_products(string_to_list(command[1]))
    
    def check_products(self):

        product_to_be_ordered = [0] * 5
        status = 'GREEN'
        for i, product_amount in enumerate(self.products_buffer):
            if product_amount < PARTS_THRESHOLD:
                status = 'RED'
                product_to_be_ordered[i] = 1
            elif product_amount < PARTS_THRESHOLD * 2:
                status = 'YELLOW'
        
        print('parts buffer on product stock:', self.products_buffer)
        print('parts buffer status on product stock: %s' %(status))

        # return false if lack of stock         
        return not product_to_be_ordered.count(1) > 0

    def receive_products(self, products):

        print("factory received products from production lines")
        for i in range(NUM_PRODUCTS):
            self.products_buffer[i] += products[i]

    def send_daily_order(self):

        products_available = self.check_products()

        if products_available:
            # simulate orders and decrement stock
            for i in range(NUM_PRODUCTS):
                product_ordered_amount = random.randint(0, 40)
                self.products_buffer[i] -= product_ordered_amount # potential break
                print('daily consume of product %s = %s' %(str(i + 1), str(product_ordered_amount)))

            self.update_factory()
        else:
            print("order could not be done: lack of stock")
    
    def update_factory(self):

        message = "update_factory" + list_to_string(self.products_buffer)
        self.client.publish("factory", message)

def main():

    product_stock = ProductStock()
    
    while True:

        product_stock.send_daily_order()
        time.sleep(1)

if __name__ == '__main__':

    main()

