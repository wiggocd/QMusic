#!python
# EASY-INSTALL-ENTRY-SCRIPT: 'py2exe==0.9.2.2','console_scripts','build_exe'
__requires__ = 'py2exe==0.9.2.2'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('py2exe==0.9.2.2', 'console_scripts', 'build_exe')()
    )
