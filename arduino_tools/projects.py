from .common import *
from .amp_settings import *
from .files import *
from .loader import *
from .helpers import *

import os

import json
from time import time as tm

try:
  import tarfile
except ImportError:
  print('Install tarfile-write')

try:
  import network
  NETWORK_UPDATE = True
  from .amp_network import *
except ImportError:
  NETWORK_UPDATE = False

if NETWORK_UPDATE:
  try:
    import mrequests
  except ImportError:
    print('Install mrequests')
    print('https://github.com/SpotlightKid/mrequests')

try:
  import mip
  MIP_SUPPORT = True
except ImportError:
  MIP_SUPPORT = False


# THE FOLLOWING METHODS ARE IMPORTED FROM THE
# COMMON/LOADER MODULE TO AVOID CODE DUPLICATION.
# PATH and PREFIX are defined there as well as
# 
# default_project(p = None)
# get_projects()
# enter_default_project()
# get_projects(root_folder = '/', debug = False)

BOOT_BACKUP_FILE = 'boot_backup.py'
EXPORT_FOLDER = f'__{PROJECT_PREFIX}exports'
BACKUP_FOLDER = f'__{PROJECT_PREFIX}backups'


def enable_amp():
  fs_root()
  if fs_item_exists(BOOT_FILE):
    os.rename(BOOT_FILE, BOOT_BACKUP_FILE)
  
  # create bootloader from template
  success, message, exception = template_to_file('boot_amp.tpl', f'{PROJECTS_ROOT}/{BOOT_FILE}')
  if not success:
    print(f'Error creating {BOOT_FILE}: {message}')
    return None

  # create boot config file
  if not fs_item_exists(BOOT_CONFIG_FILE):
    config_file = open(BOOT_CONFIG_FILE, 'w')
    config_file.close()


def disable_amp(force_delete_boot = False):
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
    print(f'{PROJECTS_FRAMEWORK_NAME} still enabled')
    return False

def install_package(package = None, project = None, url = None):
  if not MIP_SUPPORT:
    print('mip not supported')
    return False
  lib_install_path = '/lib'
  if project:
    lib_install_path = get_project(project)['path'] + lib_install_path
  if not url:
    mip.install(package, target=lib_install_path)
  else:
    mip.install(url, target=lib_install_path) 


# Managing projects

def create_project(project_name = None, set_default = False, hidden = False):
  p_name = project_name or 'untitled'
  p_name = "".join(c for c in p_name if c.isalpha() or c.isdigit() or c==' ' or c == '_').rstrip()
  p_name = p_name.replace(' ', '_')
  if validate_project(project_name):
    return None
  project_path = f'{PROJECTS_ROOT}amp_{p_name}'

  # create project's folders
  if fs_item_exists(project_path):
    return None
  os.mkdir(project_path)
  os.mkdir(project_path + '/lib')

  # create project's main from template
  success, message, exception = template_to_file('main.tpl', f'{project_path}/{MAIN_FILE}', project_name = p_name)
  if not success:
    print(f'Error creating {MAIN_FILE}: {message}')
    return None

  md = app_settings.copy()
  md['name'] = p_name
  md['amp_version'] = TOOLS_VERSION
  with open(f'{project_path}/{PROJECT_SETTINGS}', 'w') as config_file:
    json.dump(md, config_file)
    config_file.close()

  if hidden:
    hide_project(p_name)

  if set_default:
    default_project(project_name)
  return md


def set_project_visibility(project_name, visible = True):
  if not validate_project(project_name):
    print(f'project {project_name} does not exist')
    return False
  project_path = f'{PROJECTS_ROOT}amp_{project_name}'
  if visible:
    if fs_item_exists(f'{project_path}/.hidden'):
      os.remove(f'{project_path}/.hidden')
  else:
    hidden_file = open(f'{project_path}/.hidden', 'w')
    hidden_file.write('# this project is hidden')
    hidden_file.close()
  return True


def hide_project(project_name = None):
  return(set_project_visibility(project_name, False))


def unhide_project(project_name = None):
  return(set_project_visibility(project_name, True))


def delete_project(project_name = None, force_confirm = False):
  project_name = project_name.replace(PROJECT_PREFIX, '')
  if validate_project(project_name):
    folder_name = PROJECT_PREFIX + project_name
    is_default = project_name == default_project()
    is_default_message = f'"{project_name}" is your default project.\n' if is_default else ''
    confirm = input(f'{is_default_message}Are you sure you want to delete {project_name}? [Y/n]') if not force_confirm else 'Y'
    if confirm == 'Y':
      if is_default:
        default_project('')
      print(f'Deleting project {project_name}')
      fs_root()
      delete_folder(f'{PROJECTS_ROOT}{folder_name}', confirm)
      return True
    else:
      print(f'Project {project_name} not deleted')
      return False
  else:
    return False


def export_project(project_name = None):
  if validate_project(project_name):
    export_folder = f'{PROJECTS_ROOT}{EXPORT_FOLDER}'
    if not fs_item_exists(export_folder):
      os.mkdir(export_folder)
    exported_file_path = f'{export_folder}/{project_name}.tar'
    if fs_item_exists(exported_file_path):
      exported_file_path = f'{export_folder}/{project_name}_{tm()}.tar'
    
    archive = tarfile.TarFile(exported_file_path, 'w')
    project_folder = PROJECT_PREFIX + project_name
    project_path = f'{PROJECTS_ROOT}{project_folder}'
    archive.add(project_path)
    archive.close()
    print(f'project {project_name} archived at {exported_file_path}')
    return True
  return False


def expand_project(archive_path = None, force_overwrite = False):

  backup_folder = f'{PROJECTS_ROOT}{BACKUP_FOLDER}'
  if not fs_item_exists(backup_folder):
    os.mkdir(backup_folder)
    

  if not fs_item_exists(archive_path):
    print(f'Project archive {archive_path} does not exist')
    return False
  else:
    archive_file = tarfile.TarFile(archive_path, 'r')
    os.chdir(PROJECTS_ROOT)
    first_tar_item = True
    confirm_delete_backup = 'n'
    confirm_overwrite = 'n'
    for item in archive_file:
      if item.type == tarfile.DIRTYPE:
        if first_tar_item:
          amp_name = item.name.strip('/')
          amp_backup_folder = amp_name+'_'+str(tm())
          backup_project_path = f'{backup_folder}/{amp_name}'
          if fs_item_exists(backup_project_path):
            backup_project_path = f'{backup_folder}/{amp_name}_{tm()}'

          if fs_item_exists(item.name.strip('/')):
            confirm_overwrite = input(f'Do you want to overwrite {amp_name}? [Y/n]: ') if not force_overwrite else 'Y'
            if confirm_overwrite == 'Y':
              print('Backing up existing project to', amp_backup_folder)
              # os.rename(amp_name, amp_backup_folder)
              os.rename(amp_name, backup_project_path)
            else:
              print('Operation canceled.')
              return
        os.mkdir(item.name.strip('/'))
      else:
        f = archive_file.extractfile(item)
        with open(item.name, "wb") as of:
          of.write(f.read())
      first_tar_item = False
    confirm_delete_backup = input(f'Delete backup folder {amp_backup_folder}? [Y/n]: ') if not force_overwrite else 'Y'
    if confirm_delete_backup == 'Y':
      delete_folder(backup_project_path, 'Y')
    os.remove(archive_path)
  return True


def get_project_settings(project_name, key = None):
  if not validate_project(project_name):
    print(f'{project_name} is not a valid project')
    return
  j_file = open(get_project(project_name)['path']+'/'+PROJECT_SETTINGS, 'r')
  meta_json = json.load(j_file)
  j_file.close()
  md = app_settings.copy()
  for k, v in meta_json.items():
    md[k] = v
  return md


def get_project_setting(project_name, key):
  project_settings = get_project_settings(project_name)
  return project_settings[key]


def set_project_settings(project_name, required = [], **keys):
  if not validate_project(project_name) :
    print(f'{project_name} is not a valid project')
    return
  app_json_path = get_project(project_name)['path']+'/'+PROJECT_SETTINGS
  if fs_item_exists(app_json_path):
    j_file = open(app_json_path, 'r')
    local_settings = json.load(j_file)
  else:
    local_settings = {}
  md = app_settings.copy()
  md.update(local_settings)
  for key, value in keys.items():
    md[key] = value
  if len(required) > 0:
    md['required'] = required
  j_file = open(get_project(project_name)['path']+'/'+PROJECT_SETTINGS, 'w')
  json.dump(md, j_file)
  j_file.close()


def list_projects(return_list = False, include_hidden = False):
  projects_list = []
  for project in get_projects():
    if project['hidden'] and not include_hidden:
      continue
    project['default'] = (default_project() == project['name'])
    if return_list:
      projects_list.append(project.copy())
    else:
      print(f'{'*' if default_project() == project['name'] else ' '} {project['name']}')
  projects_list= sorted(projects_list, key = lambda d: d['name'])
  if return_list:
    return projects_list

def get_projects_list(include_hidden = False):
  return list_projects(return_list = True, include_hidden= include_hidden)



# TODO:
# - add origin_url and other data to be passed to project creation
# - check for updates at origin_url
# - parse origin_url for version-matching
#   - if remote version is bigger, download
#   - expand downloaded .tar

# implement @property for get/set
# maybe in v 1.0 wrap in 
# class This(sys.__class__):
