# -*- coding: utf-8 -*-
import binascii
import nfc
import time
import datetime
from colorama import init
from colorama import Fore, Back, Style
from threading import Thread, Timer

#print(Fore.RED + 'some red text')
#print(Style.DIM + 'and in dim text')
#print(Style.RESET_ALL)
#print('back to normal now')

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
#file = ["/home/pi/Desktop/nfcpy/add on codex/idm.txt"]


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
        file = open("idm.txt" , "r")
      #  print(file.read())
          #  print("idm is" + idm)
          #  print("id is" + id)
        store = ""
        try:
           with open("idm.txt", "r") as file:
               for line in file:
                   if (idm == line):
                       store = ("Authorised Personnel")
                       print(Fore.MAGENTA + "Authorised Personnel")
                       # call in the all the functions #
                       if (idm == "010102122b128d28"):
                           print ("Daniel")
                       elif (idm == "010108016e181013"):
                           print ("Edwin")
                       now = datetime.datetime.now()
                       print(Fore.GREEN + now.strftime("%Y-%m-%d %H:%M:%S"))
                       break
                   else:
                       store = ("Denied Personnel") 
       # except Expection as ValueError:
          #  print ("Access Denied")
        finally:
           # now = datetime.datetime.now()
           # print(Fore.GREEN)
           # print (now.strftime("%Y-%m-%d %H:%M:%S"))
            print (Fore.RED)
            print(Style.RESET_ALL)
            if store == ("Denied Personnel"):
                print store
            file.close()
    time.sleep(TIME_wait)
    #end if

    clf.close()

#end while