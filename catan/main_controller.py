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

from utils.bt_utils import BluetoothServer
from catan.gpio_controller import GPIOController

class MainController(object):
  _IMAGE_WIDTH = 1200
  _HEX_FILE = "config/hexagons.npy"
  _CONFIG_FILE = "config/config.json"
  _BUTTON_PIN = 17

  def __init__(self):
    self._camera_hex_config = CVConfig.load_json("config/camera_hex.json")
    self._camera_nums_config = CVConfig.load_json("config/camera_nums.json")

    self._bt_server = BluetoothServer()
    self._debugger = Debugger(self._bt_server)
    self._gpio = GPIOController()
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
      Debugger.show_hexagons(img, hexes, 250)

  # Called to detect resources and numbers
  def _handle_resource_init(self, debug=False):
    num_img = self._get_image(self._camera_nums_config)
    res_img = self._get_image()

    initial = time.time()
    tiles = self._game.new_game(res_img, num_img)

    if debug:
      print "Resources/numbers detected, moving on to pieces, time: ", time.time() - initial
      Debugger.show_resources(num_img, tiles, 250)

    self._debugger.log("Resource/number detection finished.", "RESOURCES")
    self._debugger.log_tiles(tiles)

  # Called to detect new properties and deal cards based on roll
  def _handle_dice_roll(self, num, debug=False):
    img = self._get_image()
    initial = time.time()
    (detected, instructions) = self._game.dice_rolled(num, img)

    if debug:
      print "Pieces detected, exiting..., time: ", time.time() - initial
      Debugger.show_properties(img, detected, 250)
      
    self._debugger.log("Finished processing dice roll.", "DICE")
    self._debugger.log_pieces(detected)
    self._debugger.log_instructions(instructions)
    # TODO something with the instructions


  def _listen_for_dice(self, sock, debug=False):
    

    while True:
      num = self._bt_server.receive(sock)
      if num == '\n':
        break
      
      self._gpio.led_off()
      self._debugger.log("Dice roll received: " + num, "DICE")
      self._handle_dice_roll(int(num), debug)
      self._gpio.led_on()

    self._bt_server.close(sock)
    self._bt_server.close_server()





  def start_auto(self, visual_debug=False):
    self._gpio.init_button(self._BUTTON_PIN)

    # Wait for button PRESS to continue, or HOLD to exit
    self._gpio.led_on()
    if self._gpio.wait_for_press_or_hold(self._BUTTON_PIN) == 'HOLD':
      self._gpio.led_restore()
      return
    self._gpio.led_off()

    try:
      self._config = self._prepare_config()
      self._camera = Camera(self._config)
      self._camera.start()
      self._game = CatanomousGame(self._config)

      self._bt_server.start()
      self._gpio.led_on()
      # LED - ON = waiting for something, OFF = processing something

      # PRESS to connect debugger, HOLD to skip
      if self._gpio.wait_for_press_or_hold(self._BUTTON_PIN) == 'PRESS':
        self._gpio.led_off()
        self._debugger.accept()
        self._gpio.led_on()
        self._debugger.log("Connected to bluetooth debugger.", "CONNECT")
      else:
        self._debugger.log("No debugger chosen.", "CONNECT")
        self._gpio.led_blink(3)

      time.sleep(1.5)
      try:
        # Wait for dice detector to connect
        self._gpio.led_off()
        self._debugger.log("Waiting for dicebox to connect...", "CONNECT")
        dice_sock = self._bt_server.accept()
        self._gpio.led_on()
        self._debugger.log("Dice box connected.", "CONNECT")

        # Wait for HOLD to indicate reset hexagons, PRESS means load saved
        self._debugger.log("HOLD to reset hexes, PRESS to load.", "INPUT")
        reset_hexagons = self._gpio.wait_for_press_or_hold(self._BUTTON_PIN) == 'HOLD'
        self._debugger.log("Reset hexagons: " + str(reset_hexagons), "HEXAGONS")
        self._gpio.led_off()
        self._handle_hexagon_init(reset_hexagons, debug=visual_debug)
        self._gpio.led_on()
        self._debugger.log("Hexagons detected.", "HEXAGONS")

        # PRESS to initialize resources and numbers
        self._debugger.log("PRESS after setting up resources/numbers", "INPUT")
        self._gpio.wait_for_press(self._BUTTON_PIN)
        self._gpio.led_off()
        self._debugger.log("Starting resource/number detection.", "RESOURCES")
        self._handle_resource_init(debug=visual_debug)
        self._gpio.led_on()

        # Wait for signals from dice detector
        self._debugger.log("Waiting for dice rolls...", "INPUT")
        self._listen_for_dice(dice_sock, debug=visual_debug)

      except Exception as e:
        # Send to debugger and reraise to blink LED
        self._debugger.log(str(e), 'ERROR')
        raise e
    except Exception as e:
      # BLink to indicate an error occured
      import subprocess
      subprocess.call('sudo sh -c "echo ' + str(e) + ' > /home/pi/logs/pylog.txt"', shell=True)
      while True:
        self._gpio.led_on()
        time.sleep(1)
        self._gpio.led_off()
        time.sleep(1)
    return



  def start(self):
    self._config = self._prepare_config()
    self._camera = Camera(self._config)
    self._camera.start()
    self._game = CatanomousGame(self._config)

    while (True):
      print '1 to init hexagons, 2 for resources/numbers, 3 for pieces, 4 to use bluetooth'
      token = raw_input("Input: ")

      if token == '1':
        reset = raw_input("Reset?") == 'Y'
        self._handle_hexagon_init(reset, debug=True)
      elif token == '2':
        self._handle_resource_init(debug=True)
      elif token == '3':
        num = raw_input("Num? ")
        self._handle_dice_roll(int(num), debug=True)
      elif token == '4':
        self._bt_server.start()
        sock = self._bt_server.accept()
        self._listen_for_dice(sock, debug=True)
      elif token == 'X':
        break
    return


  def start_test(self, reset_hexes=False, skip_resources=False, dont_reset=False):
    self._config = self._prepare_config(not dont_reset)
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




