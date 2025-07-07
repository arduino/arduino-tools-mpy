from .common import *
from .properties import *
from .files import *
from .loader import *
from .helpers import *
import errno
 
import os

import json
from time import time as tm

try:
  import mip
  MIP_SUPPORT = True
except ImportError:
  MIP_SUPPORT = False

try:
  import tarfile

except ImportError:
  print('tarfile not installed')
  print('install tarfile-write')
  
# THE FOLLOWING METHODS ARE IMPORTED FROM THE
# COMMON/LOADER MODULE TO AVOID CODE DUPLICATION.
# PATH and PREFIX are defined there as well as
# 
# default_app(p = None)
# get_apps()
# get_apps(root_folder = '/', debug = False)

BOOT_BACKUP_FILE = 'boot_backup.py'
EXPORT_FOLDER = f'__{APP_PREFIX}exports'
BACKUP_FOLDER = f'__{APP_PREFIX}backups'

app_data_cache = {}

def enable_apps():
  fs_root()
  if fs_item_exists(BOOT_FILE):
    os.rename(BOOT_FILE, BOOT_BACKUP_FILE)
  
  # create bootloader from template
  success, message, exception = template_to_file('boot_apps.tpl', f'{APPS_ROOT}{BOOT_FILE}')
  if not success:
    print(f'Error creating {BOOT_FILE}: {message}')
    return None

  # create boot config file
  if not fs_item_exists(BOOT_CONFIG_FILE):
    config_file = open(BOOT_CONFIG_FILE, 'w')
    config_file.close()


def disable_apps(force_delete_boot = False):
  fs_root()
  if fs_item_exists(BOOT_BACKUP_FILE):
    os.rename(BOOT_BACKUP_FILE, BOOT_FILE)
  else:
    show_cursor(False)
    if not force_delete_boot:
      choice = input(f'''
This operation will delete {BOOT_FILE} from your board.
You can choose to:
A - Create plain {BOOT_FILE}
B - No {BOOT_FILE}
C - Do nothing\n''').strip() or 'C'
      choice = choice.upper()
    else:
      choice = 'B'

    if choice == 'A':
      create_plain_boot()
    if choice == 'B':
      if fs_item_exists(f'/{BOOT_FILE}'):
        os.remove(f'/{BOOT_FILE}')

    if choice == 'A' or choice == 'B':
      show_cursor()
      return True
    
    show_cursor()
    print(f'{APPS_FRAMEWORK_NAME} still enabled')
    return False

def install_package(package = None, app = None, url = None):
  if not MIP_SUPPORT:
    print('mip not supported')
    return False
  lib_install_path = '/lib'
  if app:
    lib_install_path = get_app(app)['path'] + lib_install_path
  if not url:
    mip.install(package, target=lib_install_path)
  else:
    mip.install(url, target=lib_install_path) 


# Managing apps

def create_app(app_name = None, friendly_name = None, set_default = False, hidden = False):
  a_name = app_name or 'untitled'
  a_name = "".join(c for c in a_name if c.isalpha() or c.isdigit() or c==' ' or c == '_').rstrip()
  a_name = a_name.replace(' ', '_')
  if validate_app(app_name):
    return(OSError(errno.EEXIST, f'App {app_name} already exists'))
  app_path = f'{APPS_ROOT}{APP_PREFIX}{a_name}'

  # create app's folders
  if fs_item_exists(app_path):
    return(OSError(errno.EEXIST, f'Folder {app_path} already exists'))
  os.mkdir(app_path)
  os.mkdir(app_path + '/lib')
  app_friendly_name = friendly_name or a_name
  # create app's main from template
  success, message, exception = template_to_file('main.tpl', f'{app_path}/{MAIN_FILE}', app_name = a_name, app_friendly_name = app_friendly_name)
  if not success:
    print(f'Error creating {MAIN_FILE}: {message}')
    return None

  md = app_properties_template.copy()
  md['name'] = a_name
  if friendly_name:
    md['friendly_name'] = friendly_name

  
  md['tools_version'] = TOOLS_VERSION
  with open(f'{app_path}/{APP_PROPERTIES}', 'w') as config_file:
    json.dump(md, config_file)
    

  if friendly_name:
    set_friendly_name(a_name, friendly_name)
  if hidden:
    hide_app(a_name)

  if set_default:
    default_app(app_name)
  return md


def set_friendly_name(app_name, friendly_name):
  if not validate_app(app_name):
    print(f'{app_name} is not a valid app')
    return
  with open(get_app(app_name)['path']+'/'+APP_FRIENDLY_NAME_FILE, 'w') as friendly_name_file:
    friendly_name_file.write(friendly_name)
  set_app_properties(app_name, friendly_name = friendly_name)

def set_app_visibility(app_name, visible = True):
  if not validate_app(app_name):
    print(f'app {app_name} does not exist')
    return False
  
  app_path = f'{APPS_ROOT}{APP_PREFIX}{app_name}'
  if visible:
    if fs_item_exists(f'{app_path}/{APP_HIDDEN_FILE}'):
      os.remove(f'{app_path}/{APP_HIDDEN_FILE}')
  else:
    with open(f'{app_path}/{APP_HIDDEN_FILE}', 'w') as hidden_file:
      hidden_file.write('# this app is hidden')
  return True

def hide_app(app_name = None):
  return(set_app_visibility(app_name, False))

def unhide_app(app_name = None):
  return(set_app_visibility(app_name, True))

def delete_app(app_name = None, force_confirm = False):
  app_name = app_name.replace(APP_PREFIX, '')
  if validate_app(app_name):
    folder_name = APP_PREFIX + app_name
    is_default = app_name == default_app()
    is_default_message = f'"{app_name}" is your default app.\n' if is_default else ''
    confirm = input(f'{is_default_message}Are you sure you want to delete {app_name}? [Y/n]') if not force_confirm else 'Y'
    if confirm == 'Y':
      if is_default:
        default_app('')
      print(f'Deleting app {app_name}')
      fs_root()
      delete_folder(f'{APPS_ROOT}{folder_name}', confirm)
      return True
    else:
      print(f'Project {app_name} not deleted')
      return False
  else:
    return False


def export_app(app_name = None):
  if validate_app(app_name):
    export_folder = f'{APPS_ROOT}{EXPORT_FOLDER}'
    if not fs_item_exists(export_folder):
      os.mkdir(export_folder)
    exported_file_path = f'{export_folder}/{app_name}.tar'
    if fs_item_exists(exported_file_path):
      exported_file_path = f'{export_folder}/{app_name}_{tm()}.tar'
    
    archive = tarfile.TarFile(exported_file_path, 'w')
    app_folder = APP_PREFIX + app_name
    app_path = f'{APPS_ROOT}{app_folder}'
    archive.add(app_path)
    archive.close()
    # print(f'app {app_name} archived at {exported_file_path}')
    return exported_file_path
  return(OSError(errno.EINVAL, f'{app_name} is not a valid app'))


def import_app(archive_path = None, force_overwrite = False):

  backup_folder = f'{APPS_ROOT}{BACKUP_FOLDER}'
  if not fs_item_exists(backup_folder):
    os.mkdir(backup_folder)
    

  if not fs_item_exists(archive_path):
    print(f'App archive {archive_path} does not exist')
    return False
  else:
    archive_file = tarfile.TarFile(archive_path, 'r')
    os.chdir(APPS_ROOT)
    first_tar_item = True
    confirm_delete_backup = 'n'
    confirm_overwrite = 'n'
    for item in archive_file:
      if item.type == tarfile.DIRTYPE:
        if first_tar_item:
          app_name = item.name.strip('/')
          app_backup_folder = app_name+'_'+str(tm())
          backup_app_path = f'{backup_folder}/{app_name}'
          if fs_item_exists(backup_app_path):
            backup_app_path = f'{backup_folder}/{app_name}_{tm()}'

          if fs_item_exists(item.name.strip('/')):
            confirm_overwrite = input(f'Do you want to overwrite {app_name}? [Y/n]: ') if not force_overwrite else 'Y'
            if confirm_overwrite == 'Y':
              print('Backing up existing app to', app_backup_folder)
              os.rename(app_name, backup_app_path)
            else:
              print('Operation canceled.')
              return
        os.mkdir(item.name.strip('/'))
      else:
        f = archive_file.extractfile(item)
        with open(item.name, "wb") as of:
          of.write(f.read())
      first_tar_item = False
    confirm_delete_backup = input(f'Delete backup folder {app_backup_folder}? [Y/n]: ') if not force_overwrite else 'Y'
    if confirm_delete_backup == 'Y':
      delete_folder(backup_app_path, 'Y')
    os.remove(archive_path)
  return True


# PLACEHOLDER
# this method will allow us to define which properties are required for this app
# might turn useful for internet connection details, etc.
def set_required_app_properties(app_name, **keys):
  if not validate_app(app_name) :
    raise ValueError(f'Invalid app: {app_name}')
  

def list_apps(return_list = False, include_hidden = False):
  apps_list = []
  for app in get_apps():
    if app['hidden'] and not include_hidden:
      continue
    app['default'] = (default_app() == app['name'])
    if return_list:
      apps_list.append(app.copy())
    else:
      print(f'{'*' if default_app() == app['name'] else ' '} {app['name']}')
  apps_list= sorted(apps_list, key = lambda d: d['name'])
  if return_list:
    return apps_list

def get_apps_list(include_hidden = False):
  return list_apps(return_list = True, include_hidden= include_hidden)

