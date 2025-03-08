import os
from .constants import *
from sys import path as sys_path

APPS_ROOT = '/' # always add trailing '/'

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

def default_app(p = None, fall_back = None):
  f'''
  Displays or sets the default app to run on board startup or reset,
  immediately after {BOOT_FILE} has finished execution

  default_app('')             > no default app: if there is a {MAIN_FILE} in root it will be run
  default_app('some_app') > the {MAIN_FILE} file in /app_some_app will run after {BOOT_FILE}

  default_app()               > returns the default app if set

  Note: a default app is not mandatory. See list_apps()
  '''
  default_p = '' if p == None else p
  if p != None:
    if (not validate_app(default_p)) and default_p != '':
      return(OSError(9, f'Project {default_p} does not exist'))
    with open(APPS_ROOT + BOOT_CONFIG_FILE, 'w') as a_cfg:
      a_cfg.write(default_p)
      if fall_back != None:
        a_cfg.write('\n')
        a_cfg.write(fall_back)
  else:
    if fs_item_exists(APPS_ROOT + BOOT_CONFIG_FILE):
      with open(APPS_ROOT + BOOT_CONFIG_FILE, 'r') as a_cfg:
        default_p = a_cfg.readline().strip()
    else:
      default_p = None
    return default_p if default_p != None else None

# more targeted approach
def get_app(app_name):  
  if validate_app(app_name):
    app_folder = APP_PREFIX + app_name.replace(APP_PREFIX, '')
    prj_dict = {
      'name': '',
      'path': '',
      'hidden': False
    }
    prj_dict['name'] = app_folder.replace(APP_PREFIX, '')
    prj_dict['path'] = APPS_ROOT + app_folder
    if fs_item_exists(APPS_ROOT + app_folder + '/.hidden'):
      prj_dict['hidden'] = True
    return prj_dict
  else:
    return None

def get_apps(root_folder = '/'):
  for fs_item in os.ilistdir(root_folder):
    fs_item_name = fs_item[0]
    if fs_item_name[0:len(APP_PREFIX)] != APP_PREFIX:
      continue
    if validate_app(fs_item_name):
      prj_dict = {
        'name': '',
        'friendly_name': '',
        'path': '',
        'hidden': False
      }
      # app_name = fs_item_name.replace('app_', '')
      prj_dict['name'] = fs_item_name.replace('app_', '')
      prj_dict['path'] = APPS_ROOT + fs_item_name
      try:
        with open(APPS_ROOT + fs_item_name + '/' + APP_FRIENDLY_NAME_FILE, 'r') as friendly_name_file:
          friendly_name = friendly_name_file.read()
      except:
        friendly_name = ''
      
      prj_dict['friendly_name'] = prj_dict['name'] if friendly_name == '' else friendly_name
      if fs_item_exists(APPS_ROOT + fs_item_name + '/.hidden'):
        prj_dict['hidden'] = True
      yield prj_dict


def fs_item_exists(path):
  try:
    os.stat(path)
    return True
  except OSError as e:
    return False
