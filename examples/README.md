# Examples and demo assets

## boot_restore.py

This file, when added to the board's root, is loaded at start and offers a method to restore a launcher in case of failure.
In this case the condition to restore `app_launcher` as the default application loading is to have `Pin(2)` pulled `LOW`.

## versions.json

This is an example `JSON` file to be reachable at an App's `origin_url` address.
The method `update_app(path = None)`, if `path` is not provided, will query that `URL` and verify that new versions of the App are available.

### Example usage (requires an active network connection)

```python
from arduino_tools.app import App
my_app = App('valid_app_name')
my_app.update()
```

## app_demo

This is a sample App that displays the structure of an application.
It includes a local `lib` folder, which highlights the fact that libraries local to the application don't need to be installed system-wide, also allowing other versions of packages to be installed on an App basis.
The loader add the local App's `lib` folder at the beginning of `system.path`.
