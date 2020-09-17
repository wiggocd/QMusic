#
#   main.py
#   Entrypoint to the application
#

from PySide2 import QtWidgets
import sys
from MainWindow import MainWindow

if __name__ == "__main__":
    #   -   Create QApplication and MainWindow
    #   -   Exit on app exec_ method

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
