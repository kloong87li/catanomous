import cv2
import numpy as np

from utils.cv import CVUtils
from utils.gui import GUIUtils

from math import sqrt

class PieceDetector(object):

  _ROI_RADIUS = 25 # region of interest radius when looking for pieces around a vertex
  _PLAYER_COLORS = ['RED', 'BLUE', 'ORANGE', 'WHITE']
  _PIECE_AREA_THRESH = 400

  def __init__(self, config):
    self._config = config

  def detect_properties(self, img, contour):
    # Compute top most point
    vertices = [v[0] for v in contour]
    (top_i, top_v) = min(enumerate(vertices), key=lambda x: x[1][1])

    props = []
    prev = None
    (x,y,w,h) = cv2.boundingRect(contour)
    for i in xrange(len(vertices)):
      v = vertices[(top_i + i) % len(vertices)]
      
      if prev is None or self._point_distance(prev, v) > h/3:
        prev = v

        # Determine if this is a property
        piece_color = self._detect_piece_color(v, img)
        if piece_color is not None:
          props.append((v, piece_color))


    # return list of properties
    return props

  def _detect_piece_color(self, v, img):
    # isolate circlular area
    rd = self._ROI_RADIUS
    (l, r, t, b) = (v[0]-rd, v[0]+rd, v[1]-rd, v[1]+rd)
    roi = img[t:b, l:r]
    mask = np.zeros((roi.shape[0], roi.shape[1]), np.uint8)
    cv2.circle(mask, (rd, rd), rd, 255, -1)
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

  def _point_distance(self, pt1, pt2):
    return sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)


