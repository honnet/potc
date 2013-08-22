#!/usr/bin/python
import os
import sys
import time
import serial
import random
import glob

""" TODO:
- adapt to real sound folder name
- make the serial choice more generic !!
"""

#################################### init ####################################
# sound files:
SOUND_ROOT  = "sounds" # TODO: adapt to real folder name
SLOW_SOUNDS = glob.glob( os.path.join(SOUND_ROOT, 'slow/*') )
FAST_SOUNDS = glob.glob( os.path.join(SOUND_ROOT, 'fast/*') )

# in this file we'll log time stamps, voltages and heartbeats:
logfile = "log.txt"
out = open(logfile, 'w')

# first in first out file in which the playback speed is requested
fifo_file = "/tmp/mplayer.fifo"

# create a fresh FIFO file:
if os.path.exists(fifo_file):
    os.remove(fifo_file)
    print "old FIFO removed"
os.mkfifo(fifo_file)
print "FIFO created"

# open serial port to listen to the arduino:
try:
    ser = serial.Serial('/dev/ttyACM0', 9600);
except:
    ser = serial.Serial('/dev/ttyACM1', 9600); # TODO make more generic !!

################################# funktions ##################################
# start the sound and listen to speed modulation requests
def play(speed):
    if speed < 0.5 or speed > 2.6:
        return False
    elif speed < 1:
        sound = random.choice(SLOW_SOUNDS)
    else: #speed < 2.6:
        sound = random.choice(FAST_SOUNDS)

    command = "mplayer -af scaletempo -slave -input file="
    command = command + fifo_file + " " + sound + "&"
    print "***", command

    os.system(command)
    set_volume(100)
    set_speed(speed)
    return True

# playback volume modulation request:
def set_volume(volume):
    command = "echo volume " + str(volume) + " 1 > " + fifo_file + "&"
    print "***", command
    os.system(command)

# playback speed modulation request:
def set_speed(speed):
    command = "echo speed_set " + str(speed) + " > " + fifo_file
    print "***", command
    os.system(command )

# decrease the volume at the end of a track:
def fade_out():
    duration = 1.5 # sec
    steps = 5    # percentage
    for volume in range(100, 0, -steps):
        set_volume(volume)
        time.sleep(duration * steps / 100.0)
    os.system("echo 'quit' > " + fifo_file)
    os.system("echo volume 100 1 > " + fifo_file + "&")
    return False # = not playing anymore

# allow a clean exit using ctrl+c
def signal_handler(signal, frame):
    os.system("echo quit > " + fifo_file)
    os.remove(fifo_file)
    sys.exit(0)

# wait for the Begin instruction:
def wait_to_begin():
    cmd = ""
    while cmd != 'B':
        rx = ser.readline()
        print "...waiting: RX:", rx[:-1] # remove the final '\n'
        cmd = rx[0]
    print "Starting !"
    return cmd

# to write in logfile
def get_timestamp():
    return time.strftime('%b %d %Y %H:%M:%S',time.localtime()) + '\n'

#################################### loop ####################################
avg_heartbeat = 100.0
speed = 0.0
isPlaying = False

prev_cmd = wait_to_begin()

while True:
    rx = ser.readline()
    print "*** RX:", rx[:-1] # remove the final '\n'

    if not rx:
        continue
    cmd = rx[0]
    # B/E: begin/end timestamp
    # V: voltage
    # H: heartbeat

    # SUGGESTION:
    # B => new speed too
    # E => voltage too !

    if cmd == 'B':
        print "*** beginning..."
        out.write("B: " + get_timestamp())

    elif cmd == 'E':
        print "*** ending..."
        out.write("E: " + get_timestamp())
        if isPlaying:
            isPlaying = fade_out()

    elif cmd == 'V':
        print "*** voltage =", rx[1:]
        out.write("V: " + rx[1:])

    elif cmd == 'H':
        out.write("H: " + rx[1:])
        try:
            speed = int(rx[1:]) / avg_heartbeat
        except:
            continue
        print "*** speed =", speed

        if prev_cmd == 'B':
            print "*** prev_cmd = 'B'"
            isPlaying = play(speed)
        else:
            print "*** prev_cmd =", prev_cmd
            set_speed(speed)

    else:
        continue

    prev_cmd = cmd
    time.sleep(0.5)

