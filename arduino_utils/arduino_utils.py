__author__ = "ubi de feo"
__license__ = "MIT License"
__version__ = "0.2.0"
__maintainer__ = "ubi de feo [github.com/ubidefeo]"

from .amp_common import *
from .amp_settings import *
import mip
import json
from time import ticks_ms
from machine import soft_reset

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

# THE FOLLOWING ARE IMPORTED FROM THE RUNTIME MODULE
# TO AVOID CODE DUPLICATION
# PATH and PREFIX configurations are also part of the RUNTIME module
# 
# validate_project(project_name)
# default_project(p = None)
# get_projects()
# enter_default_project()
# get_projects(root_folder = '/', debug = False)

BOOT_BACKUP_FILE = 'boot_backup.py'
BACKUP_FOLDER = f'{PROJECT_PREFIX}backups'

_VERSION = '0.3.0'

def enable_amp():
  fs_root()
  if fs_item_exists(BOOT_FILE):
    os.rename(BOOT_FILE, BOOT_BACKUP_FILE)
  
  # enable bootloader
  boot_file = open(BOOT_FILE, 'w')
  boot_file.write('from arduino_utils.amp_common import *\n')
  boot_file.write('enter_default_project()')
  boot_file.close()

  # create boot config file
  config_file = open(CONFIG_FILE, 'w')
  config_file.close()


def disable_amp(force_delete_boot = 'N'):
  fs_root()
  if fs_item_exists(BOOT_BACKUP_FILE):
    os.rename(BOOT_BACKUP_FILE, BOOT_FILE)
  else:
    show_cursor(False)
    if force_delete_boot == 'N':
      choice = input(f'''
This operation will delete {BOOT_FILE} from your board.
You can choose to:
A - Create a default one
B - No {BOOT_FILE}
C - Cancel\n''').strip() or 'C'
      choice = choice.upper()
    else:
      choice = 'B'
      
    if choice == 'A':
      create_plain_boot()
    if choice == 'B':
      if fs_item_exists(f'/{BOOT_FILE}'):
        os.remove(f'/{BOOT_FILE}')
    show_cursor()
    print(f'{PROJECTS_FW_NAME} still enabled')

def install_package(package = None, project = None, url = None):
  destination_path = '/lib'
  if project:
    destination_path = get_project(project)['path'] + destination_path
  if not url:
    mip.install(package, target=destination_path)
  else:
    mip.install(url, target=destination_path) 


# Managing projects

def create_project(project_name = None, set_default = False, hidden = False):
  p_name = project_name or 'untitled'
  p_name = "".join(c for c in p_name if c.isalpha() or c.isdigit() or c==' ' or c == '_').rstrip()
  p_name = p_name.replace(' ', '_')
  if not validate_project(project_name):
    project_path = f'{PROJECTS_ROOT}amp_{p_name}'

    # create project's folders
    os.mkdir(project_path)
    os.mkdir(project_path + '/lib')

    # create project's main
    main_py = open(f'{project_path}/{MAIN_FILE}', 'w')
    main_py.write(f'# Project Name: {project_name}\n')
    main_py.write(f'# write your code here\n')
    main_py.write(f'# have fun :) \n')
    main_py.write(f'print("Hello from project {project_name}")')
    main_py.close()
    md = app_settings.copy()
    md['name'] = p_name
    md['amp_version'] = _VERSION
    with open(f'{project_path}/{PROJECT_SETTINGS}', 'w') as config_file:
      json.dump(md, config_file)
      config_file.close()

    if hidden:
      hide_project(p_name)

    if set_default:
      default_project(project_name)
    return md
  return False


def hide_project(project_name = None):
  if not validate_project(project_name):
    print(f'project {project_name} does not exist')
    return
  project_path = f'{PROJECTS_ROOT}amp_{project_name}'
  if not fs_item_exists(f'{project_path}/.hidden'):
    hidden_file = open(f'{project_path}/.hidden', 'w')
    hidden_file.write('# this project is hidden')
    hidden_file.close()


def unhide_project(project_name = None):
  if not validate_project(project_name):
    print(f'project {project_name} does not exist')
    return
  project_path = f'{PROJECTS_ROOT}amp_{project_name}'
  if fs_item_exists(f'{project_path}/.hidden'):
      os.remove(f'{project_path}/.hidden')


def default_project(p = None, fall_back = None):
  f'''
  Displays or sets the default project to run on board startup or reset,
  immediately after {BOOT_FILE} has finished execution

  default_project('')             > no default project: if there is a {MAIN_FILE} in root it will be run
  default_project('some_project') > the {MAIN_FILE} file in /amp_some_project will run after {BOOT_FILE}

  default_project()               > returns the default project if set

  Note: a default project is not mandatory. See list_projects()
  '''
  default_p = '' if p is None else p
  if p is not None:
    if (not validate_project(default_p)) and not default_p is '':
      return(OSError(9, f'Project {default_p} does not exist'))
    a_cfg = open(PROJECTS_ROOT + CONFIG_FILE, 'w')
    a_cfg.write(default_p)
    if fall_back is not None:
      a_cfg.write('\n')
      a_cfg.write(fall_back)
    a_cfg.close()
    # if default_p == '':
    #   disable_amp()
    
  else:
    if fs_item_exists(PROJECTS_ROOT + CONFIG_FILE):
      a_cfg = open(PROJECTS_ROOT + CONFIG_FILE, 'r')
      default_p = a_cfg.readline().strip()
    else:
      return(OSError(errno.ENOENT, 'config file not found'))
    return default_p if default_p is not None else None


def delete_project(project_name = None, force_confirm = 'n'):
  project_name = project_name.replace(PROJECT_PREFIX, '')
  folder_name = PROJECT_PREFIX + project_name
  if default_project() == project_name:
    print(f'The project "{project_name}" is set as default.')
    print(f'Set another project as default before you can delete "{project_name}"')
    return
  if validate_project(project_name):
    confirm = input(f'Are you sure you want to delete {project_name}? [Y/n]') if force_confirm != 'Y' else 'Y'
    if confirm == 'Y':
      print(f'Deleting project {project_name}')
      fs_root()
      delete_folder(f'{PROJECTS_ROOT}{folder_name}', force_confirm)
    else:
      print(f'Project {project_name} not deleted')


def backup_project(project_name = None):
  if validate_project(project_name):
    archive_folder_path = f'{PROJECTS_ROOT}{BACKUP_FOLDER}'
    if not fs_item_exists(archive_folder_path):
      os.mkdir(archive_folder_path)
    archive_path = f'{archive_folder_path}/{project_name}_{ticks_ms()}.tar'
    archive = tarfile.TarFile(archive_path, 'w')
    folder_name = PROJECT_PREFIX + project_name
    project_path = f'{PROJECTS_ROOT}{folder_name}'
    archive.add(project_path)
    archive.close()
    print(f'project {project_name} archived at {archive_path}')


def expand_project(archive_name = None):
  if not fs_item_exists(archive_name):
    print(f'Project archive {archive_name} does not exist')
    return
  else:
    archive_file = tarfile.TarFile(archive_name, 'r')
    os.chdir(PROJECTS_ROOT)
    first_tar_item = True
    confirm_delete = 'n'
    for item in archive_file:
      if item.type == tarfile.DIRTYPE:
        if first_tar_item:
          amp_name = item.name.strip('/')
          amp_backup = amp_name+'_'+str(ticks_ms())
          if fs_item_exists(item.name.strip('/')):
            confirm_delete = input(f'are you sure you want to overwrite {amp_name}? [Y/n]')
            if confirm_delete == 'Y':
              os.rename(amp_name, amp_backup)
            else:
              print('Operation canceled.')
              return
        os.mkdir(item.name.strip('/'))
      else:
        f = archive_file.extractfile(item)
        with open(item.name, "wb") as of:
          of.write(f.read())
      first_tar_item = False
    if confirm_delete == 'Y':
      delete_folder(amp_backup, 'Y')
    os.remove(archive_name)


def get_project_settings(project_name):
  return get_project_setting(project_name)


def get_project_setting(project_name, key = None):
  if not validate_project(project_name):
    print(f'{project_name} is not a valid project')
    return
  j_file = open(get_project(project_name)['path']+'/'+PROJECT_SETTINGS, 'r')
  meta_json = json.load(j_file)
  j_file.close()
  md = app_settings.copy()
  for k, v in meta_json.items():
    md[k] = v
  if key == None:
    return md
  else:
    return md[key]


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


def list_projects(return_list = False, skip_hidden = True):
  projects_list = []
  for project in get_projects():
    if project['hidden'] and skip_hidden:
      continue
    project['default'] = (default_project() == project['name'])
    
    if return_list:
      projects_list.append(project.copy())
    else:
      print(f'{'*' if default_project() == project['name'] else ' '} {project['name']}')
  projects_list= sorted(projects_list, key = lambda d: d['name'])
  if return_list:
    return projects_list


# Hashing Helpers
def hash_generator(path):
  with open(path, 'rb') as file:
    for line in file:
        yield line
    file.close()


def get_hash(file_path):
  hash_object = sha256()
  for l in hash_generator(file_path):
    hash_object.update(l)
  return hex(int.from_bytes(hash_object.digest(), 'big'))


# Generic Helpers
def version_to_number(ver_str):
  ma, mi, fi = map(lambda n: int(n), ver_str.split('.'))
  v_num = ma*100 + mi*10 + fi
  return v_num


# MicroPython Helpers
def create_plain_boot():
  boot_file = open(f'/{BOOT_FILE}', 'w')
  boot_file.write(f'# This file will be the first one to run on board startup/reset\n')
  boot_file.write(f'# {MAIN_FILE} (if present) will follow\n')
  boot_file.write(f'# place your code in {MAIN_FILE}')
  boot_file.close()


# File System Helpers
def get_module_path():
  module_path = '/'.join(__file__.split('/')[:-1])
  return module_path


def fs_root():
  os.chdir('/')


def fs_getpath():
  return os.getcwd()


def fs_item_exists(path):
  try:
    os.stat(path)
    return True
  except OSError as e:
    return False


def delete_fs_item(fs_path, is_folder = False, test = False):
  print('deleting', 'folder:' if is_folder else 'file:', fs_path)
  if test: 
    return
  if is_folder:
    os.rmdir(fs_path)
  else:
    os.remove(fs_path)


def read_file(path):
  if not fs_item_exists(path):
    return OSError(errno.ENOENT, f'{path} does not exist')
  with open(path, 'r') as file:
    for line in file.readlines():
      print(line, end = '')
    file.close()
  print()


def is_directory(path):
  return True if stat(path)[0] == 0x4000 else False


def file_tree_generator(folder_path, depth=0):
  try:
    os.listdir(folder_path)
  except OSError as err:
    if err.errno == errno.ENOENT:
      print('path not existing')
      return
  for itm in os.ilistdir(folder_path):
    item_path = folder_path + '/' + itm[0]
    item_path = item_path.replace('//', '/')
    item_path = item_path.replace('./', '/')
    if is_directory(item_path):
      yield from file_tree_generator(item_path, depth=depth + 1)
    else:
      yield depth, False, item_path
  yield depth, True, folder_path


def list_tree(path = '.'):
  if path == '':
    path = '.'
  for depth, is_folder, file_path in file_tree_generator(path):
    if file_path in ('.', os.getcwd()):
      continue
    file_name = file_path.split('/')[len(file_path.split('/'))-1]
    print(f'{'d'if is_folder else 'f'}: {file_path}')


def delete_folder(path = '.', force_confirm = 'n'):
  if path == '':
    path = '.'
    
  for depth, is_folder, file_path in file_tree_generator(path):
    if file_path in ('.', os.getcwd()):
      print('cannot delete current folder')
      continue
    if force_confirm == 'n':
      c = input(f'Are you sure you want to delete {'folder' if is_folder else 'file'} {file_path}? [Y/n]')
      if c == 'Y':
        delete_fs_item(file_path, is_folder)
    else:
      delete_fs_item(file_path, is_folder)


# Console helpers
def show_cursor(show = True):
    print('\033[?25' + ('h' if show else 'l'), end = '')


def clear_terminal(cursor_visible = True):
    print("\033[2J\033[H", end = '')
    show_cursor(cursor_visible)


def show_commands():
  clear_terminal()
  with open(f'{get_module_path()}/amp_help.txt', 'r') as help_file:
    for line in help_file.readlines():
      print(line, end = '')
    help_file.close()


# TODO:
# - add origin_url and other data to be passed to project creation
# - check for updates at origin_url
# - parse origin_url for version-matching
#   - if remote version is bigger, download
#   - expand downloaded .tar

# implement @property for get/set
# maybe in v 1.0 wrap in 
# class This(sys.__class__):
