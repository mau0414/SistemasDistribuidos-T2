import paho.mqtt.client as mqtt
import sys
import time
from utils import string_to_list, list_to_string

PARTS_THRESHOLD = 10
PARTS_TO_SEND_AMOUNT = 80

class Supplier:

    def __init__(self):
        self.client = self.broker_connection()
        self.waitingOrder = False

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
            client.subscribe("supplier")

    def on_message(self, client, userdata, message):

        msg = str(message.payload.decode("utf-8"))

        command = msg.split("/")
        print(command)

        if command[0] == 'send_parts':
            self.send_parts(string_to_list(command[1]))

    def send_parts(self, parts_ordered):
        
        parts_to_send = [0] * 100
        for part_number, part_need in enumerate(parts_ordered):
            if part_need:
                parts_to_send[part_number] = PARTS_TO_SEND_AMOUNT
        
        result = "receive_parts" + "/" + list_to_string(parts_to_send) 
        print("enviando \n\n\n", list_to_string(parts_to_send))
        self.client.publish("warehouse", result)


def main():

    line = Supplier()

    while True:

        time.sleep(3)

if __name__ == '__main__':
    main()