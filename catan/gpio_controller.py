import RPi.GPIO as GPIO
import time

class GPIOController(object):

  def __init__(self):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(16, GPIO.OUT)

    import subprocess
    subprocess.call('sudo sh -c "echo none > /sys/class/leds/led0/trigger"', shell=True)
    return


  def init_button(self, pin_num):
    GPIO.setup(pin_num, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    return


  def wait_for_press(self, pin_num):
    while GPIO.input(pin_num):
      time.sleep(.2)
    
    return


  def wait_for_presses(self, pin_num, num_presses):
    for i in xrange(num_presses):
      self.wait_for_press(pin_num)

    return


  def led_on(self):
    GPIO.output(16, GPIO.LOW)

  def led_off(self):
    GPIO.output(16, GPIO.HIGH)

  def led_blink(self, num=1):
    self.led_off()
    time.sleep(.3)
    self.led_on()
    time.sleep(.3)
    self.led_off()

