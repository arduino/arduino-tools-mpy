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
    boot_entries = []
    with open(APPS_ROOT + BOOT_CONFIG_FILE, 'r') as a_cfg:
      boot_entries = a_cfg.readlines()
    
    if len(boot_entries) > 1:
      default_p = boot_entries.pop(0)
    elif len(boot_entries) == 1:
      default_p = boot_entries[0]
    else:
      default_p = ''
    default_p = default_p.strip()
    if default_p == '':
      return None
    if len(boot_entries) > 0:
      with open(APPS_ROOT + BOOT_CONFIG_FILE, 'w') as a_cfg:
        for entry in boot_entries:
          a_cfg.write(entry)
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