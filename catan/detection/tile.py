import cv2
import numpy as np
from math import sqrt
from utils.cv import CVUtils
from utils.gui import GUIUtils

from .tile_color import TileColorDetector
from .tile_num import TileNumDetector
from .tile_piece import PieceDetector




class TileDetector(object):

  _MEAN_SHIFT = 10
  _COLOR_AMPLIFICATIONS = [
    # config_key, new color
    ("TILE_AMPLIFY_WHEAT", [0, 255, 255]),  # wheat
    ("TILE_AMPLIFY_BRICK", [20, 20, 255]),     # brick
    ("TILE_AMPLIFY_WOOD", [40, 50, 60]),   # wood
    ("TILE_AMPLIFY_SHEEP", [0, 255, 0]),     # wood
    ("TILE_AMPLIFY_IRON", [200, 200, 200])     # iron
  ]
  _CIRCLE_SCALE = 1.1
  _ROBBER_THRESH = 125


  def __init__(self, config, contour, hex_img):
    self._contour = contour
    self._config = config

    # Initialize detectors
    self._color_detect = TileColorDetector(config)
    self._num_detect = TileNumDetector(config)
    self._piece_detect = PieceDetector(config)

    # Generate the mask for isolating each hexagon
    self._hex_mask = np.zeros((hex_img.shape[0], hex_img.shape[1]), np.uint8)
    cv2.drawContours(self._hex_mask, [contour], -1, [255, 255, 255], thickness=-1)
    
    self._circle = None
    self._vertices = self._get_vertices(contour)
    self._resource = None
    self._number = None

  def get_num(self):
    return self._number

  def get_res(self):
    return self._resource

  def reset_res_and_num(self):
    self._resource = None
    self._number = None

  # Detects the resource using the result of the kmeans algo
  def detect_resource(self, img, kmeans_res):
    if self._circle is None:
      self._resource = 'DESERT'
    else:
      self._resource = self._color_detect.detect_resource(self._get_roi(kmeans_res), kmeans_res)

  # Detect and set self._number if no number was previously detected
  def detect_number(self, img):
    if self._circle is None:
      return None

    # Isolate circle area
    roi = self._get_roi(img)
    mask = self._get_circle_mask(roi, scale=.7)
    img = CVUtils.mask_image(roi, mask)

    num = self._num_detect.detect_number(img, mask, self._circle)
    if self._number is None:
      self._number = num

    return num

  def num_is_blocked(self, new_img):
    # Isolate circular area
    roi = self._get_hex_roi(new_img)
    if self._circle is None: 
      self._circle = self._detect_circle(new_img)
    circle_mask = self._get_circle_mask(roi, .5)  # Only interested in center portion
    roi = CVUtils.mask_image(roi, circle_mask)

    # Check for robber color
    bounds = self._config.get('ROBBER_COLOR', new_img)
    range_mask = CVUtils.range_mask(cv2.cvtColor(roi, cv2.COLOR_BGR2HSV), bounds[0], bounds[1])
    num_ones = np.sum(range_mask) / 255

    return num_ones > self._ROBBER_THRESH

  def detect_properties(self, new_img, orig_img):
    return self._piece_detect.detect_properties(new_img, self._vertices, orig_img)

  def get_contour(self):
    return self._contour

  def get_hex_mask(self):
    return self._hex_mask

  # Returns mean color of this hexagon
  # includes some preprocessing to help make each mean unique
  def get_representative_color(self, color_board_img):
    self._circle = self._detect_circle(color_board_img)
    roi = self._get_hex_roi(color_board_img)
    
    # Eliminate circlular number piece
    circle_mask = self._get_circle_mask(roi, self._CIRCLE_SCALE)
    if circle_mask is not None:
      roi = CVUtils.mask_image(roi, CVUtils.invert_mask(circle_mask))
    else:
      return np.zeros(3)

    # Amplify colors to differentiate things like wheat from desert, brick, etc.
    for amp in self._COLOR_AMPLIFICATIONS:
      thresh = self._config.get(amp[0], color_board_img)
      roi = CVUtils.replace_range(CVUtils.to_hsv(roi), roi, thresh[0], thresh[1], amp[1])

    roi = cv2.pyrMeanShiftFiltering(roi, self._MEAN_SHIFT, self._MEAN_SHIFT)
    
    # Compute mean color
    channels = cv2.split(roi)
    return [np.uint8(np.mean(c[np.nonzero(c)])) for c in channels]


  # returns a mask that isolates this tile's circle, scaled by passed in percentage
  def _get_circle_mask(self, hex_roi, scale=1):
    circle = self._circle
    if circle is None:
      return None

    (h, w, d) = hex_roi.shape
    mask = np.zeros((h, w), np.uint8)
    # Draw mask, potentially shrink/grow radius
    cv2.circle(mask, (circle[0], circle[1]), np.uint8(circle[2]*scale), (255, 255, 255), thickness=-1)
    return mask

  # detects and returns the singular circle on the tile
  def _detect_circle(self, img):
    hex_roi = self._get_hex_roi(img)

    # Blur/erode and get circles
    img = cv2.erode(cv2.medianBlur(hex_roi, 3), np.ones((1, 1), np.uint8))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    (h, w) = gray.shape

    hough_config = self._config.get("TILE_HOUGH_CIRCLE", img)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT,1, h/hough_config[2],
                                param1=hough_config[0][1],
                                param2=hough_config[0][0],
                                minRadius=h/hough_config[1][0], maxRadius=h/hough_config[1][1])
    if circles is None:
      return None

    # Isolate circle
    # TODO assert only one circle found
    circle = np.uint8(np.around(circles))[0, :][0]
    return circle

  def _get_vertices(self, contour):
    # Compute top most point
    vertices = [v[0] for v in contour]
    (top_i, top_v) = min(enumerate(vertices), key=lambda x: x[1][1])

    def_vertex = []
    prev = None
    (x,y,w,h) = cv2.boundingRect(contour)
    for i in xrange(len(vertices)):
      v = vertices[(top_i + i) % len(vertices)]
      
      if prev is None or self._point_distance(prev, v) > int(h/2.5):
        prev = v
        def_vertex.append(v)
	if len(def_vertex) == 6:
	  break

    return def_vertex

  def _get_roi(self, img):
    (x, y, w, h) = cv2.boundingRect(self._contour)
    return img[y:y+h, x:x+w]

  def _get_hex_roi(self, img):
    hex_only = CVUtils.mask_image(img, self._hex_mask)
    return self._get_roi(hex_only)

  def _point_distance(self, pt1, pt2):
    return sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)
