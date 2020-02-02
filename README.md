# BucketTracker

This setup guide is based on https://github.com/IntelRealSense/librealsense/blob/master/doc/installation_raspbian.md

You will also need to read 
https://github.com/IntelRealSense/librealsense/blob/master/doc/t265.md
to understand how to calibrate the wheel odometer portion. The required part is the appendix. Best view direction of camera is upwards or downwards so that other moving objects do not interfere with the trackin. We need to know where he camera is placed in respect to the robot reference point. See the figure in the appendix in above link.

- BucketTrackerSimple.py: this program should update postion, velocity, pitch, roll and yaw to network tables

- BucketTracker.py: this program is work in progress and should include wheel odometry from Robot. Software team would need to provide wheel velocity of the two drop down center wheels and designers the position of the camrea in respect to the center wheel and the angle of the camera in respect to horizontal. Camera works likely best if pointed upwards. 

- BucketLIDAR.py: Attempt for LIDAR driver that provides reference wall locations and runs as separate thread. LIDAR likely works best if robot velocity is low.

Urs Utzinger 2020

## ToDo
- Test simple program
- Finish Odometer portion
- Maybe incorporate LIDAR

## Pre Requisites
- Raspberry Pi 4
- Raspian Buster
- Intel RealSense TS265 tracking camera

And you will need to have updated your operating system:
```
sudo apt-get update
sudo apt-get dist-upgrade
sudo apt autoremove
```

## Prepare the Raspberry Pi 4

### Required Packages
```
sudo apt-get install -y libdrm-amdgpu1 libdrm-dev libdrm-exynos1 libdrm-exynos1-dbg libdrm-freedreno1  libdrm-nouveau2 libdrm-omap1 libdrm-radeon1 libdrm-tegra0 libdrm2

sudo apt-get install -y libglu1-mesa libglu1-mesa-dev glusterfs-common libglu1-mesa libglu1-mesa-dev libglui-dev libglui2c2

sudo apt-get install -y libglu1-mesa libglu1-mesa-dev mesa-utils mesa-utils-extra xorg-dev libgtk-3-dev libusb-1.0-0-dev
```

## Update pip for python packages
```
wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py
sudo python3 get-pip.py
sudo rm -rf ~/.cache/pip
```

## Install Network Tables
```
pip3 install pynetworktables
```

## Install `OpenCV`
You can build from source code, but it takes at lot of much time. In this case, we will use pre-build version to save time.
This is taken from https://www.pyimagesearch.com/2019/09/16/install-opencv-4-on-raspberry-pi-4-and-raspbian-buster/

### Get supporting libraries
```
sudo apt-get install build-essential cmake pkg-config
sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng-dev
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get install libxvidcore-dev libx264-dev
sudo apt-get install libfontconfig1-dev libcairo2-dev
sudo apt-get install libgdk-pixbuf2.0-dev libpango1.0-dev
sudo apt-get install libgtk2.0-dev libgtk-3-dev
sudo apt-get install libatlas-base-dev gfortran
sudo apt-get install libhdf5-dev libhdf5-serial-dev libhdf5-103
sudo apt-get install libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5
sudo apt-get install python3-dev
```

### Install OpenCV 4
```
pip3 install opencv-contrib-python==4.1.0.25
sudo ldconfig
```

## Install  Google `protobuf`
Google protobuf compiled form source: This will take some time

```
cd ~
git clone https://github.com/google/protobuf.git
cd protobuf
./autogen.sh
./configure
make -j1
sudo make install
cd python
export LD_LIBRARY_PATH=../src/.libs
python3 setup.py build --cpp_implementation 
python3 setup.py test --cpp_implementation
sudo python3 setup.py install --cpp_implementation
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=cpp
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION_VERSION=3
sudo ldconfig
protoc --version
```

## Install `TBB`
Install intel threading building blocks from pre built libraries.

```
cd ~
wget https://github.com/PINTO0309/TBBonARMv7/raw/master/libtbb-dev_2019U5_armhf.deb
sudo dpkg -i ~/libtbb-dev_2019U5_armhf.deb
sudo ldconfig
rm libtbb-dev_2019U5_armhf.deb
```

## Install LibReal Sense
Now we are ready for Lib Real Sense to be installed on Raspberry Pi.

### Get LibRealSense
Now we need to get librealsense from the repo(https://github.com/IntelRealSense/librealsense).
```
cd ~
git clone https://github.com/IntelRealSense/librealsense.git
cd librealsense
```

### Update udev rule for new cameras
```
sudo cp config/99-realsense-libusb.rules /etc/udev/rules.d/ 
sudo udevadm control --reload-rules && udevadm trigger 

```

### Set path
```
nano ~/.bashrc
add the following line to the end of the file and ctr-X and Y
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
source ~/.bashrc
```

### Install `RealSense` SDK/librealsense
```
cd ~/librealsense
mkdir  build  && cd build
cmake .. -DBUILD_EXAMPLES=true -DCMAKE_BUILD_TYPE=Release -DFORCE_LIBUVC=true
make -j1
sudo make install
```

### Install `pyrealsense2`
```
cd ~/librealsense/build
cmake .. -DBUILD_PYTHON_BINDINGS=bool:true -DPYTHON_EXECUTABLE=$(which python3)
make -j1
sudo make install
```

Add python path
```
nano ~/.bashrc
add following line to the end and ctr-X and Y
export PYTHONPATH=$PYTHONPATH:/usr/local/lib

source ~/.bashrc
```

## Enable OpneGL on Raspberry Pi
```
sudo apt-get install python-opengl
sudo -H pip3 install pyopengl
sudo -H pip3 install pyopengl_accelerate
sudo raspi-config

"7.Advanced Options" - "A7 GL Driver" - "G2 GL (Fake KMS)"
```

Finally, we  need to reboot pi
```
sudo reboot
```

## Runing the RealSense T265 Camera
Connected camera to the pi and open terminal
```
realsense-viewer
```

## Bucket Lidar
Attempt to integrated Slamtec RPLidar
Lidar Overview: https://is.muni.cz/th/q0y8y
Dissertation: https://is.muni.cz/th/q0y8y/dp.pdf

Libraries for point could formatting and processing:

libLAS https://liblas.org/

PCL: http://www.pointclouds.org/

Laspy https://github.com/laspy/laspy

```
pip3 install adafruit_rplidar
pip3 install laspy liblas

sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key 19274DEF
sudo echo "deb http://ppa.launchpad.net/v-launchpad-jochen-sprickerhof-de/pcl/ubuntu maverick main" >> /etc/apt/sources.list
sudo apt-get update
sudo apt-get install libpcl-all

pip3 install python-pcl
```

