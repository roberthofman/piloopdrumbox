import os
import time
import sys, getopt
from Py_to_pd import Py_to_pd

def main():
    #PD_PATH = "/Applications/Pd-0.51-1.app/Contents/Resources/bin/" #mac
    PD_PATH = "" #pi (test)
    PORT_SEND_TO_PD = 3000

    # initiate python to PD class
    send_msg = Py_to_pd(PD_PATH, PORT_SEND_TO_PD)

    # start the socket (Pd_to_py)
    os.system('python3 Pd_to_py.py &')
    print("setting up socket...")
    time.sleep(1)

    # start PD
    os.system(PD_PATH + 'pd -nogui main.pd &')
    print("starting PD...")
    time.sleep(4)

    while True:
        send_msg.select_kit(input("select kit:"))

if __name__ == "__main__":
    main()
