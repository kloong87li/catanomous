import cv2
import imutils
import numpy as np
from PIL import Image

from catan.detection.dice import DiceDetector

from utils.camera import Camera
from utils.debug import Debugger
import time

class DiceController(object):
  _IMAGE_WIDTH = 1200
  _CONFIG_FILE = "config/config.json"

  def __init__(self):
    return

  def _prepare_config(self, reset=False):
    camera_config = "config/camera_dice.json"
    cv_config = self._CONFIG_FILE

    config = CVConfig(cv_config, reset)
    config.load_cv_config(cv_config)
    config.load_cam_config(camera_config)
    return config

  def _get_image(self, config=None):
    if self._camera is None:
      print "Camera unintialized"
      
    img = self._camera.capture(config)
    return imutils.resize(img, width=self._IMAGE_WIDTH)

  # Called to detect and save hexagons
  def _handle_detect_dice(self):
    img = self._get_image()
    initial = time.time()
    dice_roll = self._dice_detector.detect_roll(img)

    print "Rolled: ", dice_roll
    print "Time: ", initial - time.time()

    # TODO send to other raspi via bluetooth


  def start(self):
    self._config = self._prepare_config()
    self._camera = Camera(self._config)
    self._camera.start()
    self._dice_detector = DiceDetector(self._config)

    while (True):
      print '1 to detect dice roll'
      token = raw_input("Input: ")

      if token == '1':
        self._handle_detect_dice()
      elif token == 'X':
        break
    return
    

  def start_test(self):
    self._config = self._prepare_config(True)
    self._camera = Camera(self._config)
    self._camera.start()
    self._dice_detector = DiceDetector(self._config)

    self._handle_detect_dice()
    self._config.save_cv_config(self._CONFIG_FILE)



