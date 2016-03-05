import cv2
import imutils
import numpy as np


# Decides if a given contour is a hexagon or not
def is_hexagon(c):
  # approximate the contour
  peri = cv2.arcLength(c, True)
  approx = cv2.approxPolyDP(c, 0.04 * peri, True)

  # if the shape is a hexagon, it will have 6 vertices
  if len(approx) == 3:
    return True
  else:
    return False


# Reduce colors in image by the given ratio
# to reduce colors from 256^3 to 64, 256 per channel -> 4 per channel:
# img = color_reduce(img, 256/8)
def color_reduce(img, ratio):
  # TODO optimize with right shift instead of division
  table = np.array([np.uint8(i / ratio * ratio) for i in xrange(256)])
  return cv2.LUT(img, table)


def show_image(image, name="Window"):
  cv2.imshow(name, image)
  cv2.waitKey(0)


# removes a color from hsv image and replaces it with new color
# bounds are hsv bounds
def mask_color(hsv, img, lower, upper, new_color):
  mask = cv2.inRange(hsv, np.array(lower, np.uint8), np.array(upper, np.uint8))
  inverted = cv2.bitwise_not(mask)
  black_mask = cv2.bitwise_and(img, np.array([0, 0, 0], np.uint8), mask=mask)
  color_mask = cv2.bitwise_or(black_mask, np.array(new_color, np.uint8), mask=mask)
  masked = cv2.bitwise_and(img, img, mask=inverted)
  return cv2.add(masked, color_mask)


def main():
  test_img = "images/1536x2048.jpg"

  # load the image and resize it
  orig = cv2.imread(test_img)
  img = imutils.resize(orig, width=1000)
  ratio = orig.shape[0] / float(img.shape[0])
  show_image(img)

  # mean shift filter
  # img = cv2.pyrMeanShiftFiltering(img, 10, 15)

  # convert to hsv for color processing
  hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
  img = mask_color(hsv, img, [10,100,175], [40,255,255], [0, 255, 255])
  show_image(img)

  # erode
  img = cv2.erode(img, np.ones((3, 3), np.uint8))
  show_image(img)

  # grayscale and threshold
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV)[1]

  cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  cnts = cnts[0]
  for c in cnts:
    print cv2.boundingRect(c)

  show_image(thresh)
  
  
  


if __name__ == "__main__":
  main()