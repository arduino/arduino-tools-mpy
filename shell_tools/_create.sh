function create_app {
  app_safe_name=$1
  shift
  app_friendly_name=${*:-$app_safe_name}

  # if [ "$app_friendly_name" = "" ]; then
  #   app_friendly_name=$app_safe_name
  # fi

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
