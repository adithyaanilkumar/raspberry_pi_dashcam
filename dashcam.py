#!/usr/bin/python3
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
import os
import datetime
import time
import pytz
from pathlib import Path
import sys
import json
import syslog

# maxspace in mb
maxspace = 200000
Caption = "Hello"
Caption_BG = "hello"
RecordingPath = "/home/atherpi/developer/dashcam/videos"
framerate = 25
resHt = 1920
resWd = 1080
Region = "Asia/Kolkata"
Timezone = pytz.timezone(Region)
RecDuration = 10000

def CheckSize(Directory):
  DirSize = 0
  for (path, dirs, files) in os.walk(Directory):
      for file in files:
          filename = os.path.join(path, file)
          DirSize += os.path.getsize(filename)
  return(round(DirSize/(1000*1000),2))

def FreeUpSpace(FileList):
  for file in FileList:
    if CheckSize(RecordingPath) > float(maxspace):
      message = "Dashcam Removing {}".format(file)
      syslog.syslog(message)
      print(message)
      os.remove(file)

camera =  Picamera2()
video_config = camera.create_video_configuration(main={"size": (1280, 720)})
camera.configure(video_config)
camera.video_stabilization = True
encoder = H264Encoder(10000000)

while True:
   FileList = sorted(Path(RecordingPath).iterdir(), key=os.path.getmtime)
   FreeUpSpace(FileList)
   pattern = datetime.datetime.now(Timezone).strftime('%d%m%Y_%H:%M:%S')
   recFile = "{}/Dashcam-{}.{}".format(RecordingPath, pattern, 'mp4')
   message = "Dashcam Creating {}".format(recFile)

   increment = 1
   while os.path.exists(recFile):
      recFile = "{}/Dashcam-{}-{}.{}".format(RecordingPath, pattern, increment, 'mp4')
      increment = increment + 1
   message = "Dashcam Creating {}".format(recFile)
   syslog.syslog(message)
   print(message)
     
   timeout = time.time() + RecDuration
   output = FfmpegOutput(recFile)
   #output=recFile
   camera.start_recording(encoder, output)
   while (time.time() < timeout):
      camera.annotate_text = "{} {}".format(Caption, datetime.datetime.now(Timezone).strftime('%H:%M:%S %Y-%m-%d'))
      camera.annotate_text_size = 20
   if time.time() > timeout:
      camera.stop_recording()

camera.stop_recording()
