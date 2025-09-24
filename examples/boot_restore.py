# This file, if present, is executed on every boot/reset.
# It can be used to force booting into a predefined app,
# such as a launcher application, when a specific condition is met.

# In this example, the condition is the state of pin D2:
# At boot time, if the Arduino Tools Loader is enabled, the method
# enter_default_app() will check for the presence of this file,
# and if it exists, it will call the restore_target() method from it.
# A return value of None will be ignored, while a string will be used
# to enter the app with that name, in this case 'app_launcher'.

from machine import Pin
restore_pin = Pin('D2', Pin.IN, Pin.PULL_UP)
restore_target_app = 'app_launcher'

def restore_target():
  if restore_pin.value() == False:
    return restore_target_app
  return None
