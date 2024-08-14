import paho.mqtt.client as mqtt
import sys
import time
from utils import string_to_list, list_to_string

PARTS_THRESHOLD = 10
BROKER_ADDRESS = 'localhost'

class Entity:

    def __init__(self, entity):
        self.entity = entity
        self.client = self.broker_connection()
        self.parts_buffer = [0] * 100

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
            client.subscribe(self.entity)

    def on_message(self, client, userdata, message):

        msg = str(message.payload.decode("utf-8"))

        command = msg.split("/")
        print(command)

        return command

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

        return parts_to_be_ordered
            
    def order_parts(self, parts_to_be_ordered):

        print("ordering parts in %s %s" %(self.entity, str(self.line_id)))
        order = ""
        for part_number, part_need in enumerate(parts_to_be_ordered):
            if part_need:
                order += str(1) + ";"   

        return order 