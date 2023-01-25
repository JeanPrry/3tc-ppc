from multiprocessing import Array, Process
import random
from market import market_process
from home import home_process


def weather_process(weather):
    while True:
        for i in range(len(weather)):
            weather[i] = random.random()


if __name__ == "__main__" :

    weather_conditions = Array("d", range(2))

    pweather = Process(target=weather_process, args=(weather_conditions,))
    pmarket = Process(target=market_process, args=(weather_conditions,))

    #IMPLEMENT POOLS
    phome1 = Process(target=home_process, args=())
    phome2 = Process(target=home_process, args=())

    pweather.start()
    pmarket.start()
    phome1.start()
    phome2.start()

    pweather.join()
    pmarket.join()
    phome1.join()
    phome2.join()
