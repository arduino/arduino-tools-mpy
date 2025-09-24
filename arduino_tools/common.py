import os
from .constants import *
import sys

def get_root(has_flash_mount = True):
  if '/flash' in sys.path:
    return '/flash/'
  else:
    return '/'

APPS_ROOT = get_root()

try:
  import tarfile
  from tarfile import write
  ALLOW_EXPORT = True
except ImportError as e:
  ALLOW_EXPORT = False

try:
  import network
  NETWORK_UPDATE = True
except ImportError:
  NETWORK_UPDATE = False

def validate_app(app_name):
  app_folder = APP_PREFIX + app_name.replace(APP_PREFIX, '')
  main_py_path = APPS_ROOT + app_folder + '/main.py'
  main_mpy_path = APPS_ROOT + app_folder + '/main.mpy'
  verify_main = fs_item_exists(main_py_path) or fs_item_exists(main_mpy_path)
  properties_file_path = APPS_ROOT + app_folder + '/' + APP_PROPERTIES
  if verify_main and fs_item_exists(properties_file_path):
    return True
  else:
    return False

def default_app(app_name = None, fall_back = None):
  default_app_name = '' if app_name == None else app_name
  if app_name != None:
    if (not validate_app(default_app_name)) and default_app_name != '':
      return(OSError(9, f'Project {default_app_name} does not exist'))
    with open(APPS_ROOT + BOOT_CONFIG_FILE, 'w') as a_cfg:
      a_cfg.write(default_app_name)
      if fall_back != None:
        a_cfg.write('\n')
        a_cfg.write(fall_back)
  else:
    if fs_item_exists(APPS_ROOT + BOOT_CONFIG_FILE):
      with open(APPS_ROOT + BOOT_CONFIG_FILE, 'r') as a_cfg:
        default_app_name = a_cfg.readline().strip()
    else:
      default_app_name = ''
    return default_app_name if default_app_name != '' else None

# more targeted approach
def get_app(app_name):  
  if validate_app(app_name):
    app_folder = APP_PREFIX + app_name.replace(APP_PREFIX, '')
    app_dict = {
      'name': '',
      'path': '',
      'hidden': False
    }
    app_dict['name'] = app_folder.replace(APP_PREFIX, '')
    app_dict['path'] = APPS_ROOT + app_folder
    if fs_item_exists(APPS_ROOT + app_folder + '/.hidden'):
      app_dict['hidden'] = True
    return app_dict
  else:
    return None

def get_apps(root_folder = None):
  if root_folder is None:
    root_folder = APPS_ROOT
  for fs_item in os.ilistdir(root_folder):
    fs_item_name = fs_item[0]
    if fs_item_name[0:len(APP_PREFIX)] != APP_PREFIX:
      continue
    if validate_app(fs_item_name):
      app_dict = {
        'name': '',
        'friendly_name': '',
        'path': '',
        'hidden': False
      }
      # app_name = fs_item_name.replace('app_', '')
      app_dict['name'] = fs_item_name.replace('app_', '')
      app_dict['path'] = APPS_ROOT + fs_item_name
      try:
        with open(APPS_ROOT + fs_item_name + '/' + APP_FRIENDLY_NAME_FILE, 'r') as friendly_name_file:
          friendly_name = friendly_name_file.read()
      except:
        friendly_name = ''
      
      app_dict['friendly_name'] = app_dict['name'] if friendly_name == '' else friendly_name
      if fs_item_exists(APPS_ROOT + fs_item_name + '/.hidden'):
        app_dict['hidden'] = True
      yield app_dict


def fs_item_exists(path):
  try:
    os.stat(path)
    return True
  except OSError as e:
    return False
