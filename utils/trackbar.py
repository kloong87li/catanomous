import cv2
import imutils
import numpy as np

from utils.cv import CVUtils
from utils.gui import GUIUtils


class TrackbarWindow(object):

  def __init__(self):

    # Create window
    cv2.namedWindow(self.get_window_name())

    # Create trackbars 
    maxes = self.get_maxes()
    values = self.get_values()
    for key in maxes:
      cv2.createTrackbar(key, self.get_window_name(), 
                          values[key],
                          maxes[key],
                          self._callback_for(key))

  def _callback_for(self, key_name):
    return lambda v: self._value_changed(v, key_name)

  def _value_changed(self, value, name):
    self.on_value_change(value, name)
    self.show_image()

  def show_image(self):
    (img, width) = self.get_image()
    GUIUtils.update_image(imutils.resize(img, width=width), self.get_window_name())
    return

  def close_image(self):
    cv2.destroyWindow(self.get_window_name())

  # Implement these methods #
  def get_window_name(self):
    return "Window"

  def on_value_change(self, value, name):
    pass

  def get_image(self):
    return (None, None) # (image, width)

  def get_maxes(self):
    return {}

  def get_values(self):
    return {}

  def get_result(self):
    # Return the resulting values of the thresholding
    return None
    






class ColorThreshTrackbar(TrackbarWindow):

  _WINDOW_NAME = 'Color Threshold'

  def __init__(self, img, defaults=None, name=None, replaced_color=None):
    if name is not None:
      self._WINDOW_NAME = name

    self._replaced_color = replaced_color or [255, 255, 255]
    self._img = img
    
    # convert to hsv for color processing
    self._hsv = CVUtils.to_hsv(img)

    self._max_ranges = {
      'H_lower': 179,
      'H_upper': 179,
      'S_lower': 255,
      'S_upper': 255,
      'V_lower': 255,
      'V_upper': 255
    }

    if defaults is None:
      self._bounds = {
        'H_lower': 10,
        'H_upper': 40,
        'S_lower': 100,
        'S_upper': 255,
        'V_lower': 175,
        'V_upper': 255
      }
    else:
      self._bounds = {
        'H_lower': defaults[0][0],
        'H_upper': defaults[1][0],
        'S_lower': defaults[0][1],
        'S_upper': defaults[1][1],
        'V_lower': defaults[0][2],
        'V_upper': defaults[1][2]
      }

    super(ColorThreshTrackbar, self).__init__()

  def get_window_name(self):
    return self._WINDOW_NAME

  def on_value_change(self, value, name):
    self._bounds[name] = value

  def get_image(self):
    lower = [self._bounds['H_lower'], self._bounds['S_lower'], self._bounds['V_lower']]
    upper = [self._bounds['H_upper'], self._bounds['S_upper'], self._bounds['V_upper']]
    print lower, upper
    img = CVUtils.replace_range(self._hsv, self._img, lower, upper, self._replaced_color)
    return (img, 700)

  def get_maxes(self):
    return self._max_ranges

  def get_values(self):
    return self._bounds

  def get_result(self):
    return ([self._bounds["H_lower"], self._bounds["S_lower"], self._bounds["V_lower"]], 
            [self._bounds["H_upper"], self._bounds["S_upper"], self._bounds["V_upper"]])



class GrayThreshTrackbar(TrackbarWindow):
  _WINDOW_NAME = 'Grayscale Threshold'

  def __init__(self, gray, defaults=None, name=None, replaced_color=None):
    if name is not None:
      self._WINDOW_NAME = name

    self._gray = gray
    # self._gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    self._maxes = {
      'Lower': 255,
      'Upper': 255,
    }

    if defaults is None:
      self._values = {
        'Lower': 10,
        'Upper': 100,
      }
    else:
      self._values = {
        'Lower': defaults[0],
        'Upper': defaults[1]
      }

    super(GrayThreshTrackbar, self).__init__()

  def get_window_name(self):
    return self._WINDOW_NAME

  def on_value_change(self, value, name):
    self._values[name] = value

  def get_image(self):
    lower = self._values['Lower']
    upper = self._values['Upper']
    mask = CVUtils.range_mask(self._gray, lower, upper)
    return (mask, 700)

  def get_maxes(self):
    return self._maxes

  def get_values(self):
    return self._values

  def get_result(self):
    return (self._values['Lower'], self._values['Upper'])




class CannyTrackbar(TrackbarWindow):
  _WINDOW_NAME = 'Canny Threshold'

  def __init__(self, img, defaults=None, name=None, replaced_color=None):
    if name is not None:
      self._WINDOW_NAME = name

    self._img = img

    self._maxes = {
      'Lower': 1024,
      'Upper': 1024,
    }

    if defaults is None:
      self._values = {
        'Lower': 200,
        'Upper': 300,
      }
    else:
      self._values = {
        'Lower': defaults[0],
        'Upper': defaults[1]
      }

    super(CannyTrackbar, self).__init__()

  def get_window_name(self):
    return self._WINDOW_NAME

  def on_value_change(self, value, name):
    self._values[name] = value

  def get_image(self):
    lower = self._values['Lower']
    upper = self._values['Upper']
    print upper, lower
    edges = cv2.Canny(self._img, lower, upper)
    return (edges, 700)

  def get_maxes(self):
    return self._maxes

  def get_values(self):
    return self._values

  def get_result(self):
    return (self._values['Lower'], self._values['Upper'])



class HoughTrackbar(TrackbarWindow):
  _WINDOW_NAME = 'Hough Circle Threshold'

  # ((lower, upper), (minr, maxr), min_dist)
  # min/maxes are proportions of height
  def __init__(self, img, defaults=None, name=None, replaced_color=None):
    if name is not None:
      self._WINDOW_NAME = name

    self._img = img

    self._maxes = {
      'Lower': 100,
      'Upper': 100,
      'Min_R': 50,
      'Max_R': 50,
      'Min_Dist': 25
    }

    if defaults is None:
      self._values = {
        'Lower': 15,
        'Upper': 60,
        'Min_R': 40,
        'Max_R': 15,
        'Min_Dist': 8
      }
    else:
      self._values = {
        'Lower': defaults[0][0],
        'Upper': defaults[0][1],
        'Min_R': defaults[1][0],
        'Max_R': defaults[1][1],
        'Min_Dist': defaults[2]
      }

    super(HoughTrackbar, self).__init__()

  def get_window_name(self):
    return self._WINDOW_NAME

  def on_value_change(self, value, name):
    self._values[name] = value

  def get_image(self):
    lower = self._values['Lower']
    upper = self._values['Upper']
    minR = self._values['Min_R']
    maxR = self._values['Max_R']
    minDist = self._values['Min_Dist']
    print upper, lower, minR, maxR, minDist

    gray = cv2.cvtColor(self._img, cv2.COLOR_BGR2GRAY)
    (h, w) = gray.shape
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT,1, h/minDist,
                                param1=upper,
                                param2=lower,
                                minRadius=h/minR,maxRadius=h/maxR)

    circle_img = np.copy(self._img)

    if circles is not None:
      for circle in circles[0]:
        # Draw circles on mask
        cv2.circle(circle_img, (circle[0], circle[1]), np.uint8(circle[2]), (0, 0, 255), thickness=2)

    return (circle_img, 700)

  def get_maxes(self):
    return self._maxes

  def get_values(self):
    return self._values

  def get_result(self):
    return (
              (self._values['Lower'], self._values['Upper']),
              (self._values['Min_R'], self._values['Max_R']),
              self._values['Min_Dist']
            )

