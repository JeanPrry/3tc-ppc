import sys
import socket
import threading
from multiprocessing import Value


class Home:

    def __init__(self):
        
        consumption_rate = 100
        production_rate = 100
        policie = 1

        tcp_main = threading.Thread(target=han_tcp_main, args=(HOST, PORT_MAIN, run))
        tcp_market = threading.Thread(target=han_tcp_market, args=(HOST, PORT_MARKET, run))

        tcp_main.start()
        tcp_market.start()

        tcp_main.join()
        tcp_market.join()


    def han_tcp_main(host, port, run):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((host, port))

            while run.value:
                m = client_socket.recv(1024).decode()
                if m == "Enter":
                    print("It works !")
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


HOST = "localhost"
PORT_MAIN = 8889
PORT_MARKET = 5559

run = Value("i", 1)

home1 = Home()