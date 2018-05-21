#!/usr/bin/env python
 
import sys
import time
import RPi.GPIO as io
 
io.setmode(io.BCM)
# Pin 23 on the board
PIR_PIN = 23  
 
def main():
    io.setup(PIR_PIN, io.IN)
    last_motion_time = time.time()
 
    while True:
        if io.input(PIR_PIN):
            last_motion_time = time.time()
            sys.stdout.flush()
            print last_motion_time
            time.sleep(1)
    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        io.cleanup()



