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

def read_output(pipe, q):
    """
    reads output from `pipe`, when line has been read, puts
    line on Queue `q`
    """
    while True:
        l = pipe.readline()
        q.put(l)
        time.sleep(1/10) #check if potential lag

def read_pd_input(proc_q):
    """
    Thread process to read PureData input
    Requires the proces queue which reads the socket input
    """
    try:
        #reads the process without blocking (get(False) is non-blocking)
        pd_input = proc_q.get(False).decode()
        if pd_input:
            #If possible: create a thread for this function to avoid slowing loop
            handle_pd_msg(pd_input)
    except Empty:
        pass

def handle_pd_msg(msg):
    """
    Handle a msg from puredata, which is split by | characters
    """
    x = message.split("|")
    x.pop() #remove last element of the list (PD automatically adds \n)
    if x[0] == "counter":
        set_metronome(x[1])
    if x[0] == "status":
        print(msg)
        handle_status(x[1], x[2:])

def handle_status(action, payload):
    """
    Handle status messages from PD
    """
    if action == "clear_rec":
        print("Received: " + action + ": " + str(payload))
    elif action == "start_rec":
        buttons.set_button_color(payload, COLORS[0]) #red
        lcd.lcd_display_string("Start rec: " + str(payload), 1)
    elif action == "stop_rec":
        buttons.set_button_color(payload, COLORS[1]) #green
        lcd.lcd_display_string("Finished rec: " + str(payload), 1)
    elif action == "wait_rec":
        buttons.set_button_color(payload, COLORS[3]) #yellow
    elif action == "mute_rec":
        if payload[0] == 1:
            #mute
            buttons.set_button_color(payload[1], COLORS[2]) #blue
        if payload[0] == 0:
            #unmute
            buttons.set_button_color(payload, COLORS[1]) #green
    else:
        print("unknown status received from PD")

def set_metronome(value):
    lcd.lcd_display_string("Metro: " + str(value), 2)

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
    buttons.set_button_color(drumpad_button, COLORS[6])

# Set up the LCD
lcd = RPi_I2C_driver.lcd()

# start the socket
print("setting up socket...")
args = ["pdreceive", str(PORT_RECEIVE_FROM_PD)]
proc = Popen(args, stdout=PIPE)
# Queue for storing output lines
proc_q = Queue()
# Seperate thread for reading the output from PD
proc_thread = Thread(target = read_output, args = (proc.stdout, proc_q))
read_pd_thread = Thread(target = read_pd_input, args = (proc_q,))
proc_thread.daemon = True
read_pd_thread.daemon = True
proc_thread.start()
read_pd_thread.start()
time.sleep(1)

# start PD
os.system(PD_PATH + 'pd -nogui main.pd &')
print("starting PD...")
time.sleep(4)

print("Setup complete!")

while True:
    # Run button loop
    buttons.scan()
