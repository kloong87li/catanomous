from utils.camera import Camera
from catan.config import CVConfig

from utils.gui import GUIUtils
from utils.cv import CVUtils

import cv2
import imutils



def process_token(token, camera):
  if token == 'AWB':
    val1 = raw_input("Val1: ")
    val2 = raw_input("Val2: ")
    camera.set_setting(token, (float(val1), float(val2)))
  elif token == 'ZOOM':
    print "Not supported yet."
  elif token == 'RESOLUTION':
    val1 = raw_input("W: ")
    val2 = raw_input("H: ")
    camera.set_setting(token, (int(val1), int(val2)))
  else:
    value = raw_input("New value: ")
    camera.set_setting(token, int(value))

def get_picture(camera):
  img = imutils.resize(camera.capture(), width=1200)
  GUIUtils.update_image(img)
  cv2.waitKey(100)
  return img

def main():
  cam_config = "config/camera.json"
  config = CVConfig("config/config.json")
  config.load_cam_config(cam_config)

  camera = Camera(config)

  try:
    camera.start()

    while (True):
      print "Enter a camera setting to change. (or 'P' to preview, 'X' to quit, 'V' to see current settings, 'S' to save image)"
      token = raw_input("Input: ")

      if token == 'P':
        get_picture(camera)
      elif token == 'X':
        config.save_cam_config(cam_config)
        break
      elif token == 'V':
        settings = config.get_cam_all()
        for key in settings:
          print key, ": ", settings[key]
      elif token == 'S':
        img = get_picture(camera)
        path = raw_input("Path: ")
        CVUtils.save_img(img, path)
      else:
        process_token(token, camera)
        get_picture(camera)

  finally:
    camera.stop()



if __name__ == "__main__":
  main()
