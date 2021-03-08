import urllib.request
import logging
import os
import time
from resources import RPi_I2C_driver

logging.basicConfig(filename="/home/pi/logs/gitlogs.log", filemode="w")
DIR = '/home/pi/piloopdrumbox' 
pulled = False

def connect():
    try:
        urllib.request.urlopen('http://google.com')
        return True
    except:
        return False

while not pulled:
    if connect():
        try:
            pull = os.system('git pull')
            if not pull == 'Already up to date.':
                lcd = RPi_I2C_driver.lcd()
                lcd.lcd_display_string("Reboot to update" ,1)
                lcd.lcd_display_string("new build ready", 2)
            pulled = True
        except Exception as e:
            logging.warning('Could not reach git: ' + str(e))
            pulled = True #avoid infinite loop
    else:
        time.sleep(1)