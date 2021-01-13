import os
import time
import git
from subprocess import Popen, PIPE
from queue import Queue, Empty
from threading import Thread
from Button_pad import Button_pad
from resources import RPi_I2C_driver

#Globals
COLORS = ["red", "green", "blue", "yellow", "purple", "cyan", "white"]
LOOP_BUTTONS = [1,2,3,4,5,6,7,8]
DRUMPAD_BUTTONS = [9,10,11,12,13,14,15,16]
BLOCK = chr(255) #block to display on screen for metronome

def read_pd_input(proc, q):
    """
    Thread process to read PureData input
    Requires the queue, that stores the socket output
    """
    while True:
        pd_input = proc.readline()
        q.put(pd_input)
        time.sleep(1/10)

def process_pd_input(q):
    while True:
        try:
            #reads the queue with blocking
            pd_input = q.get().decode()
            if pd_input:
                print(pd_input)
                handle_pd_msg(pd_input)
        except Empty:
            time.sleep(1/10)
            pass

def handle_pd_msg(msg):
    """
    Handle a msg from puredata, which is split by | characters
    """
    x = msg.split("|")
    del x[-1] #remove last element of the list (PD automatically adds \n)
    if x[0] == "counter":
        set_metronome(int(x[1]), int(x[2]))
    if x[0] == "status":
        handle_status(x[1], x[2:])

def handle_status(action, payload):
    """
    Handle status messages from PD
    """
    payload = [int(i) for i in payload]
    if action == "clear_rec":
        print("Received: " + action + ": " + str(payload[0]))
    elif action == "start_rec":
        buttons.set_button_color(payload[0], COLORS[0]) #red
        lcd.lcd_display_string("Start rec: " + str(payload[0]), 1)
    elif action == "stop_rec":
        buttons.set_button_color(payload[0], COLORS[1]) #green
        lcd.lcd_display_string("Finished rec: " + str(payload[0]), 1)
    elif action == "wait_rec":
        buttons.set_button_color(payload[0], COLORS[6]) #yellow
    elif action == "mute_rec":
        if payload[0] == 1:
            #mute
            buttons.set_button_color(payload[1], COLORS[2]) #blue
        if payload[0] == 0:
            #unmute
            buttons.set_button_color(payload[1], COLORS[1]) #green
    else:
        print("unknown status received from PD")

def set_metronome(value, total_beats):
    lcd.lcd_display_string_pos(12 / total_beats * value * BLOCK, 2, 0)

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
for drumpad_button in DRUMPAD_BUTTONS:
    #Set buttons to white color
    buttons.set_button_color(drumpad_button, COLORS[5])

# Set up the LCD
lcd = RPi_I2C_driver.lcd()

# start the socket
print("setting up socket...")
args = ["pdreceive", str(PORT_RECEIVE_FROM_PD)]
process_socket_PD = Popen(args, stdout=PIPE) #second process to read PD
proc_q = Queue() #queue for messages from PD
# Seperate threads for reading/handling the output from PD
read_pd_thread = Thread(target = read_pd_input, args = (process_socket_PD.stdout, proc_q))
process_pd_thread = Thread(target = process_pd_input, args = (proc_q, ))
read_pd_thread.start()
process_pd_thread.start()
time.sleep(1)

# start PD
os.system(PD_PATH + 'pd -nogui main.pd &')
print("starting PD...")
time.sleep(4)

print("Setup complete!")
lcd.lcd_display_string("Ready to play!", 1)

while True:
    # Run button loop
    buttons.scan()
    time.sleep(1/1000)
