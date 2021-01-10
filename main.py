import os
import time
import sys, getopt
import git
import subprocess
import queue
import threading
import sys
from Button_pad import Button_pad

def read_output(pipe, q):
    """
    reads output from `pipe`, when line has been read, puts
    line on Queue `q`
    """
    while True:
        l = pipe.readline()
        q.put(l)

# Perform a git pull to get the latest version on boot
print("Checking for updates...")
dir = '~/piloopdrumbox'
g = git.cmd.Git(dir)
g.pull()

#PD_PATH = "/Applications/Pd-0.51-1.app/Contents/Resources/bin/" #mac
PD_PATH = "" #pi
PORT_SEND_TO_PD = 3000
PORT_RECEIVE_FROM_PD = 4000

# Set up the GPIO library and Pins and send the PD_to_py info
buttons = Button_pad(PD_PATH, PORT_SEND_TO_PD)
buttons.setup_buttons() #Initialize the Pins of leds/buttons

# start the socket
print("setting up socket...")
args = ["sudo", "pdreceive", str(PORT_RECEIVE_FROM_PD)]
proc = subprocess.Popen(args, stdout=subprocess.PIPE)
# Queue for storing output lines
proc_q = queue.Queue()
proc_t = threading.Thread(target=read_output, args=(proc.stdout, proc_q))
proc_t.daemon = True
proc_t.start()
time.sleep(1)

# start PD
os.system(PD_PATH + 'pd -nogui main.pd &')
print("starting PD...")
time.sleep(4)

while True:
    #incoming PD data
    try:
        l = proc_q.get(False).decode()
        print(l)
    except queue.Empty:
        pass
    #send_msg.select_kit(input("select kit:"))
    #send_msg.press_button(int(input("press buton:")))
    buttons.scan()
