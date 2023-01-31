import sys
import socket
import threading
import os
import signal
import random
from multiprocessing import Process, Array, Value, Barrier
import select
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from const import *


def weather_process(weather, change, run):
    SUNNY = - 0.2
    CLOUDY = 0.5
    RAINY = 0.7
    SNOWY = 0.9

    list_weather = [SUNNY, CLOUDY, RAINY, SNOWY]
    coef_prob = {
        "summer": {
            "mean_temperature": 30,
            "weather_coef": [70, 20, 9, 1]
        },
        "spring": {
            "mean_temperature": 20,
            "weather_coef": [60, 25, 12, 3]
        },
        "automn": {
            "mean_temperature": 15,
            "weather_coef": [30, 40, 30, 5]
        },
        "winter": {
            "mean_temperature": 5,
            "weather_coef": [20, 40, 25, 15]
        }
    }

    while run.value:
        if change.value:
            d = day.value % 365
            if 0 <= d < 91:
                season = "winter"
            elif 91 <= d < 182:
                season = "spring"
            elif 182 <= d < 273:
                season = "summer"
            elif 273 <= d < 365:
                season = "automn"

            weather[0] = random.choices(list_weather, weights=coef_prob[season]["weather_coef"], k=1)[0]
            weather[1] = random.gauss(mu=coef_prob[season]["mean_temperature"], sigma=2)
            list_temp[d] = weather[1]
            change.value = 0


def external_process(new_external, run):
    events = [EVENT1, EVENT2]
    events_prob = [1, 2]
    while run.value:
        if new_external.value:
            event = random.choices(events, weights=events_prob, k=1)  # Choose one event from the list of events
            if event[0] == EVENT1:
                print("Une guerre se déclenche !")
                os.kill(os.getppid(), signal.SIGUSR1)
            elif event[0] == EVENT2:
                print("Un nouvelle loi est passée")
                os.kill(os.getppid(), signal.SIGUSR2)
            new_external.value = 0


def han_main(weather, run, external):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT_MAIN))

        while run.value:
            m = client_socket.recv(1024).decode()
            if m == "Enter":
                next.value = 0
                weather.value = 1
            if m == "external event":
                  external.value = 1
            if m == "end":
                run.value = 0
            m = "wait for new command"


def handler_signals(sig, frame):
    global external_impact
    if sig == signal.SIGUSR1:
        external_impact = 2
    elif sig == signal.SIGUSR2:
        external_impact = 5


def han_market(run,lock1, lock2, quantite_achete, quantite_vendue):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

        server_socket.setblocking(False)
        server_socket.bind((HOST, PORT_MARKET))
        server_socket.listen(2)

        threads = []

        while run.value:
            readable, writable, error = select.select([server_socket], [], [], 1)
            if server_socket in readable and len(threads) <= 10:
                client_socket, address = server_socket.accept()
                thread = threading.Thread(target=han_client_market, args=(client_socket, run, lock1, lock2, quantite_achete, quantite_vendue))
                threads.append(thread)
                thread.start()

        for t in threads:
            t.join()


def han_client_market(client, run, lock1,lock2, quantite_achete, quantite_vendue):
    
    while run.value:
        data = client.recv(1024).decode()
        data = float(data)
        if data > 0:
            print("vend ", data)
            with lock1 :
                quantite_vendue.value+=float(data)
        elif data < 0:
            print("achete ", data)
            with lock2 :
                quantite_achete.value+=float(data)


EVENT1 = 0.025
EVENT2 = 0.7956
NOEVENT = 0

weather_conditions = Array("d", range(2))
weather_change = Value("i", 0)
new_external = Value("i", 0)
external_impact = 0
run = Value("i", 1)
day = Value("i", 0)
energy_price = Value("d", 50)
next = Value("i", 0)

quantite_achete =Value("d", 0)
quantite_vendue =Value("d", 0)
lock1 = threading.Lock()
lock2 = threading.Lock()

list_price = Array("d", [0] * 365)
list_price[0] = energy_price.value

list_temp = Array("d", [0] * 365)
list_temp[0] = weather_conditions[1]


def animate():

    fig, axs = plt.subplots(2, 1)
    line1, = axs[0].plot(range(365), list_price)
    axs[0].set_ylabel("Price")
    axs[0].set_ylim(-100, 100)
    line2, = axs[1].plot(range(365), list_temp)
    axs[1].set_ylabel("Temperature")
    axs[1].set_ylim(-5, 35)

    # Create the animation object
    ani = animation.FuncAnimation(fig, update, frames=365, blit=True, fargs=(line1, line2))
    plt.show()


def update(num, line1, line2):
    x = range(365)
    line1.set_data(x, list_price)
    line2.set_data(x, list_temp)
    return line1, line2


pweather = Process(target=weather_process, args=(weather_conditions, weather_change, run))
thread_main = threading.Thread(target=han_main, args=(weather_change, run, new_external))
thread_market = threading.Thread(target=han_market, args=(run,lock1, lock2, quantite_achete, quantite_vendue))
process_external = Process(target=external_process, args=(new_external, run))
process_plot = Process(target=animate, args=())

thread_main.start()
thread_market.start()
pweather.start()
process_external.start()
process_plot.start()
b = Barrier(2)
signal.signal(signal.SIGUSR1, handler_signals)
signal.signal(signal.SIGUSR2, handler_signals)
signal.signal(signal.SIGINT, handler_signals)

while run.value:
    while (next.value or weather_change.value or new_external.value) and run.value:
        pass

    if run.value: #dans le cas où run passe à false pendant la boucle du dessus
        day.value += 1
        next.value = 1
        print("somme achat", quantite_achete.value)
        print("somme vente", quantite_vendue.value)
        energy_price.value = 1.02 * energy_price.value + 0.002 * weather_conditions[0] - 0.002 * weather_conditions[1] + 0.1 * external_impact
        quantite_vendue.value = 0
        quantite_achete.value = 0
        list_price[day.value % 365] = energy_price.value

        #print("At day ", day.value, ", energy price : ", energy_price.value)

pweather.join()
thread_main.join()
pweather.join()
process_external.join()
process_plot.join()
