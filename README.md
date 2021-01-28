# Pi-loop-drumbox!
Welcome to my repo for the ultimate Raspberry pi + drum pad + loop station.  
For updates on the build log see the [wiki](https://github.com/roberthofman/piloopdrumbox/wiki).   

## Install requirements
### PureData
To install puredata: `sudo apt-get install puredata`.  
No extensions are required.  
In order to get the soundcard working and avoiding the  
`ALSA input error (snd_pcm_open): No such file or directory`  
error, you need to make sure that the USB-soundcard is the only audio device and has index 0. Disable the Pi's jack input via this file: `/etc/modprobe.d/alsa-blacklist.conf` and add the following line: `blacklist snd_bcm2835`.   
Then, reconfigure the index of audio devices: `/lib/modprobe.d/aliases.conf` and change the index of `options snd-usb-audio index=0`.  
Check if the only audio device is the USB-soundcard through `cat /proc/asound/cards`, which should give the index 0 to the soundcard. 

### Python
The Python code is based on Python3. 
Make sure you have installed the packages to work with GPIO pins:  
`sudo apt-get install python-rpi.gpio`  
You'll need a couple of python libraries:   
* python-rpi.gpio
* i2c–tools
* smbus

You'll need to wire up the GPIO pins to the correct pin numbers, which are coded in `Button_pad.py`. I followed [this](https://learn.sparkfun.com/tutorials/button-pad-hookup-guide?_ga=2.228180057.552363603.1611515792-1928249015.1605036658) guide.  
I used an I2C driver by [DenisFromHR](https://gist.github.com/DenisFromHR/cc863375a6e19dce359d). 

### Drum sounds
I added a couple drum sounds. You can add additional .wav files following the number sintax in the folder. 
