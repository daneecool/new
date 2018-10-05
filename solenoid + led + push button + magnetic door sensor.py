import RPi.GPIO as GPIO
import time
import sys
import signal 
GPIO.setmode(GPIO.BCM)

# Define Pins
PULLPUSHSOLENOID_PIN_SIG = 27
LEDG_PIN_VIN = 18
LEDR_PIN_VIN = 12
MAGNETICDOORSWITCH3V3_PIN_SIG = 4
PUSHBUTTON_PIN = 17

# Initially we don't know if the door sensor is open or closed...
isOpen = None
aldOpen = None

# Set up the light pins.
GPIO.setup(LEDR_PIN_VIN , GPIO.OUT)
GPIO.setup(LEDG_PIN_VIN , GPIO.OUT)

# Set up the door sensor pin + pushbutton 
GPIO.setup(MAGNETICDOORSWITCH3V3_PIN_SIG , GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(PUSHBUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Set up the solenoid pin.
GPIO.setup(PULLPUSHSOLENOID_PIN_SIG , GPIO.OUT, HIGH)
GPIO.setup(PULLPUSHSOLENOID_PIN_SIG , GPIO.OUT, LOW)

# Make sure all lights are off.
GPIO.output(LEDR_PIN_VIN , False)
GPIO.output(LEDG_PIN_VIN , False)

# Make sure the solenoid is in rest state
GPIO.output(PULLPUSHSOLENOID_PIN_SIG , False)

# Set the cleanup handler for when user hits Ctrl-C to exit
signal.signal(signal.SIGINT, cleanupLights) 

while True:
    input_state = GPIO.input(PULLPUSHSOLENOID_PIN_SIG , GPIO.OUT , HIGH)  
    if (isOpen and (isOpen != aldOpen)):
        GPIO.output(LEDR_PIN_VIN , False)
        GPIO.output(LEDG_PIN_VIN , True)
   # input_state = GPIO.input(PULLPUSHSOLENOID_PIN_SIG , GPIO.OUT , LOW)		
    elif (isOpen != aldOpen):
        GPIO.output(LEDG_PIN_VIN , False)
        GPIO.output(LEDR_PIN_VIN , True)
    else:
        input_state = GPIO.input(PULLPUSHSOLENOID_PIN_SIG , GPIO.OUT , HIGH)
        print("Push button is pressed!, door unlcoked")
        GPIO.output(LEDG_PIN_VIN , True)
        GPIO.output(LEDR_PIN_VIN , False)
        time.sleep(0.1)
