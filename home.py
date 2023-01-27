import sys
import socket
import threading
from multiprocessing import Value, Queue, Process, Array
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def han_tcp_main(host, port, run):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))

        while run.value:
            m = client_socket.recv(1024).decode()
            if m == "Enter":
                #print("It works !")
                next.value = 0

            if m == "end":
                run.value = 0
            m = "wait for new command"


def han_tcp_market(host, port, run):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        msg = client_socket.recv(1024).decode()
        while run.value:
            print(msg)
            msg = client_socket.recv(1024).decode()


class Home:

    def __init__(self):

        self.consumption_rate = random.randint(1, 100)
        self.production_rate = random.randint(1, 100)
        self.policy = 1

        tcp_main = threading.Thread(target=han_tcp_main, args=(HOST, PORT_MAIN, run))
        tcp_market = threading.Thread(target=han_tcp_market, args=(HOST, PORT_MARKET, run))

        tcp_main.start()
        tcp_market.start()


HOST = "localhost"
PORT_MAIN = 1115
PORT_MARKET = 4445

run = Value("i", 1)
next = Value("i", 0)

home_list = []
largeur = 0.3

home1 = Home()
home_list.append(home1)
home2 = Home()
home_list.append(home2)
home3 = Home()
home_list.append(home3)

y1 = Array("d", range(len(home_list)))
y2 = Array("d", range(len(home_list)))
x1 = Array("d", range(len(home_list)))
x2 = Array("d", [i + largeur for i in x1])

for i in range(len(home_list)):
    y1[i] = home_list[i].consumption_rate
    y2[i] = home_list[i].production_rate


def animate():
    fig, ax = plt.subplots()
    # Create the animation object
    ani = animation.FuncAnimation(fig, update, frames=3, fargs=(ax,))
    plt.show()


def update(num, ax):

    ax.clear()
    ax.bar(x1, y1, width=largeur, color='blue', label='consumption')
    ax.bar(x2, y2, width=largeur, color='red', label='production')
    ax.set_xticks([r + largeur/2 for r in range(len(y1))], ['Home1', 'Home2', 'Home3'])
    ax.legend()


p = Process(target=animate, args=())

p.start()
surplus = Queue()
carence = Queue()

while run.value:
    while next.value and run.value:
        pass
    if run.value: #dans le cas où run passe à false pendant la boucle du dessus
        next.value = 1
        for home in home_list:
            if home.consumption_rate < home.production_rate:
                surplus.put(home)
            else:
                carence.put(home)
        print(next.value)
        #print(surplus.qsize())
        #print(carence.qsize())
        surplus = Queue()
        carence = Queue()
        i = 0
        for h in home_list:
            h.consumption_rate = random.randint(1, 100)
            h.production_rate = random.randint(1, 100)
            y1[i] = home_list[i].consumption_rate
            y2[i] = home_list[i].production_rate
            i += 1

p.join()
