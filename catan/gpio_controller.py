import RPi.GPIO as GPIO
import time, subprocess

class GPIOController(object):

  def __init__(self):
    GPIO.setmode(GPIO.BCM)

    subprocess.call('sudo sh -c "echo none > /sys/class/leds/led0/trigger"', shell=True)
    return


  def init_button(self, pin_num):
    GPIO.setup(pin_num, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    return


  def wait_for_press(self, pin_num):
    while GPIO.input(pin_num):
      time.sleep(.2)

    while not GPIO.input(pin_num):
      time.sleep(.2)
    
    return

  def wait_for_presses(self, pin_num, num_presses):
    for i in xrange(num_presses):
      self.wait_for_press(pin_num)

    return


  def led_on(self):
    subprocess.call('sudo sh -c "echo 1 >/sys/class/leds/led0/brightness"', shell=True)

  def led_off(self):
    subprocess.call('sudo sh -c "echo 0 >/sys/class/leds/led0/brightness"', shell=True)

  def led_blink(self, num=1, delay=.3):
    self.led_off()
    time.sleep(delay)
    self.led_on()
    time.sleep(delay)
    self.led_off()

