'''
This module is still in experimental mode, and its APIs might change.
The file "network_credentials.json" will be created in the board's root (be it "/" or "/flash" based on port).
auto_connect(): will attempt to connect to previously saved networks.
connect(ssid=None, key=None, interface=None): will cascade down from
  - connecting to specified ssid:key
  - using auto_connect()
  - using interactive connect_to_network() in REPL
'''
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

NETWORK_CACHE_LIFE = 10
NETWORK_CONFIG_FILE = f'{get_root()}network_config.json'

net_if = None

net_config = {
  "ap":{},
  "known_networks":[]
}

net_entry = {
  "name":b'',
  "mac": b'',
  "key": b''
}

local_networks_cache = {
  'last_scan': 0,
  'networks': []
}

ALLOW_PWD_CHAR_RANGE = range(32, 127)
MIN_PWD_LEN = 8
MAX_PWD_LEN = 63

def init_if(network_interface = None):
  global net_if
  interface = None
  if network_interface == None:
    interface = network.WLAN(network.STA_IF)
  else:
    interface = network_interface
  interface.active(False)
  time.sleep_ms(100)
  interface.active(True)
  net_if = interface
  return interface

def set_ap_config(ssid, key):
  net_config['ap'] = {'ssid': ssid, 'key': key}
  save_network_config()

def init_ap(ssid, key):
  global net_if, net_config
  if net_if != None:
    net_if.active(False)
  net_if = network.WLAN(network.AP_IF)
  
  net_if.active(True)
  network_security = None
  if platform == 'esp32':
    network_security = network.AUTH_WPA2_PSK
  if 'Nano RP2040' in implementation._machine:
    network_security = net_if.SEC_WEP
  
  net_if.config(ssid=ssid, security = network_security, key=key)
  set_ap_config(ssid, key)

def get_network_index(network_name):
  if type(network_name) == bytes:
    network_name = network_name.decode('utf-8')
  # networks_list = local_networks_cache['networks']
  networks_list = net_config['known_networks']
  result = list(filter(lambda m:networks_list[m]['name'] == network_name, range(len(networks_list))))
  if len(result) > 0:
    return result[0]
  else:
    return None

def get_network_index_by_mac(network_mac):
  if type(network_mac) == bytes:
    network_mac = binascii.hexlify(network_mac)
  # networks_list = local_networks_cache['networks']
  networks_list = net_config['known_networks']
  result = list(filter(lambda m:networks_list[m]['mac'] == network_mac, range(len(networks_list))))
  if len(result) > 0:
    return result[0]
  else:
    return None

def get_ap_settings():
  try:
    ssid = net_config['ap']['ssid']
    key = net_config['ap']['key']
    return ssid, key
  except KeyError:
    return None
  # return net_config['ap']['ssid'], net_config['ap']['key']

def find_scanned_matches():
  scanned_known_networks = []
  
  for n in net_config['known_networks']:
    # TODO: match b'MAC' first, b'NAME' after, since name might have changed
    # print('encoded name: ', (n['name']).encode())
    # print('mac: ', (n['mac']).encode())
    
    filtered = [item for item in local_networks_cache['networks'] if item[0] == (n['name']).encode() or binascii.hexlify(item[1]) == n['mac'].encode()]
    # print('filtered: ', filtered)
    if len(filtered) > 0:
      scanned_known_networks.append(n)
      
      
  return scanned_known_networks

def auto_connect(progress_callback = None):
  init_if()
  load_network_config()
  scan()
  matches = find_scanned_matches()
  # print(matches)
  connection_success = False
  for i, n in enumerate(matches):
    print(f'{i:<2}: {n}')
    if connect(ssid = n['name'], key = n['key'], progress_callback = progress_callback):
      connection_success = True
      break
  return connection_success
  
  

def scan(force_scan = False):
  if net_if == None:
    init_if()
  now = time.mktime(time.localtime())
  if now - local_networks_cache['last_scan'] < NETWORK_CACHE_LIFE and force_scan == False:
    return local_networks_cache['networks']
  networks_list = net_if.scan()
  networks_list.sort(key=lambda tup:tup[0])
  
  # global local_networks_cache
  local_networks_cache['networks'] = networks_list
  local_networks_cache['last_scan'] = time.mktime(time.localtime())
  return networks_list


def list_networks(rescan = False):
  scan(rescan)
  list_scan_results()

def list_scan_results():
  for i, n in enumerate(local_networks_cache['networks']):
    mac = binascii.hexlify(n[1], ':')
    print(f'{i:>2}: {(n[0]).decode('utf-8'):<20} [{mac}]')

def connect_to_network(id = None):
  print(f'*** CONNECT TO NETWORK {id}')
  if id == None:
    list_networks()
    choice = input('Choose a network [or ENTER to skip]: ')
    if choice == '':
      print('Connection canceled')
      return
    id = int(choice)
    
  networks_list = local_networks_cache['networks']
  ssid = networks_list[id][0]
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
  global net_if
  print(f'{ssid=} | {key=} | {progress_callback=}')
  if ssid == None and key == None:
    if not auto_connect(progress_callback):
      connect_to_network()
    return
  time.sleep_ms(500)
  global net_if
  print("net_if:", net_if)
  if interface == None:
    net_if = init_if()
  else:
    net_if = interface

  net_if.active(False)
  time.sleep_ms(100)
  net_if.active(True)
  time.sleep_ms(100)
  
  net_if.connect(ssid, key)
  connection_attempt_start_time = time.time()
  if display_progress:
    print()
    print(f"Connecting to {ssid}")
  max_dot_cols = 20
  dot_col = 0

  progress_index = 0
  progress_cycle = 0
  while net_if.isconnected() != True:
    if display_progress:
      if(dot_col % max_dot_cols == 0):
        print()
      print('>.', end = '')
      dot_col +=1
      time.sleep_ms(300)
    if progress_callback != None:
      progress_cycle += 1
      if progress_cycle % 10 == 0:
        progress_index += 1
        progress_callback(progress_index)
    if time.time() - connection_attempt_start_time > timeout:
      break

  if display_progress:
    print() 
    print(f'{"C" if net_if.isconnected() else "NOT c"}onnected to network')
    if net_if.isconnected():
      print(f'Connected to {ssid}')
      print_network_details(net_if)
    else:
      net_if.active(False)
      print(f'Connection to {ssid} failed')
      return None
  # return connection_status
  return net_if

def get_network_qrcode_string(ssid, password, security):
  return f'WIFI:S:{ssid};T:{security};P:{password};;'

def print_network_details(interface = net_if):
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
  networks_list = local_networks_cache['networks']
  net_info = networks_list[id]
  network_entry = net_entry.copy()
  network_entry['name'] = net_info[0].decode('utf-8')
  network_entry['mac'] = binascii.hexlify(net_info[1])
  network_entry['key'] = key
  # network_match_index = get_network_index(net_info[0])
  network_match_index = get_network_index_by_mac(net_info[1])
  # print(f'network match index: {network_match_index}')
  if network_match_index != None:
    # print('network match index is not None')
    net_config['known_networks'].pop(network_match_index)
  net_config['known_networks'].append(network_entry)
  save_network_config()
  return network_entry

def save_network_config():
  # fails when field is b''
  try:
    with open(NETWORK_CONFIG_FILE, 'w', encoding = 'utf-8') as f:
      return json.dump(net_config, f, separators=(',', ':'))
  except OSError as e:
    return None

def load_network_config():
  global net_config
  try:
    with open(NETWORK_CONFIG_FILE, 'r') as f:
      net_config = json.load(f)  
  except OSError as e:
    print(e)
    pass
  return net_config

def connection_progress_callback(t):
  print(f'- {t:^5} -')

# TODO/IDEAS
# encrypt passwords for stored network credentials
# use encryption function with a 4-6 numeric PIN to decrypt

