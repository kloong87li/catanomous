import cv2
import numpy as np

from utils.cv import CVUtils
from utils.gui import GUIUtils

class CatanHexagon(object):

  _TILE_COLOR_BOUNDS = {
    'WHEAT': ([0, 0, 157], [179, 255, 255]),
    'SHEEP': ([27, 0, 0], [179, 255, 255]),
    'BRICK': ([0, 0, 0], [13, 255, 255]),
    'WOOD': ([19, 0, 0], [27, 255, 255]),
    'IRON': ([0, 0, 0], [25, 164, 142])
  }

  def __init__(self, contour, img):
    self._contour = contour

    # Isolate hexagon
    contour_mask = np.zeros((img.shape[0], img.shape[1]), np.uint8)
    cv2.drawContours(contour_mask, [contour], -1, [255, 255, 255], thickness=-1)
    masked = CVUtils.mask_image(img, contour_mask)

    # Get ROI
    (x, y, w, h) = cv2.boundingRect(contour)
    roi = masked[y:y+h, x:x+w]

    # Compute mean color
    channels = cv2.split(roi)
    mean = [np.uint8(np.mean(c[np.nonzero(c)])) for c in channels]

    # TEMP: Show mean color on original
    np.copyto(img, CVUtils.replace_color(img, contour_mask, mean))

    self._resource = 'DESERT'
    for key in self._TILE_COLOR_BOUNDS:
      if self._color_in_range(mean, self._TILE_COLOR_BOUNDS[key]):
        self._resource = key
        break

  def _color_in_range(self, value, (lower, upper)):
    res = True
    for i in xrange(len(value)):
      res = res and (lower[i] < value[i] and value[i] < upper[i])
    return res



