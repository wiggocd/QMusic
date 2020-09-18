![alt text](https://github.com/[username]/[reponame]/blob/[branch]/image.jpg?raw=true)

### QMusic

QMusic is a simple application for audio playback written in Python using the PySide2 Qt5 framework.

*Please note: PySide2 version 5.14 or lower is required as of now due to a bug in QtMultimedia leading to QUrls containing spaces not working in Qt 5.15.*

## Dependencies

Python 3.5 or newer, with `python` or `python3` available in your path.

To install the required packages: `python3 setup.py install`

## Running

To run the program using the Python interpreter: `python3 setup.py run`


### Other Build Commands

*Please note, compilation is currently broken due to Nuitka not supporting PySide2.*

`python3 setup.py compile` - transpile the Python program to C and compile it to binary using Nuitka

`python3 setup.py run` - run the binary

`python3 setup.py compile -m` - build an application for macOS

`python3 setup.py run -m` - run the macOS application

`python3 setup.py clean` - clean the build environment

For more info, use `python3 setup.py --help`

For more commands, use `python3 setup.py --help-commands`
