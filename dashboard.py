import matplotlib.pyplot as plt
import numpy as np
import time
from src.utils import broker_connection, string_to_list
import sys

# Criando a figura e os eixos
fig, ax = plt.subplots()

days = 0

# products names
products = ['Produto 1', 'Produto 2', 'Produto 3', 'Produto 4', 'Produto 5']
parts = [''] * 100
for i in range(100):
    parts[i] = 'peca '+ str(i + 1)

def update_bars(entity, stock, consume=None):

    ax.clear()

    plt.title(entity)

    if entity.startswith('product'):
     
        width = 0.35
        indices = np.arange(len(products))
        
        # plot bars
        ax.bar(indices - width/2, stock, width, label='Estoque', color='blue')

        
        ax.bar(indices + width/2, consume, width, label='Consumo', color='red')
    else:
        pass

    
    # labels
    ax.set_xticks(indices)
    ax.set_xticklabels(products)
    
    # limit on y
    ax.set_ylim(0, 200)
    ax.legend()
    
    # draw and update
    plt.draw()
    plt.pause(0.01) 
    print("desenhou")


def on_message(ch, method, properties, message):

        # days += 1
        msg = message.decode()

        command = msg.split("/")
        print(command)

        # if command[0].startswith('line') or command[0].startswith('warehouse'):
        #     update_bars(command[0], string_to_list(command[1]))
        # elif command[0].startswith('product'):
        #     print('entrou aqui')
        #     update_bars(command[0], string_to_list(command[1]), string_to_list(command[2]))
        



def main(topic):

    print('teste')
    _, client = broker_connection(topic, on_message)


if __name__ == '__main__':

    time.sleep(3)
    topic = sys.argv[1]
    main(topic)