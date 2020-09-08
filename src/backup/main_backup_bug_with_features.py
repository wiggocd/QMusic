#
#   main.py
#   Entrypoint to the application.
#

from PySide2 import QtWidgets, QtCore, QtMultimedia, QtGui
import sys
import os
from typing import Union

def get_execdir() -> str:
    return os.path.realpath(os.path.dirname(__file__))

def get_resourcepath(resourceName: str, exec_dir: str) -> str:
    return os.path.join(os.path.dirname(exec_dir), "resources", resourceName)

def to_hhmmss(ms: int) -> str:
    #   Synopsis:
    #   round ms divided to s
    #   m and s = rem s / 60
    #   h and m = rem m / 60
    #

    s = round(ms / 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    
    return ("%d:%02d:%02d" % (h, m, s)) if h else ("%d:%02d" % (m, s))

def get_coverart(coverart_dir: str) -> Union[str, None]:
    #   Synopsis:
    #   -   Scan directory for images by splitting the extension and add to array
    #   -   If any of those images contains the words cover or folder, return the first file
    
    dirList = os.listdir(coverart_dir)
    relativeImagePaths = []
    for relativePath in dirList:
        split = relativePath.split(".")
        extension = split[len(split)-1]
        if extension == "jpg" or "jpeg" or "png" or "bmp":
            relativeImagePaths.append(relativePath)

    for relativePath in relativeImagePaths:
        pathLower = relativePath.lower()
        if pathLower.__contains__("cover") or pathLower.__contains__("folder") or pathLower.__contains__("front"):
            return os.path.join(coverart_dir, relativePath)

    return None


class ClickableLabel(QtWidgets.QLabel):
    #   Synopsis:
    #   - Create pyqtSignal for click
    #   Init (remember QLabel args):
    #       - Call super with arguments
    #       - Set stylesheet for QLabel hover and pressed states, with background color and margin
    #   mousePressEvent:
    #       - Call self click signal emit method
    #

    pressed = QtCore.Signal()

    def __init__(self, text: str = "", clickMethod = None, parent: QtWidgets.QWidget = None):
        super(ClickableLabel, self).__init__(text, parent)

        if clickMethod:
            self.pressed.connect(clickMethod)

    def mousePressEvent(self, event):
        self.pressed.emit()


class ClickableImageLabel(ClickableLabel):
    def __init__(self, pixmap: QtGui.QPixmap = None, clickMethod = None, parent: QtWidgets.QWidget = None):
        super(ClickableImageLabel, self).__init__("", clickMethod, parent)

        if pixmap:
            self.setPixmap(pixmap)

        self.setStyleSheet(
            """
            QLabel {margin: 4px;}
            QLabel:hover {background-color: #DBDBDB}
            QLabel:pressed {background-color: #C9C9C9}
            """
        )


class ImageLabel(QtWidgets.QLabel):
    def __init__(self, pixmap: QtGui.QPixmap = None):
        super(ImageLabel, self).__init__()
        
        if pixmap:
            self.setPixmap(pixmap)


class ImageLabelScaled(ImageLabel):
    def __init__(self, imageWidth: int, pixmap: QtGui.QPixmap = None):
        self.imageWidth = imageWidth
        super(ImageLabelScaled, self).__init__(pixmap)

    def setPixmap(self, pixmap: QtGui.QPixmap):
        super().setPixmap(pixmap.scaledToWidth(self.imageWidth))


class PlaylistModel(QtCore.QAbstractListModel):
    #   Synopsis:
    #   init:
    #       call super
    #       set playlist from argument
    #   data:
    #       if role is display role, set media from playlist media method at index row member
    #           return media canonical file name
    #   rowCount:
    #       return playlist media count

    def __init__(self, playlist: QtMultimedia.QMediaPlaylist):
        super(PlaylistModel, self).__init__()
        self.playlist = playlist

    def data(self, index: QtCore.QModelIndex, role: QtCore.Qt.ItemDataRole):
        if role == QtCore.Qt.DisplayRole:
            media = self.playlist.media(index.row())
            return media.canonicalUrl().fileName()
    
    def rowCount(self, index: QtCore.QModelIndex):
        return self.playlist.mediaCount()


class MainWindow(QtWidgets.QMainWindow):
    #   Synopsis:
    #   1.  Create class derived from QMainWindow
    #       -   Call init of super from class init
    #           -   Set window geometry and title
    #           -   Create widgets: media controls, volume, time and playlist, add to centralWidget
    #           -   Initialize QMediaPlayer, connect to media controls
    #               -   Update duration/position: convert from ms to h:m:s
    #           -   Initialize QMediaPlaylist with model, connect to QMediaPlayer
    #           -   Enable drag and drop and QFileDialog, with playlist.addMedia(QMediaContent...)
    #           -   Add widgets to layout: window QVBoxLayout with nested QHBoxLayouts
    #           -   Create app menu entries using menuBar, addMenu method and QAction: self.triggered.connect
    #           -   Add keyPressEvent method to emit keyPressed signal
    #           -   Show
    #

    def __init__(self):
        super().__init__()

        self.exec_dir = get_execdir()
        self.initUI()

    def initUI(self):
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 240
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle("QAmp")
        
        self.createWidgets()
        self.initPlayer()
        self.pause()
        self.initPlaylist()
        self.createLayout()
        self.createCentralWidget()
        self.createMenus()
        self.update_coverart()
        self.show()

    def createWidgets(self):
        self.control_playpause = ClickableImageLabel()
        self.control_previous = ClickableImageLabel(QtGui.QPixmap(get_resourcepath("control_previous.png", self.exec_dir)))
        self.control_next = ClickableImageLabel(QtGui.QPixmap(get_resourcepath("control_next.png", self.exec_dir)))
        self.control_stop = ClickableImageLabel(QtGui.QPixmap(get_resourcepath("control_stop.png", self.exec_dir)))

        self.volumeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.timeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)

        self.maximumVolume = 100
        self.volumeSlider.setMaximum(self.maximumVolume)
        self.volumeSlider.setValue(self.maximumVolume)

        self.time_elapsed = QtWidgets.QLabel()
        self.time_remaining = QtWidgets.QLabel()
        self.time_elapsed.setStyleSheet(
            """
            QLabel {color: #A7A7A7}
            """
        )
        self.time_remaining.setStyleSheet(
            """
            QLabel {color: #A7A7A7}
            """
        )

        self.coverartWidth = 64
        self.coverart = ImageLabelScaled(self.coverartWidth)
        self.coverart.hide()

        self.pixmap_play = QtGui.QPixmap(get_resourcepath("control_play.png", self.exec_dir))
        self.pixmap_pause = QtGui.QPixmap(get_resourcepath("control_pause.png", self.exec_dir))

    def initPlayer(self):
        # Create player, use volume and time slider valueChanged connect function to the corresponding player set and position properties, connect stop button
        self.player = QtMultimedia.QMediaPlayer()
        self.volumeSlider.valueChanged.connect(self.player.setVolume)
        self.timeSlider.valueChanged.connect(self.player.setPosition)
        self.control_stop.pressed.connect(self.stopPlayback)

        # Connect player duration and positionChanged
        self.player.durationChanged.connect(self.update_duration)
        self.player.positionChanged.connect(self.update_position)

    def update_duration(self):
        # Set time slider maximum value to track duration
        self.timeSlider.setMaximum(self.player.duration())
    
    def update_position(self):
        # Set time slider position and update time labels from position method
        pos = self.player.position()
        self.timeSlider.setValue(pos)
        self.time_elapsed.setText(to_hhmmss(pos))
        if self.player.currentMedia().isNull() != True:
            self.time_remaining.setText(to_hhmmss(self.player.duration() - pos))
        else:
            self.time_remaining.setText(to_hhmmss(0))

    def initPlaylist(self):
        # Create QMediaPlaylist, set player playlist, create QListView and connect media controls
        self.playlist = QtMultimedia.QMediaPlaylist()
        self.player.setPlaylist(self.playlist)
        self.playlistView = QtWidgets.QListView()
        self.control_previous.pressed.connect(self.playlist.previous)
        self.control_next.pressed.connect(self.playlist.next)

        # Create instance of PlaylistModel, set model on playlist view, connect playlist index changed to playlist position changed method
        self.playlistModel = PlaylistModel(self.playlist)
        self.playlistView.setModel(self.playlistModel)
        self.playlist.currentIndexChanged.connect(self.playlist_position_changed)

        # Create selection model from playlist view and connect to playlist selection changed method
        selection_model = self.playlistView.selectionModel()
        selection_model.selectionChanged.connect(self.playlist_selection_changed)

        # Accept drag n drop (see dragEnterEvent and dropEvent)
        self.setAcceptDrops(True)

        # Initialise types of current and last media for later use
        self.currentMedia: QtMultimedia.QMediaContent = None
        self.lastMedia: QtMultimedia.QMediaContent = None

    def playlist_position_changed(self, index: QtCore.QModelIndex):
        # Set current playlist index
        self.playlist.setCurrentIndex(index)

    def playlist_selection_changed(self, selection: QtCore.QItemSelection):
        # If selection indexes array is not empty, set index from array item row
        if len(selection.indexes()) > 0:
            index = selection.indexes()[0]
            # Get model index at index and set playlist view current index
            ix = self.playlistModel.index(index.row())
            self.playlistView.setCurrentIndex(ix)

    def createLayout(self):
        self.vLayout = QtWidgets.QVBoxLayout()

        self.hControlLayout = QtWidgets.QHBoxLayout()
        self.hControlLayout.addWidget(self.control_previous)
        self.hControlLayout.addWidget(self.control_playpause)
        self.hControlLayout.addWidget(self.control_next)
        self.hControlLayout.addWidget(self.control_stop)
        self.hControlLayout.addWidget(self.volumeSlider)

        self.hTimeLayout = QtWidgets.QHBoxLayout()
        self.hTimeLayout.addWidget(self.time_elapsed)
        self.hTimeLayout.addWidget(self.timeSlider)
        self.hTimeLayout.addWidget(self.time_remaining)

        self.vDetailsLayout = QtWidgets.QVBoxLayout()
        self.vDetailsLayout.addLayout(self.hControlLayout)
        self.vDetailsLayout.addLayout(self.hTimeLayout)

        self.hDetailsLayout = QtWidgets.QHBoxLayout()
        self.hDetailsLayout.addLayout(self.vDetailsLayout)
        self.hDetailsLayout.addWidget(self.coverart)

        self.detailsGroup = QtWidgets.QGroupBox()
        self.detailsGroup.setLayout(self.hDetailsLayout)

        self.vLayout.addWidget(self.detailsGroup)
        self.vLayout.addWidget(self.playlistView)

    def createCentralWidget(self):
        self.centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.vLayout)

    def play(self):
        if self.playlist.mediaCount() > 0:
            # Play, set pause image on button, connect to pause function
            self.player.play()
            self.control_playpause.setPixmap(self.pixmap_pause)
            self.control_playpause.pressed.connect(self.pause)
            
            # Check if media has changed, if so, update the cover art
            self.currentMedia = self.getCurrentMedia()

            if self.currentMedia != self.lastMedia:
                self.update_coverart()
            self.lastMedia = self.currentMedia

    def pause(self):
        # Pause, set play image on button, connect to play function
        self.player.pause()
        self.control_playpause.setPixmap(self.pixmap_play)
        self.control_playpause.pressed.connect(self.play)

    def open_file(self):
        # Set path and _ to QFileDialog getOpenFileNames, with specified file types: format "File type name (*.extension);;Next file type name..."
        paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select one or more files to open", "", "All files (*.*);;Waveform Audio (*.wav);;mp3 Audio (*.mp3)")

        # If paths have been returned, add media to playlist from QMediaContent from local file with path (QUrl), repeat for each path
        if paths:
            for path in paths:
                self.playlist.addMedia(
                    QtMultimedia.QMediaContent(
                        QtCore.QUrl.fromLocalFile(path)
                    )
                )

        # Emit playlist model layout changed signal
        self.playlistModel.layoutChanged.emit()

        # If player state is not playing state, play
        if self.player.state != QtMultimedia.QMediaPlayer.PlayingState:
            self.play()

    #   Synopsis of drag and drop
    #   dragEnterEvent:
    #       -   Call event accept proposed action method if event mime data has urls
    #   dropEvent:
    #       -   Add media to playlist from urls
    #       -   Emit model layout change
    #       -   If not playing, play

    def dragEnterEvent(self, event: QtGui.QDropEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QtGui.QDropEvent):
        # For every url from event mime data url method, add QMediaContent from url to playlist
        for url in event.mimeData().urls():
            self.playlist.addMedia(
                QtMultimedia.QMediaContent(url)
            )

        self.playlistModel.layoutChanged.emit()

        if self.player.state != QtMultimedia.QMediaPlayer.PlayingState:
            self.play()
        
    def update_coverart(self):
        # If current media exists, set pixmap on cover art label using get coverart method with argument passed from current media url
        if self.getCurrentMedia().isNull() != True:
            urlString = self.getCurrentMedia().request().url().toString().split("file://")[1]
            coverart_dir = os.path.dirname(urlString)
            coverart_path = get_coverart(coverart_dir)
            if coverart_path != None:
                self.coverart.setPixmap(QtGui.QPixmap(coverart_path))
                self.coverart.show()
            else:
                self.coverart.hide()
        elif self.coverart.isHidden != True:
            self.coverart.hide()
            
    def set_default_coverart(self):
        self.coverart.setPixmap(QtGui.QPixmap(get_resourcepath("default_coverart.png", self.exec_dir)))

    def getCurrentMedia(self) -> QtMultimedia.QMediaContent:
        return self.playlist.media(self.playlist.currentIndex())

    def stopPlayback(self):
        # Pause, stop the player, remove playlist media, update playlist model layout, update duration, position and cover art
        self.pause()
        self.player.stop()
        for i in range(self.playlist.mediaCount()):
            self.playlist.removeMedia(i)
        self.playlistModel.layoutChanged.emit()
        self.update_duration()
        self.update_position()
        self.update_coverart()

    def createMenus(self):
        # Create menu from menuBar method, addMenu for file, add QActions with menu addAction and connect methods to triggered member
        self.menu = self.menuBar()
        self.fileMenu = self.menu.addMenu("File")
        self.openAction = QtWidgets.QAction("Open")
        self.openAction.triggered.connect(self.open_file)
        self.fileMenu.addAction(self.openAction)


if __name__ == "__main__":
    #   Synopsis:
    #       - Create QApplication, create instance of window class, exit on exec_ method of application
    #
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())