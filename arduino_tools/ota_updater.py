# ABSOLUTELY WORK IN PROGRESS
# BROKEN PIECE OF... CODE
# HERE JUST AS A PLACEHOLDER
# GO AWAY, SHOO!
# THIS IS NOT THE FILE YOU ARE LOOKING FOR
# MOVE ALONG

"""Example of how to download a file in chunk using a pre-allcoated buffer
and print download progress."""

from .apps import *
import sys
import mrequests

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


if len(sys.argv) > 1:
    url = sys.argv[1]

    if len(sys.argv) > 2:
        filename = sys.argv[2]
    else:
        filename = url.rsplit("/", 1)[1]
else:
    host = "http://httpbin.org/"
    # host = "http://localhost/"
    url = host + "image"
    filename = "image.png"


file_download = None

def ota_get(url, file_path):
    r = mrequests.get(url, headers={b"accept": b"application/x-tar"}, response_class=ResponseWithProgress)
    if r.status_code == 200:
        r.save(file_path, buf=buf)
        print("file saved to '{}'.".format(file_path))
    else:
        print("Request failed. Status: {}".format(r.status_code))

    r.close()


ota_url = get_app_properties('ubi_ota', 'origin_url')
ota_get(ota_url, '/ubi_ota.tar')
