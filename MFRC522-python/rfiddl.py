#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal
import time
import pymysql

#sett mysql access
con = pymysql.connect(db="absen", user="user", passwd="user",host="10.10.0.163",port=3306,autocommit=True)

print ("connect successful!!")

# Card Register

adminid = '1711792300'
lockcard = '895212290'
#GPIO setup

digitalPIN = 8
GPIO.setmode(GPIO.BOARD)
GPIO.setup(digitalPIN, GPIO.OUT)

def lockdoor():
    GPIO.output(8, GPIO.HIGH)
    return;
def opendoor():
    GPIO.output(8, GPIO.LOW)
    return;

continue_reading = True

def end_read(signal,frame):
    global continue_reading
    print("Ctrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

while continue_reading:

# Scan for cards
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print("Card detected")

    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        # Print UID
        UIDcode = str(uid[0])+str(uid[1])+str(uid[2])+str(uid[3])
        print(UIDcode)

        # Control door lock
        statusFile = open('/home/pi/virtualenv/rfid/MFRC522-python/status.txt', 'r')
        locked = statusFile.readline()
        statusFile.close()
        statusFile2 = open('/home/pi/virtualenv/rfid/MFRC522-python/status2.txt', 'r')
        openTrigSwitch = statusFile2.readline()
        statusFile2.close()

        if UIDcode == adminid:
            adminpriv = 1
        else:
            adminpriv = 0

        if UIDcode == adminid or UIDcode == lisacard or UIDcode == colincard:
            if locked == '0' or adminpriv == 1:
                opendoor()
                print("Door open")
                time.sleep(3)
                lockdoor()
                print("Finished")
            else:
                print("Door locked")
        elif UIDcode == lockcard:
            counter = 0
            if locked == '0':
                while counter != 5:
                    opendoor()
                    time.sleep(0.05)
                    lockdoor()
                    time.sleep(0.05)
                    counter += 1
                locked = 1
                time.sleep(3)
            else:
                while counter != 2:
                    lockdoor()
                    time.sleep(0.5)
                    opendoor()
                    time.sleep(0.05)
                    counter += 1
                locked = 0
                time.sleep(3)

            fh = open('status.txt', 'w')
            fh.write(str(locked))
            fh.close()

        else:
            print("Unrecognised Card")
