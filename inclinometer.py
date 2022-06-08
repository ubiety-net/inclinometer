#!/usr/bin/env python2

from gps import *
import math
import serial
import threading

# GPSD_SOCKET="/usr/local/var/gpsd.sock" PATH=$PATH:/usr/local/sbin /usr/local/opt/gpsd/sbin/gpsdctl add /dev/tty.usbserial-1440
# brew services restart gpsd
# /usr/local/opt/gpsd/sbin/gpsd -N -F /usr/local/var/gpsd.sock
# to get raw sentences: gpspipe -r
# to get gpsd output: gpspipe -w

gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)
port = '/dev/cu.usbmodem00000000001A1'
array_length = 10
values = []
run_threads = True
gps_lat = '0'
gps_lon = '0'
gps_time = '0'


def setup(usbacc):
    print 'setup'

def gpsd_callback():
    global gps_lat
    global gps_lon
    global gps_time

    report = gpsd.next() #
    if report['class'] == 'TPV':
        # print 'latitude\tlongitude\ttime utc\t\t\taltitude\tepv\tept\tspeed\tclimb'
        # print  getattr(report,'lat',0.0),"\t",
        # print  getattr(report,'lon',0.0),"\t",
        # print getattr(report,'time',''),"\t",
        # print  getattr(report,'alt','nan'),"\t\t",
        # print  getattr(report,'epv','nan'),"\t",
        # print  getattr(report,'ept','nan'),"\t",
        # print  getattr(report,'speed','nan'),"\t",
        # print getattr(report,'climb','nan'),"\t"
        gps_lat = getattr(report,'lat',0.0)
        gps_lon = getattr(report,'lon',0.0)
        gps_time = getattr(report,'time','')

    if run_threads:
        threading.Timer(1, gpsd_callback).start()

def timer_callback():
    x = 0
    y = 0
    z = 0
    length = len(values)
    for value in values:
        sub_values = value.split(',')
        x += int(sub_values[0])
        y += int(sub_values[1])
        z += int(sub_values[2])

    if x != 0 and y != 0 and z != 0:
        roll = math.atan2(y, z) * 57.3;
        pitch = math.atan2(-x , math.sqrt((y * y) + (z * z))) * 57.3;
        print '{},{},{},{},{}'.format(gps_time, gps_lat, gps_lon, int(roll), int(pitch)) 

    if run_threads:
        threading.Timer(1, timer_callback).start()

def main():
    global run_threads

    try:
        usbacc = serial.Serial(port)
        setup(usbacc)
        gpsd_callback()
        timer_callback()

        while True:
            values.append(usbacc.readline().strip())
            while len(values) > array_length:
                values.pop(0)    
    except (KeyboardInterrupt, SystemExit):
        run_threads = False
        print "Ctrl-C pressed, exiting"
    
    usbacc.close()

if __name__ == "__main__":
    main()
