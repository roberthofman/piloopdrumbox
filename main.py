import os
#puredata path: change on Pi!
path = "/Applications/Pd-0.51-1.app/Contents/Resources/bin/"
       
def send2Pd(channel, message=''):
    """
    Send messages from Python to PD.
    channel: Link each message to a channel to be received in PD
        0: DSP status (0: off, 1: on)
        1: select_kit (int value)
    message: should be a string msg to be send as variable to PD
    """
    os.system("echo '" + str(channel) + " " + str(message) + ";' | "+ path + "pdsend 3000")

def audio_on():
    """
    turn on DSP in PD
    channel: 0
    """
    message = '1'
    send2Pd(0, message)

def audio_off():
    """
    turn off DSP in PD
    channel: 0
    """
    message = '0'
    send2Pd(0, message)

def select_kit(kit):
    """
    kit: numeric value that for selecting a kit
    channel: 1
    """
    send2Pd(1, kit)

def press_button(button):
    """
    button: numeric value of the pressed button (loop: 1-8, drumbox: 9-16)
    channel: 2
    """
    if button > 16 or button < 1:
        raise("button_error: range of buttons should be between 1:16")
    else:
        send2Pd(2, button)
    
#kit = input("select drum kit (1-5): ")
#select_kit(kit)
press_button(11)

