"""

"""

###############################################################################
# Imports
###############################################################################

import os
from math import cos, sin, pi, floor

# Multi Threading
from threading import Thread
from threading import Lock
from threading import Event

#
import logging
import time
import sys

# Open Computer Vision
import cv2

from adafruit_rplidar import RPLidar

###############################################################################
# Scan Capture
###############################################################################

class lidar(Thread):
    """
    This thread continually captures from SlamTec LIDARa
    """

    # Initialize the Camera Thread
    # Opens Capture Device and Sets Capture Properties
    def __init__(self, camera_num: int = 0, res: (int, int) = None,            # width, height
                 exposure: float = None):
        # initialize 
        self.logger     = logging.getLogger("lidar")

        # Setup the RPLidar
        PORT_NAME = '/dev/ttyUSB0'
        self.lidar = RPLidar(None, PORT_NAME)

        if not self.lidar == ??:
            self.logger.log(logging.CRITICAL, "Status:Failed to open lidar!")

        self.lidar.stop_motor()
        self.scan = [0]*360


        # Threading Locks, Events
        self.lidar_lock    = Lock() # before changing capture settings lock them
        self.stopped       = True

        # Init Scan and Thread
        self.scan_data  = [0]*360
        self.new_scan = False
        self.stopped   = False
        self.measured_scanrate = 0.0

        Thread.__init__(self)

    #
    # Thread routines #################################################
    # Start Stop and Update Thread

    def stop(self):
        """stop the thread"""
        self.stopped = True

    def start(self):
        """ set the thread start conditions """
        self.stopped = False        
        self.lidar.set_pwm(1023)
        self.lidar.start_motor()
        T = Thread(target=self.update, args=())
        T.daemon = True # run in background
        T.start()

    # After Stating of the Thread, this runs continously
    def update(self):
        """ run the thread """
        last_fps_time = time.time()
        last_exposure_time = last_fps_time
        num_scans = 0
        while not self.stopped:
            current_time = time.time()
            # FPS calculation
            if (current_time - last_fps_time) >= 5.0: # update frame rate every 5 secs
                self.measured_fps = num_frames/5.0
                self.logger.log(logging.DEBUG, "Status:SPS:{}".format(self.measured_sanrate))
                num_scans = 0
                last_fps_time = current_time

            with self.lidar_lock:
                raw_scan = lidar.iter_scans(max_buf_meas=500, min_len=360)

            ordered_scan = [0]*360
            for (_, angle, distance) in raw_scan:
                ordered_scan[min([359, floor(angle)])] = distance
            num_scans += 1

            self.scan = ordered_scan

            # creating point could data`
            # not finihed
            for angle in range(360):
                distance = self.scan[angle]
                if distance > 0:   
                    radians = angle * pi / 180.0
                    x = distance * cos(radians)
                    y = distance * sin(radians)


            if self.stopped:
                self.lidar.stop_motor()
    
    #
    # Scan routines ##################################################
    # Each lidar stores scan locally
    ###################################################################

    @property
    def scan(self):
        """ returns most recent frame """
        self._new_scan = False
        return self._scan

    @scan.setter
    def scan(self, scan):
        """ set new frame content """
        with self.scan_lock:
            self._scan = scan
            self._new_scan = True

    @property
    def new_scan(self):
        """ check if new scan available """
        out = self._new_scan
        return out

    @new_scan.setter
    def new_scan(self, val):
        """ override wether new scan is available """
        self._new_scan = val
