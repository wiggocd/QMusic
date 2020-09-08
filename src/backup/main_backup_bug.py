#
#   main.py
#   Entrypoint to the application.
#

from PySide2 import QtWidgets, QtCore, QtGui, QtMultimedia
import sys
import os

def get_execpath() -> str:
    # Return parent directory of real path for current file
    return os.path.dirname(os.path.realpath(__file__))

def get_resourcepath(resourceName: str, execpath: str) -> str:
    # Return resource inside resources directory within parent directory of the path to the executable
    return os.path.join(os.path.dirname(execpath), "resources", resourceName)

def to_hhmmss(ms: int) -> str:
    #   Synopsis:
    #   -   s = ms / 1000 rounded
    #   -   m and s = s modulo 60
    #   -   h and m = m modulo 60
    #   -   Return hh:mm:ss formatted/padded string if h, else return mm:ss

    s = round(ms / 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)

    return ("%d:%02d:%02d" % (h, m, s)) if h else ("%d:%02d" % (m, s))


#
#   Revise
#

class PlaylistModel(QtCore.QAbstractListModel):
    #   Synopsis:
    #   init:
    #       -   Call init from super
    #       -   Set playlist from argument
    #   data:
    #       -   If role is display role, set media from playlist media method at index row member
    #               Return canonical file name of media from playlist at index row
    #   rowCount:
    #       -   Return playlist media count

    def __init__(self, playlist: QtMultimedia.QMediaPlaylist):
        super().__init__()
        self.playlist = playlist

    def data(self, index: QtCore.QModelIndex, role: QtCore.Qt.ItemDataRole):
        if role == QtCore.Qt.DisplayRole:
            media = self.playlist.media(index.row())
            return media.canonicalUrl().fileName()
    
    def rowCount(self, index):
        return self.playlist.mediaCount()


class MainWindow(QtWidgets.QMainWindow):
    #   Synopsis:
    #   -   init: call init on super, initUI:
    #       -   Set geometry and title
    #       -   Set variable with path to executable to find resources later on
    #       -   Create widgets: buttons for media controls, labels, sliders
    #       -   Initialise player, connect to time and volume sliders
    #       -   Set to paused state
    #       -   Update the duration to 0
    #       -   Initialise playlist
    #       -   Add widgets to layout
    #       -   Create central widget and set layout on central widget
    #       -   Create menus
    #       -   Show

    def __init__(self):
        super().__init__()
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.title = "QAmp"

        self.get_execpath()
        self.initUI()

    def initUI(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)

        self.createWidgets()
        self.initPlayer()
        self.initPlaylist()
        self.pause()
        self.update_duration(0)
        self.createLayout()
        self.createCentralWidget()
        self.createMenus()
        
        self.show()

    def get_execpath(self):
        self.execpath = get_execpath()

    def createWidgets(self):
        # Create buttons, labels and sliders
        self.control_playpause = QtWidgets.QPushButton("Play")
        self.control_playpause.pressed.connect(self.play)
        self.control_previous = QtWidgets.QPushButton("Previous")
        self.control_next = QtWidgets.QPushButton("Next")
        self.control_stop = QtWidgets.QPushButton("Stop")

        self.volumeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setValue(100)
        self.timeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.totalTimeLabel = QtWidgets.QLabel()

    def initPlayer(self):
        # Create QMediaPlayer and connect to time and volume sliders value changed members, connect player position/duration changed to update position and duration methods
        self.player = QtMultimedia.QMediaPlayer()
        self.volumeSlider.valueChanged.connect(self.player.setVolume)
        self.timeSlider.valueChanged.connect(self.player.setPosition)
        self.player.durationChanged.connect(self.update_duration)
        self.player.positionChanged.connect(self.update_position)

    def update_duration(self, duration: int):
        # If a track is playing, set time slider maximum from argument
        if duration > 0:
            self.timeSlider.setMaximum(duration)

        # Set the total time label to the formatted duration
        self.totalTimeLabel.setText(to_hhmmss(duration))


    def update_position(self):
        # Set time slider value, refresh labels
        self.timeSlider.setValue(self.player.position())

    def initPlaylist(self):
        # Create QMediaPlaylist, connect to player, create and connect playlist model, connect media control pressed signals to playlist methods
        self.playlist = QtMultimedia.QMediaPlaylist()
        self.player.setPlaylist(self.playlist)
        self.playlistModel = PlaylistModel(self.playlist)
        self.control_previous.pressed.connect(self.playlist.previous)
        self.control_next.pressed.connect(self.playlist.next)

        # Create playlist view and set model, create selection model from playlist view and connect playlist selection changed method
        self.playlistView = QtWidgets.QListView()
        self.playlistView.setModel(self.playlistModel)
        selectionModel = self.playlistView.selectionModel()
        selectionModel.selectionChanged.connect(self.playlist_selection_changed)

        self.setAcceptDrops(True)

    #
    #   Revise
    #

    def playlist_position_changed(self, index: QtCore.QModelIndex):
        # Set playlist current index from model index row
        self.playlist.setCurrentIndex(index.row())

    #
    #   Revise
    #

    def playlist_selection_changed(self, selection: QtCore.QItemSelection):
        # If selection indexes are passed, set index to the first row from the index array
        if len(selection.indexes()) > 0:
            index = selection.indexes()[0].row()

            # If index is not negative, (deselection), set playlist view current index to model index from local index
            if index > -1:
                ix = self.playlistModel.index(index)
                self.playlistView.setCurrentIndex(ix)

    def pause(self):
        # Call the pause method of the player and replace play/pause button properties to play; disconnect, set icon and connect to play method
        self.player.pause()
        self.control_playpause.setText("Play")
        self.control_playpause.pressed.connect(None)
        self.control_playpause.pressed.disconnect()
        self.control_playpause.pressed.connect(self.play)

    def play(self):
        # If playlist has media, call the play method of the player and replace play/pause button properties to pause; disconnect, set icon and connect to pause method
        if self.playlist.mediaCount() > 0:
            self.player.play()
            self.control_playpause.setText("Pause")
            self.control_playpause.pressed.connect(None)
            self.control_playpause.pressed.disconnect()
            self.control_playpause.pressed.connect(self.pause)
    
    def createLayout(self):
        # Create main vertical layout, add horizontal layouts with added sub-widgets to vertical layout
        self.vLayout = QtWidgets.QVBoxLayout()
        
        hControlLayout = QtWidgets.QHBoxLayout()
        hControlLayout.addWidget(self.control_previous)
        hControlLayout.addWidget(self.control_playpause)
        hControlLayout.addWidget(self.control_next)
        hControlLayout.addWidget(self.control_stop)
        hControlLayout.addWidget(self.volumeSlider)

        hTimeLayout = QtWidgets.QHBoxLayout()
        hTimeLayout.addWidget(self.timeSlider)
        hTimeLayout.addWidget(self.totalTimeLabel)

        vDetailsLayout = QtWidgets.QVBoxLayout()
        vDetailsLayout.addLayout(hControlLayout)
        vDetailsLayout.addLayout(hTimeLayout) 

        detailsGroup = QtWidgets.QGroupBox()
        detailsGroup.setLayout(vDetailsLayout)

        self.vLayout.addWidget(detailsGroup)
        self.vLayout.addWidget(self.playlistView)

    def createCentralWidget(self):
        # Create central widget, call set central widget method and set widget layout
        self.centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.vLayout)

    def createMenus(self):
        # Create main menu from menuBar method, use addMenu for submenus and add QActions accordingly with triggered connect method
        self.mainMenu = self.menuBar()
        fileMenu = self.mainMenu.addMenu("File")
        
        openAction = QtWidgets.QAction("Open", self)
        openAction.triggered.connect(self.open_file)
        fileMenu.addAction(openAction)

    #
    #   Revise
    #

    def open_file(self):
        # Set paths from QFileDialog getOpenFileNames, filetypes formatted as "Name (*.extension);;Name2" etc.
        paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Open Files", "", "All Files (*.*);;Waveform Audio (*.wav);;mp3 Audio (*.mp3)")

        # For each path, add media QMediaContent from local file to playlist
        if paths:
            for path in paths:
                self.playlist.addMedia(
                    QtMultimedia.QMediaContent(
                        QtCore.QUrl.fromLocalFile(path)
                    )
                )

        # Emit playlist model layout change and play if paused
        self.playlistModel.layoutChanged.emit()

        if self.isPlaying() == False:
            self.play()

    #
    #   Revise
    #
    #   Synopsis of drag and drop:
    #       - Set accept drops to true
    #   dragEnterEvent (QDragEnterEvent):
    #       -   Call event accept proposed action method if event mime data has urls
    #   dropEvent (QDropEvent):
    #       -   Add media to playlist from urls
    #       -   Emit model layout change
    #       -   If not playing, play
    #

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QtGui.QDropEvent):
        for url in event.mimeData().urls():
            self.playlist.addMedia(
                QtMultimedia.QMediaContent(url)
            )
        
        self.playlistModel.layoutChanged.emit()

        if self.isPlaying() == False:
            self.play()

    def isPlaying(self) -> bool:
        if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
            return True
        else:
            return False


if __name__ == "__main__":
    #   Main synopsis:
    #   -   Create QApplication and MainWindow
    #   -   Exit on app exec_ method

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())