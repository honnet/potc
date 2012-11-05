#!/usr/bin/python
import os
import sys
import time
import signal
import serial

# first in first out file in which the playback speed is requested
fifo_file = "/tmp/mplayer.fifo"
sound = sys.argv[1] # TODO generate name

# allow a clean exit using ctrl+c
def signal_handler(signal, frame):
    os.remove(fifo_file)
    os.system("killall mplayer")
    sys.exit(0)

# assume that there is only 1 arduino connected:
ser = serial.Serial('/dev/ttyACM0', 9600);
ser.isOpen()

if not os.path.exists(fifo_file):
    os.mkfifo(fifo_file)

# generate the player command:
command = "mplayer -af scaletempo -slave -input file=" + fifo_file + " "
# and execute it with the sound argumend
os.system( command + sound + "&")

MAX_VAL=100.0

while True:
    speed = int(ser.readline()) / MAX_VAL
    print " *** speed = ", speed, " ***\n"

    os.system("echo speed_set " + str(speed) + " > " + fifo_file)

    time.sleep(0.5)

