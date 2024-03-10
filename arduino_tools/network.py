import network
import binascii
import time

network_if = network.WLAN(network.STA_IF)

def connect(ssid = '', pwd = '', interface = network.WLAN(network.STA_IF), timeout = 10, display_progress = True):
  interface.active(False)
  time.sleep_ms(500)
  interface.active(True)
  time.sleep_ms(100)
  interface.connect(ssid, pwd)
  # Network Connection Progress
  max_dot_cols = 20
  dot_col = 0
  connection_attempt_start_time = time.time()
  if display_progress:
    print()
    print(f"Connecting to {ssid}")
    while not interface.isconnected():
      if(dot_col % max_dot_cols == 0):
          print()
      print('.', end = '')
      dot_col +=1
      if time.time() - connection_attempt_start_time > timeout:
        break
      time.sleep_ms(300)

    print() 
    print(f'{"C" if interface.isconnected() else "NOT c"}onnected to network')
    if interface.isconnected():
      print(f'Connected to {ssid}')
      network_details = interface.ifconfig()
      mac_address = binascii.hexlify(interface.config('mac'), ':')
      print(f'MAC: {mac_address}')
      print(f'IP: {network_details[0]}')
      print(f'Subnet: {network_details[1]}')
      print(f'Gateway: {network_details[2]}')
      print(f'DNS: {network_details[3]}')
    else:
      print(f'Connection to {ssid} failed')

def check_for_update(project_name):
  if not validate_project(project_name):
    print(f'{project_name} is not valid or does not exist')
    return
  p_meta = get_project_settings(project_name)
  

