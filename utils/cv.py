import cv2
import imutils
import numpy as np


class CVUtils(object):

  @staticmethod
  def to_hsv(img):
    # convert to hsv for color processing
    return cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

  # Reduce colors in image by the given ratio
  # to reduce colors from 256^3 to 64, 256 per channel -> 4 per channel:
  # img = color_reduce(img, 256/8)
  @staticmethod
  def color_reduce(img, ratio):
    # TODO optimize with right shift instead of division
    table = np.array([np.uint8(i / ratio * ratio) for i in xrange(256)])
    return cv2.LUT(img, table)


  @staticmethod
  def range_mask(img, lower, upper):
    if isinstance(lower, list):
      return cv2.inRange(img, np.array(lower, np.uint8), np.array(upper, np.uint8))
    else:
      return cv2.inRange(img, lower, upper)

  # removes a color from hsv image and replaces it with new color
  # bounds are hsv bounds
  @staticmethod
  def replace_range(hsv, img, lower, upper, new_color):
    mask = CVUtils.range_mask(hsv, lower, upper)
    return CVUtils.replace_color(img, mask, new_color)

  @staticmethod
  def replace_color(img, mask, new_color):
    inverted = CVUtils.invert_mask(mask)
    black_mask = cv2.bitwise_and(img, np.array([0, 0, 0], np.uint8), mask=mask)
    color_mask = cv2.bitwise_or(black_mask, np.array(new_color, np.uint8), mask=mask)
    masked = CVUtils.mask_image(img, inverted)
    return cv2.add(masked, color_mask)

  @staticmethod
  def invert_mask(mask):
    return cv2.bitwise_not(mask)

  @staticmethod
  def mask_image(img, mask):
    return cv2.bitwise_and(img, img, mask=mask)








