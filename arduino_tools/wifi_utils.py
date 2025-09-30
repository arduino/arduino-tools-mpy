'''
Module still in experimental phase, API might change.
"network_credentials.json" will be created in root ("/" or "/flash").
auto_connect(): attempts connection to previously saved networks.
connect(): will trickle down through
  - connecting to ssid:key
  - auto_connect()
  - interactive connect_to_network() in REPL
'''
# TODO/IDEAS
# encrypt passwords for stored network credentials
# use encryption function with a 4-6 numeric PIN to decrypt


import json
import network
import time
import binascii
from sys import platform, implementation
from .common import get_root

'''
ONLY for ESP32
1000 STAT_IDLE – no connection and no activity,
1001 STAT_CONNECTING – connecting in progress,
 202 STAT_WRONG_PASSWORD – failed due to incorrect password,
 201 STAT_NO_AP_FOUND – failed because no access point replied,
 203 STAT_ASSOC_FAIL/STAT_CONNECT_FAIL – failed due to other problems,
1010 STAT_GOT_IP – connection successful.
'''

_NETWORK_CACHE_LIFE = 10
_NETWORK_CONFIG_FILE = f'{get_root()}network_config.json'

_net_if = None

_net_config = {
  "ap":{},
  "known_networks":[]
}

_net_entry = {
  "name":b'',
  "mac": b'',
  "key": b''
}

_local_networks_cache = {
  'last_scan': 0,
  'networks': []
}

_ALLOW_PWD_CHAR_RANGE = range(32, 127)
_MIN_PWD_LEN = 8
_MAX_PWD_LEN = 63

def init_if(network_interface = None):
  global _net_if
  interface = None
  if network_interface == None:
    interface = network.WLAN(network.STA_IF)
  else:
    interface = network_interface
  interface.active(False)
  time.sleep_ms(100)
  interface.active(True)
  _net_if = interface
  return interface

def set_ap_config(ssid, key):
  _net_config['ap'] = {'ssid': ssid, 'key': key}
  save_network_config()

def init_ap(ssid, key):
  global _net_if, _net_config
  if _net_if != None:
    _net_if.active(False)
  _net_if = network.WLAN(network.AP_IF)
  
  _net_if.active(True)
  network_security = None
  if platform == 'esp32':
    network_security = network.AUTH_WPA2_PSK
  if 'Nano RP2040' in implementation._machine:
    network_security = _net_if.SEC_WEP
  
  _net_if.config(ssid=ssid, security = network_security, key=key)
  set_ap_config(ssid, key)

def get_network_index(network_name):
  if type(network_name) == bytes:
    network_name = network_name.decode('utf-8')
  # network_list = local_networks_cache['networks']
  network_list = _net_config['known_networks']
  result = list(filter(lambda m:network_list[m]['name'] == network_name, range(len(network_list))))
  if len(result) > 0:
    return result[0]
  else:
    return None

def get_network_index_by_mac(network_mac):
  if type(network_mac) == bytes:
    network_mac = binascii.hexlify(network_mac)
  network_list = _net_config['known_networks']
  result = list(filter(lambda m:network_list[m]['mac'] == network_mac, range(len(network_list))))
  if len(result) > 0:
    return result[0]
  else:
    return None

def get_ap_settings():
  try:
    ssid = _net_config['ap']['ssid']
    key = _net_config['ap']['key']
    return ssid, key
  except KeyError:
    return None

def find_scanned_matches():
  scanned_known_networks = []
  
  for n in _net_config['known_networks']:
    # TODO: match b'MAC' first, b'NAME' after, since name might have changed
    # print('encoded name: ', (n['name']).encode())
    # print('mac: ', (n['mac']).encode())
    
    # filtered = [item for item in _local_networks_cache['networks'] if item[0] == (n['name']).encode() or binascii.hexlify(item[1]) == n['mac'].encode()]
    filtered = [item for item in _local_networks_cache['networks'] if binascii.hexlify(item[1]) == n['mac'].encode()]
    if len(filtered) > 0:
      scanned_known_networks.append(n)
  return scanned_known_networks

def auto_connect(progress_callback = None):
  init_if()
  load_network_config()
  wifi_scan()
  matches = find_scanned_matches()
  connection_success = False
  for i, n in enumerate(matches):
    print(f'{i:<2}: {n}')
    if connect(ssid = n['name'], key = n['key'], progress_callback = progress_callback):
      connection_success = True
      break
  return connection_success
  
  
def wifi_scan(force_scan = False):
  if _net_if == None:
    init_if()
  now = time.mktime(time.localtime())
  if now - _local_networks_cache['last_scan'] < _NETWORK_CACHE_LIFE and force_scan == False:
    return _local_networks_cache['networks']
  network_list = _net_if.scan()
  network_list.sort(key=lambda tup:tup[0])
  _local_networks_cache['networks'] = network_list
  _local_networks_cache['last_scan'] = time.mktime(time.localtime())
  return network_list

def list_networks(rescan = False):
  wifi_scan(rescan)
  print_scan_results()

def print_scan_results():
  for i, n in enumerate(_local_networks_cache['networks']):
    mac = binascii.hexlify(n[1], ':')
    print(f'{i:>2}: {(n[0]).decode('utf-8'):<20} [{mac}]')


def connect_to_network(id = None):
  print(f'*** CONNECTING TO NETWORK {id}')
  if id == None:
    list_networks()
    choice = input('Choose a network [or ENTER to skip]: ')
    if choice == '':
      print('Connection canceled')
      return
    id = int(choice)
    
  network_list = _local_networks_cache['networks']
  ssid = network_list[id][0]
  print(f'Connect to {ssid.decode('utf-8')}')
  key = input('Password: ')
  net_if = connect(ssid, key, display_progress = True)
  if net_if is not None:
    print(f'Successful connection to {ssid} on interface: {net_if}')
    if net_if.ifconfig()[0] != '0.0.0.0':
      store_net_entry(id, key)
  else:
    raise OSError(f"Failed to connect to {ssid}")


def connect(ssid = None, key = None, interface = None, timeout = 10, display_progress = False, progress_callback = None):
  global _net_if
  print(f'{ssid=} | {key=} | {progress_callback=}')
  if ssid == None and key == None:
    if not auto_connect(progress_callback):
      connect_to_network()
    return
  time.sleep_ms(500)
  global _net_if
  print("net_if:", _net_if)
  if interface == None:
    _net_if = init_if()
  else:
    _net_if = interface

  _net_if.active(False)
  time.sleep_ms(100)
  _net_if.active(True)
  time.sleep_ms(100)
  
  _net_if.connect(ssid, key)
  connection_attempt_start_time = time.time()
  if display_progress:
    print()
    print(f"Connecting to {ssid}")
  

  progress_index = 0
  progress_cycle = 0
  while _net_if.isconnected() != True:
    if display_progress:
      progress_callback = progress_callback or _sample_connection_progress_callback
    if progress_callback != None:
      progress_cycle += 1
      if progress_cycle % 10 == 0:
        progress_index += 1
        progress_callback(progress_index)
    if time.time() - connection_attempt_start_time > timeout:
      break

  if display_progress:
    print() 
    print(f'{"C" if _net_if.isconnected() else "NOT c"}onnected to network')
    if _net_if.isconnected():
      print(f'Connected to {ssid}')
      print_network_details(_net_if)
    else:
      _net_if.active(False)
      print(f'Connection to {ssid} failed')
      return None
  return _net_if

def get_network_qrcode_string(ssid, password, security):
  return f'WIFI:S:{ssid};T:{security};P:{password};;'

def print_network_details(interface = _net_if):
  if interface is None:
    raise AttributeError("Network interface not initialized")
  network_details = interface.ifconfig()
  mac_address = binascii.hexlify(interface.config('mac'), ':')
  print(f'MAC: {mac_address}')
  print(f'IP: {network_details[0]}')
  print(f'Subnet: {network_details[1]}')
  print(f'Gateway: {network_details[2]}')
  print(f'DNS: {network_details[3]}')


def store_net_entry(id, key):
  network_list = _local_networks_cache['networks']
  net_info = network_list[id]
  network_entry = _net_entry.copy()
  network_entry['name'] = net_info[0].decode('utf-8')
  network_entry['mac'] = binascii.hexlify(net_info[1])
  network_entry['key'] = key
  network_match_index = get_network_index_by_mac(net_info[1])
  if network_match_index != None:
    _net_config['known_networks'].pop(network_match_index)
  _net_config['known_networks'].append(network_entry)
  save_network_config()
  return network_entry

def save_network_config(net_config_file_path = None):
  net_config_file_path = net_config_file_path or _NETWORK_CONFIG_FILE
  try:
    with open(net_config_file_path, 'w', encoding = 'utf-8') as f:
      return json.dump(_net_config, f, separators=(',', ':'))
  except OSError as e:
    return None

def load_network_config(net_config_file_path = None):
  global _net_config
  net_config_file_path = net_config_file_path or _NETWORK_CONFIG_FILE
  try:
    with open(net_config_file_path, 'r') as f:
      _net_config = json.load(f)  
  except OSError as e:
    print(e)
    pass
  return _net_config

# Connection progress callback example
_max_dot_cols = 20
_dot_col = 0
def _sample_connection_progress_callback(t):
  global _dot_col
  if(_dot_col % _max_dot_cols == 0):
    print()
  print('.', end = '')
  _dot_col +=1
