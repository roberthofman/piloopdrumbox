import RPi.GPIO as GPIO
from Py_to_pd import Py_to_pd
import time
from datetime import datetime
import math

class Button_pad:
    def __init__(self, PD_PATH, PORT_SEND_TO_PD, lcd):
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
        self.btnColumnPins = [31, 33, 35, 37] # Pin numbers for columns (4)
        self.btnRowPins = [13, 15, 19, 21] # Pin numbers for rows (4)
        self.ledColumnPins = [32, 36, 38, 40] # Pin numbers for the LED's (columns) (4)
        self.colorPins = [[8, 18, 7], [10, 22, 23], [12, 24, 11], [16, 26, 29]] # 1: red 2: blue 3: green
        # Tracks how often a button is pressed
        self.debounce_count = self.create_matrix(0, self.NUM_BTN_COLUMNS, self.NUM_BTN_ROWS)
        # Tracks the LED status
        self.LED_output = self.create_matrix("", self.NUM_LED_COLUMNS, self.NUM_LED_ROWS)
        self.button_press_time = self.create_matrix(0, self.NUM_BTN_COLUMNS, self.NUM_BTN_ROWS)
        self.button_timer = self.create_matrix(0, self.NUM_BTN_COLUMNS, self.NUM_BTN_ROWS)
        # initiate python to PD class
        self.send_msg = Py_to_pd(PD_PATH, PORT_SEND_TO_PD)
        # be able to send msg to LCD
        self.lcd = lcd
        # Options variables
        self.options_open = False
        self.option_number = 0
        self.options = {0: "select_kit", 1: "toggle_sound", 2: "clear_all"}
        self.option_values = {0:1, 1:True, 2:0} # standard values
        self.total_drumkits = 3
        # loop variables
        self.active_loops = {1:False, 2:False, 3:False, 4:False, 5:False, 6:False, 7:False, 8:False}

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

    def toggle_options(self):
        """
        Function that toggles the option menu
        """
        self.options_open = not self.options_open
        if self.options_open:
            self.update_option_lcd()
        else:
            self.options_open = False
            self.option_number = 0
            self.option_values[2] = 0
            self.lcd.lcd_display_string("Ready to play!", 1)

    def update_option_lcd(self):
        """
        Update the lcd with the selected option
        """
        self.lcd.lcd_display_string("Options", 1)
        current_option = self.options[self.option_number]
        self.lcd.lcd_display_string(current_option + ":" + str(int(self.option_values[self.option_number])), 2)

    def handle_button_press(self, column, row):
        """
        This function handles the button press, not the release
        There's a lot of sintax regarding the
        """
        #Send button press
        if self.options_open:
            # Handle options
            button_num = 1 + 4 * column + row
            self.update_option_lcd()
            if not button_num in [14, 15, 16]:
                # Unknown options button
                self.lcd.lcd_display_string("Use but 14/15/16", 1)
            if button_num == 14:
                # next option
                self.option_number = 0 if self.option_number == (len(self.options)-1) else self.option_number + 1
                self.update_option_lcd()
            if button_num == 15:
                # apply option
                if self.option_number == 0:
                    # select_kit
                    self.option_values[self.option_number] = 1 if self.option_values[self.option_number] == self.total_drumkits else self.option_values[self.option_number] + 1
                    self.send_msg.select_kit(self.option_values[self.option_number])
                if self.option_number == 1:
                    # toggle_sound
                    self.option_values[self.option_number] = not self.option_values[self.option_number]
                    if self.option_values[self.option_number]:
                        self.send_msg.audio_on()
                    else:
                        self.send_msg.audio_off()
                if self.option_number == 2:
                    # clear_all
                    self.send_msg.clear_all()
                    self.option_values[self.option_number] = 1
                    self.active_loops = {1:False, 2:False, 3:False, 4:False, 5:False, 6:False, 7:False, 8:False}
                self.update_option_lcd()
            if button_num == 16:
                # quit options
                self.toggle_options()
        else:
            self.button_press_time[column][row] = datetime.now()
            button_num = 1 + 4 * column + row
            if button_num > 8 or not self.active_loops[button_num]:
                # Press the button if drumkit or no active loop
                # For active loops: wait for release timer (clear or (un)mute)
                self.send_msg.press_button(button_num)

    def handle_button_release(self, column, row):
        """
        Function that handles when a button is released (up)
        - Checks if the button is actually pressed
        - Checks if the button is an active loop, and monitors the time of the
        button press
        - Checks if the pressed button = 13, if long press: open options
        - Lastly: reset the button timer and press time
        """
        #Send key release
        if not self.button_press_time[column][row] == 0:
            #error if only key up is registered: avoid by if
            button_num = 1 + 4 * column + row
            self.button_timer[column][row] = datetime.now() - self.button_press_time[column][row]
            if button_num < 9:
                # loop button
                if self.active_loops[button_num]:
                    #active loop: release longer than 1 second: clear loop, else press_button
                    if self.button_timer[column][row].seconds > 1:
                        #send clear loop if row 1 or 2
                        self.send_msg.clear_loop(button_num)
                    else:
                        self.send_msg.press_button(button_num)
                #turn into an active loop
                self.active_loops[button_num] = True
            if self.button_timer[column][row].seconds > 1 and button_num == 13:
                #open the option menu
                self.toggle_options()
            self.button_timer[column][row] = 0
            self.button_press_time[column][row] = 0

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
                            self.handle_button_press(column, row)
                else:
                    # Button is released
                    if self.debounce_count[column][row] > 0:
                        self.debounce_count[column][row] -= 1
                        if self.debounce_count[column][row] == 0:
                            self.handle_button_release(column, row)

            time.sleep(1/1000)

            # Reset button to init value
            GPIO.output(self.btnColumnPins[column], GPIO.HIGH)
            GPIO.output(self.ledColumnPins[column], GPIO.HIGH)

            for row in range(self.NUM_LED_ROWS):
                for color in range(self.NUM_COLORS):
                    GPIO.output(self.colorPins[row][color], GPIO.LOW)
