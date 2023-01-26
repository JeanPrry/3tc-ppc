import sys
import socket
import threading
import os
import signal
import random
from multiprocessing import Process, Array, Value
import select
import matplotlib.pyplot as plt


def weather_process(weather, change, run):
    SUNNY = 0.2
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
            m = month.value % 12
            if 0 <= m < 3:
                season = "winter"
            elif 3 <= m < 6:
                season = "spring"
            elif 6 <= m < 9:
                season = "summer"
            elif 9 <= m < 12:
                season = "automn"

            weather[0] = random.choices(list_weather, weights=coef_prob[season]["weather_coef"], k=1)[0]
            weather[1] = random.gauss(mu=coef_prob[season]["mean_temperature"], sigma=1)
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
        external_impact = 20
    elif sig == signal.SIGUSR2:
        external_impact = 50


def han_market(run):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

        server_socket.setblocking(False)
        server_socket.bind((HOST, PORT_MARKET))
        server_socket.listen(2)

        threads = []

        while run.value:
            readable, writable, error = select.select([server_socket], [], [], 1)
            if server_socket in readable and len(threads) <= 10:
                client_socket, address = server_socket.accept()
                thread = threading.Thread(target=han_client_market, args=(client_socket,run))
                threads.append(thread)
                thread.start()

        for t in threads:
            t.join()


def han_client_market(client, run):

    while run.value:
        client.sendall(input().encode())


HOST = "localhost"
PORT_MAIN = 8889
PORT_MARKET = 5559

EVENT1 = 0.025
EVENT2 = 0.7956
NOEVENT = 0

weather_conditions = Array("d", range(2))
weather_change = Value("i", 0)
new_external = Value("i", 0)
external_impact = 0
run = Value("i", 1)
month = Value("i", 0)
energy_price = Value("d", 50)
next = Value("i", 0)

list_price = [energy_price.value]
list_month = [month.value]

pweather = Process(target=weather_process, args=(weather_conditions, weather_change, run))
thread_main = threading.Thread(target=han_main, args=(weather_change, run, new_external))
thread_market = threading.Thread(target=han_market, args=(run, ))
process_external = Process(target=external_process, args=(new_external, run))

thread_main.start()
thread_market.start()
pweather.start()
process_external.start()

signal.signal(signal.SIGUSR1, handler_signals)
signal.signal(signal.SIGUSR2, handler_signals)
signal.signal(signal.SIGINT, handler_signals)

while run.value:
    while (next.value or weather_change.value or new_external.value) and run.value:
        pass

    if run.value: #dans le cas où run passe à false pendant la boucle du dessus
        month.value += 1
        next.value = 1
        energy_price.value = energy_price.value + 0.1 * weather_conditions[0] + 0.5 * weather_conditions[1] + 0.8 * external_impact

        list_price.append(energy_price.value)
        list_month.append(month.value)

        plt.xlabel('Months')
        plt.ylabel("Energy Price")
        plt.plot(list_month, list_price)
        plt.show()
        plt.close()

        print("At month ", month.value, ", energy price : ", energy_price.value)

pweather.join()
thread_main.join()
pweather.join()
process_external.join()
