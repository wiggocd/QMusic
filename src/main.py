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
    #   -   Write the default config JSON if it doesn't exist and proceed to load the main config JSON
    #   -   Create QApplication
    #   -   Load QDarkStyle, set the app stylesheet from the config and create the lyrics object
    #   -   Create MainWindow
    #   -   Exit on app exec_ method

    lib.configDir = lib.get_configDir(lib.progName)
    lib.create_configDir(lib.configDir)
    lib.execDir = lib.get_execdir()
    # lib.styles.append(lib.loadQDarkStyle_fs(lib.execDir))
    lib.writeDefaultConfig()
    lib.config = lib.loadMainConfigJSON()

    app = QtWidgets.QApplication(sys.argv)

    lib.globalStyleIndex = lib.config["style"]
    lib.loadQDarkStyle_lib()
    lib.globalStyleSheet = lib.styles[lib.globalStyleIndex].styleSheet
    app.setStyleSheet(lib.globalStyleSheet)
    lib.setLyricsObject(lib.execDir)
    
    window = MainWindow(app)

    sys.exit(app.exec_())
