__author__ = "ubi de feo"
__license__ = "MPL 2.0"
__version__ = "0.4.0"
__maintainer__ = "ubi de feo [github.com/ubidefeo]"


try:
  from boot_restore import restore_target
  restore_available = True
except ImportError:
  restore_available = False

def enter_default_project():
  if restore_available and restore_target():
    enter_project(restore_target())
    return True
  
  if fs_item_exists(PROJECTS_ROOT + CONFIG_FILE):
    a_cfg = open(PROJECTS_ROOT + CONFIG_FILE, 'r')
    default_p = a_cfg.readline().strip()
    reboot_to = a_cfg.readline().strip()
    a_cfg.close()
    if reboot_to != '':
      a_cfg = open(PROJECTS_ROOT + CONFIG_FILE, 'w')
      a_cfg.write(reboot_to)
      a_cfg.close()
    enter_project(default_p)
    return True
  
  return False
  

def enter_project(project_name):
  project = get_project(project_name) if validate_project(project_name) else None
  if project == None:
    return False
  path.remove('.frozen')
  path.remove('/lib')
  path.append(project['path'] + '/lib')
  path.append('/lib')
  path.append('.frozen')
  chdir(project['path'])
  return True

