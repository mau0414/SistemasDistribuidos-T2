import pika
import threading
import time

'''

how much send?
when red is achived, send the amount to work considering batch size = 48 for more 30 days for the lines and to make more
3 deliveries available for the warehouse
-> for the warehouse to send for each line: 48 x 30
-> for the supplier to send for the warehouse: 13 lines * 48 parts * 30 days * 5 deliveries = 93600 (/48 = 1950)

what are the red limits?
48 x 13 lines x 3 days (limit of red) = 1872 products per day in two fabrics with 13 lines
-> for warehouse limit of 1 delivery: 13 x 48 x 30 = 18720 (/48 = 390)
-> for each individual line, red limit of 3 days production = 48 * 3 = 144


yellow is the double of red in each case


'''

TIME_SLEEP = 3
BROKER_ADDRESS = 'rabbitmq'
BATCH_SIZE = 48
YELLOW_ALERT_LINE = BATCH_SIZE * 6
YELLOW_ALERT_WAREHOUSE = BATCH_SIZE * 780
RED_ALERT_LINE = BATCH_SIZE * 3
RED_ALERT_WAREHOUSE = BATCH_SIZE * 390 
RED_ALERT_PRODUCT_STOCK = 500
PRODUCTS_N = 5
FACTORY_N = 2
PARTS_TO_SEND_AMOUNT_SUPPLIER = BATCH_SIZE * 1950
PARTS_TO_SEND_AMOUNT_WAREHOUSE = BATCH_SIZE * 30
DAYS_MAX = 100
MIN_ORDERED_AMOUNT = 50
MAX_ORDERED_AMOUNT = 250

def list_to_string(list):
    result = ""
    for item in list:
        result += str(item) + ";"

    return result[:-1]

def string_to_list(string):
    
    string_list = string.split(";") 
    result = [0] * len(string_list)
    
    for i, item in enumerate(string_list):
        result[i] = int(item)
    
    return result

def print_update(msg, entity_name):

    final_msg = '\n'
    final_msg += '===============================================================================\n'
    final_msg += msg + '\n'
    final_msg += '===============================================================================\n' 

    print(msg)

    with open('src/output/' + entity_name + '.txt', 'a') as file:
        file.write(final_msg)

def create_conn():

    parameters = pika.ConnectionParameters(
        "rabbitmq",
        5672,
    )
    while True:
        try:
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            return channel
        except pika.exceptions.AMQPConnectionError:
            print("RabbitMQ not available yet, retrying in 5 seconds...")
            time.sleep(5)

    return channel

# rabbitmq is not thread safe so create one connection per thread
def broker_connection(topic, callback):

    sub_channel = create_conn()
    pub_channel = create_conn()

    sub_channel.queue_declare(queue=topic)
    sub_channel.basic_consume(queue=topic, on_message_callback=callback, auto_ack=True)

    print(topic + " connected.")
    threading.Thread(target=sub_channel.start_consuming).start()

    return sub_channel, pub_channel
