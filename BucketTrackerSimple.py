#!/usr/bin/python
#!/usr/bin/env python
"""
###############################################################################
# Bucket Tracker
# Uses Intel Realsense Tracking Camera T265 to obtain pose, position and 
# velocity.
# Publishes results in Network Tables
# This code is based on the intel realsense python wrapper examples and 
# some parts of BucketVision.
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
import threading
import numpy as np
import cv2
import pyrealsense2 as rs

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

ap = argparse.ArgumentParser()
ap.add_argument('-ip', '--ip_address', default='localhost', required=False, help='Team IP number or localhost.')
args = ap.parse_args()

cond = threading.Condition()
notified = [False]
NetworkTables.initialize(server=args.ip_address)
NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

# if not connected then block and wait
# Uncomment to run with Network Tables
#with cond:
#    print("Waiting")
#    if not notified[0]:
#        cond.wait()

sd = NetworkTables.getTable("SmartDashboard")
# robotTime = sd.getNumber("dsTime", -1))

bt = NetworkTables.getTable("BucketTracking")
bt.putString("BucketVisionState", "Starting")
bt.putNumber("trackerTime", time.perf_counter())

# Declare RealSense pipeline, encapsulating the actual device and sensors
pipe = rs.pipeline()

# Build config object and request pose dataPPP
cfg = rs.config()
cfg.enable_stream(rs.stream.pose)

# Start streaming with requested config
pipe.start(cfg)

try:
    while (True):
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

            bt.putNumber("trackerTime",             time.perf_counter())
            bt.putNumber("Frame",                   pose.frame_number)
            bt.putNumberArray("Position",           [data.translation.x,          data.translation.y,          data.translation.z])
            bt.putNumberArray("Velocity",           [data.velocity.x,             data.velocity.y,             data.velocity.z])
            bt.putNumberArray("Acceleration",       [data.acceleration.x,         data.acceleration.y,         data.acceleration.z])
            bt.putNumberArray("AngularVelocity",    [data.angular_velocity.x,     data.angular_velocity.y,     data.angular_velocity.z] )
            bt.putNumberArray("AngularAcceleration",[data.angular_acceleration.x, data.angular_acceleration.y, data.angular_acceleration.z])
            bt.putNumberArray("RPY",                [pitch, roll, yaw])
finally:
    pipe.stop()
