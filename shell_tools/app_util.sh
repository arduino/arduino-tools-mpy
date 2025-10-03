#!/bin/bash
source _common.sh

# clean_error=$(echo $error | tr -d '\r\n')
if ! check_arduino_tools; then
  echo "Arduino Apps Framework not installed."
  echo "Please install Arduino Apps Framework for MicroPython on your board."
    echo "https://github.com/arduino/arduino-tools-mpy"
    read -p "Install now? [y/n]: " confirm
    confirm=${confirm:-n}
    if [ $confirm == "y" ]; then
      mpremote mip --target=/lib install $ARDUINO_TOOLS_MIP_URL
      mpremote mip --target=/lib install tarfile-write
      echo "Arduino Tools for MicroPython installed."
    fi
    echo -e "\nArduino Apps Framework for MicroPython not installed. Exiting."
    exit 1
fi

commands=("help" "create" "install" "backup" "remove" "delete" "list" "run")
function command_valid {
  for command in "${commands[@]}"; do
    if [ "$1" == "$command" ]; then
      return 0
    fi
  done
  return 1
}

function show_help {
  echo "Usage: ./app_util.sh <command>:"
  for cmd in "${commands[@]}"; do echo "• $cmd"; done
  
}

function run_local {
  echo "Running local app <$1> [WIP]"
  # 1. install local app to temporary folder on the board
  # 2. invoke run with app name
}

function run {
  echo "Running app <$1> from the board [WIP]"
  # 1. set default app to selected app
  # 2. soft reboot
}

if ! command_valid $1; then
  show_help
  exit 1
fi

command=$1
shift
case "$command" in
  help)
    show_help
    exit 1
  ;;
  create)
    ./_create.sh $@
  ;;
  install)
    ./_install.sh $@
  ;;
  remove|delete)
    ./_remove.sh $@
  ;;
  backup)
    ./_backup.sh $@
  ;;
  list)
    if device_present == 0; then
      echo "❌ No MicroPython board found. Exiting."
      exit 1
    fi
    cmd="${PYTHON_HELPERS}list_apps()"
    error=$(mpremote exec "$cmd")
    echo "Apps on board:"
    if [ $? -ne 0 ]; then
      echo "Error: $error"
      return 0
    fi
    clean_string=$(echo "$error" | tr -d '\r\n')
    apps_list=($clean_string)
    for app in "${apps_list[@]}"; do
      echo " • $app"
    done
  ;;
  run)
    # Run an app on the board
    # WIP: currently only supports running main.py from the local (PC) filesystem
    #
    # TODO:
    # √ install local app to the board (overwrite if already exists)
    # - use temporary app folder to test run apps
    # - run app directly from the board

    if device_present == 0; then
      echo "❌ No MicroPython board found. Exiting."
      exit 1
    fi
    if [ "$1" = "" ]; then
      echo "Please provide an app name to run."
      exit 1
    fi
    # app_folder=$1
    if [[ $1 == "$APPS_PREFIX"* ]]; then
      app_folder=$1
    else
      app_folder="$APPS_PREFIX$1"
    fi
    app_path="$app_folder/main.py"
    
    error=$(mpremote run "$app_path")
    if [ $? -ne 0 ]; then
      echo "Error: $error"
    fi
  ;;
  *)
    echo "Unknown command: $command"
    show_help
    exit 1
  ;;
esac

