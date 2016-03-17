import cv2
import numpy as np

from utils.cv import CVUtils
from utils.gui import GUIUtils

class TileColorDetector(object):

  _TILE_COLOR_BOUNDS = {
    'DESERT': ([0, 0, 0], [1, 1, 1]),
    'BRICK': ([0, 146, 0], [16, 255, 255]),
    'IRON': ([0, 0, 123], [179, 145, 255]),
    'WHEAT': ([13, 0, 151], [179, 255, 255]),
    'WOOD': ([19, 0, 0], [27, 255, 255]),
    'SHEEP': ([27, 0, 0], [179, 255, 255]),
  }

  _TILE_COLORS = [
    'DESERT', 'BRICK', 'IRON', 'WHEAT', 'WOOD', 'SHEEP'
  ]

  # Classify the resource based on its color in the passed in the region of interest
  def detect_resource(self, roi):
    (h, w, z) = roi.shape

    # Get mean for this hexagon
    mean = roi[h/2, w/2]
    hsv_mean = cv2.cvtColor(np.array([[mean]], np.uint8), cv2.COLOR_BGR2HSV).flatten()
    
    # Check each color bound
    for key in self._TILE_COLORS:
      if self._color_in_range(hsv_mean, self._TILE_COLOR_BOUNDS[key]):
        return key
        break
    return None

  # Determine if the given color is within the given bounds
  def _color_in_range(self, value, (lower, upper)):
    res = True
    for i in xrange(len(value)):
      res = res and (lower[i] <= value[i] and value[i] < upper[i])
    return res




