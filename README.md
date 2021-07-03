# About
Script to get all the DM and available server channels from the discord data package.
After retrieving these, all messages in the channel will be deleted (depending on parameters)

# Usage
`pip install -r requirements.txt`

`python main.py`

The script will guide you through the process

You will have to provide a user token and the path to the unzipped discord data package

# Building the .exe

`pip install pyinstaller`

`pyinstaller main.py --onefile -n 'clearcord_datapackage' -i NONE`

.exe in `./dist`

# TODO
 - Support for Group DM
