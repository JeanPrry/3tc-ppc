import socket
import threading
from multiprocessing import Value, Process, Array, Barrier
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sysv_ipc
from const import *


key = 42


def q_server(consumptions, productions, policies, run, barrier):    # Gestion de la queue

    mq_demande = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
    mq_offre = sysv_ipc.MessageQueue(key + 1, sysv_ipc.IPC_CREAT)

    while run.value:

        barrier.wait()
        print(consumptions[0], " ", productions[0], " , ", consumptions[1], " ", productions[1], " , ", consumptions[2], " ", productions[2])

        for k in range(3):

            for i in range(len(consumptions)):

                energy_left = productions[i] - consumptions[i]

                if energy_left > 0: # Si on a de l'énergie en trop
                    if policies[i] == 1:    # On donne tout le temps
                        mq_offre.send(str(energy_left).encode())
                        productions[i] -= energy_left

                    elif policies[i] == 2:  # On vend direct au market
                        pass

                    elif policies[i] == 3:  # On donne si on a de la demande
                        try:
                            message, type = mq_demande.receive(block=False)
                            message = message.decode()
                            if message != "":   # Si on a de la demande
                                energy_to_send = float(message)
                                if energy_to_send > energy_left:    # Si on a moins d'énergie que demandé
                                    mq_offre.send(str(energy_left).encode())
                                    productions[i] -= energy_left

                                else:   # Si on a plus d'énergie que demandé
                                    mq_offre.send(str(energy_to_send).encode())
                                    productions[i] -= energy_to_send

                            else:
                                # on envoie au market
                                pass

                        except sysv_ipc.BusyError:
                            pass

                        message, type = mq_demande.receive(timeout=0.01)
                        message = message.decode()
                        if message != "":   # Si on a de la demande
                            energy_to_send = float(message)
                            if energy_to_send > energy_left:    # Si on a moins d'énergie que demandé
                                mq_offre.send(str(energy_left).encode())
                                productions[i] -= energy_left

                            else:   # Si on a plus d'énergie que demandé
                                mq_offre.send(str(energy_to_send).encode())
                                productions[i] -= energy_to_send

                        else:
                            # on envoie au market
                            pass

                else:   # Si on a est en déficit
                    deficit = -energy_left
                    try:
                        energy_received, _ = mq_offre.receive(block=False)
                        energy_received = energy_received.decode()

                        if energy_received != "":  # On regarde si il y a de l'énergie disponible
                            energy_received = float(energy_received)

                            if energy_received < deficit:  # Si on a recu moins que nécessaire
                                productions[i] += energy_received
                            else:  # Si on a recu plus que nécessaire
                                productions[i] += deficit
                                mq_offre.send(str(energy_received - deficit).encode())  # On renvoie l'énergie en trop
                        else:
                            mq_demande.send(str(deficit).encode())  # On fait une demande

                    except sysv_ipc.BusyError:
                        pass

        print(consumptions[0], " ", productions[0], " , ", consumptions[1], " ", productions[1], " , ", consumptions[2],
              " ", productions[2], "\n")

        # Empty the queues
        while True:
            try:
                message, t = mq_demande.receive(block=False)
            except sysv_ipc.BusyError:
                break
        while True:
            try:
                message, t = mq_offre.receive(block=False)
            except sysv_ipc.BusyError:
                break
        barrier.wait()

    mq_demande.remove()
    mq_offre.remove()


def han_tcp_main(host, port, run, barrier):

    barrier.wait()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))

        while run.value:
            m = client_socket.recv(1024).decode()
            if m == "Enter":
                barrier.wait()
                barrier.wait()

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


run = Value("i", 1)

largeur = 0.3

nb_home = 3
barrier = Barrier(nb_home + 2)

y1 = Array("d", range(nb_home))
y2 = Array("d", range(nb_home))
x1 = Array("d", range(nb_home))
x2 = Array("d", [i + largeur for i in x1])
policies = Array("i", range(nb_home))

for i in range(nb_home):
    y1[i] = random.randint(1, 100)
    y2[i] = random.randint(1, 100)
    policies[i] = 1

    tcp_main = threading.Thread(target=han_tcp_main, args=(HOST, PORT_MAIN, run, barrier))
    tcp_market = threading.Thread(target=han_tcp_market, args=(HOST, PORT_MARKET, run))
    tcp_main.start()
    tcp_market.start()


def animate():
    fig, ax = plt.subplots()
    # Create the animation object
    ani = animation.FuncAnimation(fig, update, frames=3, fargs=(ax,))
    plt.show()


def update(num, ax):

    ax.clear()
    ax.bar(x1, y1, width=largeur, color='blue', label='consumption')
    ax.bar(x2, y2, width=largeur, color='red', label='production')

    ax.set_xticks([r + largeur/2 for r in range(len(y1))], [f'Home{j}' for j in range(len(y1))])
    ax.legend()


p = Process(target=animate, args=())
p_q = Process(target=q_server, args=(y1, y2, policies, run, barrier))

p.start()
p_q.start()

barrier.wait()

while run.value:

    barrier.wait()
    j = 0
    for i in range(len(y1)):
        y1[i] = random.randint(1, 100)
        y2[i] = random.randint(1, 100)
        j += 1
    barrier.wait()


p.join()
p_q.join()
