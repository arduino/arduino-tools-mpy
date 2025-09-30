ARDUINO_TOOLS_CHECK='''
import sys
sys.path.insert(0, "/lib")
try:
    from arduino_tools.projects import create_project, export_project
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

if check_arduino_tools; then
  echo "OK"
else
  echo "Arduino tools are not installed. Exiting..."
  echo "Please install Arduino Tools for MicroPython on your board."
fi