from utils.gui import GUIUtils
from utils.trackbar import CannyTrackbar, ColorThreshTrackbar, HoughCircleTrackbar, HoughLineTrackbar

import json

class CVConfig(object):

  def __init__(self, config_file, reset=False, always_reset=False, no_file=False):
    self._config_file = config_file
    self._always_reset = always_reset

    self._values = {
      # key: [saved, trackbar_class, is_reset]
      "BOARD_CANNY": [(100, 900), CannyTrackbar],
      "BOARD_COLOR_WATER": [([56, 0, 30], [169, 255, 169]), ColorThreshTrackbar],
      "BOARD_HOUGH_CIRCLE": [((20, 60), (45, 25), 10), HoughCircleTrackbar],
      "BOARD_HOUGH_LINE": [(65, 46, 10), HoughLineTrackbar],

      "TILE_AMPLIFY_WHEAT": [([0, 200, 200], [36, 255, 255]), ColorThreshTrackbar],
      "TILE_AMPLIFY_BRICK": [([2, 149, 117], [9, 255, 255]), ColorThreshTrackbar],
      "TILE_AMPLIFY_IRON": [([0, 81, 81], [46, 154, 187]), ColorThreshTrackbar],
      "TILE_AMPLIFY_SHEEP": [([30, 232, 87], [112, 255, 157]), ColorThreshTrackbar],

      'TILE_COLOR_DESERT': [([0, 0, 0], [1, 1, 1]), ColorThreshTrackbar],
      'TILE_COLOR_BRICK': [([0, 146, 0], [16, 255, 255]), ColorThreshTrackbar],
      'TILE_COLOR_IRON': [([0, 0, 123], [179, 145, 255]), ColorThreshTrackbar],
      'TILE_COLOR_WHEAT': [([13, 0, 151], [179, 255, 255]), ColorThreshTrackbar],
      'TILE_COLOR_WOOD': [([19, 0, 0], [27, 255, 255]), ColorThreshTrackbar],
      'TILE_COLOR_SHEEP': [([27, 0, 0], [179, 255, 255]), ColorThreshTrackbar],

      "DICE_HOUGH_CIRCLE": [((20, 60), (45, 25), 10), HoughCircleTrackbar]
    }


    # Append reset status
    for key in self._values:
      self._values[key].append(reset)

    if no_file:
      print "!! [CONFIG] Not using a config file. Using hardcoded defaults instead."
      return

    # try to load from _CONFIG_FILE
    try:
      cfile = open(self._config_file, 'r+')
      config_json = json.load(cfile)

      self._load_config_json(config_json)

      cfile.close()
    except IOError as e:
      print "!! [CONFIG] No config file found, using hardcoded defaults."


  # Save config to a json file
  def save(self):
    try:
      cfile = open(self._config_file, 'w+')

      config_json = self._get_config_json()
      json.dump(config_json, cfile)

      cfile.close()
    except IOError as e:
      print "!! [CONFIG] IOError occurred while saving settings. Settings lost."
    return


  # Retrieve a key, launching a config GUI if necessary
  def get(self, key, img):
    if self._values[key][2]: # is_reset
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


  def _load_config_json(self, config_json):
    for key, value in config_json.iteritems():
      self._values[key][0] = value
    return

  def _get_config_json(self):
    ret = {}
    for key, value in self._values.iteritems():
      ret[key] = value[0]
    return ret







