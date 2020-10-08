#
#   main.py
#   Entrypoint to the application
#

from PySide2 import QtWidgets
import sys
from widgets import MainWindow
import lib

if __name__ == "__main__":
    #   -   Set the config directory and check to create it
    #   -   Create QApplication
    #   -   Create MainWindow
    #   -   Exit on app exec_ method

    lib.configDir = lib.get_configDir(lib.progName)
    lib.create_configDir(lib.configDir)

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(app)

    sys.exit(app.exec_())
