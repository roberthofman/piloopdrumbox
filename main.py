import os
import time
import sys, getopt
import git
from Button_pad import Button_pad

# Perform a git pull to get the latest version on boot
print("Checking for updates...")
dir = '~/piloopdrumbox'
g = git.cmd.Git(dir)
g.pull()

#PD_PATH = "/Applications/Pd-0.51-1.app/Contents/Resources/bin/" #mac
PD_PATH = "" #pi
PORT_SEND_TO_PD = 3000

# Set up the GPIO library and Pins and send the PD_to_py info
buttons = Button_pad(PD_PATH, PORT_SEND_TO_PD)
buttons.setup_buttons() #Initialize the Pins of leds/buttons

# start the socket (Pd_to_py)
socket_message = {}
previous_socket_message = {}
os.system('python3 Pd_to_py.py &')
print("setting up socket...")
time.sleep(1)

# start PD
os.system(PD_PATH + 'pd -nogui main.pd &')
print("starting PD...")
time.sleep(4)

while True:
    if socket_message and not socket_message == previous_socket_message:
        print(socket_message)
        previous_socket_message = socket_message
    #send_msg.select_kit(input("select kit:"))
    #send_msg.press_button(int(input("press buton:")))
    buttons.scan()
