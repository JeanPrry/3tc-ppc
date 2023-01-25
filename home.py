import socket
import sysv_ipc
import random
import threading


def home_process():

    # Attributes
    production_rate = random.randint(0, 100)
    consumption_rate = random.randint(0, 100)
    policy = random.choice([1, 2, 3])

    socket_thread = threading.Thread(target=han_tcp, args=())
    rqueue_thread = threading.Thread(target=receive_queue, args=())
    squeue_thread = threading.Thread(target=send_queue, args=())

    socket_thread.start()
    rqueue_thread.start()
    squeue_thread.start()

    socket_thread.join()
    rqueue_thread.join()
    squeue_thread.join()


def han_tcp():
    # TCP Socket
    HOST = "localhost"
    PORT = 3333
    connected = True

    while connected:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((HOST, PORT))
                m = "bjr"
                #m = input("message> ")
                while True:
                    client_socket.sendall(m.encode())
                    data = client_socket.recv(1024)
                    #print(str(data))
                    #m = input("message> ")
                connected = False

        except:
            pass


def send_queue():
    key = 128

    mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
    value = 1
    while value:
        message = str(value).encode()
        mq.send(message)

    mq.remove()


def receive_queue():
    key = 128

    mq = sysv_ipc.MessageQueue(key)

    while True:
        message, t = mq.receive()
        value = message.decode()
        value = int(value)
        if value:
            print("received:", value)
        else:
            print("exiting.")
            break