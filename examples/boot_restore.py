__author__ = "ubi de feo"
__license__ = "MPL 2.0"
__version__ = "0.4.0"
__maintainer__ = "ubi de feo [github.com/ubidefeo]"

from machine import Pin
restore_pin = Pin('D2', Pin.IN, Pin.PULL_UP)
restore_target_project = 'alvik_launcher'

def restore_target():
  if restore_pin.value() == False:
    return restore_target_project
  return None
