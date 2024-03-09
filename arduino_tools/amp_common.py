__author__ = "ubi de feo"
__license__ = "MIT License"
__version__ = "0.2.0"
__maintainer__ = "ubi de feo [github.com/ubidefeo]"

import errno
import os
from hashlib import sha256
from os import stat, ilistdir
from sys import path

PROJECTS_ROOT = '/'
PROJECT_PREFIX = 'amp_'
BOOT_FILE = 'boot.py'
CONFIG_FILE = 'boot.cfg'
MAIN_FILE = 'main.py'
PROJECT_SETTINGS = 'app.json'
PROJECTS_FW_NAME = 'AMP'

try:
  from boot_restore import restore_target
  restore_available = True
except ImportError:
  restore_available = False

def validate_project(project_name):
  project_folder = PROJECT_PREFIX + project_name.replace(PROJECT_PREFIX, '')
  try:
    main_file = open(PROJECTS_ROOT + project_folder + '/main.py', 'r')
    settings = open(PROJECTS_ROOT + project_folder + '/' + PROJECT_SETTINGS, 'r')
  except OSError as e:
    return False
  return True

def enter_default_project():
  if restore_available and restore_target():
    enter_project(restore_target())
    return
  
  if fs_item_exists(PROJECTS_ROOT + CONFIG_FILE):
    a_cfg = open(PROJECTS_ROOT + CONFIG_FILE, 'r')
    default_p = a_cfg.readline().strip()
    reboot_to = a_cfg.readline().strip()
    a_cfg.close()
    if reboot_to is not '':
      a_cfg = open(PROJECTS_ROOT + CONFIG_FILE, 'w')
      a_cfg.write(reboot_to)
      a_cfg.close()
  else:
    return(OSError(errno.ENOENT, 'config file not found'))
  # default_p if default_p is not None else None
  enter_project(default_p)

def enter_project(project_name):
  project = get_project(project_name) if validate_project(project_name) else None
  if project is None:
    return
  path.remove('.frozen')
  path.remove('/lib')
  path.append(project['path'] + '/lib')
  path.append('/lib')
  path.append('.frozen')
  os.chdir(project['path'])

def get_projects(root_folder = '/'):
  for fs_item in os.ilistdir(root_folder):
    fs_item_name = fs_item[0]
    if validate_project(fs_item_name):
      prj_dict = {
        'name': '',
        'path': '',
        'hidden': False
      }
      # project_name = fs_item_name.replace('amp_', '')
      prj_dict['name'] = fs_item_name.replace('amp_', '')
      prj_dict['path'] = PROJECTS_ROOT + fs_item_name
      if fs_item_exists(PROJECTS_ROOT + fs_item_name + '/.hidden'):
        prj_dict['hidden'] = True
      yield prj_dict

def get_project(project_name):
  for project in get_projects():
    if project['name'] == project_name:
      return project
  return None

def fs_item_exists(path):
  try:
    os.stat(path)
    return True
  except OSError as e:
    return False