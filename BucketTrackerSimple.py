#!/usr/bin/python
#!/usr/bin/env python
"""
###############################################################################
# Bucket Tracker
# Uses Intel Realsense Tracking Camera T265 to obtain pose, position and 
# velocity.
# Publshes results in Network Tables
#
# Urs Utiznger
# 2020
###############################################################################
"""
###############################################################################
# Imports
###############################################################################

from __future__ import print_function
import sys
import time
import argparse
import math
import pyrealsense2 as rs
import numpy as np
import cv2
from networktables import NetworkTables

def connectionListener(connected, info):
    """ used to wait till network tables is initalized """
    print(info, '; Connected=%s' % connected)
    with cond:
        notified[0] = True
        cond.notify()

# Setup logging
import logging
logging.basicConfig(level=logging.DEBUG)

ap = argparse.ArgumentParser(description='IP number.')
ap.add_argument('-i', '--ip', dest='ip', default="10.41.83.2", help='Team IP number or localhost.')
args = vars(ap.parse_args())

cond = threading.Condition()
notified = [False]
NetworkTables.initialize(server=ip)
NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

# if not connected then block and wait
with cond:
    print("Waiting")
    if not notified[0]:
        cond.wait()

sd = NetworkTables.getTable("SmartDashboard")
dsTime = sd.getNumber("dsTime", -1))

bt = NetworkTables.getTable("BucketTracking")
bt.putString("BucketVisionState", "Starting")
bt.putNumber("trackerTime", time.perf_counter())

od = NetworkTables.getTable("BucketWheelOdometry")

# Declare RealSense pipeline, encapsulating the actual device and sensors
pipe = rs.pipeline()

# Build config object and request pose dataPPP
cfg = rs.config()parse_args
cfg.enable_stream(rs.stream.pose)

# Start streaming with requested config
pipe.start(cfg)

while True:
    # Wait for the next set of frames from the camera
    frames = pipe.wait_for_frames()

    # Fetch pose frame
    pose = frames.get_pose_frame()
    if pose:
        # Print some of the pose data to the terminal
        data = pose.get_pose_data()

        w =  data.rotation.w
        x = -data.rotation.z
        y =  data.rotation.x
        z = -data.rotation.y

        pitch =  -math.asin(2.0 * (x*z - w*y)) * 180.0 / math.pi
        roll  =  math.atan2(2.0 * (w*x + y*z), w*w - x*x - y*y + z*z) * 180.0 / math.pi
        yaw   =  math.atan2(2.0 * (w*z + x*y), w*w + x*x - y*y - z*z) * 180.0 / math.pi

        bt.putNumber("trackerTime", time.perf_counter())
        bt.putNumber("Frame",       pose.frame_number)
        bt.putNumber("Position",    data.translation)
        bt.putNumber("Velocity",    data.velocity)
        bt.putNumber("Acceleration",data.acceleration)
        bt.putNumber("Pitch",       pitch)
        bt.putNumber("Roll",        roll)
        bt.putNumber("Yaw",         yaw)

pipe.stop()
