#!/usr/bin/python
import os
import sys
import time
import signal
import serial

""" TODO:
- pseudo random music selection
- replace os.system by write(fifo)
- write voltages & timestamp in log file
"""
#################################### init ####################################
# first in first out file in which the playback speed is requested
fifo_file = "/tmp/mplayer.fifo"
sound = sys.argv[1] # TODO generate name
logfile = "logfile"

if not os.path.exists(fifo_file):
    os.mkfifo(fifo_file)
play_command = "mplayer -af scaletempo -slave -input file=" + fifo_file + " "

# allow a clean exit using ctrl+c
def signal_handler(signal, frame):
    os.system("echo quit > " + fifo_file)
    os.remove(fifo_file)
    sys.exit(0)

# assume that there is only 1 arduino connected:
ser = serial.Serial('/dev/ttyACM0', 9600);
ser.isOpen()

#################################### loop ####################################
avg_heartbeat = 100.0
fade_out == False
speed = 0.0
volume = 100

while True:
    rx = ser.readline()
    if not rx:
        break
    cmd = rx[0]
    # B: begin timestamp
    # E: end timestamp
    # V: voltage
    # H: heartbeat

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    print " === debug === "

    if cmd == 'B':
        print "beginning..."
        speed = 0.0             # wait to get the speed
        # TODO: log time

    elif cmd == 'E':
        print "ending..."
        fade_out == True        # will stop when
        # TODO: log time

    elif cmd == 'V':
        print "voltage = " + rx[1:]
        # TODO: log voltage

    elif cmd == 'H':
        speed = int(rx[1:]) / avg_heartbeat
        print "speed = " + speed
        os.system("echo speed_set " + str(speed) + " > " + fifo_file)

    else:
        break

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    if speed > 0.5:
        # TODO: call function to select sound
        os.system(play_command + sound + "&")

    if fade_out == True:
        if volume > 0:
            os.system("echo volume_set " + str(volume) + " > " + fifo_file)
            volume = volume - 25
        else:
            os.system("echo quit > " + fifo_file)
            fade_out == False


    time.sleep(0.25)

