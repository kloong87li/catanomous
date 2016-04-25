import cv2
import imutils
import numpy as np

from picamera.array import PiRGBArray
from picamera import PiCamera
import time

class Camera(object):

  def __init__(self, config):
    self._cam = None
    self._rawCapture = None
    self._config = config
    self._is_default_config = True


  def start(self):
    # initialize the camera and grab a reference to the raw camera capture
    self._cam = PiCamera()
    self._cam.framerate = 30
    self._cam.awb_mode = 'off'
     
    # allow the camera to warmup
    time.sleep(0.1)

    # set settings based on cam file
    cam_config = self._config.get_cam_all()
    self._set_config(cam_config)
    self._is_default_config = True

  def capture(self, config=None):
    if config is not None:
      self._set_config(config)
      self._is_default_config = False
    elif not self._is_default_config:
      self._set_config(self._config.get_cam_all())
      self._is_default_config = True

    # grab an image from the camera
    rawCapture = PiRGBArray(self._cam)
    self._cam.capture(rawCapture, format="bgr")
    return rawCapture.array

  def set_setting(self, key, value):
    if key == "AWB":
      self._cam.awb_gains = value
    elif key == "BRIGHTNESS":
      self._cam.brightness = value
    elif key == "CONTRAST":
      self._cam.contrast = value
    elif key == "EXPOSURE_COMPENSATION":
      self._cam.exposure_compensation = value
    elif key == "ISO":
      self._cam.iso = value
    elif key == "RESOLUTION":
      self._cam.resolution = tuple(value)
    elif key == "SATURATION":
      self._cam.saturation = value
    elif key == "SHARPNESS":
      self._cam.sharpness = value
    elif key == "ZOOM":
      self._cam.zoom = value
    else:
      print "!! [CONFIG] Invalid key for camera configuration."
      return
      
    self._config.set_cam(key, value)


  def stop(self):
    self._cam.close()
    return

  def start_preview(self):
    self._cam.start_preview()

  def stop_preview(self):
    self._cam.stop_preview()

  def _set_config(self, config):
    for key in config:
      self.set_setting(key, config[key])

    # Wait for the settings to change
    time.sleep(1)




