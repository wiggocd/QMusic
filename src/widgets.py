#
#   widgets.py
#   Classes for widgets and windows
#

from PySide2 import QtWidgets, QtCore, QtGui, QtMultimedia
import lib
import os
from playlist import PlaylistModel, PlaylistView
import mutagen
from typing import List
import threading
import time

is_admin = lib.getAdminStatus()
if is_admin:
    import keyboard

class MainWindow(QtWidgets.QMainWindow):
    #   -   init: 
    #       -   Call init on super
    #       -   Set geometry variables from geometry key in config if the key exists, otherwise set them to defaults
    #       -   Set app from QApplication parameter
    #       -   Set player fade rates
    #       -   Call initUI
    #   -   initUI:
    #       -   Set geometry and title
    #       -   Set variable with path to executable to find resources later on
    #       -   Create widgets: buttons for media controls, labels, sliders
    #       -   Initialise player, connect to time and volume sliders
    #       -   Set to paused state
    #       -   Update the duration to 0
    #       -   Initialise playlist
    #       -   Add widgets to layout
    #       -   Create central widget and set layout on central widget
    #       -   Create menus and shortcuts
    #       -   If the player was in the mini layout last launch, switch to the mini layout
    #       -   Set volume from config dictionary, add the media from the config, set the current playlist index from the config, reset lastMediaCount, isTransitioning, isFading, lastVolume and currentLayout variables and reset the metadata
    #       -   Set variables for fade out and in rates
    #       -   Set the minimum size to the current minimum size
    #       -   If the config contains it, load and set the minimum size, otherwise if the layout is set to standard, save the minimum size to the config dictionary and to disk
    #       -   Show

    def __init__(self, app: QtWidgets.QApplication):
        super().__init__()

        if lib.config.__contains__("geometry") and lib.config["geometry"].__contains__("mainWindow"):
            geometry = lib.config["geometry"]["mainWindow"]
            self.left = geometry["left"]
            self.top = geometry["top"]
            self.width = geometry["width"]
            self.height = geometry["height"]
        else:
            self.left = lib.defaultLeft
            self.top = lib.defaultTop
            self.width = lib.defaultWidth
            self.height = lib.defaultHeight

            if not lib.config.__contains__("geometry"):
                lib.config["geometry"] = {}
            lib.config["geometry"]["mainWindow"] = {}
            lib.config["geometry"]["mainWindow"]["left"] = self.left
            lib.config["geometry"]["mainWindow"]["top"] = self.top
            lib.config["geometry"]["mainWindow"]["width"] = self.width
            lib.config["geometry"]["mainWindow"]["height"] = self.height

        self.width_mini = lib.miniWidth
        self.height_mini = lib.miniHeight
        self.title = lib.progName
        self.app = app

        self.rate_ms_fadeOut = 200
        self.rate_ms_fadeIn = 200
        
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

        self.originalMinimumSize = self.minimumSize()

        if lib.config.__contains__("layout"):
            self.currentLayout = lib.config["layout"]
            self.switchLayout(self.currentLayout)
        else:
            self.currentLayout = lib.config["layout"] = 0
            self.switchLayout(self.currentLayout)

        self.setVolume(lib.config["volume"])
        self.addMediaFromConfig()
        self.setPlaylistIndexFromConfig()
        self.lastMediaCount = 0
        self.isTransitioning = False
        self.isFading = False
        self.lastVolume = self.player.volume()
        self.metadata = None

        if self.currentLayout == 0 and not lib.config.__contains__("mainWindow_minSize"):
            self.originalMinimumSize = self.minimumSize()
            lib.config["mainWindow_minSize"] = {}
            lib.config["mainWindow_minSize"]["w"] = self.originalMinimumSize.width()
            lib.config["mainWindow_minSize"]["h"] = self.originalMinimumSize.height()
            lib.writeToMainConfigJSON(lib.config)

        elif lib.config.__contains__("mainWindow_minSize"):
            minSize = lib.config["mainWindow_minSize"]
            self.originalMinimumSize = QtCore.QSize(minSize["w"], minSize["h"])
        
        self.show()

    def moveEvent(self, event: QtGui.QMoveEvent):
        # Set the left and top keys in the geometry key of the config dictionary to the corresponding geometric values and write the config to disk
        lib.config["geometry"]["mainWindow"]["left"] = self.geometry().left()
        lib.config["geometry"]["mainWindow"]["top"] = self.geometry().top()

        lib.writeToMainConfigJSON(lib.config)

    def resizeEvent(self, event: QtGui.QResizeEvent):
        # Set the width and height keys in the geometry key of the config dictionary to the corresponding geometric values and write the config to disk
        lib.config["geometry"]["mainWindow"]["width"] = self.geometry().width()
        lib.config["geometry"]["mainWindow"]["height"] = self.geometry().height()

        lib.writeToMainConfigJSON(lib.config)

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
        lib.setAltLabelStyle(self.timePositionLabel)
        lib.setAltLabelStyle(self.totalTimeLabel)

        self.metadata_label = QtWidgets.QLabel()
        lib.setAltLabelStyle(self.metadata_label)
        self.metadata_label.hide()

        self.coverart_label = QtWidgets.QLabel()
        self.coverart_label.hide()
        self.coverart_width = 64

        self.basichelp_label = ClickableLabel("""Welcome to QMusic, to get started go to File --> Open or drag and drop a song or folder into the window""")
        self.basichelp_label.setWordWrap(True)
        lib.setAltLabelStyle(self.basichelp_label)
        self.basichelp_label.hide()
        self.basichelp_label.pressed.connect(self.basichelp_label.hide)

        # Create playlist and action buttons, connect pressed signals
        self.control_playlist_moveDown = QtWidgets.QPushButton(self.tr("Move Down"))
        self.control_playlist_moveUp = QtWidgets.QPushButton(self.tr("Move Up"))
        self.control_playlist_remove = QtWidgets.QPushButton(self.tr("Remove"))
        self.control_playlist_clear = QtWidgets.QPushButton(self.tr("Clear"))

        self.control_playlist_moveDown.pressed.connect(self.playlist_moveDown)
        self.control_playlist_moveUp.pressed.connect(self.playlist_moveUp)
        self.control_playlist_remove.pressed.connect(self.removeMedia)
        self.control_playlist_clear.pressed.connect(self.playlist_clear)

        self.lyricsView = None

    def initPlayer(self):
        # Create QMediaPlayer and connect to time and volume sliders value changed members, connect player position/duration changed to update position and duration methods
        self.player = QtMultimedia.QMediaPlayer()
        self.volumeSlider.valueChanged.connect(self.setVolume)

        # Note: self.player.setPosition adds pauses to playback
        self.timeSlider.valueChanged.connect(self.setPosition)
        self.player.durationChanged.connect(self.update_duration)
        self.player.positionChanged.connect(self.update_position)

    def setVolume(self, volume: int):
        # Set the player volume, set the slider position and update the main config
        self.player.setVolume(volume)
        self.volumeSlider.setSliderPosition(volume)
        lib.updateMainConfig("volume", volume)

    def setPosition(self, position: int):
        # Get player position and if the new slider position has changed, set the player position
        player_position = self.player.position()
        if position > player_position + 1 or position < player_position - 1:
            self.player.setPosition(position)

        # If position is near the end, fade out
        duration = self.player.duration()
        if not self.isTransitioning and position > duration - 1000:
            self.isTransitioning = True
            self.fadeOut()

        # If transitioning and the new track has started, reset the transitioning state and restore volume
        if self.isTransitioning and not self.isFading and position < duration - 1000:
            self.fadeIn()

    def fadeOut(self):
        # Run the fade out on a new thread with the function set as the target for the thread and by calling start
        self.fadeThread = threading.Thread(target=self._fadeOut)
        self.fadeThread.start()
        
    def _fadeOut(self):
        # Set the last volume and lower volume by incriment every x ms until the volume is equal to 0, exit if the track has already switched
        self.lastVolume = self.player.volume()
        volume = self.lastVolume
        self.lastTrackIndex = self.playlist.currentIndex()

        while volume != 0 and self.playlist.currentIndex() == self.lastTrackIndex:
            volume -= 1
            self.player.setVolume(volume)
            self.isFading = True
            time.sleep(1 / self.rate_ms_fadeOut)
        
        # If not fading and the track has changed, instantly restore the volume to prevent volume from staying at 0
        if not self.isFading and self.playlist.currentIndex() != self.lastTrackIndex:
            self.restoreVolume()
        
        self.isFading = False

    def fadeIn(self):
        # Run the fade in on a new thread with the function set as the target for the thread and by calling start
        self.fadeThread = threading.Thread(target=self._fadeIn)
        self.fadeThread.start()

    def _fadeIn(self):
        # Increase volume by incriment every x ms until the volume has reached the pre-fade volume, reset isTransitioning
        volume = self.player.volume()
        while volume != self.lastVolume:
            volume += 1
            self.player.setVolume(volume)
            self.isFading = True
            time.sleep(1 / self.rate_ms_fadeIn)

        self.isFading = False
        self.isTransitioning = False

    def restoreVolume(self):
        # Set the player volume to the last recorded volume
        self.player.setVolume(self.lastVolume)

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
        self.playlist = QtMultimedia.QMediaPlaylist(self)
        self.player.setPlaylist(self.playlist)
        self.playlistModel = PlaylistModel(self.playlist)
        self.control_previous.pressed.connect(self.previousTrack)
        self.control_next.pressed.connect(self.nextTrack)
        self.playlist.currentIndexChanged.connect(self.playlistIndexChanged)

        # Create playlist view with model passed, create selection model from playlist view and connect playlist selection changed method
        self.playlistView = PlaylistView(self.playlistModel)
        # self.playlistViewSelectionModel = self.playlistView.selectionModel()
        # self.playlistViewSelectionModel.selectionChanged.connect(self.playlist_selection_changed)

        # Set view selection mode to abstract item view extended selection and connect double click signal to switch media
        self.playlistView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.playlistView.doubleClicked.connect(self.switchMedia)

        # Accept drag and drop
        self.setAcceptDrops(True)

    def previousTrack(self):
        self.playlist.previous()
        self.play()

    def nextTrack(self):
        self.playlist.next()
        self.play()

    def updatePlayingState(self):
        if self.isPlaying():
            self.play()
        else:
            self.pause()

    def playlistIndexChanged(self, index: int):
        # Save the playlist index to the config
        self.savePlaylistIndex(index)

    def savePlaylistIndex(self, index: int):
        # Write the index to the config dict and proceed to write the dict to the main config JSON
        lib.config["playlistCurrentIndex"] = index
        lib.writeToMainConfigJSON(lib.config)

    def setPlaylistIndexFromConfig(self):
        # If the config dict contains the playlist current index, set the playlist current index, otherwise save the playlist index to the config
        if lib.config.__contains__("playlistCurrentIndex"):
            self.playlist.setCurrentIndex(lib.config["playlistCurrentIndex"])
        else:
            self.savePlaylistIndex(self.playlist.currentIndex())

        # Play and pause to initialise metadata and cover art
        self.play()
        self.pause()

    #
    #   Revise
    #

    def playlist_moveDown(self):
        # Get selected indexes on the playlist view and save the current playlist index
        selectedIndexes = self.playlistView.selectedIndexes()
        currentPlaylistIndex = self.playlist.currentIndex()

        # If there are selected indexes in the index list, the index list does not contain the current track and the index after (+1) the last selected index is larger than the current index
        if len(selectedIndexes) > 0 and selectedIndexes.__contains__(self.playlistModel.index(currentPlaylistIndex)) == False and selectedIndexes[len(selectedIndexes) - 1].row() + 1 > currentPlaylistIndex:
            # Get the first and maximum index rows
            firstIndex = selectedIndexes[0].row()
            maxIndex = selectedIndexes[len(selectedIndexes) - 1].row()

            # Get selected media
            media = self.getSelectedMedia(firstIndex, maxIndex)
            
            # Set the previous selected indexes
            previousSelectedIndexes = self.playlistView.selectedIndexes()

            # Insert all of the media in the list to 2 indexes after the current on the playlist, remove the previous original media instances from the playlist and emit the playlist model layout change signal
            self.playlist.insertMedia(firstIndex + 2, media)
            self.playlist.removeMedia(firstIndex, maxIndex)
            self.playlistModel.layoutChanged.emit()

            # On the playlist view selection model, call the select function with the selection model deselect parameter to deselect all of the items in the previus selected indexes
            len_previousSelectedIndexes = len(previousSelectedIndexes)
            self.playlistViewSelectionModel.select(QtCore.QItemSelection(previousSelectedIndexes[0], previousSelectedIndexes[len_previousSelectedIndexes - 1]), QtCore.QItemSelectionModel.Deselect)

            # On the playlist view selection model, call the select function with the selection model select parameter to select all of the moved selected indexes (all of the previous selected indexes shifted by 1 over)
            self.playlistViewSelectionModel.select(QtCore.QItemSelection(self.playlistModel.index(previousSelectedIndexes[0].row() + 1), self.playlistModel.index(previousSelectedIndexes[len_previousSelectedIndexes - 1].row() + 1)), QtCore.QItemSelectionModel.Select)

    def playlist_moveUp(self):
        # Get selected indexes on the playlist view and save the current playlist index
        selectedIndexes = self.playlistView.selectedIndexes()
        currentPlaylistIndex = self.playlist.currentIndex()
        
        # If there are selected indexes in the index list, the index list does not contain the current track and the index before (-1) the last selected index is larger than the current index
        if len(selectedIndexes) > 0 and selectedIndexes.__contains__(self.playlistModel.index(currentPlaylistIndex)) == False and selectedIndexes[0].row() - 1 > currentPlaylistIndex:
            # Get the first and maximum index rows
            firstIndex = selectedIndexes[0].row()
            maxIndex = selectedIndexes[len(selectedIndexes) - 1].row()

            # Get selected media
            media = self.getSelectedMedia(firstIndex, maxIndex)
            
            # Set the previous selected indexes
            previousSelectedIndexes = self.playlistView.selectedIndexes()
            
            # Insert all of the media in the list to 1 indexes before the current on the playlist, remove the previous original media instances (+1 to first and maximum) from the playlist and emit the playlist model layout change signal
            self.playlist.insertMedia(firstIndex - 1, media)
            self.playlist.removeMedia(firstIndex + 1, maxIndex + 1)
            self.playlistModel.layoutChanged.emit()

            # On the playlist view selection model, call the select function with the selection model deselect parameter to deselect all of the items in the previus selected indexes
            len_previousSelectedIndexes = len(previousSelectedIndexes)
            self.playlistViewSelectionModel.select(QtCore.QItemSelection(previousSelectedIndexes[0], previousSelectedIndexes[len_previousSelectedIndexes - 1]), QtCore.QItemSelectionModel.Deselect)

            # On the playlist view selection model, call the select function with the selection model select parameter to select all of the moved selected indexes (all of the previous selected indexes shifted by 1 before)
            self.playlistViewSelectionModel.select(QtCore.QItemSelection(self.playlistModel.index(previousSelectedIndexes[0].row() - 1), self.playlistModel.index(previousSelectedIndexes[len_previousSelectedIndexes - 1].row() - 1)), QtCore.QItemSelectionModel.Select)

    def getSelectedMedia(self, firstIndex: int, maxIndex: int):
        # Append all selected media + 1 from playlist to a QMediaContent list
        media: List[QtMultimedia.QMediaContent] = []
        for i in range(firstIndex, maxIndex + 1):
            media.append(self.playlist.media(i))
        
        return media

    def playlist_clear(self):
        # Clear the playlist, clear the media config log and emit the playlist model layout changed signal
        self.playlist.clear()
        lib.clearConfigFile(lib.configDir, lib.mediaFileName)
        self.playlistModel.layoutChanged.emit()
    
    def switchLayout(self, layout: int):
        # Switch to the mini layout if the layout is 1 - otherwise switch to the standard layout, and for both add the layout index to the config and write to disk
        if layout == 1:
            self.switchToMinimalLayout()
            self.currentLayout = 1
        else:
            self.switchToStandardLayout()
            self.currentLayout = 0

        lib.config["layout"] = self.currentLayout
        lib.writeToMainConfigJSON(lib.config)

    def toggleLayout(self):
        # If the current layout is the standard (0), switch to the mini (1) and vice versa
        if self.currentLayout == 0:
            self.switchLayout(1)
        else:
            self.switchLayout(0)

    def switchToMinimalLayout(self):
        # Hide extra widgets, set the label alignment and set the fixed size to the mini dimensions
        self.volumeSlider.hide()
        self.coverart_label.hide()
        self.control_playlist_moveDown.hide()
        self.control_playlist_moveUp.hide()
        self.control_playlist_remove.hide()
        self.control_playlist_clear.hide()
        self.playlistView.hide()

        self.metadata_label.setAlignment(QtCore.Qt.AlignCenter)

        self.setFixedSize(self.width_mini, self.height_mini)

    def switchToStandardLayout(self):
        # Show the standard widgets, show the cover art if it was previously displayed [there is media, the coverart pixmap exists and is not a null pixmap], reset the label alignment, set the original maximum and minimum sizes and resize the window
        self.volumeSlider.show()

        coverart_pixmap = self.coverart_label.pixmap()
        if self.playlist.mediaCount() > 0 and coverart_pixmap != None and not coverart_pixmap.isNull():
            self.coverart_label.show()
        
        self.control_playlist_moveDown.show()
        self.control_playlist_moveUp.show()
        self.control_playlist_remove.show()
        self.control_playlist_clear.show()
        self.playlistView.show()

        self.metadata_label.setAlignment(QtCore.Qt.AlignLeft)

        self.setMaximumSize(lib.maxWidth, lib.maxHeight)
        self.setMinimumSize(self.originalMinimumSize)
        self.resize(self.width, self.height)

    def playlist_position_changed(self, index: QtCore.QModelIndex):
        #
        #   Not used
        #
        
        # Set playlist current index from index
        self.playlist.setCurrentIndex(index)

    def playlist_selection_changed(self, selection: QtCore.QItemSelection):
        #
        #   Deprecated
        #

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

            mutagen_metadata = mutagen.File(mediaPath)
            self.metadata = lib.Metadata(mutagen_metadata)

            if self.metadata.title and self.metadata.album:
                metadata_string = self.metadata.title + self.metadata_separator + self.metadata.album
            else:
                metadata_string = media.canonicalUrl().fileName()

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

        # If the player is in the minimal layout mode, re-hide the coverart label
        if self.currentLayout == 1:
            self.coverart_label.hide()

    def update_media(self, media: QtMultimedia.QMediaContent):
        # If playing, update the play/pause button to the playing state, otherwise set its properties to the paused state
        self.updatePlayingState()
        
        # Called on media change, update track metadata and cover art
        self.update_metadata(media)
        self.update_coverart(media)

        # If the lyrics view has been created, emit the track changed signal
        if self.lyricsView != None:
            self.lyricsView.trackChanged.emit()

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

        actionsLayout = QtWidgets.QHBoxLayout()
        actionsLayout.addWidget(self.control_playlist_moveDown)
        actionsLayout.addWidget(self.control_playlist_moveUp)
        actionsLayout.addWidget(self.control_playlist_remove)
        actionsLayout.addWidget(self.control_playlist_clear)

        self.vLayout = QtWidgets.QVBoxLayout()
        self.vLayout.addWidget(detailsGroup)
        self.vLayout.addLayout(actionsLayout)
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
        fileMenu = self.mainMenu.addMenu(self.tr("File"))
        playerMenu = self.mainMenu.addMenu(self.tr("Player"))
        playlistMenu = self.mainMenu.addMenu(self.tr("Playlist"))
        helpMenu = self.mainMenu.addMenu(self.tr("Help"))

        closeAction = QtWidgets.QAction(self.tr("Close Window"), self)
        closeAction.triggered.connect(self.closeWindow)
        closeAction.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+W", "File|Close Window")))

        preferencesAction = QtWidgets.QAction(self.tr("Preferences"), self)
        preferencesAction.triggered.connect(self.showPreferences)
        preferencesAction.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+,", "File|Preferences")))

        openFileAction = QtWidgets.QAction(self.tr("Open File"), self)
        openFileAction.triggered.connect(self.open_files)
        openFileAction.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+O", "File|Open")))

        openDirAction = QtWidgets.QAction(self.tr("Open Directory"), self)
        openDirAction.triggered.connect(self.open_directory)
        openDirAction.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+Shift+O", "File|Open Directory")))

        switchSizeAction = QtWidgets.QAction(self.tr("Switch Player Size"), self)
        switchSizeAction.triggered.connect(self.toggleLayout)
        switchSizeAction.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+Shift+S", "Player|Switch Player Size")))

        lyricsAction = QtWidgets.QAction(self.tr("Lyrics"), self)
        lyricsAction.triggered.connect(self.showLyrics)
        lyricsAction.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+L", "Player|Lyrics")))

        playlistRemoveAction = QtWidgets.QAction(self.tr("Remove"), self)
        playlistRemoveAction.triggered.connect(self.removeMedia)

        playlistClearAction = QtWidgets.QAction(self.tr("Clear"), self)
        playlistClearAction.triggered.connect(self.playlist_clear)
        playlistClearAction.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+Backspace", "Playlist|Clear")))

        helpWindowAction = QtWidgets.QAction(self.tr("Help Window"), self)
        helpWindowAction.triggered.connect(self.showHelp)
        helpWindowAction.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+Shift+H", "Help|Help Window")))

        fileMenu.addAction(closeAction)
        fileMenu.addAction(preferencesAction)
        fileMenu.addAction(openFileAction)
        fileMenu.addAction(openDirAction)
        playerMenu.addAction(switchSizeAction)
        playerMenu.addAction(lyricsAction)
        playlistMenu.addAction(playlistRemoveAction)
        playlistMenu.addAction(playlistClearAction)
        helpMenu.addAction(helpWindowAction)

    def closeWindow(self):
        # Get the active window from the QApplication, quit the application if the active window is the player, otherwise hide and then destroy that window
        activeWindow = self.app.activeWindow()

        if activeWindow == self:
            self.app.quit()
        else:
            # Note: the widget must be hidden before destruction, otherwise a segmentation fault can occur when quitting the application
            activeWindow.hide()
            activeWindow.destroy()

    def showPreferences(self):
        # Create instance of preferences widget with the QApplication given as a parameter
        self.preferencesView = Preferences(self.app, self)

    def showLyrics(self):
        # Create instance of lyrics widget
        self.lyricsView = LyricsWidget(self)
    def showHelp(self):
        # Create instance of lyrics widget
        self.helpView = HelpWidget(self)

    def show_basichelp(self):
        # Show the label
        self.basichelp_label.show()

    def open_files(self):
        # Set last media count for playlist media check later on
        self.lastMediaCount = self.playlist.mediaCount()
        
        # Set paths from QFileDialog getOpenFileNames, filetypes formatted as "Name (*.extension);;Name" etc.
        paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self, self.tr("Open File"), "", self.tr("All Files (*.*);;Waveform Audio (*.wav);;mp3 Audio (*.mp3)"))

        # For each path, add media QMediaContent from local file to playlist if the filetype is supported
        if paths:
            for path in paths:
                if self.isSupportedFileFormat(path):
                    self.addMediaFromFile(path)
            
            # Emit playlist model layout change and play if paused
            self.playlistModel.layoutChanged.emit()

            # Check new media and play if conditions are met
            self.playNewMedia()

            # Write media to config
            self.writeMediaToConfig()

    def isSupportedFileFormat(self, path: str) -> bool:
        # Split the path by the extension separator and if the list of supported formats contains the last element of the list, return true
        split = path.split(os.path.extsep)

        if lib.supportedFormats.__contains__(split[len(split)-1]):
            return True
        else:
            return False

    def open_directory(self):
        # Set last media count for playlist media check later on
        self.lastMediaCount = self.playlist.mediaCount()

        # Set directory from QFileDialog getExistingDirectory
        dirPath = QtWidgets.QFileDialog.getExistingDirectory(self, self.tr("Open Folder"), "")

        # If a path was returned, get a directory listing, sort it and for every file in the list get the full path: if the format is supported, add the media to the playlist
        if dirPath:
            dirList = os.listdir(dirPath)
            dirList.sort()
            
            for fname in dirList:
                path = os.path.join(dirPath, fname)
                
                if self.isSupportedFileFormat(path):
                    self.addMediaFromFile(path)

            # Emit playlist model layout change and play if paused
            self.playlistModel.layoutChanged.emit()

            # Check new media and play if conditions are met
            self.playNewMedia()

            # Write media to config
            self.writeMediaToConfig()

    def addMediaFromFile(self, path: str):
        # Add the media to the playlist with a QMediaContent instance from the local file
        self.playlist.addMedia(
            QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(path))
        )

    def addMediaFromConfig(self):
        # If the file exists, read in each line of the media log to a list and add the media content from each path to the playlist
        paths: List[str] = []
        mediaLog = os.path.join(lib.configDir, lib.mediaFileName)

        if os.path.isfile(mediaLog):
            with open(mediaLog, "r") as mediaData:
                paths = mediaData.read().split("\n")

            for path in paths:
                if path != "":
                    self.addMediaFromFile(path)

        # Emit the playlist model layout changed signal
        self.playlistModel.layoutChanged.emit()

    def writeMediaToConfig(self):
        # Add path from canonical url string of each media item in the playlist to a list and write it to the config
        paths: List[str] = []
        for i in range(self.playlist.mediaCount()):
            urlString = self.playlist.media(i).canonicalUrl().toString()
            paths.append(lib.urlStringToPath(urlString))
        
        lib.writeToConfig(lib.configDir, lib.mediaFileName, paths)

    def isPlaying(self) -> bool:
        if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
            return True
        else:
            return False

    #
    #   Revise
    #

    def removeMedia(self):
        # Get the selected indexes from the playlist view and if there are indexes selected, remove the corresponding media from the playlist and emit the playlist model layout change signal
        selectedIndexes: List[QtCore.QModelIndex] = self.playlistView.selectedIndexes()

        if len(selectedIndexes) > 0:
            firstIndex = selectedIndexes[0]
            lastIndex = selectedIndexes[len(selectedIndexes)-1]

            self.playlist.removeMedia(firstIndex.row(), lastIndex.row())
            self.playlistModel.layoutChanged.emit()

    def createShortcuts(self):
        # Create QShortcuts from QKeySequences with the shortcut and menu item passed as arguments
        shortcut_playpause_space = QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("Space")), self)
        shortcut_playpause = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_MediaPlay), self)
        shortcut_playpause_space.activated.connect(self.playpause)
        shortcut_playpause.activated.connect(self.playpause)

        shortcut_delete = QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("Backspace")), self)
        shortcut_delete.activated.connect(self.removeMedia)

        shortcut_previous = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_MediaLast), self)
        shortcut_previous.activated.connect(self.playlist.previous)

        shortcut_next = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_MediaNext), self)
        shortcut_next.activated.connect(self.playlist.next)

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
    #       -   If a url is a directory, append paths from os.listdir of supported files to a list
    #           - Sort the list and add urls from the paths
    #       -   Add media to playlist from urls
    #       -   Emit model layout change
    #       -   Call playNewMedia:
    #           - If not playing and last media count was 0, play
    #       -   Write media to config
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
                        paths.append(os.path.join(path, fname))
                
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
        self.writeMediaToConfig()

    def playNewMedia(self):
        # Play if not playing and the last media count is not 0
        if self.isPlaying() == False and self.lastMediaCount == 0:
            self.play()

    def switchMedia(self):
        # Get selected indexes from playlist view, if there are indexes selected, set the new current playlist index and play the new media
        selectedIndexes = self.playlistView.selectedIndexes()
        if len(selectedIndexes) > 0:
            self.playlist.setCurrentIndex(selectedIndexes[0].row())
            self.playNewMedia()

#
#
#   Revise
#
#

class ClickableLabel(QtWidgets.QLabel):
    #   -   Call super init from init with text and parent passed depending on if they are set or not
    #   -   Emit the pressed signal on the mousePressEvent

    pressed = QtCore.Signal()

    def __init__(self, text: str = None, parent: QtWidgets.QWidget = None):
        if text != None:
            super().__init__(text, parent)
        else:
            super().__init__(parent)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        self.pressed.emit()

class Preferences(QtWidgets.QWidget):
    #   -   init:
    #       -   Set geometry variables including from parent widget if a parent was passed, title and application from parameter
    #       -   Call initUI
    #   -   initUI:
    #       -   Set geometry and window title
    #       -   Create widgets and layout
    #       -   Show

    def __init__(self, app: QtWidgets.QApplication, parent: QtWidgets.QWidget = None):
        super().__init__()

        if parent != None:
            parentGeometry = parent.geometry()
            self.left = parentGeometry.left()
            self.top = parentGeometry.top()
        else:
            self.left = 0
            self.top = 0

        self.width = 0
        self.height = 0
        self.title = lib.progName + lib.titleSeparator + self.tr("Preferences")
        self.app = app

        self.initUI()

    def initUI(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)
        self.createWidgets()
        self.createLayout()

        self.show()

    def createWidgets(self):
        # Create the style label and combo box, add options from style list
        self.styleLabel = QtWidgets.QLabel(self.tr("Style"), self)
        self.styleBox = QtWidgets.QComboBox(self)
        
        for style in lib.styles:
            self.styleBox.addItem(self.tr(style.name))
        
        # Connect the combo box index change signal to the style selection handler and set the current index to the current style
        self.styleBox.currentIndexChanged.connect(self.styleSelectionChanged)
        self.styleBox.setCurrentIndex(lib.globalStyleIndex)

        # Create icon check box and connecing the press signals
        #self.iconCheckBox = QtWidgets.QCheckBox("Enable Icons",self)
        #self.iconCheckBox.stateChanged.connect(self.iconCheckChanged)

        # Create other widgets and buttons connecting pressed signals
        self.button_clearConfig = QtWidgets.QPushButton(self.tr("Clear All Config"))
        self.button_clearConfig.pressed.connect(lib.removeConfigDir)

    def createLayout(self):
        # Create the QGridLayout and add widgets accordingly with coordinates passed as parameters, set the layout alignment and set the layout
        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self.styleLabel, 0, 0)
        layout.addWidget(self.styleBox, 0, 1)
        layout.addWidget(self.button_clearConfig, 1, 0)
        layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(layout)

    def styleSelectionChanged(self, index: int):
        # Set the global style index and stylesheet from the current style in the list, set the QApplication stylesheet and update the main config with the new style index
        lib.globalStyleIndex = index
        lib.globalStyleSheet = lib.styles[lib.globalStyleIndex].styleSheet
        self.app.setStyleSheet(lib.globalStyleSheet)
        lib.updateMainConfig("style", index)
    """
    def iconCheckChanged(self):
        # Check if the icon checkbox is checked, if it is write to config file
        if self.iconCheckBox.isChecked():
            lib.updateMainConfig("icons",1)
        else:
            lib.updateMainConfig("icons",0)
    """

class LyricsWidget(QtWidgets.QWidget):
    #   -   Signal trackChanged
    #   -   init:
    #       -   Set parent propery
    #       -   Set geometry variables including from the parent window if no geometry was previously recorded in the config for the lyrics widget, otherwise set the previous geometry, as well as title / track detail variables
    #       -   Call initUI
    #   -   initUI:
    #       -   Set the window geometry and title
    #       -   Save the geometry to the config if it has not been previously
    #       -   Set the default text, boolean variables and loading animation properties
    #       -   Create the widgets and layout, along with setting the lyrics token from the executable directory
    #       -   Connect the track changed signal to the search from metadata function, call serach from metadata if the parent player has media
    #       -   Show

    trackChanged = QtCore.Signal()

    def __init__(self, parent: MainWindow = None):
        super().__init__()

        self.parent = parent

        if lib.config.__contains__("geometry") and lib.config["geometry"].__contains__("lyrics"):
            geometry = lib.config["geometry"]["lyrics"]
            self.left = geometry["left"]
            self.top = geometry["top"]
            self.width = geometry["width"]
            self.height = geometry["height"]
        elif parent != None:
            parentGeometry = self.parent.geometry()
            self.left = parentGeometry.left()
            self.top = parentGeometry.top()
            self.width = lib.lyrics_defaultWidth
            self.height = lib.lyrics_defaultHeight
        else:
            self.left = lib.defaultLeft
            self.top = lib.defaultTop
            self.width = lib.lyrics_defaultWidth
            self.height = lib.lyrics_defaultHeight

        self.title = lib.progName + lib.titleSeparator + self.tr("Lyrics")

        self.initUI()
    
    def initUI(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)

        if not lib.config.__contains__("geometry") or not lib.config["geometry"].__contains__("lyrics"):
            if not lib.config.__contains__("geometry"):
                lib.config["geometry"] = {}
            lib.config["geometry"]["lyrics"] = {}
            lib.config["geometry"]["lyrics"]["left"] = self.left
            lib.config["geometry"]["lyrics"]["top"] = self.top
            lib.config["geometry"]["lyrics"]["width"] = self.width
            lib.config["geometry"]["lyrics"]["height"] = self.height

        self.songText = ""
        self.artistText = ""
        self.lastSearchedSong = None
        self.lastSearchedArtist = None
        self.loadingText = ["Loading", "Loading.", "Loading..", "Loading..."]
        self.loadedLyrics = False
        self.loadingAnimationInterval_ms = 100
        
        self.createWidgets()
        self.createLayout()
        # lib.setLyricsToken(lib.execDir)

        self.trackChanged.connect(self.loadAndSearchFromMetadata)
        if not self.parent.player.media().isNull():
            self.loadAndSearchFromMetadata()

        self.show()

    def moveEvent(self, event: QtGui.QMoveEvent):
        # Set the left and top keys in the geometry key of the config dictionary to the corresponding geometric values and write the config to disk
        lib.config["geometry"]["lyrics"]["left"] = self.geometry().left()
        lib.config["geometry"]["lyrics"]["top"] = self.geometry().top()

        lib.writeToMainConfigJSON(lib.config)

    def resizeEvent(self, event: QtGui.QResizeEvent):
        # Set the width and height keys in the geometry key of the config dictionary to the corresponding geometric values and write the config to disk
        lib.config["geometry"]["lyrics"]["width"] = self.geometry().width()
        lib.config["geometry"]["lyrics"]["height"] = self.geometry().height()

        lib.writeToMainConfigJSON(lib.config)

    def createWidgets(self):
        # Create labels and Line Edit boxes for song details entry, create the search button ad scroll view with the output label and word wrap enabled
        self.artistLabel = QtWidgets.QLabel("Artist")
        self.songLabel = QtWidgets.QLabel("Song")

        self.artistBox = QtWidgets.QLineEdit()
        self.artistBox.textChanged.connect(self.setArtistText)
        self.artistBox.editingFinished.connect(self.search)

        self.songBox = QtWidgets.QLineEdit()
        self.songBox.textChanged.connect(self.setSongText)
        self.songBox.editingFinished.connect(self.search)

        self.searchButton = QtWidgets.QPushButton("Search")
        self.searchButton.pressed.connect(self.search)

        self.scrollView = QtWidgets.QScrollArea()
        self.outputLabel = QtWidgets.QLabel()
        self.outputLabel.setWordWrap(True)
        self.scrollView.setWidget(self.outputLabel)
        self.scrollView.setWidgetResizable(True)

        self.infoLabel = QtWidgets.QLabel()
        lib.setAltLabelStyle(self.infoLabel)
        self.infoLabel.hide()

    def createLayout(self):
        # Create the group boxes, create the grid layout with coordinates added for each widget comprising song details entry, create the layouts for the button and text groups and set the layout
        entryGroup = QtWidgets.QGroupBox()
        buttonGroup = QtWidgets.QGroupBox()
        textGroup = QtWidgets.QGroupBox()

        entryLayout = QtWidgets.QGridLayout()
        entryLayout.setSpacing(10)
        entryLayout.addWidget(self.artistLabel, 0, 0)
        entryLayout.addWidget(self.artistBox, 0, 1)
        entryLayout.addWidget(self.songLabel, 1, 0)
        entryLayout.addWidget(self.songBox, 1, 1)

        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addWidget(self.searchButton)

        textLayout = QtWidgets.QHBoxLayout()
        textLayout.addWidget(self.scrollView)

        entryGroup.setLayout(entryLayout)
        buttonGroup.setLayout(buttonLayout)
        textGroup.setLayout(textLayout)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(entryGroup)
        layout.addWidget(buttonGroup)
        layout.addWidget(textGroup)
        layout.addWidget(self.infoLabel)
    
        self.setLayout(layout)

    def setArtistText(self, text: str):
        # Set the artist text
        self.artistText = text
    
    def setSongText(self, text: str):
        # Set the song text
        self.songText = text

    def loadAndSearchFromMetadata(self):
        # If the player has the metadata set, set the placeholder text from the parent metadata on the song details entry boxes, set the artist and song text and run the search
        if self.parent.metadata:
            metadata = self.parent.metadata

            self.artistBox.setPlaceholderText(metadata.artist)
            self.songBox.setPlaceholderText(metadata.title)

            self.setArtistText(metadata.artist)
            self.setSongText(metadata.title)

            self.search()

    def search(self):
        # If the lyrics object exists, the song and artist names are set and one of the song details has changed, run the second stage search function on a new thread using the threading library, the target specified and the start method
        if lib.lyricsObject != None and self.songText != "" and self.artistText != "" and self.lastSearchedArtist != self.artistText or self.lastSearchedSong != self.songText:
            searchThread = threading.Thread(target=self._search)
            searchThread.start()

    def _search(self):
        # Start the loading animation, set the song from the lyrics object, switch the loading state when finished, set the output label text from the song lyrics property and set the last searched song and artist
        self.loadedLyrics = False
        self.loadingAnimation()
        self.song = lib.lyricsObject.search_song(self.songText, self.artistText)
        self.loadedLyrics = True

        self.outputLabel.setText(self.song.lyrics)
        self.lastSearchedSong = self.songText
        self.lastSearchedArtist = self.artistText
    def loadingAnimation(self):
        # Run the loading animation on another thread
        self.loadingThread = threading.Thread(target=self._loadingAnimation)
        self.loadingThread.start()

    def _loadingAnimation(self):
        # Set the last info text, set the info hidden state, show the info label and whilst the lyrics have not loaded reset the animation index if the animation cycle has completed, set the info label text to the current animation frame text, increment the animation index and sleep for the set interval
        lastInfoText = self.infoLabel.text()

        if self.infoLabel.isHidden():
            infoWasHidden = True
            self.infoLabel.show()
        else:
            infoWasHidden = False
        
        animationIndex = 0
        animationFrameCount = len(self.loadingText)

        while not self.loadedLyrics:
            if animationIndex == animationFrameCount:
                animationIndex = 0

            self.infoLabel.setText(self.loadingText[animationIndex])
            animationIndex += 1
            time.sleep(self.loadingAnimationInterval_ms / 1000)

        # Reset the info label text to the last recorded value and hide the info label if it was previously hidden
        self.infoLabel.setText(lastInfoText)

        if infoWasHidden:
            self.infoLabel.hide()

class HelpWidget(QtWidgets.QWidget):

    
    def __init__(self, parent: MainWindow = None):
        super().__init__()

        self.parent = parent

        if lib.config.__contains__("geometry") and lib.config["geometry"].__contains__("help"):
            geometry = lib.config["geometry"]["help"]
            self.left = geometry["left"]
            self.top = geometry["top"]
            self.width = geometry["width"]
            self.height = geometry["height"]
        elif parent != None:
            parentGeometry = self.parent.geometry()
            self.left = parentGeometry.left()
            self.top = parentGeometry.top()
            self.width = lib.lyrics_defaultWidth
            self.height = lib.lyrics_defaultHeight
        else:
            self.left = lib.defaultLeft
            self.top = lib.defaultTop
            self.width = lib.lyrics_defaultWidth
            self.height = lib.lyrics_defaultHeight

        self.title = lib.progName + lib.titleSeparator + self.tr("Help")
        self.initUI()


    def initUI(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)
        #Load Window Position

        if not lib.config.__contains__("geometry") or not lib.config["geometry"].__contains__("lyrics"):
            if not lib.config.__contains__("geometry"):
                lib.config["geometry"] = {}
            lib.config["geometry"]["help"] = {}
            lib.config["geometry"]["help"]["left"] = self.left
            lib.config["geometry"]["help"]["top"] = self.top
            lib.config["geometry"]["help"]["width"] = self.width
            lib.config["geometry"]["help"]["height"] = self.height
        
        #Set fixed Size
        self.setFixedSize(550,380)

        self.songText = ""
        self.artistText = ""
        self.lastSearchedSong = None
        self.lastSearchedArtist = None
        
        self.createWidgets()
        self.createLayout()

        self.show()
    def moveEvent(self, event: QtGui.QMoveEvent):
        # Set the left and top keys in the geometry key of the config dictionary to the corresponding geometric values and write the config to disk
        lib.config["geometry"]["help"]["left"] = self.geometry().left()
        lib.config["geometry"]["help"]["top"] = self.geometry().top()

        lib.writeToMainConfigJSON(lib.config)

    def createWidgets(self):

        #Create Widgets for Help Window

        self.mainPlayerHelpButton = QtWidgets.QPushButton()
        self.mainPlayerHelpButton.setIconSize(QtCore.QSize(100,100))
        self.mainPlayerHelpButton.setStyleSheet("background-color: rgba(255, 255, 255, 0)")
        self.mainPlayerHelpButton.pressed.connect(self.showMainHelp)

        self.miniPlayerHelpButton = QtWidgets.QPushButton()
        self.miniPlayerHelpButton.setIconSize(QtCore.QSize(100,100))
        self.miniPlayerHelpButton.setStyleSheet("background-color: rgba(255, 255, 255, 0)")
        self.miniPlayerHelpButton.pressed.connect(self.showMiniHelp)

        self.lyricsHelpButton = QtWidgets.QPushButton()
        self.lyricsHelpButton.setIconSize(QtCore.QSize(100,100))
        self.lyricsHelpButton.setStyleSheet("background-color: rgba(255, 255, 255, 0)")
        self.lyricsHelpButton.pressed.connect(self.showLyricHelp)

        self.mainPlayerHelpLabel = QtWidgets.QLabel("Main Player")
        self.mainPlayerHelpLabel.setAlignment(QtCore.Qt.AlignCenter)

        self.miniPlayerHelpLabel = QtWidgets.QLabel("Mini Player")
        self.miniPlayerHelpLabel.setAlignment(QtCore.Qt.AlignCenter)

        self.lyricsHelpLabel = QtWidgets.QLabel("Lyrics")
        self.lyricsHelpLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.welcomeLabel = QtWidgets.QLabel("""
        Welcome to the QMusic Help Window
        To get started, simply click an icon below""")
        self.welcomeLabel.setAlignment(QtCore.Qt.AlignVCenter)

        self.mainHelp = QtWidgets.QLabel("""
        The main player is the main window that will start when you open QMusic. 
        Here you can add music to the playlist by either:
        - Dragging and Dropping an audio file
        - Selecting File -> Open File in the menu bar
        - Open an entire folder by selecting File -> Open Directory""")
        self.mainHelp.setAlignment(QtCore.Qt.AlignLeft)

        self.miniHelp = QtWidgets.QLabel("""
        To enter the Mini Player window, go to Player -> Switch Player Size
        Here you can use a simplified player without a playlist and volume view
        To exit simply click Switch Player Size Again""")
        self.miniHelp.setAlignment(QtCore.Qt.AlignLeft)

        self.lyricHelp = QtWidgets.QLabel("""
        To enter the Lyrics Window, simply go to Player -> Lyrics
        Here you can enter a song and artist name to get lyrics from genius.com
        To exit simply close the window""")
        self.lyricHelp.setAlignment(QtCore.Qt.AlignLeft)
        style = lib.config["style"]

        if style == 1:
            self.mainPlayerHelpButton.setIcon(QtGui.QIcon("resources/main_help_inverted.png"))
            self.miniPlayerHelpButton.setIcon(QtGui.QIcon("resources/mini_help_inverted.png"))
            self.lyricsHelpButton.setIcon(QtGui.QIcon("resources/lyrics_help_inverted.png"))
        else:
            self.mainPlayerHelpButton.setIcon(QtGui.QIcon("resources/main_help_icon.png"))
            self.miniPlayerHelpButton.setIcon(QtGui.QIcon("resources/mini_help_icon.png"))
            self.lyricsHelpButton.setIcon(QtGui.QIcon("resources/lyrics_help_icon.png"))
    
    def createLayout(self):
        # Create Layout

        labelGroup = QtWidgets.QGroupBox()
        buttonGroup = QtWidgets.QGroupBox()

        buttonLayout = QtWidgets.QGridLayout()
        buttonLayout.setSpacing(10)
        buttonLayout.addWidget(self.mainPlayerHelpButton,0,0)
        buttonLayout.addWidget(self.miniPlayerHelpButton,0,1)
        buttonLayout.addWidget(self.lyricsHelpButton,0,2)
        buttonLayout.addWidget(self.mainPlayerHelpLabel,1,0)
        buttonLayout.addWidget(self.miniPlayerHelpLabel,1,1)
        buttonLayout.addWidget(self.lyricsHelpLabel,1,2)

        labelLayout = QtWidgets.QGridLayout()
        labelLayout.setSpacing(0)
        labelLayout.addWidget(self.mainHelp)
        labelLayout.addWidget(self.miniHelp)
        labelLayout.addWidget(self.lyricHelp)
        labelLayout.addWidget(self.welcomeLabel)
        self.mainHelp.hide()
        self.miniHelp.hide()
        self.lyricHelp.hide()

        buttonGroup.setLayout(buttonLayout)
        labelGroup.setLayout(labelLayout)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.addWidget(labelGroup)
        layout.addWidget(buttonGroup)


        self.setLayout(layout)
    
    # Hide and show widgets for each button
  
    def showMainHelp(self):
        self.mainHelp.show()
        self.miniHelp.hide()
        self.lyricHelp.hide()
        self.welcomeLabel.hide()
    def showMiniHelp(self):
        self.miniHelp.show()
        self.mainHelp.hide()
        self.lyricHelp.hide()
        self.welcomeLabel.hide()
    def showLyricHelp(self):   
        self.lyricHelp.show()
        self.mainHelp.hide()
        self.miniHelp.hide()
        self.welcomeLabel.hide()

        
        





    
