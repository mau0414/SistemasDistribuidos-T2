import paho.mqtt.client as mqtt

# Callback para quando o cliente se conecta ao broker
def on_connect(client, userdata, flags, rc):
    print("Conectado com resultado de retorno code=%s." % str(rc))

# Callback para quando uma mensagem é publicada
def on_publish(client, userdata, mid):
    print("Mensagem publicada com mid: " + str(mid))

# Configura o cliente MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_publish = on_publish

# Conecta ao broker MQTT (substitua com o endereço do seu broker)
broker_address="localhost"
client.connect(broker_address)

# Publica uma mensagem no tópico "meu_topico"
client.publish("teste", "Hello, world!/TETE")

# Mantém o cliente rodando
client.loop_forever()