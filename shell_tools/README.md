# MicroPython Apps Framework developer helpers [WIP]

These `bash` shell scripts simplify working with the framework from the host machine and allows creating, deploying and backing up applications to and fromt he board.

## Requirements

These scripts require `arduino-tools-mpy` to be installed on the board and `mpremote` to be installed on the host computer:

```shell
pip install mpremote
```

## How to use
```shell
./chmod +x app_util
./app_util
mpremote: no device found
Usage: ./app_util.sh <command>:
• help
• create
• install
• backup
• remove
• delete
• list
• run
```

## How it works

These scripts will leverage the board's installed `arduino-tools-mpy` to create, backup and delete MicroPython apps on the board.
For example, creating an app with `./app_util create {APP_NAME} {App Friendly Name}` will run code on the board, create the app (will ask for confirmation to overwrite if already present), back it up to a `.tar` archive and transfer it to the local machine, expand it and make it available locally.

Running

```shell
./app_util create demo_app Demo Application
```

Will generate the following output:

```shell
☑️ Querying MicroPython board...
☑️ Checking if "/app_weather" exists on board
📦 App "Weather Widget" does not exist on board. Creating...
☑️ Creating app "weather" with friendly name "Weather Widget"
☑️ Archiving "weather" on board
☑️ Copying app "weather" archive to local machine
☑️ 🗜️ Extracting "weather_23987.tar" to app_weather

✅ App "Weather Widget" created and available locally
```

