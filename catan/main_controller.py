import cv2
import imutils
import numpy as np
from PIL import Image

from utils.cv import CVUtils
from utils.gui import GUIUtils
from catan.config import CVConfig
from catan.game import CatanomousGame

from utils.camera import Camera
from utils.debug import Debugger
import time

from utils.bluetooth import BluetoothServer

class MainController(object):
  _IMAGE_WIDTH = 1200
  _HEX_FILE = "config/hexagons.npy"
  _CONFIG_FILE = "config/config.json"

  def __init__(self):
    self._camera_hex_config = CVConfig.load_json("config/camera_hex.json")
    self._camera_nums_config = CVConfig.load_json("config/camera_nums.json")

    return

  def _prepare_config(self, reset=False):
    hex_config = self._HEX_FILE
    camera_config = "config/camera.json"
    cv_config = self._CONFIG_FILE

    config = CVConfig(cv_config, reset)
    config.load_cv_config(cv_config)
    config.load_cam_config("config/camera.json")
    config.load_hex_config(hex_config)

    return config

  def _get_image(self, config=None):
    if self._camera is None:
      print "Camera unintialized"
      
    img = self._camera.capture(config)
    return imutils.resize(img, width=self._IMAGE_WIDTH)

  # Called to detect and save hexagons
  def _handle_hexagon_init(self, reset=True, debug=False):
    img = self._get_image(self._camera_hex_config)
    if reset:
      self._config.set_hexagons(None)
    initial = time.time()
    hexes = self._game.init_game(img)

    if reset:
      self._game.save_hexagons(self._HEX_FILE)

    if debug:
      print "Hexagons detected, moving on to resources, time: ", time.time() - initial
      Debugger.show_hexagons(img, hexes, 0)

  # Called to detect resources and numbers
  def _handle_resource_init(self, debug=False):
    num_img = self._get_image(self._camera_nums_config)
    res_img = self._get_image()

    initial = time.time()
    tiles = self._game.new_game(res_img, num_img)

    if debug:
      print "Resources/numbers detected, moving on to pieces, time: ", time.time() - initial
      Debugger.show_resources(num_img, tiles, 0)

  # Called to detect new properties and deal cards based on roll
  def _handle_dice_roll(self, num, debug=False):
    img = self._get_image()
    initial = time.time()
    instructions = self._game.dice_rolled(num, img)

    if debug:
      print "Pieces detected, exiting..., time: ", time.time() - initial
      Debugger.show_properties(img, instructions, 0)
      
    # TODO something with the instructions


  def _listen_for_dice(debug=False):
    self._bt_server.start()
    sock = self._bt_server.accept()

    while True:
      num = self._bt_server.receive(sock)
      if num == '\n':
        break
      
      self._handle_dice_roll(num, debug)

    self._bt_server.close(sock)
    self._bt_server.close_server()


  def start(self, enable_bt):
    self._config = self._prepare_config()
    self._camera = Camera(self._config)
    self._camera.start()
    self._game = CatanomousGame(self._config)
    self._bt_server = BluetoothServer()

    while (True):
      print '1 to init hexagons, 2 for resources/numbers, 3 for pieces, 4 to use bluetooth'
      token = raw_input("Input: ")

      if token == '1':
        reset = raw_input("Reset?") == 'Y'
        self._handle_hexagon_init(reset, debug=True)
      elif token == '2':
        self._handle_resource_init(debug=True)
      elif token == '3':
        self._handle_dice_roll(1, debug=True)
      elif token == '4':
        self._listen_for_dice(debug=True)
      elif token == 'X':
        break
    return


  def start_test(self, reset_hexes=False, skip_resources=False):
    self._config = self._prepare_config(True)
    self._camera = Camera(self._config)
    self._camera.start()
    self._game = CatanomousGame(self._config)

    self._handle_hexagon_init(reset_hexes, debug=True)
    self._config.save_cv_config(self._CONFIG_FILE)

    if not skip_resources:
      self._handle_resource_init(debug=True)
      self._config.save_cv_config(self._CONFIG_FILE)

    self._handle_dice_roll(1, debug=True)
    self._config.save_cv_config(self._CONFIG_FILE)




