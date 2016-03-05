import cv2
import imutils
import numpy as np


class GUIUtils(object):

  @staticmethod
  def show_image(image, name="Window"):
    cv2.imshow(name, image)
    cv2.waitKey()

  @staticmethod
  def update_image(image, name="Window"):
    cv2.imshow(name, image)
  
  @staticmethod
  def wait():
    cv2.waitKey()
