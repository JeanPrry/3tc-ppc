import sys
import socket
import threading
from multiprocessing import Value
from multiprocessing import Queue
import random


def han_tcp_main(host, port, run):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))

        while run.value:
            m = client_socket.recv(1024).decode()
            if m == "Enter":
                print("It works !")
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
        self.policie = 1

        tcp_main = threading.Thread(target=han_tcp_main, args=(HOST, PORT_MAIN, run))
        tcp_market = threading.Thread(target=han_tcp_market, args=(HOST, PORT_MARKET, run))

        tcp_main.start()
        tcp_market.start()

        





HOST = "localhost"
PORT_MAIN = 2704
PORT_MARKET = 2708

run = Value("i", 1)
next = Value("i", 0)

home_list=[]


home1 = Home()


home_list.append(home1)



surplus = Queue()
carence = Queue()

while run.value:
    while (next.value) and run.value:
        pass
    if run.value: #dans le cas où run passe à false pendant la boucle du dessus
        while next.value==0 :
            next.value =1
        for home in home_list :
            if home.consumption_rate<home.production_rate :
                surplus.put(home)
            else :
                carence.put(home)
        print(surplus.qsize())
        print(carence.qsize())
        print(run.value)
        surplus = Queue()
        carence = Queue()
        home1.consumption_rate= random.randint(1, 100)
        home1.production_rate=random.randint(1, 100)

            
        


