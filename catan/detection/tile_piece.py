import cv2
import numpy as np

from utils.cv import CVUtils
from utils.gui import GUIUtils

from math import sqrt

class PieceDetector(object):

  _ROI_RADIUS = 40 # region of interest radius when looking for pieces around a vertex
  _PLAYER_COLORS = ['RED', 'BLUE', 'ORANGE', 'WHITE']
  _PIECE_AREA_THRESH = 400
  _MARKER_DIST_FROM_CENTER = 20

  def __init__(self, config):
    self._config = config

  def detect_properties(self, img, vertices):
    props = []
    for v in vertices:
      piece_color = self._detect_piece_color(v, img)
      if piece_color is not None:
        props.append((v, piece_color))

    # return list of properties
    return props

  def _point_distance(self, pt1, pt2):
    return sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)

  def _detect_piece_color(self, v, img):
    # isolate region around vertex
    rd = self._ROI_RADIUS
    (l, r, t, b) = (v[0]-rd, v[0]+rd, v[1]-rd, v[1]+rd)
    roi = img[t:b, l:r]

    # Look for a circlular indicator
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    (h, w) = gray.shape
    hough_config = self._config.get("PIECE_HOUGH_CIRCLE", roi)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT,1, h/hough_config[2],
                                param1=hough_config[0][1],
                                param2=hough_config[0][0],
                                minRadius=h/hough_config[1][0], maxRadius=h/hough_config[1][1])
    if circles is None:
      # No circle means no piece
      return None

    # Determine if circle is legit i.e its center is close enough to the center
    circle = np.uint8(np.around(circles))[0, :][0]
    if self._point_distance((rd, rd), (circle[0], circle[1])) > self._MARKER_DIST_FROM_CENTER:
      return None

    # Isolate circlular piece marker
    mask = np.zeros((roi.shape[0], roi.shape[1]), np.uint8)
    cv2.circle(mask, (circle[0], circle[1]), circle[2], 255, -1)
    circle_roi = CVUtils.mask_image(roi, mask)
    circle_hsv = cv2.cvtColor(circle_roi, cv2.COLOR_BGR2HSV)

    # Check for each piece color in the image
    for color in self._PLAYER_COLORS:
      bounds = self._config.get('PIECE_COLOR_'+color, img)
      range_mask = CVUtils.range_mask(circle_hsv, bounds[0], bounds[1])
      num_ones = np.sum(range_mask) / 255
      if num_ones > self._PIECE_AREA_THRESH:
        return color

    return None


