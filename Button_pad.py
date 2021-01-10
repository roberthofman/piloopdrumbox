import RPi.GPIO as GPIO
from Py_to_pd import Py_to_pd
import time
from datetime import datetime

class Button_pad:
    def __init__(self, PD_PATH, PORT_SEND_TO_PD):
        """
        Hooking up the button pad: Config variables / Global Variables
        Source: https://tinyurl.com/y6qafxfs
        """
        # GPIO.setwarnings(False) #later warnings suppression (if needed)
        # Leds rows/cols
        self.NUM_LED_COLUMNS = 4
        self.NUM_LED_ROWS = 4
        # Buttons rows/cols
        self.NUM_BTN_COLUMNS = 4
        self.NUM_BTN_ROWS = 4
        # Change to RGB later
        self.NUM_COLORS = 3
        # Vary this number if the key press is not registered correctly
        # It basically sets the sensitivity of the button (press/no press)
        self.MAX_DEBOUNCE = 3 # should range between 2-3 accorinding to Sparkfun
        # Global Variables
        self.LED_output = self.create_matrix(False, self.NUM_LED_COLUMNS, self.NUM_LED_ROWS)
        self.btnColumnPins = [31, 33, 35, 37] # Pin numbers for columns (4)
        self.btnRowPins = [13, 15, 19, 21] # Pin numbers for rows (4)
        self.ledColumnPins = [32, 36, 38, 40] # Pin numbers for the LED's (columns) (4)
        self.colorPins = [[8, 18, 7], [10, 22, 23], [12, 24, 11], [16, 26, 29]] # 1: red 2: green 3: blue
        # Tracks how often a button is pressed
        self.debounce_count = self.create_matrix(0, self.NUM_BTN_COLUMNS, self.NUM_BTN_ROWS)
        self.button_press_time = self.create_matrix(0, self.NUM_BTN_COLUMNS, self.NUM_BTN_ROWS)
        self.button_timer = self.create_matrix(0, self.NUM_BTN_COLUMNS, self.NUM_BTN_ROWS)
        # initiate python to PD class
        self.send_msg = Py_to_pd(PD_PATH, PORT_SEND_TO_PD)

    def create_matrix(self, value, y_range, x_range):
        """
        Creates an x by y matrix with an init value
        """
        return( [ [ value for y in range(y_range) ] for x in range(x_range) ] )

    def setup_buttons(self):
        """
        Initialize PINS
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

    def handle_button_press(self, column, row):
        #Send button press
        print("Key Down: " + str(column) + ", " + str(row))
        self.LED_output[column][row] += 1
        self.button_press_time[column][row] = datetime.now()
        button_num = 1 + 4 * row + column
        if row > 1:
            #Drumbox
            self.send_msg.press_button(button_num)
        else:
            #loop
            self.send_msg.press_button(button_num)

    def handle_button_release(self, column, row):
        #Send key release
        print("Key Up: " + str(column) + ", " + str(row))
        self.button_timer[column][row] = datetime.now() - self.button_press_time[column][row]
        if self.button_timer.seconds > 2 and row < 2:
            #send clear loop if row 1 or 2
            button_num = 1 + 4 * row + column
            self.send_msg.clear_loop(button_num)
        self.button_timer[column][row] = 0

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
                val = self.LED_output[column][row]
                if(self.LED_output[column][row]):
                    GPIO.output(self.colorPins[row][val-1], GPIO.HIGH)

            time.sleep(1/1000)

            # read the button inputs
            for row in range(self.NUM_BTN_ROWS):
                val = GPIO.input(self.btnRowPins[row])
                if val == GPIO.LOW:
                    # Active low: val is low when btn is pressed
                    if self.debounce_count[column][row] < self.MAX_DEBOUNCE:
                        self.debounce_count[column][row] += 1
                        if self.debounce_count[column][row] == self.MAX_DEBOUNCE:
                            self.handle_button_press(column, row)
                else:
                    # Button is released
                    if self.debounce_count[column][row] > 0:
                        self.debounce_count[column][row] -= 1
                        if self.debounce_count[column][row] == 0:
                            self.handle_button_press(column, row)

            time.sleep(1/1000)

            # Reset button to init value
            GPIO.output(self.btnColumnPins[column], GPIO.HIGH)
            GPIO.output(self.ledColumnPins[column], GPIO.HIGH)

            for row in range(self.NUM_LED_ROWS):
                for color in range(self.NUM_COLORS):
                    GPIO.output(self.colorPins[row][color], GPIO.LOW)
