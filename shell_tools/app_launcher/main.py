# App Name: loader - Application Loader
# Created with Arduino Tools for MicroPython

# The following two lines will take care of initializing the app
from arduino_tools.apps_manager import *
from arduino_tools.app import *
my_app = App('launcher')

apps_list = get_apps_list()

def set_boot_app():
  for i, app in enumerate(apps_list):
    print(f'{i}: {app['name']}')
  a = input(f'select app ID: [0-{i}]')
  default_app(apps_list[int(a)]['name'], 'loader')

set_boot_app()