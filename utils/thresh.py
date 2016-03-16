import cv2
import imutils
import numpy as np

from .cv import CVUtils
from .gui import GUIUtils
from .trackbar import ColorThreshTrackbar, GrayThreshTrackbar, CannyTrackbar



def do_canny(img):
  canny = CannyTrackbar(img)
  canny.show_image()
  GUIUtils.wait()
  canny.close_image()
  return canny.get_image()[0]

def do_color_thresh(img):
  thresh = ColorThreshTrackbar(img)
  thresh.show_image()
  GUIUtils.wait()
  thresh.close_image()
  return thresh.get_image()[0]

def do_gray_thresh(img):
  thresh = GrayThreshTrackbar(img)
  thresh.show_image()
  GUIUtils.wait()
  thresh.close_image()
  return thresh.get_image()[0]

def main():
  test_img = "images/1536x2048.jpg"

  # load the image and resize it
  orig = cv2.imread(test_img)
  img = imutils.resize(orig, width=1000)
  ratio = orig.shape[0] / float(img.shape[0])

  # erode
  img = cv2.erode(img, np.ones((3, 3), np.uint8))

  do_canny(img)
  do_color_thresh(img)
  do_gray_thresh(img)


  # get rid of some colors
  # hsv = CVUtils.to_hsv(img)
  # white = [0, 0, 0]
  # img = CVUtils.replace_range(hsv, img, [0, 0, 8], [14, 172, 85], [14, 172, 85]) # mountains
  # img = CVUtils.replace_range(hsv, img, [19, 0, 7], [179, 255, 255], [179, 255, 255]) # greens
  # img = CVUtils.replace_range(hsv, img, [10, 100, 175], [40, 255, 255], [40, 255, 255]) # sand
  # img = CVUtils.replace_range(hsv, img, [0, 237, 0], [179, 255, 255], [179, 255, 255]) # brick

  # thresh = ThresholdedImage(img)
  # thresh.show_image()
  # GUIUtils.wait()
  # thresh.close_image()

  # GrayThreshImage(cv2.cvtColor(img, cv2.COLOR_HSV2BGR)).show_image()
  # GUIUtils.wait()

  # grayscale and threshold
  # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  # thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV)[1]

  # show_image(thresh)
  
  
  


if __name__ == "__main__":
  main()
