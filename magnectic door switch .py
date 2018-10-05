import RPi.GPIO as GPIO
import time
import sys
import signal 
GPIO.setmode(GPIO.BCM)

#  Define Pins
LEDG_PIN_VIN = 18
LEDR_PIN_VIN = 12
MAGNETICDOORSWITCH3V3_PIN_SIG = 4

# Initially we don't know if the door sensor is open or closed...
isOpen = None
aldOpen = None

# Clean up when the user exits with keyboard interrupt
def cleanupLights(signal, frame): 
    GPIO.output(LEDR_PIN_VIN , False) 
    GPIO.output(LEDG_PIN_VIN , False) 
    GPIO.cleanup() 
    sys.exit(0) 

# Set up the door sensor pin.
GPIO.setup(MAGNETICDOORSWITCH3V3_PIN_SIG , GPIO.IN, pull_up_down = GPIO.PUD_UP)
 
# Set up the light pins.
GPIO.setup(LEDR_PIN_VIN , GPIO.OUT)
GPIO.setup(LEDG_PIN_VIN , GPIO.OUT) 

# Make sure all lights are off.
GPIO.output(LEDR_PIN_VIN , False)
GPIO.output(LEDG_PIN_VIN , False)

# Set the cleanup handler for when user hits Ctrl-C to exit
signal.signal(signal.SIGINT, cleanupLights) 

while True: 
    aldOpen = isOpen 
    isOpen = GPIO.input(MAGNETICDOORSWITCH3V3_PIN_SIG)  
    if (isOpen and (isOpen != aldOpen)):  
        print("Space is unoccupied!")  
        GPIO.output(LEDR_PIN_VIN , False)  
        GPIO.output(LEDG_PIN_VIN , True) 
    elif (isOpen != aldOpen):  
        print("Space is occupied!")  
        GPIO.output(LEDG_PIN_VIN , False)  
        GPIO.output(LEDR_PIN_VIN , True)  
    time.sleep(0.1)