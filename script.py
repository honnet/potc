#!/usr/bin/python
import os
import sys
import time
import serial
import random
import glob

#################################### init ####################################
# sound files:
SOUND_ROOT = os.environ['HOME'] + "/POTC_music/songs/"
LOW_SOUNDS = glob.glob( os.path.join(SOUND_ROOT, 'low/*') )
MIDLOW_SOUNDS = glob.glob( os.path.join(SOUND_ROOT, 'midlow/*') )
MIDHIGH_SOUNDS = glob.glob( os.path.join(SOUND_ROOT, 'midhigh/*') )
HIGH_SOUNDS = glob.glob( os.path.join(SOUND_ROOT, 'high/*') )
MAX_VOL = 100

# in this file we'll log time stamps, voltages and heartbeats:
logfile = "log.txt"
out = open(logfile, 'w')

# first in first out file in which the playback speed is requested
fifo_file = "/tmp/mplayer.fifo"

# create a fresh FIFO file:
if os.path.exists(fifo_file):
    os.remove(fifo_file)
os.mkfifo(fifo_file)

# open serial port to listen to the arduino:
try:
    ser = serial.Serial('/dev/ttyACM0', 9600);
except:
    ser = serial.Serial('/dev/ttyACM1', 9600); # TODO make more generic !!

################################# funktions ##################################
# start the sound and listen to speed modulation requests
def play(heart_bpm):
    quit() # kill a potential survivor
    if heart_bpm < 50 or heart_bpm > 200:
        return False
    elif heart_bpm < 100:
        sound_path = random.choice(LOW_SOUNDS)
    elif heart_bpm < 120:
        sound_path = random.choice(MIDLOW_SOUNDS)
    elif heart_bpm < 140:
        sound_path = random.choice(MIDHIGH_SOUNDS)
    else: #heart_bpm < 200:
        sound_path = random.choice(HIGH_SOUNDS)

    command = "mplayer -af scaletempo -slave -input file="
    command = command + fifo_file + " " + sound_path + "&"
    print command
    os.system(command)
    set_volume(MAX_VOL)

    sound_file = os.path.basename(sound_path)
    try:
        track_bpm = float(sound_file[:3])
        return track_bpm
    except:
        return 0

# playback volume modulation request:
def set_volume(volume):
    procTrue = checkProc()
    if procTrue > 0:
        command = "echo volume " + str(volume) + " 1 > " + fifo_file

        print command
        os.system(command)

# playback speed modulation request:
def set_speed(speed):
    procTrue = checkProc()
    if procTrue > 0:
        command = "echo speed_set " + str(speed) + " > " + fifo_file
        print command
        os.system(command)

# quit the player
def quit():
    command = "killall mplayer"
    print command
    print os.system(command)

# decrease the volume at the end of a track:
def fade_out():
    duration = 1.0 # sec, need a float!
    step = 5
    for volume in range(MAX_VOL, 0, -step):
        set_volume(volume)
        time.sleep(duration * step / MAX_VOL)
    set_volume(MAX_VOL)
    quit()
    return 0 # not playing anymore

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

# check if mplayer is still running
def checkProc():
    processname = 'mplayer'
    tmp = os.popen("ps -Af").read()
    proccount = tmp.count(processname)
    return proccount

#################################### loop ####################################
track_bpm = 0
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

    if cmd == 'B':
        out.write("B: " + get_timestamp())

    elif cmd == 'E':
        out.write("E: " + get_timestamp())
        if track_bpm != 0:
            track_bpm = fade_out()

    elif cmd == 'V':
        out.write("V: " + rx[1:])

    elif cmd == 'H':
        out.write("H: " + rx[1:])
        try:
            heart_bpm = float(rx[1:])
        except:
            continue
        if prev_cmd == 'B':
            track_bpm = play(heart_bpm)
        if track_bpm != 0:
            set_speed(heart_bpm / track_bpm)

    else:
        continue

    prev_cmd = cmd
    time.sleep(0.5)

