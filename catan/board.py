import cv2
import imutils
import numpy as np

from utils.cv import CVUtils
from utils.gui import GUIUtils

from .hexagon import CatanHexagon


class BoardDetector(object):

  def __init__(self, img):
    contours = self._get_init_contours(img)
    mean_colors = np.copy(img)

    # Create and process each hexagon
    self._hexagons = []
    for c in contours:
      hexagon = CatanHexagon(c, img)
      self._hexagons.append(hexagon)

      # Replace hexagon with its mean color
      mean = hexagon.get_mean_color()
      np.copyto(mean_colors, CVUtils.replace_color(mean_colors, hexagon.get_hex_mask(), mean))

    # Isolate hexagons in original image
    contour_mask = np.zeros((mean_colors.shape[0], mean_colors.shape[1]), np.uint8)
    cv2.drawContours(contour_mask, contours, -1, [255, 255, 255], thickness=-1)
    mean_colors = CVUtils.mask_image(mean_colors, contour_mask)

    # Run kmeans
    kmeans = self._kmeans(mean_colors)

    # Classify resources based on the mean
    for h in self._hexagons:
      h.classify_resource(kmeans)

    GUIUtils.show_image(kmeans)

  def get_hexagons(self):
    return self._hexagons


  ####################################
  #                                  #
  # Computer Vision related methods  #
  #                                  #
  ####################################

  def _get_init_contours(self, img):
    # erode image first
    eroded = cv2.erode(img, np.ones((3, 3), np.uint8))
    # isolate board using color thresholding
    board = self._isolate_board(eroded)
    # get edges using canny edge detction
    edges = cv2.Canny(board, 163, 1023) # threshold found from thresh.py tool
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8))
    # isolate hexagons and erode to exaggerate
    hexagons = CVUtils.mask_image(board, CVUtils.invert_mask(edges))
    hexagons = cv2.erode(hexagons, np.ones((3, 3), np.uint8))
    # Convert to grayscale and threshold
    gray = cv2.cvtColor(hexagons, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)[1]
    # Get markers from watershed algorithm
    markers = self._get_watershed_markers(hexagons, thresh)
    # Get countours
    return self._get_hexagon_contours(img, markers)

  def _get_water_only(self, hsv):
    return CVUtils.range_mask(hsv, [60, 0, 30], [115, 255, 255])

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
    sure_bg = cv2.dilate(thresh, np.ones((3,3),np.uint8), iterations=3)
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
      if cv2.contourArea(c) < (.25*h*w):
        result.append(c)

    return result

  def _kmeans(self, img):
    Z = img.reshape((-1,3))
    # convert to np.float32
    Z = np.float32(Z)

    # Define criteria, number of clusters(K) and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 1, 2.0)
    K = 8
    ret,label,center = cv2.kmeans(Z, K, None, criteria, 1, cv2.KMEANS_PP_CENTERS)

    # Now convert back into uint8, and make original image
    center = np.uint8(center)
    res = center[label.flatten()]
    return res.reshape((img.shape))



