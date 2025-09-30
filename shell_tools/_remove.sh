#!/bin/bash
source _common.sh

folder_name=$1
app_name=$1
force_confirm=$2
app_safe_name=$(echo $app_name | tr ' [:punct:]' '_')
echo "$app_name"
if [ "$app_name" = "" ]; then
  input_msg="Insert App name: "
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

if [ "$app_name" == "" ]; then
  app_name=$folder_name
fi

APPNAME=$app_name
APP_DIR="$folder_name"
SRCDIR=$APP_DIR
# if APPS_ROOT is not "/", make sure it's trailed with a "/"
# e.g. APPS_ROOT="/apps/"


# If the AMP root directory do not exist, create it
echo "Deleting app \"$APPNAME\""

if directory_exists "${APPS_ROOT}${APP_DIR}"; then
  # echo "Deleting previously existing $APPS_ROOT$APP_DIR on board"
  if [ "$force_confirm" != "Y" ]; then
    output_msg="Deleting \"$APPNAME\" from your board is not reversible. Are you sure you want to continue?"
    echo -n "⚠️ $output_msg [Y/n]: "
    read confirm
    confirm=${confirm:-N}
  else
    confirm="Y"
  fi
  # output_msg="Deleting \"$APPNAME\" from your board is not reversible. Are you sure you want to continue?"
  # echo -n "⚠️ $output_msg [Y/n]: "
  # read confirm
  # confirm=${confirm:-n}
  if [ "$confirm" = "Y" ]; then
    echo -ne "\033[F\r\033[2K"
    echo "👍🏼 $output_msg"
    delete_folder "${APPS_ROOT}${APP_DIR}"
  else
    echo "❌ $app_name not removed"
    exit 1
  fi

else
  echo "App \"$APPNAME\" does not exist on board"
  exit 1
fi


echo "✅ App \"$APPNAME\" uninstalled successfully"