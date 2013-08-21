#!/usr/bin/python
import os
import sys
import time
import serial
import random
import glob

""" TODO:
- adapt to real sound folder name
- replace os.system by write(fifo)
"""

#################################### init ####################################
# first in first out file in which the playback speed is requested
fifo_file = "/tmp/mplayer.fifo"
play_command = "mplayer -af scaletempo -slave -input file=" + fifo_file + " "
logfile = "log.txt"
out = open(logfile, 'w')

if not os.path.exists(fifo_file):
    try:
        print "mkfifo &"
        os.system("mkfifo " + fifo_file + " &")
    except :
        print "mkfifo bis"
        os.mkfifo(fifo_file)

# allow a clean exit using ctrl+c
def signal_handler(signal, frame):
    os.system("echo quit > " + fifo_file)
    os.remove(fifo_file)
    sys.exit(0)

try:
    ser = serial.Serial('/dev/ttyACM0', 9600);
except:
    ser = serial.Serial('/dev/ttyACM1', 9600);

SOUND_ROOT  = "sounds" # TODO: adapt to real folder name
SLOW_SOUNDS = glob.glob( os.path.join(SOUND_ROOT, 'slow/*') )
FAST_SOUNDS = glob.glob( os.path.join(SOUND_ROOT, 'fast/*') )

#################################### loop ####################################
avg_heartbeat = 100.0
speed = 0.0
prev_cmd = ''
playing = False

def fade_out():
    duration = 1.5 # sec
    steps = 5    # percentage
    for volume in range(100, 0, -steps):
        print "*** fading out, volume =", volume
        os.system("echo volume " + str(volume) + " 1 > " + fifo_file + "&")
        time.sleep(duration * steps / 100.0)
    os.system("echo 'quit' > " + fifo_file)
    playing = False


while True:
    rx = ser.readline()
    print "*** RX:", rx

    if not rx:
        continue
    cmd = rx[0]
    # B/E: begin/end timestamp
    # V: voltage
    # H: heartbeat

    # SUGGESTION:
    # B => new speed too
    # E => voltage too !

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    if cmd == 'B':
        print "*** beginning..."
        timestamp = time.strftime('%b %d %Y %H:%M:%S',time.localtime())
        out.write("B: " + timestamp + '\n')

    elif cmd == 'E':
        print "*** ending..."
        timestamp = time.strftime('%b %d %Y %H:%M:%S',time.localtime())
        out.write("E: " + timestamp + '\n')
        fade_out()

    elif cmd == 'V':
        print "*** voltage =", rx[1:]
        out.write("V: " + rx[1:])

    elif cmd == 'H':
        print "*** speed =", speed
        out.write("H: " + rx[1:])
        try:
            speed = int(rx[1:]) / avg_heartbeat
        except:
            continue
        if playing == True:
            os.system("echo speed_set " + str(speed) + " > " + fifo_file)

    else:
        continue

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    if prev_cmd == 'B' and speed > 0.5:
        if speed < 1:
            sound = random.choice(SLOW_SOUNDS)
        elif speed < 2.6:
            sound = random.choice(FAST_SOUNDS)
        else:
            continue
        os.system(play_command + sound + "&")
        playing = True

    prev_cmd = cmd
    time.sleep(0.5)

