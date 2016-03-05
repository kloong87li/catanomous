import cv2
import numpy as np

from utils.cv import CVUtils
from utils.gui import GUIUtils

class CatanHexagon(object):

  _TILE_COLOR_BOUNDS = {
    'DESERT': ([13, 0, 146], [22, 255, 172]),
    'WHEAT': ([13, 0, 151], [179, 255, 255]),
    'IRON': ([12, 0, 0], [20, 255, 139]),
    'WOOD': ([19, 0, 0], [27, 255, 255]),
    'SHEEP': ([27, 0, 0], [179, 255, 255]),
    'BRICK': ([0, 0, 0], [12, 255, 255]),
  }

  _TILE_COLORS = [
    'DESERT', 'WHEAT', 'IRON', 'WOOD', 'SHEEP', 'BRICK'
  ]

  def __init__(self, contour, img):
    self._contour = contour

    # Isolate hexagon
    contour_mask = np.zeros((img.shape[0], img.shape[1]), np.uint8)
    cv2.drawContours(contour_mask, [contour], -1, [255, 255, 255], thickness=-1)
    
    # Store results
    self._hex_mask = contour_mask
    self._hex_img = CVUtils.mask_image(img, contour_mask)

    self._resource = '???'

  # Determine if the given color is within the given bounds
  def _color_in_range(self, value, (lower, upper)):
    res = True
    for i in xrange(len(value)):
      res = res and (lower[i] < value[i] and value[i] < upper[i])
    return res

  # Returns the ROI of this hexagon in the given img
  def _get_roi(self, img):
    (x, y, w, h) = cv2.boundingRect(self._contour)
    return img[y:y+h, x:x+w]

  # Classify the resource based on the results of kmeans algo
  def classify_resource(self, kmeans_res):
    roi = self._get_roi(kmeans_res)
    (h, w, z) = roi.shape

    # Get mean for this hexagon
    mean = roi[h/2, w/2]
    hsv_mean = cv2.cvtColor(np.array([[mean]], np.uint8), cv2.COLOR_BGR2HSV).flatten()
    
    # Check each color bound
    for key in self._TILE_COLORS:
      if self._color_in_range(hsv_mean, self._TILE_COLOR_BOUNDS[key]):
        self._resource = key
        break

  def get_hex_mask(self):
    return self._hex_mask

  # Returns mean color of this hexagon
  # includes some preprocessing to help make each mean unique
  def get_mean_color(self):
    # get ROI
    (x, y, w, h) = cv2.boundingRect(self._contour)
    roi = self._get_roi(self._hex_img)
    
    roi = cv2.pyrMeanShiftFiltering(roi, 10, 10)
    # Amplify yellow to differentiate wheat from desert
    roi = CVUtils.replace_range(CVUtils.to_hsv(roi), roi, [0, 200, 200], [36, 255, 255], [255, 255, 255])
    # Amplify red to differentiate brick
    roi = CVUtils.replace_range(CVUtils.to_hsv(roi), roi, [2, 149, 117], [9, 255, 255], [0, 0, 255])
    
    # Compute mean color
    channels = cv2.split(roi)
    return [np.uint8(np.mean(c[np.nonzero(c)])) for c in channels]



