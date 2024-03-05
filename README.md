# Arduino Utilities for MicroPython

A set of tools to implement, create and manage MicroPython Projects/Apps.

A new approach to enabling a MicroPython board
to host/store multiple projects with the choice of running one as default.

It will not interfere with the canonical boot.py/main.py approach,
but will allow users to easily implement such functionality.

The framework is based on one or more well structured projects
which consist of folders named "amp_{project-name}" and contain a set of files (`main.py`, `lib/`, `app.json`).
These are the conditions for a project to be considered "valid".
Other files can be added to a user's discretion.

The framework exploits the standard behaviour of MicroPython at start:
1. run `boot.py`
1. run `main.py`

The framework's boot.py is only comprised of two lines which in turn

- import the minimum required parts of arduino_utils (common) from the board's FileSystem (preferrably installed as a module in /lib)
- call a method to enter the default project

If no default project is set, it will fall back to the `main.py` in the board's root if present.
No error condition will be generated, as MicroPython is capable of handling the absence of `boot.py` and/or `main.py`.

The reason for this to work is that if a default project is selected, the `enter_default_project()` will issue an `os.chdir()` command and enter the project's folder.
MicroPython will automatically run the main.py it finds in its Current Working Directory.


**NOTES:**

- each project can contain a `.hidden` file that will hide the project from AMP, effectively preventing listing or deletion.
The `list_projects()` command accepts a `skip_hidden = False` parameter to return everything.

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

## How to use it

**NOTE:** The API is not yet final, hence subject to changes.
Same goes for the name of the module(s)

The only requirement is that the files should be transferred to the board using your preferred method.

Enter a REPL session

```python
from arduino_utils import *
show_commands()
```

read through the commands to know more.

To enable the projects framework run
enable_amp_projects()

The current boot.py (if present) will be backed up to boot_backup.py.
Any other file, including a main.py in the root, will remain untouched.

disable_amp_projects() will restore boot.py from boot_backup.py if it was previously created.
If no backup file will be found it will ask the following:

This operation will delete "boot.py" from your board.
You can choose to:
A - Create a default one
B - Proceed to delete
C - Do nothing (default)\n''').strip() or 'C'

unless disable_amp_projects('Y') is invoked, which will force the choice to be B.

Setting the default project to '' (default_project('')) will also generate a choice menu.

The above behaviour is the result of Q&A sessions with other
MicroPython developers and is subject to change until a v1.0.0 is released
