#Test script for the buttons
from ..Button_pad import Button_pad

# Set up the GPIO library and Pins
buttons = Button_pad()
buttons.setup_buttons() #Initialize the Pins of leds/buttons

while True:
    buttons.scan()
