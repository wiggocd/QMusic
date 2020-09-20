#
#   MainWindow.py
#   Class extended from QMainWindow
#

from PySide2 import QtWidgets, QtCore, QtGui, QtMultimedia
import lib
import os
from PlaylistModel import PlaylistModel
import mutagen
from typing import List

#keyboard: any
#is_admin = lib.get_admin_status()
#lib.importKeyboard(is_admin)

class miniwindow(QtWidgets.QMainWindow):
        def __init__(self):
            super().__init__()
            self.left = 0
            self.top = 0
            self.width = 200
            self.height = 400
            self.title = "MiniPlayer"

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
            self.show()

        def createWidgets(self):
            self.coverart_label = QtWidgets.QLabel()
            self.coverart_label.hide()
            self.coverart_width = 64

            self.metadata_label = QtWidgets.QLabel()
            self.metadata_label.hide()

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

            self.control_playpause = QtWidgets.QPushButton()
            self.control_playpause.setFixedWidth(85)
            self.control_previous = QtWidgets.QPushButton(self.tr(""))
            self.control_next = QtWidgets.QPushButton(self.tr(""))
            self.control_previous.setIcon(QtGui.QIcon("resources/control_previous"))
            self.control_previous.setIconSize(QtCore.QSize(20,20))
            self.control_next.setIcon(QtGui.QIcon("resources/control_next"))
            self.control_next.setIconSize(QtCore.QSize(20,20))
            self.basichelp_label = QtWidgets.QLabel("""Welcome to QMusic, to get started go to File --> Open or Drag and Drop a Song or Folder into the window""")
            self.basichelp_label.hide()

        def initPlayer(self):
        # Create QMediaPlayer and connect to time and volume sliders value changed members, connect player position/duration changed to update position and duration methods
            self.player = QtMultimedia.QMediaPlayer()
            self.volumeSlider.valueChanged.connect(self.player.setVolume)

        # Note: self.player.setPosition adds pauses to playback
            self.timeSlider.valueChanged.connect(self.setPosition)
            self.player.durationChanged.connect(self.update_duration)
            self.player.positionChanged.connect(self.update_position)

        def setPosition(self, position: int):
                player_position = self.player.position()
                if position > player_position + 1 or position < player_position - 1:
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

        # No Longer needed due to added icon support
        #self.control_playpause.setText(self.tr("Play"))

            self.control_playpause.setIcon(QtGui.QIcon("resources/control_play"))
            self.control_playpause.setIconSize(QtCore.QSize(20,20))
            self.control_playpause.pressed.connect(self.play)
        
        def pause(self):
        # Call the pause method of the player and replace play/pause button properties to play; disconnect, set icon and connect to play method
            self.player.pause()
        
            self.control_playpause.setIcon(QtGui.QIcon("resources/control_play"))
            self.control_playpause.setIconSize(QtCore.QSize(20,20))
            self.control_playpause.pressed.disconnect()

        # No Longer needed due to added icon support
        #self.control_playpause.setText("Play")
        
            self.control_playpause.pressed.connect(self.play)
        
        def play(self):
        # If playlist has media, call the play method of the player and replace play/pause button properties to pause; disconnect, set icon and connect to pause method
            if self.playlist.mediaCount() > 0:
                self.player.play()
            
                self.control_playpause.setIcon(QtGui.QIcon("resources/control_pause"))
                self.control_playpause.setIconSize(QtCore.QSize(20,20))
                self.control_playpause.pressed.disconnect()
                self.control_playpause.pressed.connect(self.pause)
        def playpause(self):
        # If not playing, playing, otherwise pause
            if self.isPlaying():
                self.pause()
            else:
                self.play()
        def update_coverart(self, media: QtMultimedia.QMediaContent):
        # If no media is playing, hide the cover art, otherwise separate the url string into a path, set the label pixmap and show
            if media.isNull():
                self.coverart_label.hide()
            else:
                mediaPath = lib.urlStringToPath(media.canonicalUrl().toString())
                coverart_path = lib.get_coverart(os.path.dirname(mediaPath))
                if coverart_path:
                    self.coverart_label.setPixmap(QtGui.QPixmap(coverart_path).scaledToWidth(self.coverart_width))
                    self.coverart_label.show()
                else:
                    self.coverart_label.hide()
        def update_media(self, media: QtMultimedia.QMediaContent):
        # Called on media change, update track metadata and cover art
            self.update_metadata(media)
            self.update_coverart(media)
            if self.isPlaying():
                self.play()
            else:
                self.pause()
        
        def connect_update_media(self):
        # Connect cover art update method to playlist current media changed signal
            self.playlist.currentMediaChanged.connect(self.update_media)
        

        # If playing, update the play/pause button to the playing state, otherwise set its properties to the paused state
            
        
        

        
        def createLayout(self):

            detailsGroup = QtWidgets.QGroupBox()
        
            hArtLayout = QtWidgets.QHBoxLayout()
            hArtLayout.addWidget(self.coverart_label)

            hControlLayout = QtWidgets.QHBoxLayout()
            
            hControlLayout.addWidget(self.control_previous)
            hControlLayout.addWidget(self.control_playpause)
            hControlLayout.addWidget(self.control_next)
            

            hVolumeLayout = QtWidgets.QHBoxLayout()
            hVolumeLayout.addWidget(self.volumeSlider)

            hTimeLayout = QtWidgets.QHBoxLayout()
            hTimeLayout.addWidget(self.timePositionLabel)
            hTimeLayout.addWidget(self.timeSlider)
            hTimeLayout.addWidget(self.totalTimeLabel)

            vDetailsLayout = QtWidgets.QVBoxLayout()
            vDetailsLayout.addLayout(hArtLayout)
            vDetailsLayout.addLayout(hControlLayout)
            vDetailsLayout.addLayout(hVolumeLayout)
            vDetailsLayout.addLayout(hTimeLayout)
            vDetailsLayout.addWidget(self.metadata_label)

            hDetailsLayout = QtWidgets.QHBoxLayout()
            hDetailsLayout.addLayout(vDetailsLayout)
            detailsGroup.setLayout(hDetailsLayout)

            self.vLayout = QtWidgets.QVBoxLayout()
            self.vLayout.addWidget(detailsGroup)
            self.vLayout.addWidget(self.playlistView)
            self.vLayout.addWidget(self.basichelp_label)

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
            #helpMenu = self.mainMenu.addMenu("Help")
            #basichelp = QtWidgets.QAction("Basic Help", self)
            #basichelp.triggered.connect(self.basic_help)
            #basichelp.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+H", "Help|Basic Help")))
            #helpMenu.addAction(basichelp)

        def open_file(self):
        # Set last media count for playlist media check later on
            self.lastMediaCount = self.playlist.mediaCount()
        
        # Set paths from QFileDialog getOpenFileNames, filetypes formatted as "Name (*.extension);;Name" etc.
            paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self, self.tr("Open file(s)"), "", self.tr("All Files (*.*);;Waveform Audio (*.wav);;mp3 Audio (*.mp3)"))

        # For each path, add media QMediaContent from local file to playlist if the filetype is supported
            if paths:
                for path in paths:
                    split = path.split(os.path.extsep)

                    if lib.supportedFormats.__contains__(split[len(split)-1]):
                        self.playlist.addMedia(
                            QtMultimedia.QMediaContent(
                                QtCore.QUrl.fromLocalFile(path)
                            )
                        )
        def basic_help(self):
            self.basichelp_label.show()

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

        def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
            if event.mimeData().hasUrls():
                event.acceptProposedAction()

        def dropEvent(self, event: QtGui.QDropEvent):
            self.lastMediaCount = self.playlist.mediaCount()
        
            for url in event.mimeData().urls():
                path = lib.urlStringToPath(url.toString())

                if os.path.isdir(path):
                    paths: List[str] = []

                    for fname in os.listdir(path):
                        split = fname.split(os.path.extsep)

                        if lib.supportedFormats.__contains__(split[len(split)-1]):
                            paths.append(path + fname)
                
                    if paths:
                        paths.sort()
                        for path in paths:
                            self.playlist.addMedia(
                                QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(path))
                            )
                else:
                    split = url.toString().split(os.path.extsep)

                    if lib.supportedFormats.__contains__(split[len(split)-1]):
                        self.playlist.addMedia(
                                QtMultimedia.QMediaContent(url)
                        )

            self.playlistModel.layoutChanged.emit()
            self.playNewMedia()

        def playNewMedia(self):
            if self.isPlaying() == False and self.lastMediaCount == 0:
                self.play()


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
        self.width = 660
        self.height = 400
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
        self.control_previous = QtWidgets.QPushButton(self.tr(""))
        self.control_next = QtWidgets.QPushButton(self.tr(""))
        self.control_previous.setIcon(QtGui.QIcon("resources/control_previous"))
        self.control_previous.setIconSize(QtCore.QSize(20,20))
        self.control_next.setIcon(QtGui.QIcon("resources/control_next"))
        self.control_next.setIconSize(QtCore.QSize(20,20))

        self.mini_player_button = QtWidgets.QPushButton("Mini Player")
        self.mini_player_button.clicked.connect(self.mini_button_clicked)
        
        self.basichelp_label = QtWidgets.QLabel("""Welcome to QMusic, to get started go to File --> Open or Drag and Drop a Song or Folder into the window""")
        self.basichelp_label.hide()
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
        
        #self.basichelp_label.hide()
        self.metadata_label = QtWidgets.QLabel()
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
        player_position = self.player.position()
        if position > player_position + 1 or position < player_position - 1:
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

        # No Longer needed due to added icon support
        #self.control_playpause.setText(self.tr("Play"))

        self.control_playpause.setIcon(QtGui.QIcon("resources/control_play"))
        self.control_playpause.setIconSize(QtCore.QSize(20,20))
        self.control_playpause.pressed.connect(self.play)
        
        
    def mini_button_clicked(self):
        self.m = miniwindow()
        self.m.show()


    def pause(self):
        # Call the pause method of the player and replace play/pause button properties to play; disconnect, set icon and connect to play method
        self.player.pause()
        
        self.control_playpause.setIcon(QtGui.QIcon("resources/control_play"))
        self.control_playpause.setIconSize(QtCore.QSize(20,20))
        self.control_playpause.pressed.disconnect()

        # No Longer needed due to added icon support
        #self.control_playpause.setText("Play")
        
        self.control_playpause.pressed.connect(self.play)
    
    def play(self):
        # If playlist has media, call the play method of the player and replace play/pause button properties to pause; disconnect, set icon and connect to pause method
        if self.playlist.mediaCount() > 0:
            self.player.play()
            
            self.control_playpause.setIcon(QtGui.QIcon("resources/control_pause"))
            self.control_playpause.setIconSize(QtCore.QSize(20,20))
            self.control_playpause.pressed.disconnect()
            self.control_playpause.pressed.connect(self.pause)

    def playpause(self):
        # If not playing, playing, otherwise pause
        if self.isPlaying():
            self.pause()
        else:
            self.play()

    def update_metadata(self, media: QtMultimedia.QMediaContent):
        # Todo: if no media is playing, hide the metadata, otherwise set the metadata from the metadata class and set the label text
        self

    def update_coverart(self, media: QtMultimedia.QMediaContent):
        # If no media is playing, hide the cover art, otherwise separate the url string into a path, set the label pixmap and show
        if media.isNull():
            self.coverart_label.hide()
        else:
            mediaPath = lib.urlStringToPath(media.canonicalUrl().toString())
            coverart_path = lib.get_coverart(os.path.dirname(mediaPath))
            if coverart_path:
                self.coverart_label.setPixmap(QtGui.QPixmap(coverart_path).scaledToWidth(self.coverart_width))
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
        hControlLayout.addWidget(self.mini_player_button)
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
        self.vLayout.addWidget(self.basichelp_label)

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
        helpMenu = self.mainMenu.addMenu("Help")
        basichelp = QtWidgets.QAction("Basic Help", self)
        basichelp.triggered.connect(self.basic_help)
        basichelp.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+H", "Help|Basic Help")))
        helpMenu.addAction(basichelp)

    def open_file(self):
        # Set last media count for playlist media check later on
        self.lastMediaCount = self.playlist.mediaCount()
        
        # Set paths from QFileDialog getOpenFileNames, filetypes formatted as "Name (*.extension);;Name" etc.
        paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self, self.tr("Open file(s)"), "", self.tr("All Files (*.*);;Waveform Audio (*.wav);;mp3 Audio (*.mp3)"))

        # For each path, add media QMediaContent from local file to playlist if the filetype is supported
        if paths:
            for path in paths:
                split = path.split(os.path.extsep)

                if lib.supportedFormats.__contains__(split[len(split)-1]):
                    self.playlist.addMedia(
                        QtMultimedia.QMediaContent(
                            QtCore.QUrl.fromLocalFile(path)
                        )
                    )
    def basic_help(self):
        self.basichelp_label.show()


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

        #if is_admin:
        #    keyboard.addHotkey("VK_MEDIA_PLAY_PAUSE", self.playpause)

    #
    #   Revise
    #
    #   Synopsis of drag and drop:
    #       - Set accept drops to true
    #   dragEnterEvent (QDragEnterEvent):
    #       -   Call event accept proposed action method if event mime data has urls
    #   dropEvent (QDropEvent):
    #       -   Set last media count
    #       -   If a url is a directory, append paths from os.listdir of supported files to a list
    #           - Sort the list and add urls from the paths
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
            path = lib.urlStringToPath(url.toString())

            if os.path.isdir(path):
                paths: List[str] = []

                for fname in os.listdir(path):
                    split = fname.split(os.path.extsep)

                    if lib.supportedFormats.__contains__(split[len(split)-1]):
                        paths.append(path + fname)
                
                if paths:
                    paths.sort()
                    for path in paths:
                        self.playlist.addMedia(
                            QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(path))
                        )
            else:
                split = url.toString().split(os.path.extsep)

                if lib.supportedFormats.__contains__(split[len(split)-1]):
                    self.playlist.addMedia(
                            QtMultimedia.QMediaContent(url)
                    )

        self.playlistModel.layoutChanged.emit()
        self.playNewMedia()

    def playNewMedia(self):
        if self.isPlaying() == False and self.lastMediaCount == 0:
            self.play()


