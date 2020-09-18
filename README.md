# QMusic

QMusic is a simple application for audio playback written in Python using the PySide2 Qt5 framework.

*Please note: PySide2 version 5.14 or lower is required as of now due to a bug in QtMultimedia leading to QUrls containing spaces not working in Qt 5.15.*

# Dependencies

Python 3.5 or newer, with `python` or `python3` available in your path.

`python3 setup.py install` - install the required packages

# Running

`python3 setup.py run` - run the program using the Python interpreter

# Screenshots

<img src="resources/documentation/screenshot.png" width=320 style="border-radius: 4px; margin-bottom: 10px"/>

# Other Environment Commands

`python3 setup.py clean` - clean the build environment

For more info, use `python3 setup.py --help`

For more commands, use `python3 setup.py --help-commands`


**Please note, compilation is currently broken due to Nuitka not supporting PySide2.**

~~`python3 setup.py compile` - transpile the Python program to C and compile it to binary using Nuitka~~

~~`python3 setup.py run -e` - run the binary~~

~~`python3 setup.py compile -m` - build an application for macOS~~

~~`python3 setup.py run -m` - run the macOS application~~
