from hashlib import sha256
import os
from .common import *
from .files import *


# Hashing Helpers
def hash_generator(path):
  with open(path, 'rb') as file:
    for line in file:
        yield line


def get_hash(file_path):
  hash_object = sha256()
  for l in hash_generator(file_path):
    hash_object.update(l)
  return hex(int.from_bytes(hash_object.digest(), 'big'))


# MicroPython Helpers
def create_plain_boot():
  # create project's main from template
  success, message, exception = template_to_file('boot_plain.tpl', f'{APPS_ROOT}/{BOOT_FILE}')
  if not success:
    print(f'Error creating {BOOT_FILE}: {message}')
    return None
  return True


# File System Helpers
def get_module_path():
  module_path = '/'.join(__file__.split('/')[:-1])
  return module_path


def fs_root():
  os.chdir(get_root())


def fs_getpath():
  return os.getcwd()


def delete_fs_item(fs_path, is_folder=False):
  (os.rmdir if is_folder else os.remove)(fs_path)


def read_file(path):
  if not fs_item_exists(path):
    print(f'{path} does not exist')
  with open(path, 'r') as file:
    for line in file.readlines():
      print(line, end = '')
  print()


def is_directory(path):
  return True if os.stat(path)[0] == 0x4000 else False


def file_tree_generator(folder_path, depth=0):
  try:
    os.listdir(folder_path)
  except OSError as err:
    print('path not existing')
    return False
  for itm in os.ilistdir(folder_path):
    item_path = folder_path + '/' + itm[0]
    item_path = item_path.replace('//', '/')
    if is_directory(item_path):
      yield from file_tree_generator(item_path, depth=depth + 1)
    else:
      yield depth, False, item_path
  yield depth, True, folder_path


def get_directory_tree(path = '.'):
  tree_list = []
  if path in ('', '.'):
    path = os.getcwd()
  for depth, is_folder, file_path in file_tree_generator(path):
    if file_path in ('.', os.getcwd()):
      continue
    file_name = file_path.split('/')[len(file_path.split('/'))-1]
    tree_list.insert(0, (depth, file_path, file_name, is_folder))
  return tree_list


def list_directory(path = '.'):
  print(get_directory_tree(path))


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
  with open(f'{get_module_path()}/help.txt', 'r') as help_file:
    for line in help_file.readlines():
      print(line, end = '')

