import socket
import threading
from multiprocessing import Value, Queue, Process, Array
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sysv_ipc


key = 42


def q_server(homes, run): # Gestion de la queue

    mq_demande = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
    mq_offre = sysv_ipc.MessageQueue(key + 1, sysv_ipc.IPC_CREAT)

    while run.value:

        for home in homes:

            energy_left = home.production_rate - home.consumption_rate

            if energy_left > 0: # Si on a de l'énergie en trop
                if home.policy == 1:    # On donne tout le temps
                    mq_offre.send(str(energy_left).encode())
                    home.production_rate -= energy_left

                elif home.policy == 2:  # On vend direct au market
                    pass

                elif home.policy == 3:  # On donne si on a de la demande
                    message, type = mq_demande.receive()
                    message = message.decode()
                    if message != "":   # Si on a de la demande
                        energy_to_send = int(message)
                        if energy_to_send > energy_left:    # Si on a moins d'énergie que demandé
                            mq_offre.send(str(energy_left).encode())
                            home.production_rate -= energy_left

                        else:   # Si on a plus d'énergie que demandé
                            mq_offre.send(str(energy_to_send).encode())
                            home.production_rate -= energy_to_send

                    else:
                        # on envoie au market
                        pass

            else:   # Si on a est en déficit
                deficit = -energy_left
                mq_demande.send(str(deficit).encode())

                energy_received, _ = mq_offre.receive()
                energy_received = int(energy_received.decode())

                if energy_received < deficit:  # Si on a recu moins que nécessaire
                    home.production_rate += energy_received
                else:   # Si on a recu plus que nécessaire
                    home.production_rate += deficit
                    mq_offre.send(str(energy_received - deficit).encode())  # On renvoie l'énergie en trop

    mq_demande.remove()
    mq_offre.remove()


def han_tcp_main(host, port, run, barrier):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))

        while run.value:
            m = client_socket.recv(1024).decode()
            if m == "Enter":
                #print("It works !")
                next.value = 0
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


class Home:

    def __init__(self, barrier):

        self.consumption_rate = random.randint(1, 100)
        self.production_rate = random.randint(1, 100)
        self.policy = 1

        tcp_main = threading.Thread(target=han_tcp_main, args=(HOST, PORT_MAIN, run, barrier))
        tcp_market = threading.Thread(target=han_tcp_market, args=(HOST, PORT_MARKET, run))

        tcp_main.start()
        tcp_market.start()


HOST = "localhost"
PORT_MAIN = 1118
PORT_MARKET = 4446

run = Value("i", 1)
next = Value("i", 0)

home_list = []
largeur = 0.3

nb_home = 3
barrier = threading.Barrier(nb_home + 1)

for i in range(nb_home):
    home = Home(barrier)
    home_list.append(home)

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

    ax.set_xticks([r + largeur/2 for r in range(len(y1))], [f'Home{j}' for j in range(len(y1))])
    ax.legend()


p = Process(target=animate, args=())

p.start()
surplus = Queue()
carence = Queue()

while run.value:
    while next.value and run.value:
        pass
    if run.value: #dans le cas où run passe à false pendant la boucle du dessus
        barrier.wait()
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
