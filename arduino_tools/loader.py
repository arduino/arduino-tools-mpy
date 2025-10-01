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

def load_app(app_name = None, cycle_mode = False):
  if app_name == None or cycle_mode:
    return enter_default_app(cycle_mode = cycle_mode)
  return enter_app(app_name)

def enter_default_app(cycle_mode = False):
  if restore_available and restore_target():
    enter_app(restore_target())
    return None

  if fs_item_exists(APPS_ROOT + BOOT_CONFIG_FILE):
    boot_entries = []
    with open(APPS_ROOT + BOOT_CONFIG_FILE, 'r') as a_cfg:
      boot_entries = [entry.strip() for entry in a_cfg]
    
    if len(boot_entries) > 1:
      default_p = boot_entries.pop(0)
    elif len(boot_entries) == 1:
      default_p = boot_entries[0]
    else:
      default_p = ''
    # default_p = default_p.strip()
    if default_p == '':
      return None
    if len(boot_entries) > 0:
      if cycle_mode:
        boot_entries.append(default_p)
      with open(APPS_ROOT + BOOT_CONFIG_FILE, 'w') as a_cfg:
        for i, entry in enumerate(boot_entries):
          new_line = '\n' if i < len(boot_entries) - 1 else ''
          a_cfg.write(entry + new_line)
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