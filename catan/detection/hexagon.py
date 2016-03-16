import cv2
import imutils
import numpy as np

from utils.cv import CVUtils
from utils.gui import GUIUtils

#
# Detects and returns hexagon contours in the given image of a board
#
class HexagonDetector(object):

  _INITAL_EROSION = (3, 3)
  _CANNY_THRESH = { # threshold found from thresh.py tool
    'LOWER': 163,
    'UPPER': 1023
  }
  _WATER = { #HSV
    'LOWER': [60, 0, 30],
    'UPPER': [115, 255, 255]
  }
  _HEX_CONTOUR_SIZE = .25 # percent of total board


  # Returns list of hexagon contours
  def detect_hexagons(self, img):
    return self._get_contours(img)


  ####################################
  #                                  #
  # Private methods                  #
  #                                  #
  ####################################

  def _get_contours(self, img):
    # erode image first
    eroded = cv2.erode(img, np.ones(self._INITAL_EROSION, np.uint8))
    # isolate board using color thresholding
    board = self._isolate_board(eroded)
    # get edges using canny edge detction
    edges = cv2.Canny(board, self._CANNY_THRESH['LOWER'], self._CANNY_THRESH['UPPER'])
    edges = cv2.dilate(edges, np.ones(self._INITAL_EROSION, np.uint8))
    # isolate hexagons and erode to exaggerate
    hexagons = CVUtils.mask_image(board, CVUtils.invert_mask(edges))
    hexagons = cv2.erode(hexagons, np.ones(self._INITAL_EROSION, np.uint8))
    # Convert to grayscale and threshold
    gray = cv2.cvtColor(hexagons, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)[1]
    # Get markers from watershed algorithm
    markers = self._get_watershed_markers(hexagons, thresh)
    # Get countours
    return self._get_hexagon_contours(img, markers)

  def _get_water_only(self, hsv):
    return CVUtils.range_mask(hsv, self._WATER['LOWER'], self._WATER['UPPER'])

  def _isolate_board(self, img):
    # Isolate water
    hsv = CVUtils.to_hsv(img)
    water_mask = self._get_water_only(hsv)
    (h, w) = water_mask.shape

    # add 2 rows and columns for floodFill requirements
    column_zeros = np.zeros((h, 1), np.uint8)
    row_zeros = np.zeros((1, w+2), np.uint8)
    # TODO optimize this?
    floodfill_mask = np.append(column_zeros, water_mask, 1)
    floodfill_mask = np.append(floodfill_mask, column_zeros, 1)
    floodfill_mask = np.append(row_zeros, floodfill_mask, 0)
    floodfill_mask = np.append(floodfill_mask, row_zeros, 0)

    # isolate board w/ water
    cv2.floodFill(water_mask, floodfill_mask, (h/2, w/2), 255)
    board = CVUtils.mask_image(img, water_mask)

    # remove water
    return CVUtils.mask_image(board, CVUtils.invert_mask(self._get_water_only(hsv)))

  def _get_watershed_markers(self, img, thresh):
    # Taken from http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_imgproc/py_watershed/py_watershed.html
    
    # Get area that we are sure is BG
    sure_bg = cv2.dilate(thresh, np.ones(self._INITAL_EROSION, np.uint8), iterations=3)
    # Get area that we are sure is FG
    dist_transform = cv2.distanceTransform(thresh, cv2.DIST_L2, 5)
    ret, sure_fg = cv2.threshold(dist_transform, 0.7*dist_transform.max(), 255, 0)
    # Find region that we are not sure about
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg, sure_fg)
    # Label Markers
    ret, markers = cv2.connectedComponents(sure_fg)
    # Add one to all labels so that sure_bg area is not 0, but 1
    markers = markers + 1
    # Now, mark the region of unknown with zero
    markers[unknown == 255] = 0
    # Get markers
    markers = cv2.watershed(img, markers)
    return markers

  def _get_hexagon_contours(self, img, markers):
    result = []

    # allocate memory for masking each label
    (h, w, channels) = img.shape
    mask = np.zeros((h, w), dtype="uint8")

    for label in np.unique(markers):
      # if the label is zero, we are examining the 'background'
      # so simply ignore it
      if label <= 0:
        continue
     
      # clear mask and set label region in mask
      mask.fill(0)
      mask[markers == label] = 255
     
      # detect contours in the mask and grab the largest one
      cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
      c = max(cnts, key=cv2.contourArea)

      # only include contours that are small enough
      if cv2.contourArea(c) < (self._HEX_CONTOUR_SIZE*h*w):
        result.append(c)

    return result



