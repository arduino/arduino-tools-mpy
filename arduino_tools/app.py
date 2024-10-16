from arduino_tools.common import validate_app, get_app
from arduino_tools.properties import get_app_properties, update_app_properties

import os

class App:
  properties = {}
  def __init__(self, app_name):
    self.app_name = app_name
    if not validate_app(app_name):
      raise ValueError('Invalid app')
    self.properties = get_app_properties(app_name)
    os.chdir(get_app(app_name)['path'])
  
  def get_property(self, property):
    return self.properties.get(property)

  def set_property(self, property, value):
    self.properties[property] = value
  
  def save_properties(self):
    update_app_properties(self.app_name, self.properties)
