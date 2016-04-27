import cv2
import numpy as np
import imutils

from utils.cv import CVUtils
from utils.gui import GUIUtils

from .hexagon import HexagonDetector
from .tile import TileDetector


class BoardDetector(object):

  _KMEANS_ATTEMPTS = 2

  def __init__(self, config, hexagon_img):
    self._config = config

    contours = config.get_hexagons()
    self._contours = contours
    if contours is None:
      contours = HexagonDetector(config).detect_hexagons(hexagon_img)

    # Create and process each hexagon
    self._hexagons = []
    for c in contours:
      # Initialize detector
      hexagon = TileDetector(config, c, hexagon_img)
      self._hexagons.append(hexagon)

  def get_hex_contours(self):
    return [h.get_contour() for h in self._hexagons]

  def detect_resources(self, img):
    mean_colors = np.copy(img)

    for hexagon in self._hexagons:
      # Replace hexagon with its mean color
      mean = hexagon.get_representative_color(img)
      np.copyto(mean_colors, CVUtils.replace_color(mean_colors, hexagon.get_hex_mask(), mean))

    # Isolate hexagons in mean color image
    hex_mask = np.zeros((img.shape[0], img.shape[1]), np.uint8)
    cv2.drawContours(hex_mask, self.get_hex_contours(), -1, [255, 255, 255], thickness=-1)
    mean_colors = CVUtils.mask_image(mean_colors, hex_mask)

    # Run kmeans
    kmeans = self._kmeans(mean_colors)


    # Classify resources based on the kmeans result and detect the number
    for h in self._hexagons:
      h.detect_resource(img, kmeans)

  def detect_numbers(self, img):
    for h in self._hexagons:
      h.detect_number(img)

  def detect_properties(self, img):
    orig = img
    # Get circles only
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    (h, w) = gray.shape
    hough_config = self._config.get("PIECES_HOUGH_CIRCLE", img, True)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT,1, h/hough_config[2],
                                param1=hough_config[0][1],
                                param2=hough_config[0][0],
                                minRadius=h/hough_config[1][0],maxRadius=h/hough_config[1][1])
    circle_mask = np.zeros((h, w), np.uint8)
    for circle in circles[0]:
      # Draw circles on mask
      cv2.circle(circle_mask, (circle[0], circle[1]), np.uint8(circle[2]), 255, thickness=-1)
    img = CVUtils.mask_image(img, circle_mask)

    tiles = []
    for tile in self._hexagons:
      properties = tile.detect_properties(img, orig)
      tiles.append((tile, properties))
    return tiles




  def _kmeans(self, img):
    Z = img.reshape((-1,3))
    # convert to np.float32
    Z = np.float32(Z)

    # Define criteria, number of clusters (K) and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 3, 1.0)
    K = 6
    ret,label,center = cv2.kmeans(Z, K, None, criteria, self._KMEANS_ATTEMPTS, cv2.KMEANS_PP_CENTERS)

    # Now convert back into uint8, and make original image
    center = np.uint8(center)
    res = center[label.flatten()]
    return res.reshape((img.shape))



