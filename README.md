# piloopdrumbox
Raspberry pi + drum pad + loop station

# Usefull sources
* puredata: https://puredata.info/docs/raspberry-pi/
* Linux audio/rpi: https://wiki.linuxaudio.org/wiki/raspberrypi
  * e.g.: The RPi has a USB2.0 controller that apparently can cause issues with USB1.1 audio interfaces. The solution is to force the controller to use USB1.1 mode. You can do this by adding the following kernel parameter to your /boot/cmdline.txt file on your RPi: 
 
        dwc_otg.speed=1
