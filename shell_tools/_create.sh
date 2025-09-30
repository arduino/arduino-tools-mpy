#!/bin/bash
#
# Create an Arduino MicroPython App on the target board.
#
# ./_create.sh <app_name> <friendly_name> 

#########################
# VERY WORK IN PROGRESS #
#########################
source _common.sh
app_name=$1
app_safe_name=$(echo $app_name | tr ' [:punct:]' '_')
shift
app_friendly_name=$*


function create_app {
  app_safe_name=$1
  shift
  app_friendly_name=$*

  if [ "$app_friendly_name" = "" ]; then
    app_friendly_name=$app_safe_name
  fi

  output_msg="Creating app \"$app_safe_name\" with friendly name \"$app_friendly_name\""
  echo -n "⏳ $output_msg"

  # Run mpremote and capture the error message
  cmd="${PYTHON_HELPERS}"
  cmd+='''
'''
  cmd+="create_app('$app_safe_name', friendly_name = '$app_friendly_name')"
  cmd+='''
'''
  
  cmd+="print('App $app_safe_name created')"
  error=$(mpremote exec "$cmd")
  # Print error message if return code is not 0
  if [ $? -ne 0 ]; then
    echo -ne "\r\033[2K"
    echo "❌ $output_msg"
    echo "Error: $error"
    exit 1
  fi
  echo -ne "\r\033[2K"
  echo "☑️ $output_msg"
}

remote_app_path="$APPS_ROOT""$APPS_PREFIX""$app_safe_name"
echo $remote_app_path
if directory_exists $remote_app_path; then
  echo "App \"$app_friendly_name\" already exists on board. Delete first."
  exit 1
else
  echo "App \"$app_friendly_name\" does not exist on board. Creating..."
  create_app $app_safe_name $app_friendly_name
fi

transfer_app $app_safe_name

echo -e "\n✅ App \"$app_friendly_name\" created and available locally"
