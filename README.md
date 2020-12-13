# piloopdrumbox
Raspberry pi + drum pad + loop station

## Update: 13 december 2020
<p>I got a Raspberry Pi this month to start my looper/drumbox project. I want to make a loop station including a drum box, which can connect to my keyboard and loop over both the drum box and the music input. Obviously, it should also include an output jack to output the loop. After a bit of searching, <a href="https://youtu.be/_nBK8sAl9nw">this</a> video turned out to be a nice inspiration, except for all the fancy synth buttons and effects, as those will come out of my keyboard anyway.</p> 

<p>As of now, I plan to combine Python with PureData (as the guy from the video shared all of his code, I think that would be a good start). PureData is a visual code language which is often used for building musical instruments/pedals/effects/etc, so that seems appropriate. </p>

<p>Together with Peter (luckily with a lot more technical knowledge than I have), we made a list of items we would definitely need:</p>
<ul>
 <li><a href="https://www.sparkfun.com/products/7835">Buttons (16) and a PCB</a> to link it to the Pi (same as in the video)</li> 
 <li>A <a href="https://www.thomann.de/nl/behringer_ucontrol_uca_222.htm">soundcard</a> which should work well with the Pi</li>
 <li>LED's, RGB for some shiny colors on the buttons</li>
 <li>An LCD, mainly to visualize the beat/tempo of the loop</li>
 <li>Cables, and diodes to connect it all and make the buttons work</li>
</ul>
<p>I got the basic technical parts from <a href="https://opencircuit.nl/">opencircuit</a>, which were super fast in delivering the first parts. Now we wait for the soundcard and the buttons to arrive and we can start to wire it all up. Finally, I would like to share the initial render for the box, also made by Peter (friends TU Delft ftw)! </p>
<p>
<img src="https://github.com/roberthofman/piloopdrumbox/blob/main/images/first_delivery.jpeg" align="left" height="40%" width="40%">
<img src="https://github.com/roberthofman/piloopdrumbox/blob/main/images/init_render.jpg" height="40%" width="40%">
<br><br><br><br><br><br><br>
</p>



# Usefull sources
* puredata: https://puredata.info/docs/raspberry-pi/
* Linux audio/rpi: https://wiki.linuxaudio.org/wiki/raspberrypi
  * e.g.: The RPi has a USB2.0 controller that apparently can cause issues with USB1.1 audio interfaces. The solution is to force the controller to use USB1.1 mode. You can do this by adding the following kernel parameter to your /boot/cmdline.txt file on your RPi: 
 
        dwc_otg.speed=1
