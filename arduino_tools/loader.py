from sys import path as sys_path
import os
from .constants import *
from .common import *

try:
  from boot_restore import restore_target
  restore_available = True
except ImportError:
  restore_available = False

default_path = sys_path.copy()

def enter_default_app():
  if restore_available and restore_target():
    enter_app(restore_target())
    return None

  if fs_item_exists(APPS_ROOT + BOOT_CONFIG_FILE):
    a_cfg = open(APPS_ROOT + BOOT_CONFIG_FILE, 'r')
    default_p = a_cfg.readline().strip()
    reboot_to = a_cfg.readline().strip()
    a_cfg.close()
    if reboot_to != '':
      a_cfg = open(APPS_ROOT + BOOT_CONFIG_FILE, 'w')
      a_cfg.write(reboot_to)
      a_cfg.close()
    return enter_app(default_p)

  return None


def enter_app(app_name):
  app = get_app(app_name)
  if app == None:
    return None
  
  # Try to remove the default local path
  # which will be added back later as the first element
  try:
    sys_path.remove('')
  except ValueError:
    pass
  sys_path.insert(0, app['path'] + '/lib')
  sys_path.insert(0, '')
  os.chdir(app['path'])
  return True

def restore_path():
  global sys_path
  sys_path = default_path.copy()
  os.chdir('/')