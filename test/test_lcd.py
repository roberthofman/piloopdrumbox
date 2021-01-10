import RPi_I2C_driver 
import time

while True:
    mylcd = RPi_I2C_driver.lcd()
    mylcd.lcd_display_string("Peet soldeer",1)
    mylcd.lcd_display_string("Robert kijkt",2)
    print("Text should show up")
    time.sleep(2)
    mylcd.lcd_clear()
    print("lcd should be cleared")
    time.sleep(2)
