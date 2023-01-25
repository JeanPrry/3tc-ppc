import random
import signal
import os


EVENT1 = 0.025
EVENT2 = 0.7956
NOEVENT = 0


def external_process():
    events = [NOEVENT, EVENT1, EVENT2]
    events_prob = [198, 1, 1]
    while True:
        event = random.choices(events, weights=events_prob, k=1) #Choose one event from the list of events
        if event[0] != 0:
            if event[0] == EVENT1:
                os.kill(os.getpid(), signal.SIGUSR1)
            elif event[0] == EVENT2:
                os.kill(os.getpid(), signal.SIGUSR2)
