#!/usr/bin/python3
import serial
import time
import glob
import os
import json

# Not an immediate thing to read
SLEEP_TIME=.3

def setup(): 
    # Sets up the serial interface

    # Usually USB0 but sometimes not so grab newest
    serials = glob.glob('/dev/ttyUSB*')
    if len(serials) > 0:
        serialfile = serials[-1]
    else:
        print("No /dev/ttyUSBX found")
        exit -1

    initcom = [b'ate0\r', b'atl1\r', b'ath0\r', b'ats1\r', b'atal\r', b'atsp0\r']
    ser = serial.Serial(serialfile, 38400, timeout=1)

    # Sets up the connection for simplicity of the script
    for i in initcom:
        ser.write(i)
        time.sleep(SLEEP_TIME)
        ser.read(ser.in_waiting) #CHANGE

    return ([], ser)

def curtime():
    # Timestamp return
    f = time.ctime(time.time()).split(' ')
    f.remove('')
    return ' '.join(f[1:])

def sampledata(samplist, ser):
    # Collect all the data we care about
    samptime = curtime()
    #sampdict[samptime] = {}

    # Each hex call, data translation and title for each value
    avgper = lambda val: (int(val[2], 16) + int(val[5], 16)) / (2 * 2.55)
    collection = [(b'0104\r', avgper, 'Engine Load'),
                  (b'0105\r', lambda val: (int(val[2], 16) + int(val[5], 16) - 80) / 2, 'Coolant Temp'),
                  (b'010c\r', lambda val: ((int(value[2], 16) + int(value[6], 16)) * 256 + int(value[3], 16) + int(value[7], 16))/8, 'RPM'),
                  (b'010d\r', lambda val: (int(val[2], 16) + int(val[5], 16)) / 2, 'Vehicle Speed'),
                  (b'0111\r', avgper, 'Throttle Position'),
                  (b'0110\r', lambda val: (int(val[2], 16) * 256 + int(val[3], 16))/100, 'MAF')]

    if len(samplist) == 1:
        samplist.append([samptime])
    #elif samplist[-1].split(':')[0][-2:] == '23' and samplist[-1].split(':')[1] == '59' and int(samplist[-1].split(':')[2][0:2]) > 58:
    #    samplist.append([samptime])
    else:
        samplist.append([samptime.split(' ')[2]])

    for i in collection:
        ser.write(i[0])
        time.sleep(SLEEP_TIME)
        value = ser.read(ser.in_waiting).decode('unicode_escape').split() #CHANGE
        if len(value) >= 3:
            # To make sure theres no error
            if i[2] == 'MAF':
                mpgnum = samplist[-1][4] * 7.718 / i[1](value)
                if mpgnum > 99.9:
                    mpgnum = 99.9
                samplist[-1].append(mpgnum)
            else:
                samplist[-1].append(i[1](value))
            #sampdict[samptime][i[2]] = i[1](value)

    return samplist

if __name__ == '__main__':
    samplist, ser = setup()
    i = 0
    samplist.append(['Time', 'Engine Load', 'Coolant Temp', 'RPM', 'Vehicle Speed', 'Throttle Position', 'MPG'])

    ser.write(b'010c\r')
    ser.read(ser.in_waiting)
    time.sleep(1)
    sampledata(samplist, ser)
    print("Data sampling once a second...")

    while True:
        SLEEP_TIME = .1
        data = open("data" + str(i) + ".txt", "w")
        f = sampledata(samplist, ser)
        data.write(json.dumps(f))
        data.close()
        time.sleep(.3)
        i = 1 - i

