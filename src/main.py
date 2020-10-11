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
    #   -   Set the execDir path to the directory of the executed file
    #   -   Create QApplication
    #   -   Create MainWindow
    #   -   Exit on app exec_ method

    lib.configDir = lib.get_configDir(lib.progName)
    lib.create_configDir(lib.configDir)
    lib.execDir = lib.get_execdir()
    lib.styles.append(lib.loadQDarkStyle(lib.execDir))

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(app)

    sys.exit(app.exec_())
