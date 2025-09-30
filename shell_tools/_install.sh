#!/bin/bash
#
# Install an AMP project on the target board.
# This script accepts an optional argument to compile .py files to .mpy.
# Simply run the script with the optional argument:
#
# ./install.sh mpy

#########################
# VERY WORK IN PROGRESS #
#########################
source _common.sh

folder_name=$1
app_name=$1
app_safe_name=$(echo $app_name | tr ' [:punct:]' '_')

if [ "$app_name" == "" ]; then
  input_msg="Insert App or local folder name: "
  read -p "❔ $input_msg" app_name
  if [[ $app_name == "" ]]; then
    echo "No app name provided. Exiting..."
    exit 1
  fi
fi

if [[ $app_name == "$APPS_PREFIX"* ]]; then
  folder_name=$app_name
  app_name=${app_name:4}
else
  folder_name="$APPS_PREFIX$app_name"
  app_name=$app_name
fi

if [ ! -d "$folder_name" ]; then
  echo "App '$app_name' does not exist. Exiting..."
  exit 1
fi

if [ -f "$folder_name/.friendly_name" ]; then
  app_name=$(<"$folder_name/.friendly_name")
fi

if [ "$app_name" == "" ]; then
  app_name=$folder_name
fi


APPNAME=$app_name
APP_DIR="$folder_name"
SRCDIR=$APP_DIR
# if APPS_ROOT is not "/", make sure it's trailed with a "/"
# e.g. APPS_ROOT="/apps/"
APPS_ROOT="/"

# File system operations such as "mpremote mkdir" or "mpremote rm"
# will generate an error if the folder exists or if the file does not exist.
# These errors can be ignored.
# 
# Traceback (most recent call last):
#   File "<stdin>", line 2, in <module>
# OSError: [Errno 17] EEXIST

# Check if a directory exists
# Returns 0 if directory exists, 1 if it does not



echo "Installing app \"$APPNAME\""

# If the AMP root directory do not exist, create it
if ! directory_exists "${APPS_ROOT}"; then
  # echo "Creating $APPS_ROOT on board"
  create_folder "${APPS_ROOT}"
fi

if directory_exists "${APPS_ROOT}${APP_DIR}"; then
  # echo "Deleting previously existing $APPS_ROOT$APP_DIR on board"
  delete_folder "${APPS_ROOT}${APP_DIR}"
fi

create_folder "${APPS_ROOT}${APP_DIR}"


# echo "Creating $APPS_ROOT$APP_DIR on board"
# mpremote mkdir "${APPS_ROOT}${APP_DIR}"

# if ! directory_exists "${APPS_ROOT}${APP_DIR}"; then
#   echo "Creating $APPS_ROOT$APP_DIR on board"
#   mpremote mkdir "/${APPS_ROOT}${APP_DIR}"
# fi


ext="py"
if [ "$2" = "mpy" ]; then
  ext=$2
  echo ".py files will be compiled to .mpy"
fi

reset=true
for arg in "$@"; do
  if [ "$arg" == "--no-reset" ]; then
    reset=false
  fi
done

find $APP_DIR -name ".DS_Store" -type f -delete


app_files=($(find "$APP_DIR" -mindepth 1))
for item in "${app_files[@]}"; do
  if [ -d "$item" ]; then
    create_folder $APPS_ROOT$item
  elif [ -f "$item" ]; then
    f_name=`basename $item`
    source_extension="${f_name##*.}"
    destination_extension=$source_extension
    if [[ "$ext" == "mpy" && "$source_extension" == "py" ]]; then
      echo "Compiling $SRCDIR/$f_name to $SRCDIR/${f_name%.*}.$ext"
      mpy-cross "$SRCDIR/$f_name"
      destination_extension=$ext
      copy_file ${item%.*}.$destination_extension ":${APPS_ROOT}${item%.*}.$destination_extension"
    else
      copy_file $item ":${APPS_ROOT}$item"
    fi
  else
    echo -n "symlink file ignored"  # Second echo, handles other cases like symlinks
  fi
done


if [ "$ext" == "mpy" ]; then
  output_msg="Cleaning up .mpy files"
  echo -n "⏳ $output_msg"
  rm $SRCDIR/*.mpy
  echo -ne "\r\033[2K"
  echo "✅ $output_msg"
fi

echo -e "\n✅ App \"$APPNAME\" installed successfully"
if [ "$reset" = true ]; then
  echo "🔄 Resetting target board ..."
  mpremote reset
  exit 1
fi
