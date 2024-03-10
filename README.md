# Arduino Tools for MicroPython

A set of tools and helpers to implement, create and manage MicroPython Projects/Apps.

A new approach to enabling a MicroPython board to host/store multiple projects with the choice of running one as default, as well as have a mechanism of fallback to a default launcher.
It does not interfere with the canonical `boot.py`  > `main.py` run paradigm, and allows users to easily activate this functionality on top of any stock MicroPython file-system.

The Arduino MicroPython Projects framework relies on the creation of well structured projects enclosed in their own folders named "amp_{project-name}", which in turn contain a set of files (`main.py`, `lib/`, `app.json`, etc.).
These are the conditions for a project to be considered "valid".
Other files can be added to user's discretion, for instance to store assets or log/save data.

The framework exploits the standard behaviour of MicroPython at start/reset/soft-reset:

1. run `boot.py`
1. run `main.py`

The framework's boot.py only requires two lines for the following operations:

- import the minimum required parts of arduino_tools (common) from the board's FileSystem (preferrably installed as a module in /lib/arduino_tools)
- call a method to enter the default project's path and apply some temporary settings to configure the running environment (search paths and launch configuration changes) which will be reset at the next start.

If no default project is set, it will fall back to the `main.py` in the board's root if present.
No error condition will be generated, as MicroPython is capable of handling the absence of `boot.py` and/or `main.py`.

The reason for this to work is that if a default project is selected, the `enter_default_project()` will issue an `os.chdir()` command and enter the project's folder.
MicroPython will automatically run the main.py it finds in its Current Working Directory.

**NOTES:**

- each project can contain a `.hidden` file that will hide the project from AMP, effectively preventing listing or deletion.
The `list_projects()` command accepts a `skip_hidden = False` parameter to return every project, not just the visible ones.

- each project should contain a metadata file named `app.json`
  {
    "name": "",
    "author": "",
    "created": 0,
    "modified": 0,
    "version": "x.y.z",
    "origin_url": "",  
    "amp_version": "x.y.z"
  }
- while some fields should be mandatory ("name", "hidden") others could not be a requirement, especially for students projects who do not care about versions or source URL.
We should also handle if extra fields are added not to break legacy

- AMP can replace/update a project with the content of a `.tar` archive.
This is useful for updating versions of apps/launcher/demos.
An app launcher could be delegated to checking for available updates to any of the other apps it manages.

## How to setup

**NOTE:** The API is not yet final, hence subject to changes.
Same goes for the name of the module(s)

The only requirement is that all the files in `arduino_tools` should be transferred to the board using one's preferred method.
Best practice is to copy all the files in the board's `/lib/arduino_tools`, which is what happens when installing with the `mip` tool.

Enter a REPL session

```python
from arduino_tools.projects import *
show_commands()
```

read through the commands to know more.

To enable the projects framework run
`enable_amp_projects()`

The current `boot.py` (if present) will be backed up to `boot_backup.py`.
Any other file, including the `main.py` in the root (if present), will remain untouched.

`disable_amp_projects()` will restore boot.py from boot_backup.py if it was previously created.
If no backup file will be found it will ask the following:

This operation will delete "boot.py" from your board.
You can choose to:
A - Create a default one
B - Proceed to delete
C - Do nothing (default)

unless `disable_amp_projects('Y')` is invoked, which will force the choice to be B.

Setting the default project to '' (default_project('')) will also generate a choice menu.

The above behaviour is the result of Q&A sessions with other MicroPython developers and might be subject to change until a v1.0.0 is released.

## Basic usage

Enable AMP and create a few projects

```python
>>> from arduino_tools import *
>>> enable_amp_projects()

>>> create_project('abc')
>>> create_project('def')
>>> create_project('ghi')
>>> create_project('new project')

>>> list_projects()
  abc
  def
  ghi
  new_project

>>> default_project()
''

>>> default_project('def')
>>> default_project()
'def'

>>> import machine
>>> machine.soft_reset

MPY: soft reboot
Hello from project def
MicroPython v1.23.0-preview.138.gdef6ad474 on 2024-02-16; Arduino Nano ESP32 with ESP32S3
Type "help()" for more information.
>>> 
```
