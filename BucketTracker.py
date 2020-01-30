#!/usr/bin/env python
"""
###############################################################################
# Bucket Tracker
# Uses Intel Realsense Tracking Camera T265 to obtain pose, position and 
# velocity.
# Utilized robot wheel odometry
# Publshes results in Network Tables
#
# Urs Utiznger
# 2019, 2020
###############################################################################
"""
###############################################################################
# Imports
###############################################################################

from __future__ import print_function
import sys
import time
import argparse
import pyrealsense2 as rs
import numpy as np
import cv2
from networktables import NetworkTables

# To see messages from networktables, you must setup logging
import logging
logging.basicConfig(level=logging.DEBUG)

ap = argparse.ArgumentParser(description='IP number.')
ap.add_argument('-i', '--ip', dest='ip', default="10.41.83.2", help='Team IP number.')
args = vars(ap.parse_args())

NetworkTables.initialize(server=ip)
sd = NetworkTables.getTable("SmartDashboard")

# load wheel odometry config before pipe.start(...)
# get profile/device/ wheel odometry sensor by profile = cfg.resolve(pipe)
pipe    = rs.pipeline()
cfg     = rs.config()
profile = cfg.resolve(pipe)
dev     = profile.get_device()
tm2     = dev.as_tm2()

if(tm2):
    # tm2.first_wheel_odometer()?
    pose_sensor = tm2.first_pose_sensor()
    wheel_odometer = pose_sensor.as_wheel_odometer()

    # calibration to list of uint8
    f = open("calibration_odometry.json")
    chars = []
    for line in f:
       for c in line:
           chars.append(ord(c))  # char to uint8

    # load/configure wheel odometer
    wheel_odometer.load_wheel_odometery_config(chars)


    pipe.start()
    try:
        for _ in range(100):
            frames = pipe.wait_for_frames()
            pose = frames.get_pose_frame()
            if pose:
                data = pose.get_pose_data()
                print("Frame #{}".format(pose.frame_number))
                print("Position: {}".format(data.translation))

                # provide wheel odometry as vecocity measurement
                wo_sensor_id = 0  # indexed from 0, match to order in calibration file
                frame_num = 0  # not used
                v = rs.vector()
                v.x = 0.1  # m/s
                wheel_odometer.send_wheel_odometry(wo_sensor_id, frame_num, v)
    finally:
        pipe.stop()
