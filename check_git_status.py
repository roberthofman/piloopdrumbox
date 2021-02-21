import git
import urllib.request
import logging
import time
from resources import RPi_I2C_driver

logging.basicConfig(filename="/home/pi/logs/gitlogs.log", filemode="w")
DIR = '/home/pi/piloopdrumbox' 
pulled = False
lcd = RPi_I2C_driver.lcd()

def connect():
    try:
        urllib.request.urlopen('http://google.com')
        return True
    except:
        return False

while not pulled:
    if connect():
        try:
            g = git.cmd.Git(DIR)
            pull = g.pull()
            if not pull == 'Already up to date.':
                lcd.lcd_display_string("Reboot to update" ,1)
            pulled = True
        except Exception as e:
            logging.warning('Could not reach git: ' + str(e))
            pulled = True #avoid infinite loop
    else:
        time.sleep(10)