from .utils.semver import *
from .apps_manager import *
import sys

apps = []
for app in get_apps_list():
  apps.append(get_app_properties(app['name']))

buf = bytearray(1024)

if NETWORK_UPDATE:
  try:
    import mrequests
  except ImportError:
    print('Install mrequests')
    print('https://github.com/SpotlightKid/mrequests')

class ResponseWithProgress(mrequests.Response):
    _total_read = 0

    def readinto(self, buf, size=0):
        bytes_read = super().readinto(buf, size)
        self._total_read += bytes_read
        print("Progress: {:.2f}%".format(self._total_read / (self._content_size * 0.01)))
        return bytes_read


# if len(sys.argv) > 1:
#     url = sys.argv[1]

#     if len(sys.argv) > 2:
#         filename = sys.argv[2]
#     else:
#         filename = url.rsplit("/", 1)[1]
# else:
#     host = "http://httpbin.org/"
#     # host = "http://localhost/"
#     url = host + "image"
#     filename = "image.png"

def get_updated_version(app_name, url, version):
    current_version = SemVer.from_string(version)
    r = mrequests.get(url + '/versions.json')
    updated_version = None
    if r.status_code == 200:
        updates = json.loads(r.text)
        latest_version = SemVer.from_string(updates['latest'])
        print(f'Current version: {version}')
        print(f'Latest version: {latest_version}')
        if current_version < latest_version:
            versions = updates['versions']
            print("Update available.")
            for ver in versions:
                print(f'{ver} - {versions[ver]["file_name"]}')
            updated_version = versions[updates['latest']]
        else:
            print("No update available.")   
    else:
        print("Request failed. Status: {}".format(r.status_code))
    r.close()
    return updated_version
    

file_download = None

def file_get(url, file_path):
    r = mrequests.get(url, headers={b"accept": b"application/x-tar"}, response_class=ResponseWithProgress)
    download_success = False
    if r.status_code == 200:
        r.save(file_path, buf=buf)
        print(f'file saved to "{file_path}"')
        download_success = True
    else:
        print("Request failed. Status: {}".format(r.status_code))
    
    r.close()
    return download_success

def check_for_updates(app_name, force_update = False):
    properties = get_app_properties(app_name)
    ota_url = properties['origin_url']
    version = properties['version']
    print(ota_url, version)
    updated_version = get_updated_version(app_name, ota_url, version)
    if updated_version != None:
        if force_update:
            return app_update(app_name, ota_url, updated_version)
        else:
            confirm = input(f'Do you want to update {app_name} from {version} to {updated_version['version']}? (y/n): ')
            if confirm == 'y':
                return app_update(app_name, ota_url, updated_version)
    return False

def app_update(app_name, ota_url, updated_version):
    """Download and install app update"""
    update_file_name = updated_version['file_name']
    update_file_url = f'{ota_url}/{update_file_name}'
    
    try:
        os.mkdir('/tmp')
    except OSError:
        print('/tmp already exists')
    
    download_file_path = f'/tmp/{update_file_name}'
    download_success = file_get(update_file_url, download_file_path)
    
    if download_success:
        import_app(download_file_path, True)
        return True
    return False
