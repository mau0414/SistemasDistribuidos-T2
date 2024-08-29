import paho.mqtt.client as mqtt
import time
import sys
from utils import list_to_string, string_to_list, print_update, BROKER_ADDRESS, BATCH_SIZE, TIME_SLEEP, DAYS_MAX, RED_ALERT_PRODUCT_STOCK, PRODUCTS_N


class Factory:

    def __init__(self, fabric_type, factory_id, lines_number, batch_size):
        self.fabric_type  = fabric_type
        self.factory_id = factory_id
        self.lines_number = lines_number
        self.batch_size   = batch_size
        self.client = self.broker_connection()
        self.entity_name = 'factory' + '-' + fabric_type
        self.last_stock_status = None
        self.products_most_needed = []

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

        products_most_needed = [0] * (self.lines_number - PRODUCTS_N)

        if sum(product_buffer_on_stock) <= RED_ALERT_PRODUCT_STOCK:
            self.last_stock_status = "red"
        elif sum(product_buffer_on_stock) <= RED_ALERT_PRODUCT_STOCK * 2:
            self.last_stock_status = "yellow"
        else:
            self.last_stock_status = "green"

        for i in range(self.lines_number - PRODUCTS_N):
            lowest_quantity = None
            lowest_quantity_index = -1
            for quantitiy, j in enumerate(product_buffer_on_stock):
                if lowest_quantity == None or quantitiy < lowest_quantity:
                    lowest_quantity = quantitiy
                    lowest_quantity_index = j
            
            products_most_needed.append(lowest_quantity_index)

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
        self.client.publish('line', message)

def main(fabric_type, factory_id, lines_number, batch_size):

    factory = Factory(fabric_type, factory_id, lines_number, batch_size)
    days = 0
    while days <= DAYS_MAX:
        
        days += 1
        print_update('day '+str(days), 'factory' + '-' + fabric_type)
        
        factory.order_daily_batch()
        time.sleep(TIME_SLEEP) # 1 segundo = 1 dia

if __name__ == '__main__':

    fabric_type  = sys.argv[1]
    if fabric_type != "puxada" and fabric_type != "empurrada":
        print("fabric type invalid")
    factory_id = sys.argv[2]
    
    lines_number = int(sys.argv[3])
    batch_size   = int(sys.argv[4])
    main(fabric_type, factory_id, lines_number, batch_size)