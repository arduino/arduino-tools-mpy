# Project Name: {app_name}
# Created with Arduino Tools for MicroPython

from sample_lib import sample_lib_function
# The following two lines will take care of initializing the app
from arduino_tools.app import *
my_app = App('demo')

# Write your code below (no #) and have fun :)
print(f'Hello, I am an app and my name is {my_app.friendly_name}')
# Call a function from the sample_lib module
# To demonstrate that the app's lib/ folder is in sys.path
sample_lib_function()