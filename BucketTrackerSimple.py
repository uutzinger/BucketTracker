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

            bt.putNumber("trackerTime",          time.perf_counter())
            bt.putNumber("Frame",                pose.frame_number)
            bt.putNumber("Position_x",           data.translation.x)
            bt.putNumber("Position_y",           data.translation.y)
            bt.putNumber("Position_z",           data.translation.z)
            bt.putNumber("Velocity_x",           data.velocity.x)
            bt.putNumber("Velocity_y",           data.velocity.y)
            bt.putNumber("Velocity_z",           data.velocity.z)
            bt.putNumber("Acceleration_x",       data.acceleration.x)
            bt.putNumber("Acceleration_y",       data.acceleration.y)
            bt.putNumber("Acceleration_z",       data.acceleration.z)
            bt.putNumber("AngularVelocity_x",    data.angular_velocity.x)
            bt.putNumber("AngularVelocity_y",    data.angular_velocity.y)
            bt.putNumber("AngularVelocity_z",    data.angular_velocity.z)
            bt.putNumber("AngularAcceleration_x",data.angular_acceleration.x)
            bt.putNumber("AngularAcceleration_y",data.angular_acceleration.y)
            bt.putNumber("AngularAcceleration_z",data.angular_acceleration.z)
            bt.putNumber("Pitch", pitch)
            bt.putNumber("Roll",  roll)
            bt.putNumber("Yaw",   yaw)
finally:
    pipe.stop()
