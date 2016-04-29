import cv2
import imutils
import numpy as np
from PIL import Image

from catan.detection.dice import DiceDetector
from catan.config import CVConfig
from utils.camera import Camera
from utils.debug import Debugger
import time
from utils.bt_utils import BluetoothClient
from catan.gpio_controller import GPIOController

class DiceController(object):
  _IMAGE_WIDTH = 1200
  _CONFIG_FILE = "config/config.json"
  _SERVER_ADDR = "B8:27:EB:A6:25:50"
  _BUTTON_PIN = 17

  def __init__(self):
    self._gpio = GPIOController()
    self._gpio.init_button(self._BUTTON_PIN)
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
    # print "Time: ", time.time() - initial

    if self._bt_client is not None:
      self._bt_client.send(str(dice_roll))




  def start_auto(self):
    self._config = self._prepare_config()
    self._camera = Camera(self._config)
    self._camera.start()
    self._dice_detector = DiceDetector(self._config)
    self._bt_client = BluetoothClient()

    self._gpio.led_off()
    ret = False
    try:
      ret = self._bt_client.connect(self._SERVER_ADDR)
    except e:
      self._gpio.led_blink(3)
      return

    if ret:
      self._gpio.led_on()
    else:
      self._gpio.led_blink(3)
      return

    while(True):
      self._gpio.wait_for_press(self._BUTTON_PIN)

      self._handle_detect_dice()


  def start(self):
    self._config = self._prepare_config()
    self._camera = Camera(self._config)
    self._camera.start()
    self._dice_detector = DiceDetector(self._config)
    self._bt_client = None

    while (True):
      print '1 to detect dice roll, 2 to enable bluetooth'
      token = raw_input("Input: ")

      if token == '1':
        self._handle_detect_dice()
      elif token == '2':
        self._bt_client = BluetoothClient()
        self._bt_client.connect(self._SERVER_ADDR)
      elif token == 'X':
        if self._bt_client is not None:
          self._bt_client.send('\n')
        break
    return
    

  def start_test(self):
    self._config = self._prepare_config(True)
    self._camera = Camera(self._config)
    self._camera.start()
    self._dice_detector = DiceDetector(self._config)

    self._handle_detect_dice()
    self._config.save_cv_config(self._CONFIG_FILE)







