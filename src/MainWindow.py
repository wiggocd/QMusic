#
#   MainWindow.py
#   Class extended from QMainWindow
#

from PySide2 import QtWidgets, QtCore, QtGui, QtMultimedia
import lib
import os
from PlaylistModel import PlaylistModel
import mutagen

is_admin = lib.get_admin_status()
if is_admin:
    import keyboard

class MainWindow(QtWidgets.QMainWindow):
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
        self.left = 0
        self.top = 0
        self.width = 430
        self.height = 320
        self.title = "QMusic"
        
        self.initUI()

    def initUI(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)

        self.createWidgets()
        self.initPlayer()
        self.initPlaylist()
        self.init_playpause()
        self.connect_update_media()
        self.createLayout()
        self.createCentralWidget()
        self.createMenus()
        self.createShortcuts()

        self.show()

    def createWidgets(self):
        # Create buttons, labels and sliders
        self.control_playpause = QtWidgets.QPushButton()
        self.control_playpause.setFixedWidth(85)
        self.control_previous = QtWidgets.QPushButton(self.tr("Previous"))
        self.control_next = QtWidgets.QPushButton(self.tr("Next"))

        self.volumeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setValue(100)
        
        self.timeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.timePositionLabel = QtWidgets.QLabel(lib.to_hhmmss(0))
        self.totalTimeLabel = QtWidgets.QLabel(lib.to_hhmmss(0))
        self.timePositionLabel.setStyleSheet(
            """
            QLabel {color: #A7A7A7}
            """
        )
        self.totalTimeLabel.setStyleSheet(
            """
            QLabel {color: #A7A7A7}
            """
        )

        self.metadata_label = QtWidgets.QLabel()
        self.metadata_label.setStyleSheet(
            """
            QLabel {color: #A7A7A7}
            """
        )
        self.metadata_label.hide()

        self.coverart_label = QtWidgets.QLabel()
        self.coverart_label.hide()
        self.coverart_width = 64

    def initPlayer(self):
        # Create QMediaPlayer and connect to time and volume sliders value changed members, connect player position/duration changed to update position and duration methods
        self.player = QtMultimedia.QMediaPlayer()
        self.volumeSlider.valueChanged.connect(self.player.setVolume)

        # Note: self.player.setPosition adds pauses to playback
        self.timeSlider.valueChanged.connect(self.setPosition)
        self.player.durationChanged.connect(self.update_duration)
        self.player.positionChanged.connect(self.update_position)

    def setPosition(self, position: int):
        if position > self.player.position():
            self.player.setPosition(position)

    def update_duration(self, duration: int):
        # Set time slider maximum and set total time label text formatted from argument
        self.timeSlider.setMaximum(duration)
        self.totalTimeLabel.setText(lib.to_hhmmss(duration))

    def update_position(self):
        # Set time slider value, refresh labels
        position = self.player.position()
        self.timeSlider.setValue(position)
        self.timePositionLabel.setText(lib.to_hhmmss(position))

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

        # Accept drag and drop
        self.setAcceptDrops(True)

    #
    #   Revise
    #

    def playlist_position_changed(self, index: QtCore.QModelIndex):
        # Set playlist current index from index
        self.playlist.setCurrentIndex(index)

    def playlist_selection_changed(self, selection: QtCore.QItemSelection):
        # If selection indexes are passed, set index to the first row from the index array
        if len(selection.indexes()) > 0:
            index = selection.indexes()[0].row()

            # If index is not negative, (deselection), set playlist view current index to model index from local index
            if index > -1:
                self.playlistView.setCurrentIndex(self.playlistModel.index(index))

    def init_playpause(self):
        # Initialise the play/pause button with text/icon and signal connection
        self.control_playpause.setText(self.tr("Play"))
        self.control_playpause.pressed.connect(self.play)

    def pause(self):
        # Call the pause method of the player and replace play/pause button properties to play; disconnect, set icon and connect to play method
        self.player.pause()
        self.control_playpause.pressed.disconnect()
        self.control_playpause.setText("Play")
        self.control_playpause.pressed.connect(self.play)
    
    def play(self):
        # If playlist has media, call the play method of the player and replace play/pause button properties to pause; disconnect, set icon and connect to pause method
        if self.playlist.mediaCount() > 0:
            self.player.play()
            self.control_playpause.pressed.disconnect()
            self.control_playpause.setText(self.tr("Pause"))
            self.control_playpause.pressed.connect(self.pause)

    def playpause(self):
        # If not playing, playing, otherwise pause
        if self.isPlaying():
            self.pause()
        else:
            self.play()

    #
    #   Revise
    #

    def update_metadata(self, media: QtMultimedia.QMediaContent):
        # Todo: if no media is playing, hide the metadata, otherwise set the metadata from the metadata class and set the label text
        if media.isNull():
            self.metadata_label.hide()
        else:
            mediaPath = lib.urlStringToPath(media.canonicalUrl().toString())

            if getattr(self, "metadata_separator", None) == None:
                self.metadata_separator = " - "

            self.metadata = mutagen.File(mediaPath)
            metadata_string = self.metadata["TIT2"].text[0] + self.metadata_separator + self.metadata["TALB"].text[0]
            self.metadata_label.setText(metadata_string)
            self.metadata_label.show()

    def update_coverart(self, media: QtMultimedia.QMediaContent):
        # If no media is playing, hide the cover art, otherwise separate the url string into a path, set the label pixmap and show
        if media.isNull():
            self.coverart_label.hide()
        else:
            mediaPath = lib.urlStringToPath(media.canonicalUrl().toString())
            coverart_pixmap = lib.get_coverart_pixmap_from_metadata(mutagen.File(mediaPath))

            if coverart_pixmap == None:
                coverart_path = lib.get_coverart(os.path.dirname(mediaPath))
                if coverart_path:
                    coverart_pixmap = QtGui.QPixmap()
                    coverart_pixmap.load(coverart_path)

            if coverart_pixmap:
                self.coverart_label.setPixmap(coverart_pixmap.scaledToWidth(self.coverart_width))
                self.coverart_label.show()
            else:
                self.coverart_label.hide()

    def update_media(self, media: QtMultimedia.QMediaContent):
        # Called on media change, update track metadata and cover art
        self.update_metadata(media)
        self.update_coverart(media)

        # If playing, update the play/pause button to the playing state, otherwise set its properties to the paused state
        if self.isPlaying():
            self.play()
        else:
            self.pause()

    def connect_update_media(self):
        # Connect cover art update method to playlist current media changed signal
        self.playlist.currentMediaChanged.connect(self.update_media)

    def createLayout(self):
        # Create main vertical layout, add horizontal layouts with added sub-widgets to vertical layout
        detailsGroup = QtWidgets.QGroupBox()
        
        hControlLayout = QtWidgets.QHBoxLayout()
        hControlLayout.addWidget(self.control_previous)
        hControlLayout.addWidget(self.control_playpause)
        hControlLayout.addWidget(self.control_next)
        hControlLayout.addWidget(self.volumeSlider)

        hTimeLayout = QtWidgets.QHBoxLayout()
        hTimeLayout.addWidget(self.timePositionLabel)
        hTimeLayout.addWidget(self.timeSlider)
        hTimeLayout.addWidget(self.totalTimeLabel)

        vDetailsLayout = QtWidgets.QVBoxLayout()
        vDetailsLayout.addLayout(hControlLayout)
        vDetailsLayout.addLayout(hTimeLayout)
        vDetailsLayout.addWidget(self.metadata_label)

        hDetailsLayout = QtWidgets.QHBoxLayout()
        hDetailsLayout.addLayout(vDetailsLayout)
        hDetailsLayout.addWidget(self.coverart_label)

        detailsGroup.setLayout(hDetailsLayout)

        self.vLayout = QtWidgets.QVBoxLayout()
        self.vLayout.addWidget(detailsGroup)
        self.vLayout.addWidget(self.playlistView)

    def createCentralWidget(self):
        # Create central widget, call set central widget method and set widget layout
        self.centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.vLayout)

    def createMenus(self):
        # Create main menu from menuBar method, use addMenu for submenus and add QActions accordingly with triggered connect method, set shortcut from QKeySequence on QActions
        self.mainMenu = self.menuBar()
        fileMenu = self.mainMenu.addMenu("File")
        openAction = QtWidgets.QAction("Open", self)
        openAction.triggered.connect(self.open_file)
        openAction.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+O", "File|Open")))
        fileMenu.addAction(openAction)

    def open_file(self):
        # Set last media count for playlist media check later on
        self.lastMediaCount = self.playlist.mediaCount()
        
        # Set paths from QFileDialog getOpenFileNames, filetypes formatted as "Name (*.extension);;Name" etc.
        paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self, self.tr("Open file(s)"), "", self.tr("All Files (*.*);;Waveform Audio (*.wav);;mp3 Audio (*.mp3)"))

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

        # Check new media and play if conditions are met
        self.playNewMedia()

    def isPlaying(self) -> bool:
        if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
            return True
        else:
            return False

    def createShortcuts(self):
        # Create QShortcuts from QKeySequences with the shortcut and menu item passed as arguments
        shortcut_playpause_space = QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("Space", "")), self)
        shortcut_playpause = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_MediaPlay), self)
        shortcut_playpause_space.activated.connect(self.playpause)
        shortcut_playpause.activated.connect(self.playpause)

        if is_admin:
            keyboard.add_hotkey(0x83, self.playpause)

    #
    #   Revise
    #
    #   Synopsis of drag and drop:
    #       - Set accept drops to true
    #   dragEnterEvent (QDragEnterEvent):
    #       -   Call event accept proposed action method if event mime data has urls
    #   dropEvent (QDropEvent):
    #       -   Set last media count
    #       -   Add media to playlist from urls
    #       -   Emit model layout change
    #       -   Call playNewMedia:
    #           - If not playing and last media count was 0, play
    #

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QtGui.QDropEvent):
        self.lastMediaCount = self.playlist.mediaCount()

        for url in event.mimeData().urls():
            self.playlist.addMedia(
                QtMultimedia.QMediaContent(url)
            )

        self.playlistModel.layoutChanged.emit()
        self.playNewMedia()

    def playNewMedia(self):
        if self.isPlaying() == False and self.lastMediaCount == 0:
            self.play()