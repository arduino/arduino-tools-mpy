from collections import OrderedDict
from .common import *
import json
app_properties_template = OrderedDict({
                      "name": "",
                      "friendly_name": "",
                      "author": "", 
                      "created": 0, 
                      "modified": 0, 
                      "version": "0.0.0", 
                      "origin_url": "https://arduino.cc", 
                      "tools_version": "0.0.0"
})


def get_app_properties(app_name, key = None):
  if not validate_app(app_name):
    print(f'{app_name} is not a valid project')
    return
  project_path = get_app(app_name)['path']
  with open(project_path+'/' + APP_PROPERTIES, 'r') as json_file:
    loaded_properties = json.load(json_file)
  updated_data = app_properties_template.copy()
  for k, v in loaded_properties.items():
    updated_data[k] = v
  updated_data['path'] = project_path
  return updated_data


def get_app_property(app_name, key):
  app_properties = get_app_properties(app_name)
  return app_properties[key]

def update_app_properties(app_name, properties = {}):
  if not validate_app(app_name) :
    print(f'{app_name} is not a valid project')
    return
  app_json_path = get_app(app_name)['path'] + '/' + APP_PROPERTIES
  if fs_item_exists(app_json_path):
    with open(app_json_path, 'r') as json_file:
      loaded_properties = json.load(json_file)
  else:
    loaded_properties = {}
  updated_data = app_properties_template.copy()
  updated_data.update(loaded_properties)
  for key, value in properties.items():
    updated_data[key] = value
  
  with open(get_app(app_name)['path'] + '/' + APP_PROPERTIES, 'w') as json_file
    json.dump(updated_data, json_file)

def set_app_properties(app_name, **keys):
  if not validate_app(app_name) :
    print(f'{app_name} is not a valid project')
    return
  app_json_path = get_app(app_name)['path'] + '/' + APP_PROPERTIES
  if fs_item_exists(app_json_path):
    with open(app_json_path, 'r') as json_file:
      loaded_properties = json.load(json_file)
  else:
    loaded_properties = {}
  updated_data = app_properties_template.copy()
  updated_data.update(loaded_properties)
  for key, value in keys.items():
    updated_data[key] = value
  
  with open(get_app(app_name)['path'] + '/' + APP_PROPERTIES, 'w') as json_file:
    json.dump(updated_data, json_file)
  
