import paho.mqtt.client as mqtt
import time

# Callback para quando o cliente se conecta ao broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("cliente conectado.")
        client.subscribe("teste")

def on_message(client, userdata, message):

    msg = str(message.payload.decode("utf-8"))

    comando = msg.split("/")

    print(comando)

# Configura o cliente MQTT
client = mqtt.Client()
print("quebrou")
client.on_connect = on_connect
client.on_publish = on_message

broker_hostname ="localhost"
port = 1883

# id_fornecedor = args.id_fornecedor
# client = mqtt.Client("fornecedor" + id_fornecedor)
client.on_connect = on_connect
client.on_message = on_message

print("aqui ainda vai \n\n\n")
client.connect(broker_hostname, port) 
client.loop_start()

while True:
    time.sleep(1)

print("saiu")
