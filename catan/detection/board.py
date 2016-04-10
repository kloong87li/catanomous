import cv2
import numpy as np

from utils.cv import CVUtils
from utils.gui import GUIUtils

from .hexagon import HexagonDetector
from .tile import TileDetector


class BoardDetector(object):

  _KMEANS_ATTEMPTS = 2

  def __init__(self, config, img):
    self._config = config

    contours = HexagonDetector(config).detect_hexagons(img)
    mean_colors = np.copy(img)

    # Create and process each hexagon
    self._hexagons = []
    hex_mask = np.zeros((img.shape[0], img.shape[1]), np.uint8)
    for c in contours:
      # Isolate hexagon
      cv2.drawContours(hex_mask, [c], -1, [255, 255, 255], thickness=-1)
      hex_img = CVUtils.mask_image(img, hex_mask)

      # Initialize detector
      hexagon = TileDetector(config, c, hex_img, img)
      self._hexagons.append(hexagon)

      # Replace hexagon with its mean color
      mean = hexagon.get_representative_color()
      np.copyto(mean_colors, CVUtils.replace_color(mean_colors, hex_mask, mean))

      hex_mask.fill(0)

    # Isolate hexagons in mean color image
    cv2.drawContours(hex_mask, contours, -1, [255, 255, 255], thickness=-1)
    mean_colors = CVUtils.mask_image(mean_colors, hex_mask)

    # Run kmeans
    kmeans = self._kmeans(mean_colors)

    # Classify resources based on the kmeans result and detect the number
    for h in self._hexagons:
      h.detect_resource(kmeans)
      h.detect_number()


  def get_hexagons(self):
    return self._hexagons

  def detect_properties(self, img):
    return

  def _kmeans(self, img):
    Z = img.reshape((-1,3))
    # convert to np.float32
    Z = np.float32(Z)

    # Define criteria, number of clusters (K) and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 1, 2.0)
    K = 6
    ret,label,center = cv2.kmeans(Z, K, None, criteria, self._KMEANS_ATTEMPTS, cv2.KMEANS_PP_CENTERS)

    # Now convert back into uint8, and make original image
    center = np.uint8(center)
    res = center[label.flatten()]
    return res.reshape((img.shape))



