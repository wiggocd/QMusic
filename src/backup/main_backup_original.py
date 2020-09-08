#
#   main.py
#   Entrypoint to the application
#

from PySide2 import QtWidgets, QtCore, QtGui, QtMultimedia
import sys
import os
from typing import List

progname = "QAmp"

def getexecpath() -> str:
    return os.path.dirname(os.path.realpath(__file__))

def resourcepath(execpath: str, relativePathToResource: str) -> str:
    return os.path.dirname(execpath) + os.path.sep + "Resources" + os.path.sep + relativePathToResource

def hhmmss(ms: int) -> str:
    s = round(ms / 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return ("%d:%02d:%02d" % (h, m, s)) if h else ("%d:%02d" % (m, s))

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, execpath):
        super().__init__()
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.title = progname
        self.execpath = execpath

        self.initUI()

    def initUI(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)

        self.previousButton = QtWidgets.QPushButton("Previous Track", self)
        self.nextButton = QtWidgets.QPushButton("Next Track", self)
        self.playpauseButton = QtWidgets.QPushButton(self)
        
        self.volumeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volumeSlider.setMinimum(0)
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setValue(100)
        self.timeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.totalTimeLabel = QtWidgets.QLabel()

        self.playlistView = QtWidgets.QListView(self)

        self.initPlayer()
        self.initPlaylist()
        self.createLayout()
        self.createMenus()

        self.player.setVolume(100)

        self.mainWidget = QtWidgets.QWidget()
        self.mainWidget.setLayout(self.vLayout)
        self.setCentralWidget(self.mainWidget)
        
        self.show()
    
    def initPlayer(self):
        self.player = QtMultimedia.QMediaPlayer(self)
        self.pause()
        self.volumeSlider.valueChanged.connect(self.player.setVolume)
        self.timeSlider.valueChanged.connect(self.player.position)
        self.player.durationChanged.connect(self.update_duration)
        self.player.positionChanged.connect(self.update_position)

    def initPlaylist(self):
        self.playlist = QtMultimedia.QMediaPlaylist()
        self.player.setPlaylist(self.playlist)
        self.previousButton.pressed.connect(self.playlist.previous)
        self.nextButton.pressed.connect(self.playlist.next)

        self.model = PlaylistModel(self.playlist)
        self.playlistView.setModel(self.model)
        self.playlist.currentIndexChanged.connect(self.playlist_position_changed)
        selection_model = self.playlistView.selectionModel()
        selection_model.selectionChanged.connect(self.playlist_selection_changed)

        self.setAcceptDrops(True)
    
    def playlist_position_changed(self, index: int):
        self.playlist.setCurrentIndex(index)

    def playlist_selection_changed(self, selection: QtCore.QItemSelection):
        if len(selection.indexes()) > 0:
            index = selection.indexes()[0].row()
            if index > -1:
                ix = self.model.index(index)
                self.playlistView.setCurrentIndex(ix)

    def dragEnterEvent(self, e: QtGui.QDropEvent):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e: QtGui.QDropEvent):
        for url in e.mimeData().urls():
            self.playlist.addMedia(
                QtMultimedia.QMediaContent(url)
            )
        
        self.model.layoutChanged.emit()

        # If not playing, seek to first of newly added and play the item
        if self.player.state != QtMultimedia.QMediaPlayer.PlayingState:
            i = self.playlist.mediaCount() - len(e.mimeData().urls())
            self.playlist.setCurrentIndex(i)
            self.play()

    def open_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "mp3 Audio (*.mp3);;mp4 Video (*.mp4);;Movie files (*.mov);;All files (*.*)")

        if path:
            self.playlist.addMedia(
                QtMultimedia.QMediaContent(
                    QtCore.QUrl.fromLocalFile(path)
                )
            )
        
        self.model.layoutChanged.emit()

    def createLayout(self):
        hGroup = QtWidgets.QWidget()

        hLayout = QtWidgets.QHBoxLayout()
        hLayout.addWidget(self.previousButton)
        hLayout.addWidget(self.playpauseButton)
        hLayout.addWidget(self.nextButton)
        hLayout.addWidget(self.volumeSlider)
        hGroup.setLayout(hLayout)

        hGroup2 = QtWidgets.QWidget()

        hLayout2 = QtWidgets.QHBoxLayout()
        hLayout2.addWidget(self.timeSlider)
        hLayout2.addWidget(self.totalTimeLabel)
        hGroup2.setLayout(hLayout2)

        self.vLayout = QtWidgets.QVBoxLayout()
        self.vLayout.addWidget(hGroup)
        self.vLayout.addWidget(hGroup2)
        self.vLayout.addWidget(self.playlistView)

    def createMenus(self):
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu("File")

        openAction = QtWidgets.QAction("Open", self)
        openAction.triggered.connect(self.open_file)
        fileMenu.addAction(openAction)
        #exitAction = QtWidgets.QAction(" &Exit", self)
        #exitAction.triggered.connect(self.close)
        #fileMenu.addAction(exitAction)

    def update_duration(self, duration: int):
        self.timeSlider.setMaximum(duration)

        if duration >= 0:
            self.totalTimeLabel.setText(hhmmss(duration))
    
    def update_position(self):
        self.timeSlider.setValue(self.player.position())

    def resourcepath_local(self, relativePathToResource: str) -> str:
        return resourcepath(self.execpath, relativePathToResource)
    
    def pause(self):
        self.player.pause()
        self.playpauseButton.setText("Play")
        self.playpauseButton.pressed.connect(self.play)
        self.isPlaying = False

    def play(self):
        self.player.play()
        self.playpauseButton.setText("Pause")
        self.playpauseButton.pressed.connect(self.pause)
        self.isPlaying = True

    def playpause(self):
        if self.isPlaying:
            self.pause()
        else:
            self.play()

class PlaylistModel(QtCore.QAbstractListModel):
    def __init__(self, playlist):
        super().__init__()
        self.playlist = playlist

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            media = self.playlist.media(index.row())
            return media.canonicalUrl().fileName()

    def rowCount(self, index):
        return self.playlist.mediaCount()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(getexecpath())
    sys.exit(app.exec_())
