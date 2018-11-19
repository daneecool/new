# -*- coding: utf-8 -*-
import binascii
import nfc
import time
import RPi.GPIO as GPIO
import time
import sys
import signal 
from threading import Thread, Timer

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

# 1s cycle of standby 
TIME_cycle = 1.0
# Reaction Interval Per Second
TIME_interval = 0.2
# Seconds to be invalidated from touching until the next standby is started
TIME_wait = 1.0

# Preparation for NFC connection request
# Set by 212F (FeliCa)
target_req_suica = nfc.clf.RemoteTarget("212F")
# 0003(Nimoca)
target_req_suica.sensf_req = bytearray.fromhex("0000030000")

print('...waiting for card...')

# add-on card ids
# list = ("Daniel , Edwin")
acceptedIds = ["010102122b128d28", "010108016e181013"]

while True:
    # Connected to NFC reader connected to USB and instantiated
    clf = nfc.ContactlessFrontend('usb')
    # Awaiting for Nimoca
    # clf.sense ([Remote target], [Search frequency], [Search interval])
    target_res = clf.sense(target_req_suica, iterations=int(TIME_cycle//TIME_interval)+1 , interval=TIME_interval)

    if target_res != None:
        
        #tag = nfc.tag.tt3.Type3Tag(clf, target_res)
        #Something changed in specifications? It moved if it was ↓
        tag = nfc.tag.activate_tt3(clf, target_res)
        tag.sys = 3

        #Extract IDm
        idm = binascii.hexlify(tag.idm)
        for id in acceptedIds:
          #  print("idm is" + idm)
          #  print("id is" + id)
            if (idm == id):
                print("Authorised Personnel")
            elif (idm == "010102122b128d28"):
                print ("Daniel")
            elif (idm == "010108016e181013"):
                print ("Edwin")
            else:
                print ("Access Denied")
                aldOpen = isOpen 
                isOpen = GPIO.input(MAGNETICDOORSWITCH3V3_PIN_SIG)  
                if (isOpen and (isOpen != aldOpen)):  
                    print("Open!")  
                    GPIO.output(LEDR_PIN_VIN , True)  
                    GPIO.output(LEDG_PIN_VIN , False) 
                elif (isOpen != aldOpen):  
                    print("Lock!")  
                    GPIO.output(LEDG_PIN_VIN , True)  
                    GPIO.output(LEDR_PIN_VIN , False)  
            time.sleep(0.1)
         
        time.sleep(TIME_wait)
    #end if

    clf.close()

#end while


