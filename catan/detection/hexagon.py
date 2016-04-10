import cv2
import imutils
import numpy as np

from utils.cv import CVUtils
from utils.gui import GUIUtils

#
# Detects and returns hexagon contours in the given image of a board
#
class HexagonDetector(object):

  def __init__(self, config):
    self._config = config

  _INITAL_EROSION = (1, 1)
  _HEX_CONTOUR_MAX = .25 # percent of total board
  _HEX_CONTOUR_MIN = .005 # percent of total board

  _DIST_TRANS_PERCENT = .75 # percent of max distance


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
    canny_config = self._config.get("BOARD_CANNY", board)
    edges = cv2.Canny(board, canny_config[0], canny_config[1])
    edges = cv2.dilate(edges, np.ones((3,3), np.uint8))

    # Use hough line transform to get hexagon edges only
    # (h, w, z) = board.shape
    # line_config = self._config.get("BOARD_HOUGH_LINE", edges)
    # lines = cv2.HoughLinesP(edges, 1, np.pi/120, line_config[0], None,
    #                         line_config[1], line_config[2])
    # line_mask = np.zeros(edges.shape, np.uint8)
    # if lines is not None:
    #   for line in lines:
    #     # Draw lines on board
    #     line = line[0]
    #     pt1 = (line[0],line[1])
    #     pt2 = (line[2],line[3])
    #     cv2.line(line_mask, pt1, pt2, 255, 1)

    # isolate hexagons and erode to exaggerate
    # edges = cv2.bitwise_and(edges, line_mask)
    hexagons = CVUtils.mask_image(board, CVUtils.invert_mask(edges))
    hexagons = cv2.erode(hexagons, np.ones(self._INITAL_EROSION, np.uint8))
    # Convert to grayscale and threshold
    gray = cv2.cvtColor(hexagons, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 2, 255, cv2.THRESH_BINARY)[1]
    # Get markers from watershed algorithm
    markers = self._get_watershed_markers(hexagons, thresh)
    # Get countours
    return self._get_hexagon_contours(img, markers)

  def _get_water_only(self, img, hsv):
    water_thresh = self._config.get("BOARD_COLOR_WATER", img)
    return CVUtils.range_mask(hsv, water_thresh[0], water_thresh[1])

  def _isolate_board(self, img):
    # Isolate water
    hsv = CVUtils.to_hsv(img)
    water_mask = self._get_water_only(img, hsv)
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
    cv2.floodFill(water_mask, floodfill_mask, (w/2, h/2), 255)
    board = CVUtils.mask_image(img, water_mask)

    # remove water
    return CVUtils.mask_image(board, CVUtils.invert_mask(self._get_water_only(img, hsv)))

  def _get_watershed_markers(self, img, thresh):
    # Taken from http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_imgproc/py_watershed/py_watershed.html

    # Get area that we are sure is BG
    sure_bg = cv2.dilate(thresh, np.ones((4, 4), np.uint8), iterations=5)
    # Get area that we are sure is FG
    dist_transform = cv2.distanceTransform(thresh, cv2.DIST_L1, 3)
    ret, sure_fg = cv2.threshold(dist_transform, self._DIST_TRANS_PERCENT*dist_transform.max(), 255, 0)
    sure_fg = np.uint8(sure_fg)

    # Modification to above, use circles as reference for markers
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    (h, w) = thresh.shape
    hough_config = self._config.get("BOARD_HOUGH_CIRCLE", img)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT,1, h/hough_config[2],
                                param1=hough_config[0][1],
                                param2=hough_config[0][0],
                                minRadius=h/hough_config[1][0],maxRadius=h/hough_config[1][1])
    circle_mask = np.zeros((h, w), np.uint8)
    for circle in circles[0]:
      # Draw circles on mask
      cv2.circle(circle_mask, (circle[0], circle[1]), np.uint8(circle[2]), 255, thickness=-1)
    # dilate to make circles bigger
    # circle_mask = cv2.dilate(circle_mask, np.ones(self._INITAL_EROSION, np.uint8), iterations=2)
    sure_fg = cv2.bitwise_or(sure_fg, circle_mask)

    # Find region that we are not sure about
    unknown = cv2.subtract(sure_bg, sure_fg)

    # Label Markers
    ret, markers = cv2.connectedComponents(sure_fg)
    # Add one to all labels so that sure_bg area is not 0, but 1
    markers = markers + 1
    # Now, mark the region of unknown with zero and region of known with non-zero
    markers[unknown == 255] = 0
    # Get markers
    markers = cv2.watershed(cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR), markers)
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
      c = cv2.convexHull(c)
      c = cv2.approxPolyDP(c, 3, True)

      # only include contours that are small enough and big enough
      area = cv2.contourArea(c)
      if (self._HEX_CONTOUR_MIN*h*w) < area and area < (self._HEX_CONTOUR_MAX*h*w):
        result.append(c)

    return result



