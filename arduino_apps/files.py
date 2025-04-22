from time import time as tm
import os

def get_template_path(file_name):
  return '/'.join(__file__.split('/')[:-1]) + f'/{file_name}'


def template_to_file(template_name, destination_file, **variables):
  for k, v in variables.items():
    print(f'{k}: {v}')
  template_path = get_template_path(template_name)
  try:
    with open(get_template_path(template_name), 'r') as input_template:
      input_text = input_template.read().format(**variables)
  except OSError as e:
    return False, f'{template_name} not found', e
  try:
    with open(destination_file, 'w') as output_file:
      output_file.write(input_text)
  except OSError as e:
    return False, f'{destination_file} not created', e 
  return True, f'{destination_file} created', None


### UNUSED UNTIL EXAMPLES LOADING IS IMPLEMENTED
def new_file_from_source(file_name = None, destination_path = '.', overwrite = False, source_path = None):
  if file_name is None:
    file_name = 'main'
  new_sketch_path = f'{destination_path}/{file_name}.py'
  try:
    # open(new_sketch_path, 'r')
    os.stat(new_sketch_path)
    if not overwrite:
      file_name = f'{file_name}_{tm()}'
  except OSError:
    pass
  
  # template_path = get_template_path() if source_path is None else source_path
  template_path = source_path
  template_sketch = open(template_path, 'r')
  new_sketch_path = f'{destination_path}/{file_name}.py'

  with open(new_sketch_path, 'w') as f:
    sketch_line = None
    while sketch_line is not '':
      sketch_line = template_sketch.readline()
      f.write(sketch_line)
  template_sketch.close()
  return new_sketch_path

def copy_py(source_path = '.', destination_path = '.', file_name = None, overwrite = False):
  file_name = file_name or 'main'
  return new_file_from_source(file_name = file_name, destination_path = destination_path, overwrite = overwrite, source_path = source_path)
