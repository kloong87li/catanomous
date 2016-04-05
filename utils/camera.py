import cv2
import imutils
import numpy as np

from picamera.array import PiRGBArray
from picamera import PiCamera

class Camera(object):

  def __init__(self, config, cam_file="config/camera.json"):
    self._cam = None
    self._rawCapture = None
    self._cam_file = cam_file
    self._config = config


  def start(self):
    # initialize the camera and grab a reference to the raw camera capture
    self._cam = PiCamera()
    self._rawCapture = PiRGBArray(self._cam)
    self._cam.framerate = 30
    self._cam.awb_mode = 'off'

    self._config.load_cam_file(self._cam_file)
     
    # allow the camera to warmup
    time.sleep(0.1)

    # set settings based on cam file
    cam_config = self._config.get_cam_all()
    for key in cam_config:
      self.set_setting(key, cam_config[key])

    # Wait for the automatic gain control to settle
    time.sleep(2)

  def capture(self):
    # grab an image from the camera
    self._cam.capture(self._rawCapture, format="bgr")
    return rawCapture.array

  def set_setting(self, key, value):
    self._config.set_cam(key, value)
    if key == "AWB":
      self._cam.awb_gains = value
    elif key == "BRIGHTNESS":
      self._cam.brightness = value
    elif key == "CONTRAST":
      self._cam.contrast = value
    elif key == "EXPOSURE_COMPENSATION":
      self._cam.exposure_compensation = value
    elif key == "ISO":
      self._cam.ISO = value
    elif key == "RESOLUTION":
      self._cam.resolution = value
    elif key == "SATURATION":
      self._cam.saturation = value
    elif key == "SHARPNESS":
      self._cam.sharpness = value
    elif key == "ZOOM":
      self._cam.zoom = value
    else:
      print "!! [CONFIG] Invalid key for camera configuration."

  def stop(self):
    self._cam.close()
    self._config.save_cam_file(self._cam_file)
    return

  def start_preview(self):
    self._cam.start_preview()

  def stop_preview(self):
    self._cam.stop_preview()




