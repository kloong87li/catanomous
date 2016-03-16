import cv2
import numpy as np

from utils.cv import CVUtils
from utils.gui import GUIUtils

from .tile_color import TileColorDetector
from .tile_num import TileNumDetector



class TileDetector(object):

  _MEAN_SHIFT = 10
  _COLOR_AMPLIFICATIONS = [
    # lower, upper, new color
    ([0, 200, 200], [36, 255, 255], [255, 255, 255]),  # wheat
    ([2, 149, 117], [9, 255, 255], [0, 0, 255])        # brick
  ]
  _CIRCLE_SCALE = 1.1


  def __init__(self, contour, img):
    self._contour = contour

    # Store ROI
    self._hex_roi = self._get_roi(img)

    # Initialize detectors
    self._color_detect = TileColorDetector()
    self._num_detect = TileNumDetector(self._hex_roi)

    self._resource = None
    self._number = None


  # Detects the resource using the result of the kmeans algo
  def detect_resource(self, kmeans_res):
    self._resource = self._color_detect.detect_resource(self._get_roi(kmeans_res))


  # Returns mean color of this hexagon
  # includes some preprocessing to help make each mean unique
  def get_representative_color(self):
    roi = cv2.pyrMeanShiftFiltering(self._hex_roi, self._MEAN_SHIFT, self._MEAN_SHIFT)
    
    # Eliminate circlular number piece
    circle_mask = self._get_circle_mask(self._CIRCLE_SCALE)
    if circle_mask is not None:
      roi = CVUtils.mask_image(roi, CVUtils.invert_mask(circle_mask))

    # Amplify colors to differentiate things like wheat from desert, brick, etc.
    for amp in self._COLOR_AMPLIFICATIONS:
      roi = CVUtils.replace_range(CVUtils.to_hsv(roi), roi, amp[0], amp[1], amp[2])

    GUIUtils.show_image(roi)
    
    # Compute mean color
    channels = cv2.split(roi)
    return [np.uint8(np.mean(c[np.nonzero(c)])) for c in channels]


  # returns circle mask, scaled by passed in percentage
  def _get_circle_mask(self, scale=1):
    circle = self._detect_circle()
    if circle is None:
      return None

    (h, w, d) = self._hex_roi.shape
    mask = np.zeros((h, w), np.uint8)
    # Draw mask, potentially shrink/grow radius
    cv2.circle(mask, (circle[0], circle[1]), np.uint8(circle[2]*scale), (255, 255, 255), thickness=-1)
    return mask

  def _detect_circle(self):
    # Blur and get circles
    gray = cv2.cvtColor(cv2.medianBlur(self._hex_roi, 5), cv2.COLOR_BGR2GRAY)
    (h, w) = gray.shape
    circles = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,1, w/2,
                                param1=50,param2=30,minRadius=w/10,maxRadius=w/3)
    if circles is None:
      return None

    # Isolate circle
    # TODO assert only one circle found
    circle = np.uint8(np.around(circles))[0, :][0]
    return circle

  def _get_roi(self, img):
    (x, y, w, h) = cv2.boundingRect(self._contour)
    return img[y:y+h, x:x+w]

