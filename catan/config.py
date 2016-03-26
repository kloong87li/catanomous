from utils.gui import GUIUtils
from utils.trackbar import CannyTrackbar

import json

class CVConfig(object):

  _CONFIG_FILE = "config.json"

  def __init__(self, reset=False):

    self._is_reset = reset

    self._values = {
      # key: [saved, trackbar_class, is_reset]
      "TEST": [(100, 200), CannyTrackbar, reset]
    }

    # try to load from _CONFIG_FILE
    try:
      cfile = open(self._CONFIG_FILE, 'r+')
      config_json = json.load(cfile)

      self._load_config_json(config_json)

      cfile.close()
    except IOError as e:
      print "!! [CONFIG] No config file found, using hardcoded defaults."


  # Save config to a json file
  def save(self):
    try:
      cfile = open(self._CONFIG_FILE, 'w+')

      config_json = self._get_config_json()
      json.dump(config_json, cfile)

      cfile.close()
    except IOError as e:
      print "!! [CONFIG] IOError occurred while saving settings. Settings lost."
    return


  # Retrieve a key, launching a config GUI if necessary
  def get(self, key, img):
    if self._values[key][2]: # is_reset
      trackbar = self._values[key][1](img, self._values[key][0])
      trackbar.show_image()
      GUIUtils.wait()
      trackbar.close_image()
      result = trackbar.get_result()
      self._values[key][0] = result
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







