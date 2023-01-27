import socket
import select
import threading
import time

HOST = "localhost"
PORT = 1118

global serve
serve = True


def handler_client(list_clients):
    data = ""
    while data != "end":
        if not len(data):
            for client in list_clients:
                data = "Enter"
                client.sendall(data.encode())
                time.sleep(0.01)
        if data == "external event":
            for client in list_clients:
                client.sendall(data.encode())
                time.sleep(0.01)

        data = input()

    for client in list_clients: #Terminate connection
        client.sendall(data.encode())

    global serve
    serve = False


if __name__ == "__main__" :

    serve = True
    list_clients = []

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

        server_socket.setblocking(False)
        server_socket.bind((HOST, PORT))
        server_socket.listen(2)

        thread = threading.Thread(target=handler_client, args=(list_clients,))
        thread.start()

        while serve:
            readable, writable, error = select.select([server_socket], [], [], 1)
            if server_socket in readable:
                client_socket, address = server_socket.accept()
                list_clients.append(client_socket)

        thread.join()
