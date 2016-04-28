from utils.gui import GUIUtils
from utils.trackbar import CannyTrackbar, ColorThreshTrackbar, HoughCircleTrackbar, HoughLineTrackbar, ThreshTrackbar

import json
import numpy as np

class CVConfig(object):

  @staticmethod
  def load_json(filename):
    # try to load from _CONFIG_FILE
    cfile = None
    try:
      cfile = open(filename, 'r+')
      config_json = json.load(cfile)

      return config_json
    except IOError as e:
      print "!! [CONFIG] No config file found: " + filename
      return None

  @staticmethod
  def save_json(filename, json_obj):
    try:
      cfile = open(filename, 'w+')
      json.dump(json_obj, cfile)

      cfile.close()
    except IOError as e:
      print "!! [CONFIG] IOError occurred while saving settings. Settings lost: " + filename
    return



  def __init__(self, config_file, reset=False, always_reset=False):
    self._always_reset = always_reset

    # Initialize defaults
    self._values = {
      # key: [saved, trackbar_class, is_reset]
      "BOARD_CANNY": [(100, 900), CannyTrackbar],
      "BOARD_COLOR_WATER": [([56, 0, 30], [169, 255, 169]), ColorThreshTrackbar],
      "BOARD_HOUGH_CIRCLE": [((20, 60), (45, 25), 10), HoughCircleTrackbar],
      "BOARD_HOUGH_LINE": [(65, 46, 10), HoughLineTrackbar],

      'TILE_HOUGH_CIRCLE': [((30, 60), (45, 25), 10), HoughCircleTrackbar],
      "TILE_NUM_THRESH": [90, ThreshTrackbar],
      "TILE_AMPLIFY_WHEAT": [([0, 200, 200], [36, 255, 255]), ColorThreshTrackbar],
      "TILE_AMPLIFY_BRICK": [([2, 149, 117], [9, 255, 255]), ColorThreshTrackbar],
      "TILE_AMPLIFY_WOOD": [([0, 81, 81], [46, 154, 187]), ColorThreshTrackbar],
      "TILE_AMPLIFY_SHEEP": [([30, 232, 87], [112, 255, 157]), ColorThreshTrackbar],
      "TILE_AMPLIFY_IRON": [([30, 232, 87], [112, 255, 157]), ColorThreshTrackbar],

      'TILE_COLOR_DESERT': [([0, 0, 0], [1, 1, 1]), ColorThreshTrackbar],
      'TILE_COLOR_BRICK': [([0, 146, 0], [16, 255, 255]), ColorThreshTrackbar],
      'TILE_COLOR_IRON': [([0, 0, 123], [179, 145, 255]), ColorThreshTrackbar],
      'TILE_COLOR_WHEAT': [([13, 0, 151], [179, 255, 255]), ColorThreshTrackbar],
      'TILE_COLOR_WOOD': [([19, 0, 0], [27, 255, 255]), ColorThreshTrackbar],
      'TILE_COLOR_SHEEP': [([27, 0, 0], [179, 255, 255]), ColorThreshTrackbar],

      'PIECE_HOUGH_CIRCLE': [((20, 60), (45, 25), 10), HoughCircleTrackbar],
      'PIECE_COLOR_RED': [([0, 102, 203], [5, 255, 255]), ColorThreshTrackbar],
      'PIECE_COLOR_RED2': [([175, 102, 203], [179, 255, 255]), ColorThreshTrackbar],
      'PIECE_COLOR_BLUE': [([44, 2, 1], [179, 255, 101]), ColorThreshTrackbar],
      'PIECE_COLOR_BROWN': [([16, 1, 220], [15, 255, 255]), ColorThreshTrackbar],
      'PIECE_COLOR_GREEN': [([28, 1, 187], [27, 255, 224]), ColorThreshTrackbar],

      'PIECE_MARKER_BLACK': [([0, 0, 0], [15, 15, 15]), ColorThreshTrackbar],
      "PIECES_HOUGH_CIRCLE": [((20, 60), (45, 25), 10), HoughCircleTrackbar],
      "ROBBER_COLOR": [([0, 102, 203], [5, 255, 255]), ColorThreshTrackbar],


      "DICE_RED_MASK": [([1, 1, 1], [9, 255, 255]), ColorThreshTrackbar],
      "DICE_RED_MASK2": [([175, 1, 1], [179, 255, 255]), ColorThreshTrackbar],
      "DICE_HOUGH_CIRCLE": [((20, 60), (45, 25), 10), HoughCircleTrackbar]
    }

    self._camera_values = {
      'AWB': (1.0, 1.0),
      'BRIGHTNESS': 0,
      'CONTRAST': 0,
      'EXPOSURE_COMPENSATION': 0,
      'ISO': 0 ,
      'RESOLUTION': (1280, 720),
      'SATURATION': 0,
      'SHARPNESS': 0, 
      'ZOOM': (0.0, 0.0, 1.0, 1.0)
    }

    self._hex_contours = None

    # Append reset status
    for key in self._values:
      self._values[key].append(reset)
    

  #################################
  # CV Config related functions   #
  #################################

  def load_cv_config(self, filename):
    cjson = CVConfig.load_json(filename)
    if cjson is None:
      return

    for key, value in cjson.iteritems():
      self._values[key][0] = value
    return

  def save_cv_config(self, filename):
    cjson = {}
    for key, value in self._values.iteritems():
      cjson[key] = value[0]
    
    CVConfig.save_json(filename, cjson)

  # Retrieve a key, launching a config GUI if necessary
  def get(self, key, img, force_reset=False):
    if self._values[key][2] or force_reset: # is_reset
      trackbar = self._values[key][1](img, self._values[key][0], key)
      trackbar.show_image()
      GUIUtils.wait()
      trackbar.close_image()
      result = trackbar.get_result()
      self._values[key][0] = result

      if not self._always_reset:
        self._values[key][2] = False
      
      return result
    else:
      return self._values[key][0]


  #################################
  # Cam Config related functions  #
  #################################

  def get_cam(self, key):
    return self._camera_values[key]

  def set_cam(self, key, value):
    self._camera_values[key] = value

  def get_cam_all(self):
    return self._camera_values

  def load_cam_config(self, filename):
    cjson = CVConfig.load_json(filename)

    if cjson is not None:
      self._camera_values = cjson

  def save_cam_config(self, filename):
    CVConfig.save_json(filename, self._camera_values)



  #################################
  # Hex Config related functions  #
  #################################

  def get_hexagons(self):
    return self._hex_contours

  def set_hexagons(self, hexs):
    self._hex_contours = hexs

  def load_hex_config(self, filename):
    cnts = np.load(filename)
    self._hex_contours = cnts
    return

  def save_hex_config(self, filename):
    np.save(filename, self._hex_contours)
    return




