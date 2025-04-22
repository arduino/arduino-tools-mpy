from .common import validate_app
from .loader import enter_app
from .properties import get_app_properties, update_app_properties
import os

class App:
  properties = {}
  def __init__(self, app_name):
    self.app_name = app_name
    self.app_updater = None
    if not validate_app(app_name):
      raise ValueError('Invalid app')
    self.properties = get_app_properties(app_name)
    if os.getcwd() != self.get_path():
      enter_app(app_name)
  
  def get_property(self, property):
    return self.properties.get(property)

  def set_property(self, property, value):
    self.properties[property] = value
  
  def save_properties(self):
    update_app_properties(self.app_name, self.properties)

  def get_path(self):
    return self.get_property('path')

  def update_app(self):
    self.app_updater = __import__('arduino_apps.updater')
    updater = __import__('arduino_apps.updater')
    updater.updater.check_for_updates(self.app_name)
    # self.app_updater.check_for_updates(self.app_name)