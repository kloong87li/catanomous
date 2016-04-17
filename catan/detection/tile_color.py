import cv2
import numpy as np

from utils.cv import CVUtils
from utils.gui import GUIUtils

class TileColorDetector(object):
  _TILE_COLORS = [
    'DESERT', 'BRICK', 'IRON', 'WHEAT', 'WOOD', 'SHEEP'
  ]

  def __init__(self, config):
    self._config = config

  # Classify the resource based on its color in the passed in the region of interest
  def detect_resource(self, roi, kmeans_res):
    (h, w, z) = roi.shape

    # Get mean for this hexagon
    mean = roi[h/2][w/2]
    hsv_mean = cv2.cvtColor(np.array([[mean]], np.uint8), cv2.COLOR_BGR2HSV).flatten()

    # Check each color bound
    for key in self._TILE_COLORS:
      thresh = self._config.get("TILE_COLOR_"+key, kmeans_res)
      if self._color_in_range(hsv_mean, thresh):
        return key
        break
    return None

  # Determine if the given color is within the given bounds
  def _color_in_range(self, value, (lower, upper)):
    res = True
    for i in xrange(len(value)):
      res = res and (lower[i] < value[i] and value[i] <= upper[i])
    return res




