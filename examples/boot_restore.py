from machine import Pin
restore_pin = Pin('D2', Pin.IN, Pin.PULL_UP)
restore_target_project = 'alvik_launcher'

def restore_target():
  if restore_pin.value() == False:
    return restore_target_project
  return None
