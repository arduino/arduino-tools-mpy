# from sys import path as sys_path
import sys
import os
from .constants import *
from .common import *

try:
  from boot_restore import restore_target
  restore_available = True
except ImportError:
  restore_available = False

default_path = sys.path.copy()

def load_app(app_name = None):
  if app_name == None:
    return enter_default_app()
  return enter_app(app_name)

def enter_default_app():
  if restore_available and restore_target():
    enter_app(restore_target())
    return None

  if fs_item_exists(APPS_ROOT + BOOT_CONFIG_FILE):
    with open(APPS_ROOT + BOOT_CONFIG_FILE, 'r') as a_cfg:
      default_p = a_cfg.readline().strip()
      reboot_to = a_cfg.readline().strip()
    if default_p == '':
      return None
    if reboot_to != '':
      with open(APPS_ROOT + BOOT_CONFIG_FILE, 'w') as a_cfg:
        a_cfg.write(reboot_to)
    return enter_app(default_p)
  return None


def enter_app(app_name):
  app = get_app(app_name)
  if app == None:
    return None
  
  # Try to remove the default local path
  # which will be added back later as the first element
  sys.path = default_path.copy()
  try:
    sys.path.remove('')
  except ValueError:
    pass
  sys.path.insert(0, app['path'] + '/lib')
  sys.path.insert(0, '')
  os.chdir(app['path'])
  return True

def restore_path():
  sys.path = default_path.copy()
  os.chdir('/')