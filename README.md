# gaeb_parser
parses xml gaeb files and converts them to a pandas dataframe

![Screenshot of the example import.](example_screenshot.jpg)

## Use it:
- run main.py
- see console output

## Change it:

### Install required modules in venv

`python -m venv .venv`

`Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force`

`.venv/Scripts/activate.ps1`

`pip install -r requirements.txt`


### runt tests
`Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force`

`.venv/Scripts/activate.ps1`

`pytest`

## To-Dos:
- some elements are not parsed yet, see console output
- XML export