import matplotlib.pyplot as plt
import numpy as np
import time

# Criando a figura e os eixos
fig, ax = plt.subplots()

# products names
products = ['Produto 1', 'Produto 2', 'Produto 3', 'Produto 4', 'Produto 5']

def update_bars(day):
    
    estoque = np.random.randint(50, 150, size=5)  
    consumo = np.random.randint(20, 100, size=5)  
    
    ax.clear()

    plt.title("dia " + str(day))    
    
    width = 0.35
    indices = np.arange(len(products))
    
    # plot bars
    ax.bar(indices - width/2, estoque, width, label='Estoque', color='blue')
    ax.bar(indices + width/2, consumo, width, label='Consumo', color='red')
    
    # labels
    ax.set_xticks(indices)
    ax.set_xticklabels(products)
    
    # limit on y
    ax.set_ylim(0, 200)
    ax.legend()
    
    # draw and update
    plt.draw()
    plt.pause(0.01) 


days = 0
while True:

    days += 1
    update_bars(days)
    time.sleep(1)  


