# QMusic

QMusic is a simple application for audio playback written in Python using the PySide2 Qt5 framework.


# Dependencies

Python 3.5 or newer with `python` or `python3` available in your path along with Python setuptools.

`python3 setup.py install` - install the required packages


# Running

`python3 setup.py run` - run the program using the Python interpreter


# Screenshots

macOS default theme

<img src="resources/documentation/screenshotmacos.png" width=320 style="border-radius: 4px; margin-bottom: 10px"/>
Linux QDarkStyle theme

<img src="resources/documentation/screenshotlinux.png" width=320 style="border-radius: 4px; margin-bottom: 10px"/>

# Environment Commands

`python3 setup.py build_exec` - build an executable for the current platform on Windows or Unix systems, should output to the `dist` directory and may require sudo on some systems


# Other Environment Commands

`python3 setup.py clean` - clean the build environment

`python3 setup.py py2app -A` - build a macOS app in alias mode, requiring the local files to still be in place

`sudo python3 setup.py build_exec -a` - write a script to /usr/local/bin on Unix-like systems from which QMusic is launched

`python3 setup.py run -e` - run the built executable, app or link mode executable which will be detected

For more info, run `python3 setup.py --help`

For more commands, run `python3 setup.py --help-commands`


# Other Notes

There is a token for the lyrics from Genius in the ` ` variable of `src/lib.py`, however if the token in here is invalid, you can replace it with your own by using the Genius API from their website. The documentation can also be found in `reference.txt`.

_______________________

# Other and Non-Functional Commands

**Please note, compilation is currently broken due to Nuitka not supporting PySide2/Shiboken2 whilst the py2app configuration is currently not working with PySide2 in the standard mode.**

~~`python3 setup.py py2app` - build a macOS app~~

~~`python3 setup.py compile` - build an executable using Nuitka~~
