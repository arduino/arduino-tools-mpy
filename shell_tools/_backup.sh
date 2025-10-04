function transfer_app {
  app_safe_name=$(echo "$1" | tr -d '\r\n')
  output_msg="Archiving \"$app_safe_name\" on board"
  echo -n "⏳ $output_msg"
  cmd="${PYTHON_HELPERS}"
  cmd+='''
'''
  cmd+="res = export_app('$app_safe_name');print(res)"
  
  error=$(mpremote exec "$cmd")
  if [ $? -ne 0 ]; then
    echo -ne "\r\033[2K"
    echo "❌ $output_msg"
    echo "Error: $error"
    return 0
  fi
  
  echo -ne "\r\033[2K"
  echo "☑️ $output_msg"
  remote_archive_path=$(echo "$error" | tr -d '\r\n')

  output_msg="Copying app \"$app_safe_name\" archive to local machine"
  echo -n "⏳ $output_msg"

  error=$(mpremote cp :$remote_archive_path ./)
  if [ $? -ne 0 ]; then
    echo -ne "\r\033[2K"
    echo "❌ $output_msg"
    echo "Error: $error"
    return 0
  fi
  echo -ne "\r\033[2K"
  echo "☑️ $output_msg"

  local_folder_name="$APPS_PREFIX$app_safe_name"
  if [ -d "$local_folder_name" ]; then
    input_msg="❔ Delete local folder $local_folder_name?"
    read -p "❔ $input_msg [Y/n]: " confirm
    confirm=${confirm:-n}
    
    if [ $confirm == "Y" ]; then
      echo -ne "\033[F\r\033[2K"
      echo "☑️ $input_msg"
      output_msg="Deleting local folder $local_folder_name"
      echo -n "⏳ $output_msg"
      rm -rf "$local_folder_name"
      echo -ne "\r\033[2K"
      echo "☑️ $output_msg"
    else
      echo -ne "\r\033[2K"
      echo "❌ $input_msg"
      timestamp=$(date +%s)
      
      local_folder_backup_name="$local_folder_name""_backup_$timestamp"
      
      output_msg="Moving $local_folder_name to $local_folder_backup_name"
      echo -n "⏳ $output_msg"
      mv $local_folder_name $local_folder_backup_name
      echo -ne "\r\033[2K"
      echo "☑️ $output_msg"
    fi
  fi
  
  
  archive_name=`basename $remote_archive_path`
  output_msg="🗜️ Extracting \"$archive_name\" to $APPS_PREFIX$app_safe_name"
  tar --strip-components=1 -xf $archive_name
  rm -f $archive_name
  # Print error message if return code is not 0
  if [ $? -ne 0 ]; then
    echo -ne "\r\033[2K"
    echo "❌ $output_msg"
    echo "Error: $res"
    return 0
  fi
  echo -ne "\r\033[2K"
  echo "☑️ $output_msg"

}
