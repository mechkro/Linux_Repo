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
