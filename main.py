import socket
import select
import threading
import time
import signal
from const import *


serve = True


def handler_client(list_clients):
    data = ""
    print("handler_client started")
    global serve
    while serve:
        if not len(data):
            for client in list_clients:
                data = "Enter"
                client.sendall(data.encode())
                time.sleep(0.01)
                data = input()
        if data == "external event":
            for client in list_clients:
                client.sendall(data.encode())
                time.sleep(0.01)
                data = input()
        if data == "end":
            print("Program is terminated")
            client.sendall(data.encode())
            serve = False


if __name__ == "__main__" :
    print("Main started")

    serve = True


    def kill_process(signal_number, frame):
        print(f'Sig. number received: {signal_number}, Frame: {frame}')
        global serve
        serve = False


    signal.signal(signal.SIGINT, kill_process)
    signal.signal(signal.SIGTERM, kill_process)

    list_clients = []

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

        server_socket.setblocking(False)
        server_socket.bind((HOST, PORT_MAIN))
        server_socket.listen(2)

        thread = threading.Thread(target=handler_client, args=(list_clients,))
        thread.start()

        while serve:
            readable, writable, error = select.select([server_socket], [], [], 1)
            if server_socket in readable:
                client_socket, address = server_socket.accept()
                list_clients.append(client_socket)

        thread.join()
        print('PROGRAM IS TERMINATED SUCCESSFULLY')
