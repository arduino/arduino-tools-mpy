from os import stat, chdir
try:
  with open('arduino.cfg', 'r') as c:
    p = c.readline()
    s = stat(p)
    if s[0] == 0x4000:
      chdir(p)
    else:
      __import__(p.split('.py')[0])
except OSError:
  print('\nNo valid boot configuration found')