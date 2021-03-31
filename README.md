# QMusic

QMusic is a simple application for audio playback written in Python using the PySide2 Qt5 framework.


# Dependencies

Python 3.5 or newer with `python` or `python3` available in your path along with Python setuptools.

# Build Environment

`python3 setup.py install` - install the required packages


# Running

`python3 setup.py run`


# Screenshots
Screenshot on macOS with default theme

<img src="resources/documentation/screenshot.png" width=320 style="border-radius: 4px; margin-bottom: 10px"/>

# Build Commands

`python3 setup.py build_exec` - build an executable for the current platform on Windows or Unix systems, should output to the `dist` directory and requires sudo on Unix systems


# Other Build Commands

`python3 setup.py clean` - clean the build environment

`python3 setup.py py2app -A` - build a macOS app in alias mode, requiring the local files to still be in place

`sudo python3 setup.py build_exec -a` - write a script to /usr/local/bin on Unix-like systems from which QMusic is launched

`python3 setup.py run -e` - run the built executable, app or link mode executable which will be detected

For more info, run `python3 setup.py --help`

For more commands, run `python3 setup.py --help-commands`


# Other Notes

There is a token for the lyrics from Genius in the `lyricsToken` variable of `src/lib.py`, however if the token in here is invalid, you can replace it with your own by using the Genius API from their website. The documentation can also be found in `reference.txt`.
