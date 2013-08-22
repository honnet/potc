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
MAX_VOL = 256

# in this file we'll log time stamps, voltages and heartbeats:
logfile = "log.txt"
out = open(logfile, 'w')

# where the playback speed is requested
host = "localhost"
port = "3333"

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

    command = "cvlc --extraintf rc --rc-host "
    command = command + host + ":" + port + " " + sound + "&"
    print command
    os.system(command)

    set_volume(MAX_VOL)
    set_speed(speed)
    return True

# playback volume modulation request:
def set_volume(volume):
    command = "echo volume " + str(volume) + " | telnet " + host + " " + port + "&"
    print command
    os.system(command)

# playback speed modulation request:
def set_speed(speed):
    command = "echo rate " + str(speed) + " | telnet " + host + " " + port + "&"
    print command
    os.system(command)

# quit the player
def quit():
    command = "killall vlc"
    print command
    print os.system(command)

# decrease the volume at the end of a track:
def fade_out():
    duration = 1.0 # sec, need a float!
    step = 8
    for volume in range(MAX_VOL, 0, -step):
        set_volume(volume)
        time.sleep(duration * step / MAX_VOL)
    set_volume(MAX_VOL)
    quit()
    return False # = not playing anymore

# allow a clean exit using ctrl+c
def signal_handler(signal, frame):
    quit()
    sys.exit(0)

# wait for the Begin instruction:
def wait_to_begin():
    cmd = ""
    while cmd != 'B':
        rx = ser.readline()
        print " *** RX:", rx[:-1] # remove the final '\n'
        cmd = rx[0]
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
    print " *** RX:", rx[:-1] # remove the final '\n'

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
        out.write("B: " + get_timestamp())

    elif cmd == 'E':
        out.write("E: " + get_timestamp())
        if isPlaying:
            isPlaying = fade_out()

    elif cmd == 'V':
        out.write("V: " + rx[1:])

    elif cmd == 'H':
        out.write("H: " + rx[1:])
        try:
            speed = int(rx[1:]) / avg_heartbeat
        except:
            continue

        if prev_cmd == 'B':
            isPlaying = play(speed)
        else:
            set_speed(speed)

    else:
        continue

    prev_cmd = cmd
    time.sleep(0.5)

