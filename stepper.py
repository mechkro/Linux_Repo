from time import sleep
import RPi.GPIO as GPIO

########################################################################
#SOURCE - https://www.rototron.info/raspberry-pi-stepper-motor-tutorial/
########################################################################

"""
As always I recommend you start with a freshly wiped Pi using the latest version
of Raspbian to ensure you have all the necessary software.

The first Python example rotates a 48 SPR (steps per revolution) motor once
clockwise and then back counter-clockwise using the RPi.GPIO library.  
The DIR and STEP pins are set as outputs.  The DIR pin is set high for clockwise.
Then a for loop counts up to 48.  Each cycle toggles the STEP pin high for .0208
seconds and low for .0208 seconds.  The DIR pin is set low for counter-clockwise
and the for loop is repeated.
"""

DIR = 20   # Direction GPIO Pin
STEP = 21  # Step GPIO Pin
CW = 1     # Clockwise Rotation
CCW = 0    # Counterclockwise Rotation
SPR = 48   # Steps per Revolution (360 / 7.5)

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.output(DIR, CW)

step_count = SPR
delay = .0208

for x in range(step_count):
    GPIO.output(STEP, GPIO.HIGH)
    sleep(delay)
    GPIO.output(STEP, GPIO.LOW)
    sleep(delay)

sleep(.5)
GPIO.output(DIR, CCW)
for x in range(step_count):
    GPIO.output(STEP, GPIO.HIGH)
    sleep(delay)
    GPIO.output(STEP, GPIO.LOW)
    sleep(delay)

GPIO.cleanup()


"""
This code may result in motor vibration and jerky motion especially at low speeds.
One way to counter these result is with microstepping.  The following code snippet
is added to the code above.  The mode GPIO pins are set as outputs.  A dict holds
the appropriate values for each stepping format.  GPIO.output sets the mode to 1/32.
Note that step count is multiplied by 32 because each rotation now takes 32 times
as many cycles which results in more fluid motion.  The delay is divided by 32
to compensate for the extra steps.
"""

MODE = (14, 15, 18)   # Microstep Resolution GPIO Pins
GPIO.setup(MODE, GPIO.OUT)
RESOLUTION = {'Full': (0, 0, 0),
              'Half': (1, 0, 0),
              '1/4': (0, 1, 0),
              '1/8': (1, 1, 0),
              '1/16': (0, 0, 1),
              '1/32': (1, 0, 1)}
GPIO.output(MODE, RESOLUTION['1/32'])

step_count = SPR * 32
delay = .0208 / 32


"""
Please be aware that there are some significant downsides to microstepping.  
There is often a substantial loss of torque which can lead to a loss of accuracy.
See the resources section below for more information.

For the next example, a switch will be added to change direction. 
One terminal of the switch goes to GPIO16.  Another terminal goes to ground.

Schematic with switch

One issue with the last program is that it relies on the Python
sleep method for timing which is not very reliable.  For the next example,
I’ll use the PiGPIO library which provides hardware based PWM timing.

Before use, the PiGPIO daemon must be started using sudo pigpiod from a terminal.

>>$ sudo pigpiod


The first part of the following code is similar to the first example.
The syntax is modified for the PiGPIO library.  The set_PWM_dutycycle
method is used to set the PWM dutycycle.  This is the percentage of the pulse
that is high and low.  The value 128 sets it to 50%.  Therefore, the on and off
portions of the cycle are equal.  The set_PWM_frequency method sets the number 
of pulses per second.  The value 500 sets the frequency to 500 Hz.  An infinite
while loop checks the switch and toggles the direction appropriately.
"""

from time import sleep
import pigpio

DIR = 20     # Direction GPIO Pin
STEP = 21    # Step GPIO Pin
SWITCH = 16  # GPIO pin of switch

# Connect to pigpiod daemon
pi = pigpio.pi()

# Set up pins as an output
pi.set_mode(DIR, pigpio.OUTPUT)
pi.set_mode(STEP, pigpio.OUTPUT)

# Set up input switch
pi.set_mode(SWITCH, pigpio.INPUT)
pi.set_pull_up_down(SWITCH, pigpio.PUD_UP)

MODE = (14, 15, 18)   # Microstep Resolution GPIO Pins
RESOLUTION = {'Full': (0, 0, 0),
              'Half': (1, 0, 0),
              '1/4': (0, 1, 0),
              '1/8': (1, 1, 0),
              '1/16': (0, 0, 1),
              '1/32': (1, 0, 1)}
for i in range(3):
    pi.write(MODE[i], RESOLUTION['Full'][i])

# Set duty cycle and frequency
pi.set_PWM_dutycycle(STEP, 128)  # PWM 1/2 On 1/2 Off
pi.set_PWM_frequency(STEP, 500)  # 500 pulses per second

try:
    while True:
        pi.write(DIR, pi.read(SWITCH))  # Set direction
        sleep(.1)

except KeyboardInterrupt:
    print ("\nCtrl-C pressed.  Stopping PIGPIO and exiting...")
finally:
    pi.set_PWM_dutycycle(STEP, 0)  # PWM off
    pi.stop()
    
"""
One caveat when using the PiGPIO set_PWM_frequency method is it
is limited to specific frequency values per sample rate as specified in the following table.
"""

