import RPi.GPIO as GPIO
import time
from datetime import datetime
import math

class Button_pad:
    def __init__(self, num_drumkits):
        """
        Hooking up the button pad: Config variables / Global Variables
        Source: https://tinyurl.com/y6qafxfs (C-code for arduino)
        """
        # Leds rows/cols
        self.NUM_LED_COLUMNS = 4
        self.NUM_LED_ROWS = 4
        # Buttons rows/cols
        self.NUM_BTN_COLUMNS = 4
        self.NUM_BTN_ROWS = 4
        # RGB
        self.NUM_COLORS = 3
        # Vary this number if the key press is not registered correctly
        # It basically sets the sensitivity of the button (press/no press)
        # Higher is less sensitive, lower is more sensitive (INT)
        self.MAX_DEBOUNCE = 3 # should be 2 / 3 accorinding to Sparkfun
        # Global Variables
        self.btnColumnPins = [31, 33, 35, 37] # Pin numbers for columns (SWT_GND) 
        self.btnRowPins = [13, 15, 19, 21] # Pin numbers for rows (SWITCH) 
        self.ledColumnPins = [32, 36, 38, 40] # Pin numbers for the LED ground (LED_GND)
        # RGB pins
        # 1: red (8, 10, 12, 16) 
        # 2: blue (18, 22, 24, 26)
        # 3: green (7, 23, 11, 29)
        self.colorPins = [[8, 18, 7], [10, 22, 23], [12, 24, 11], [16, 26, 29]] 
        # Tracks how often a button is pressed
        self.debounce_count = self.create_matrix(0, self.NUM_BTN_COLUMNS, self.NUM_BTN_ROWS)
        # Tracks the LED status
        self.LED_output = self.create_matrix("", self.NUM_LED_COLUMNS, self.NUM_LED_ROWS)
        self.button_press_time = self.create_matrix(datetime.now(), self.NUM_BTN_COLUMNS, self.NUM_BTN_ROWS)
        self.button_prev_press_time = self.create_matrix(datetime.now(), self.NUM_BTN_COLUMNS, self.NUM_BTN_ROWS)
        self.button_was_pressed = self.create_matrix(False, self.NUM_BTN_COLUMNS, self.NUM_BTN_ROWS)
        self.button_was_released = self.create_matrix(False, self.NUM_BTN_COLUMNS, self.NUM_BTN_ROWS)
        # Options variables
        self.options_open = False
        self.option_number = 0
        self.options = {0: "select_kit", 1: "audio_input", 2: "clear_all"}
        self.option_values = {0:1, 1:1, 2:0} # standard values
        self.total_drumkits = num_drumkits
        # loop variables
        self.active_loops = {1:False, 2:False, 3:False, 4:False, 5:False, 6:False, 7:False, 8:False}
        self.init_loop = True

    def create_matrix(self, value, y_range, x_range):
        """
        Creates an x by y matrix with an init value
        """
        return( [ [ value for y in range(y_range) ] for x in range(x_range) ] )

    def setup_buttons(self):
        """
        Initialize PINS
        using GPIO.BOARD mode: which uses actual pin numbers (instead of only GPIO)
        """
        GPIO.setmode(GPIO.BOARD)
        for col in range(self.NUM_LED_COLUMNS):
            # LED columns
            GPIO.setup(self.ledColumnPins[col], GPIO.OUT, initial=GPIO.HIGH)

        for col in range(self.NUM_BTN_COLUMNS):
            # Button columns
            GPIO.setup(self.btnColumnPins[col], GPIO.OUT, initial=GPIO.HIGH)

        for row in range(self.NUM_BTN_ROWS):
            # Button columns
            GPIO.setup(self.btnRowPins[row], GPIO.IN, pull_up_down=GPIO.PUD_UP)

        for row in range(self.NUM_LED_ROWS):
            # LED drive lines
            for color in range(self.NUM_COLORS):
                GPIO.setup(self.colorPins[row][color], GPIO.OUT, initial=GPIO.LOW)

    def set_button_color(self, button, color):
        """
        Called from the main function
        Determines the color for a certain button
        button: 1:16
        color: red, green, blue, yellow, purple, cyan, white
        """
        column = (button-1) % 4
        row = math.floor((button-1) / 4)
        self.LED_output[row][column] = color

    def set_LED_GPIO(self, color, row):
        """
        Sets the color of the LED
        """
        if color == "red":
            GPIO.output(self.colorPins[row][0], GPIO.HIGH)
        if color == "blue":
            GPIO.output(self.colorPins[row][1], GPIO.HIGH)
        if color == "green":
            GPIO.output(self.colorPins[row][2], GPIO.HIGH)
        if color == "purple":
            GPIO.output(self.colorPins[row][0], GPIO.HIGH)
            GPIO.output(self.colorPins[row][1], GPIO.HIGH)
        if color == "yellow":
            GPIO.output(self.colorPins[row][0], GPIO.HIGH)
            GPIO.output(self.colorPins[row][2], GPIO.HIGH)
        if color == "cyan":
            GPIO.output(self.colorPins[row][1], GPIO.HIGH)
            GPIO.output(self.colorPins[row][2], GPIO.HIGH)
        if color == "white":
            GPIO.output(self.colorPins[row][0], GPIO.HIGH)
            GPIO.output(self.colorPins[row][1], GPIO.HIGH)
            GPIO.output(self.colorPins[row][2], GPIO.HIGH)
        if color == "off":
            GPIO.output(self.colorPins[row][0], GPIO.LOW)
            GPIO.output(self.colorPins[row][1], GPIO.LOW)
            GPIO.output(self.colorPins[row][2], GPIO.LOW)

    def scan(self):
        """
        Function to be looped to scan button presses
        It quickly goes over all columns and corresponding rows
        """
        for column in range(self.NUM_LED_COLUMNS):
            #Select columns -> start with low on buttons/leds
            GPIO.output(self.btnColumnPins[column], GPIO.LOW)
            GPIO.output(self.ledColumnPins[column], GPIO.LOW)

            # output LED row values
            for row in range(self.NUM_LED_ROWS):
                color = self.LED_output[column][row]
                if color:
                    self.set_LED_GPIO(color, row)

            time.sleep(1/1000)

            # read the button inputs
            for row in range(self.NUM_BTN_ROWS):
                val = GPIO.input(self.btnRowPins[row])
                if val == GPIO.LOW:
                    # Active low: val is low when btn is pressed
                    if self.debounce_count[column][row] < self.MAX_DEBOUNCE:
                        self.debounce_count[column][row] += 1
                        if self.debounce_count[column][row] == self.MAX_DEBOUNCE:
                            self.button_was_pressed[column][row] = True
                else:
                    # Button is released
                    if self.debounce_count[column][row] > 0:
                        self.debounce_count[column][row] -= 1
                        if self.debounce_count[column][row] == 0:
                            self.button_was_released[column][row] = True

            time.sleep(1/1000)

            # Reset button to init value
            GPIO.output(self.btnColumnPins[column], GPIO.HIGH)
            GPIO.output(self.ledColumnPins[column], GPIO.HIGH)

            for row in range(self.NUM_LED_ROWS):
                for color in range(self.NUM_COLORS):
                    GPIO.output(self.colorPins[row][color], GPIO.LOW)
