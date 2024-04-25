import os
from sys import path
from .constants import *

def validate_project(project_name):
  project_folder = PROJECT_PREFIX + project_name.replace(PROJECT_PREFIX, '')
  main_file_path = PROJECTS_ROOT + project_folder + '/main.py'
  settings_file_path = PROJECTS_ROOT + project_folder + '/' + PROJECT_SETTINGS
  if fs_item_exists(main_file_path) and fs_item_exists(settings_file_path):
    return True
  else:
    return False


def default_project(p = None, fall_back = None):
  f'''
  Displays or sets the default project to run on board startup or reset,
  immediately after {BOOT_FILE} has finished execution

  default_project('')             > no default project: if there is a {MAIN_FILE} in root it will be run
  default_project('some_project') > the {MAIN_FILE} file in /amp_some_project will run after {BOOT_FILE}

  default_project()               > returns the default project if set

  Note: a default project is not mandatory. See list_projects()
  '''
  default_p = '' if p == None else p
  if p != None:
    if (not validate_project(default_p)) and default_p != '':
      return(OSError(9, f'Project {default_p} does not exist'))
    a_cfg = open(PROJECTS_ROOT + CONFIG_FILE, 'w')
    a_cfg.write(default_p)
    if fall_back != None:
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
      default_p = None
    return default_p if default_p != None else None


# cycles through all the projects: resournce consuming
# def get_project(project_name):  
#   for project in get_projects():
#     if project['name'] == project_name:
#       return project
#   return None

# more targeted approach
def get_project(project_name):  
  if validate_project(project_name):
    project_folder = PROJECT_PREFIX + project_name.replace(PROJECT_PREFIX, '')
    prj_dict = {
      'name': '',
      'path': '',
      'hidden': False
    }
    prj_dict['name'] = project_folder.replace('amp_', '')
    prj_dict['path'] = PROJECTS_ROOT + project_folder
    if fs_item_exists(PROJECTS_ROOT + project_folder + '/.hidden'):
      prj_dict['hidden'] = True
    return prj_dict
  else:
    return None

def get_projects(root_folder = '/'):
  for fs_item in os.ilistdir(root_folder):
    fs_item_name = fs_item[0]
    if fs_item_name[0:len(PROJECT_PREFIX)] != PROJECT_PREFIX:
      continue
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


def fs_item_exists(path):
  try:
    os.stat(path)
    return True
  except OSError as e:
    return False
