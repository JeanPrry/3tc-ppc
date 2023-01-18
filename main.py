import threading
from multiprocessing import Value, Array, Process
import random
import signal
import os


EVENT1 = 0.025
EVENT2 = 0.7956
NOEVENT = 0
# Mon commentaire

def weather_Process(weather):
    while True:
        for i in range(len(weather)):
            weather[i] = random.random()


def market_Process(weather):
    energy_price = Value("d",0.0)
    while True:
        weather_conditions = weather
        
        signal.signal(signal.SIGUSR1, handler)
        signal.signal(signal.SIGUSR2, handler)

        pexternal = Process(target=external_Process, args=())
        pexternal.start()
    

        #pexternal.join()


def handler(sig,frame):
    if sig == signal.SIGUSR1:
        print("1")
    elif sig == signal.SIGUSR2:
        print("2")


def external_Process():
    events = [NOEVENT, EVENT1, EVENT2]
    events_prob = [9, 2, 2]
    while True:
        event = random.choices(events, weights=events_prob, k=1) #Choose one event from the list of events
        if event[0] != 0:
            if event[0] == EVENT1:
                os.kill(os.getpid(), signal.SIGUSR1)
            elif event[0] == EVENT2:
                os.kill(os.getpid(), signal.SIGUSR2)


if __name__ == "__main__" :

    weather_conditions = Array("d", range(2))

    pweather = Process(target=weather_Process, args=(weather_conditions,))
    pmarket = Process(target=market_Process, args=(weather_conditions,))
    

    pweather.start()
    pmarket.start()

    pweather.join()
    pmarket.join()
    