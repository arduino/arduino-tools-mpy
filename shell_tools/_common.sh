#!/bin/bash
APPS_ROOT="/"
APPS_PREFIX="app_"
ARDUINO_TOOLS_MIP_URL="github:arduino/arduino-tools-mpy"


PYTHON_HELPERS='''
import os

os.chdir(get_root())
from arduino_tools.apps_manager import create_app, export_app

def is_directory(path):
  return True if os.stat(path)[0] == 0x4000 else False

def get_all_files(path, array_of_files = []):
    files = os.ilistdir(path)
    for file in files:
        is_folder = file[1] == 16384
        p = path + "/" + file[0]
        array_of_files.append({
            "path": p,
            "type": "folder" if is_folder else "file"
        })
        if is_folder:
            array_of_files = get_all_files(p, array_of_files)
    return array_of_files

def delete_folder(path):
    files = get_all_files(path)
    for file in files:
        if file["type"] == "file":
            os.remove(file["path"])
    for file in reversed(files):
        if file["type"] == "folder":
            os.rmdir(file["path"])
    os.rmdir(path)

def sys_info():
    import sys
    print(sys.platform, sys.implementation.version)

def list_apps():
    import os
    from arduino_tools.apps_manager import get_apps_list
    apps = get_apps_list()
    apps_names = ""
    for i, app in enumerate(apps):
        if i != 0:
            apps_names += " "
        apps_names += app["name"]
    print(apps_names)

def get_root(has_flash_mount = True):
    if "/flash" in sys.path:
        return "/flash/"
    else:
        return "/"

os.chdir(get_root())
'''

ARDUINO_TOOLS_CHECK='''
import sys
sys.path.insert(0, "/lib")
try:
    from arduino_tools.apps_manager import create_app
    from tarfile import write
except ImportError as e:
    print("Error: ")

'''

function check_arduino_tools {
  error=$(mpremote exec "$ARDUINO_TOOLS_CHECK")
  if [[ $error == *"Error"* ]]; then
    return 1
  else
    return 0
  fi
}

# Check if device is present/connectable
# returns 0 if device is present, 1 if it is not
function device_present {
  # Run mpremote and capture the error message
  echo "⏳ Querying MicroPython board..."
  sys_info="${PYTHON_HELPERS}sys_info()"
  error=$(mpremote exec "$sys_info")
  # Return error if error message contains "OSError: [Errno 2] ENOENT"
  if [[ $error == *"no device found"* ]]; then
      return 0
  else
      return 1
  fi
}

function directory_exists {
  # Run mpremote and capture the error message
  output="Checking if \"$1\" exists on board"
  echo -ne "❔ $output"

  error=$(mpremote fs ls $1 2>&1)
  echo -ne "\r\033[2K"
  echo -e "\r☑️ $output"
  # Return error if error message contains "OSError: [Errno 2] ENOENT"
  if [[ $error == *"OSError: [Errno 2] ENOENT"* || $error == *"No such"* ]]; then
      return 1
  else
      return 0
  fi
  
}

# Copies a file to the board using mpremote
# Only produces output if an error occurs
function copy_file {
  output="Copying $1 to $2"
  echo -n "⏳ $output"
  # Run mpremote and capture the error message
  error=$(mpremote cp $1 $2)
  # Print error message if return code is not 0
  if [ $? -ne 0 ]; then
    echo "Error: $error"
  fi
  echo -ne "\r\033[2K"
  echo -e "\r☑️ $output"
}

# Deletes a file from the board using mpremote
# Only produces output if an error occurs
function delete_file {
  echo "Deleting $1"
  # Run mpremote and capture the error message
  error=$(mpremote rm $1)

  # Print error message if return code is not 0
  if [ $? -ne 0 ]; then
    echo "Error: $error"
  fi
}

function create_folder {
  output_msg="Creating $1 on board"
  echo -n "⏳ $output_msg"
  error=$(mpremote mkdir "$1")
  # Print error message if return code is not 0
  if [ $? -ne 0 ]; then
    echo "Error: $error"
  fi
  echo -ne "\r\033[2K"
  echo -e "\r☑️ $output_msg"
}

function delete_folder {
  output_msg="Deleting $1 on board"
  echo -n "⏳ $output_msg"
  delete_folder="${PYTHON_HELPERS}delete_folder(\"/$1\")"
  error=$(mpremote exec "$delete_folder")
  # Print error message if return code is not 0
  if [ $? -ne 0 ]; then
    echo "Error: $error"
  fi
  echo -ne "\r\033[2K"
  echo -e "\r☑️ $output_msg"
}