import cv2
import imutils
import numpy as np
from PIL import Image

from utils.cv import CVUtils
from utils.gui import GUIUtils
from catan.config import CVConfig
from catan.game import CatanomousGame

from utils.camera import Camera

class MainController(object):
  _IMAGE_WIDTH = 1200
  _HEX_FILE = "config/hexagons.npy"

  def __init__(self):
    self._camera_hex_config = CVConfig.load_json("config/camera_hex.json")
    self._camera_dice_config = CVConfig.load_json("config/camera_hex.json")
    return

  def _prepare_config(self, reset=False):
    hex_config = self._HEX_FILE
    camera_config = "config/camera.json"
    cv_config = "config/config.json"

    config = CVConfig(cv_config, reset)
    config.load_cv_config(cv_config)
    config.load_cam_config("config/camera.json")
    config.load_hex_config(hex_config)

    return config

  def _get_image(self, config=None):
    img = camera.capture(config)
    return imutils.resize(img, width=self._IMAGE_WIDTH)

  # Called to detect and save hexagons
  def _handle_hexagon_init(self, save=False, debug=False):
    img = self._get_image(self._camera_hex_config)
    self._config.set_hexagons(None)
    hexes = self._game.init_game(img)

    if save:
      self._game.save_hexagons()

    if debug:
      Debugger.show_hexagons(img, hexes, 0)

  # Called to detect resources and numbers
  def _handle_resource_init(self, debug=False):
    res_img = self._get_image()
    num_img = res_img

    tiles = self._game.new_game(res_img, num_img)

    if debug:
      Debugger.show_resources(img, tiles, 0)

  # Called to detect new properties and deal cards based on roll
  def _handle_dice_roll(self, num, debug=False):
    img = self._get_image()
    instructions = self._game.dice_rolled(num, img)

    if debug:
      Debugger.show_properties(img, instructions, 0)
    # TODO something with the instructions

  def start(self):
    self._config = self._prepare_config()
    self._camera = Camera(self._config)
    self._game = CatanomousGame(self._config)

    while (True):
      print '1 to init hexagons, 2 for resources/numbers, 3 for pieces'
      token = raw_input("Input: ")

      if token == '1':
        save = raw_input("Save?") == 'Y'
        self._handle_hexagon_init(save, debug=True)
      elif token == '2':
        self._handle_resource_init(debug=True)
      elif token == '3':
        self._handle_dice_roll(1, debug=True)
      elif token == 'X':
        break
    return


  def start_test(self):
    self._config = self._prepare_config(True)
    self._camera = Camera(self._config)
    self._game = CatanomousGame(self._config)

    self._handle_hexagon_init(True, debug=True)
    self._handle_resource_init(debug=True)
    self._handle_dice_roll(1, debug=True)




