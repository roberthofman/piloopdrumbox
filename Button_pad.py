import RPi.GPIO as GPIO
import time
import RPi_I2C_driver

class Button_pad:
    def __init__(self):
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
        self.LED_buffer = self.create_matrix(False, self.NUM_LED_COLUMNS, self.NUM_LED_ROWS)
        self.btnColumnPins = [31, 33, 35, 37] # Pin numbers for columns (4)
        self.btnRowPins = [13, 15, 19, 21] # Pin numbers for rows (4)
        self.ledColumnPins = [32, 36, 38, 40] # Pin numbers for the LED's (columns) (4)
        self.colorPins = [[8, 18, 7], [10, 22, 23], [12, 24, 11], [16, 26, 29]] # 1: red 2: green 3: blue
        # Tracks how often a button is pressed
        self.debounce_count = self.create_matrix(0, self.NUM_BTN_COLUMNS, self.NUM_BTN_ROWS)
        self.button_timer = self.create_matrix(0, self.NUM_BTN_COLUMNS, self.NUM_BTN_ROWS)
        self.mylcd = RPi_I2C_driver.lcd()

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
        self.mylcd.lcd_display_string("De ultieme test", 1)
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
                print(row, color)
                GPIO.setup(self.colorPins[row][color], GPIO.OUT, initial=GPIO.LOW)

    def scan(self):
        """
        Function to be looped to scan button presses
        It quickly goes over all columns (current) and corresponding rows
        """
        for current in range(self.NUM_LED_COLUMNS):
            #Select current columns -> start without LED
            GPIO.output(self.btnColumnPins[current], GPIO.LOW)
            GPIO.output(self.ledColumnPins[current], GPIO.LOW)

            # output LED row values
            for row in range(self.NUM_LED_ROWS):
                val = self.LED_buffer[current][row]
                if(self.LED_buffer[current][row]):
                    GPIO.output(self.colorPins[row][val-1], GPIO.HIGH)

            time.sleep(1/1000)

            # read the button inputs
            for row in range(self.NUM_BTN_ROWS):
                val = GPIO.input(self.btnRowPins[row])
                if val == GPIO.LOW:
                    # Active low: val is low when btn is pressed
                    if self.debounce_count[current][row] < self.MAX_DEBOUNCE:
                        self.debounce_count[current][row] += 1
                        if self.debounce_count[current][row] == self.MAX_DEBOUNCE:
                            print("Key Down: " + str(current) + ", " + str(row))
                            #Send button press
                            self.LED_buffer[current][row] += 1
                            #text = "Pressed: " + str(row) + ":" + str(current)
                            #self.mylcd.lcd_display_string("test", 1)
                else:
                    # Button is released
                    if self.debounce_count[current][row] > 0:
                        self.debounce_count[current][row] -= 1
                        if self.debounce_count[current][row] == 0:
                            print("Key Up: " + str(current) + ", " + str(row))
                            #Send key release

            time.sleep(1/1000)

            # Reset button to init value
            GPIO.output(self.btnColumnPins[current], GPIO.HIGH)
            GPIO.output(self.ledColumnPins[current], GPIO.HIGH)

            for row in range(self.NUM_LED_ROWS):
                for color in range(self.NUM_COLORS):
                    GPIO.output(self.colorPins[row][color], GPIO.LOW)
