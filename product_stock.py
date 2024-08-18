import paho.mqtt.client as mqtt
import time
import random
from utils import list_to_string, string_to_list, print_update

THRESHOLD = 20
NUM_PRODUCTS = 5

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

        # print(command)

        if command[0] == 'receive_products':
            self.receive_products(command[1], command[2], command[3])
    
    def check_products(self):

        status = 'GREEN'
        for i, product_amount in enumerate(self.products_buffer):
            if product_amount < THRESHOLD:
                status = 'RED'
            elif product_amount < THRESHOLD * 2:
                status = 'YELLOW'
        
        # print('products buffer on product stock:', self.products_buffer)
        # print('products buffer status on product stock: %s and buffer = %s' %(status, str(self.products_buffer)))
        msg = 'products buffer status on product stock: %s and buffer = %s' %(status, str(self.products_buffer))
        print_update(msg)
    
    def check_product(self, product_number, quantity):
        product_available = True
        if self.products_buffer[product_number] < quantity:
            product_available = False

        return product_available

    def receive_products(self, product_index, line_id, products):

        # print("factory received %s products of version %s from production line %s" %(products, product_index, line_id))
        print_update("factory received %s products of version %s from production line %s" %(products, product_index, line_id))
        self.products_buffer[int(product_index)] += int(products)

    def send_daily_order(self):

        products_sent = [0] * NUM_PRODUCTS
        for i in range(NUM_PRODUCTS):
                
            product_ordered_amount = random.randint(0, 40)
            product_available = self.check_product(i, product_ordered_amount)
            if not product_available:
                # print("order of product %d could not be done: lack of stock"  %(i + 1))
                print_update(("order of product %d could not be done: lack of stock"  %(i + 1)).upper())
                continue
            else:
                self.products_buffer[i] -= product_ordered_amount 
                # print('daily consume of product %s = %s' %(str(i + 1), str(product_ordered_amount)))
                print_update('daily consume of product %s = %s' %(str(i + 1), str(product_ordered_amount)))
                products_sent[i] = product_ordered_amount
            
        self.update_factory()
        self.check_products()

    def update_factory(self):

        message = "update_factory" + '/' +  list_to_string(self.products_buffer)
        self.client.publish("factory", message)

def main():

    product_stock = ProductStock()
    
    while True:

        product_stock.send_daily_order()
        time.sleep(10)

if __name__ == '__main__':

    main()

