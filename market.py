import multiprocessing
import threading
from multiprocessing import Value, Array, Process, Pool
import signal
import socket
import select
from external import external_process

serve = True


def market_process(weather):

    MAX_CONNECTION = 1

    energy_price = Value("d", 0.0)

    global serve
    HOST = "localhost"
    PORT = 3333

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

        server_socket.setblocking(False)
        server_socket.bind((HOST, PORT))
        server_socket.listen(2)

        while serve:
            readable, writable, error = select.select([server_socket], [], [], 1)
            if server_socket in readable:
                client_socket, address = server_socket.accept()
                with Pool(processes=4) as pool:
                    pool.apply(handler_client, (client_socket, address))

    while True:
        weather_conditions = weather

        signal.signal(signal.SIGUSR1, handler_signals)
        signal.signal(signal.SIGUSR2, handler_signals)
        signal.signal(signal.SIGINT, handler_signals)

        pexternal = Process(target=external_process, args=())
        pexternal.start()
        #pexternal.join()


def handler_signals(sig, frame):
    global serve

    if sig == signal.SIGUSR1:
        print(1)
    elif sig == signal.SIGUSR2:
        print(2)
    elif sig == signal.SIGINT:
        serve = False


def handler_client(s, a):
    with s:
        print("Connected to client: ", a)
        data = s.recv(1024)
        while len(data):
            s.sendall(data)
            data = s.recv(1024)
        print("Disconnecting from client: ", a)
