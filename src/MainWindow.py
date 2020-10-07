#
#   MainWindow.py
#   Class extended from QMainWindow
#

from PySide2 import QtWidgets, QtCore, QtGui, QtMultimedia
import lib
import os
from playlist import PlaylistModel, PlaylistView
import mutagen
from typing import List
#from pyside_material import apply_stylesheet
import qdarkstyle
import sys
import darkdetect
import lyricsgenius
import threading
import time
token = lyricsgenius.Genius("AwxNghHLIPG4Zs97LyrQLtRfDZEWTKJdF6ecdYCEmkDcA3CQiCXFZHrkBeUcQvBd")
#keyboard: any
#is_admin = lib.get_admin_status()
#lib.importKeyboard(is_admin)
songtext = ""
artisttext = ""
class lyricWindow(QtWidgets.QMainWindow):
    def setdarktheme(self):
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    def setlighttheme(self):
        self.setStyleSheet("")
    def __init__(self):
        super().__init__()
        self.left = 0
        self.top = 0
        self.width = 300
        self.height = 300
        self.title = "QMusic Lyrics"
        self.initlyricUI()
    def initlyricUI(self):
        if darkdetect.isDark()== True:
            self.setdarktheme()
        else:
            self.setlighttheme()
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)
        self.createLyricWidgets()
        self.createLayoutLyric()
        self.show()
    def createLyricWidgets(self):
        self.artistlabel = QtWidgets.QLabel("Artist")
        self.songlabel = QtWidgets.QLabel("Song")
        self.artistbox = QtWidgets.QLineEdit()
        self.artistbox.textChanged.connect(self.artistboxchanged)
        self.songbox = QtWidgets.QLineEdit()
        self.songbox.textChanged.connect(self.songboxchanged)
        self.searchbutton = QtWidgets.QPushButton("Search")
        self.searchbutton.pressed.connect(self.searchclicked)
        self.scroll = QtWidgets.QScrollArea()
        self.outputlabel = QtWidgets.QLabel()
        self.outputlabel.setWordWrap(True)
        self.scroll.setWidget(self.outputlabel)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(8000)
    def createLayoutLyric(self):
        lyriclayouttopgroup = QtWidgets.QGroupBox()
        lyriclayoutbuttongroup = QtWidgets.QGroupBox()
        lyriclayouttextgroup = QtWidgets.QGroupBox()

        lyriclayouttop = QtWidgets.QGridLayout()
        lyriclayouttop.setSpacing(10)
        lyriclayouttop.addWidget(self.artistlabel,0,0)
        lyriclayouttop.addWidget(self.artistbox,0,1)
        lyriclayouttop.addWidget(self.songlabel,1,0)
        lyriclayouttop.addWidget(self.songbox,1,1)



        lyriclayoutbutton = QtWidgets.QHBoxLayout()
        lyriclayoutbutton.addWidget(self.searchbutton)

        lyriclayouttext = QtWidgets.QHBoxLayout()
        lyriclayouttext.addWidget(self.scroll)

        lyriclayouttopgroup.setLayout(lyriclayouttop)
        lyriclayoutbuttongroup.setLayout(lyriclayoutbutton)
        lyriclayouttextgroup.setLayout(lyriclayouttext)

        self.lyriclayout = QtWidgets.QVBoxLayout()
        self.lyriclayout.addWidget(lyriclayouttopgroup)
        self.lyriclayout.addWidget(lyriclayoutbuttongroup)
        self.lyriclayout.addWidget(lyriclayouttextgroup)
    
        self.setLayout(self.lyriclayout)
        self.centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.lyriclayout)
    def songboxchanged(self,text):
        global songtext
        songtext = text
    def artistboxchanged(self,text):
        global artisttext
        artisttext = text

    def searchclicked(self):
        global artisttext
        global songtext
        song = token.search_song(songtext, artisttext)
        self.outputlabel.setText(song.lyrics)



class PrefWindow(QtWidgets.QMainWindow):
    def setdarktheme(self):
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    def setlighttheme(self):
        self.setStyleSheet("")
    themenumber=0
    def __init__(self):
        super().__init__()
        self.left = 0
        self.top = 0
        self.width = 60
        self.height = 50
        self.title = "QMusic Preferences"
        self.initsetUI()
    
    def initsetUI(self):
        if darkdetect.isDark()== True:
            self.setdarktheme()
        else:
            self.setlighttheme()
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)
        self.createPrefWidgets()
        self.createLayoutPref()
        self.show()

    def createPrefWidgets(self):
        self.themelabel = QtWidgets.QLabel("Theme Type")
        self.darkcheck = QtWidgets.QRadioButton("Dark",self)
        self.darkcheck.toggled.connect(self.changetheme)
        self.lightcheck = QtWidgets.QRadioButton("Light",self)
        self.lightcheck.toggled.connect(self.changetheme)
        self.autoplaycheck = QtWidgets.QCheckBox("Auto Play",self)
        self.repeatcheck = QtWidgets.QCheckBox("Repeat",self)
        self.shufflecheck = QtWidgets.QCheckBox("Shuffle",self)
    def createLayoutPref(self):
        preflayout =  QtWidgets.QGridLayout()
        preflayout.setSpacing(10)
        preflayout.addWidget(self.themelabel,0,0)
        preflayout.addWidget(self.darkcheck,1,0)
        preflayout.addWidget(self.lightcheck,2,0)
        preflayout.addWidget(self.autoplaycheck,0,2)
        preflayout.addWidget(self.repeatcheck,1,2)
        preflayout.addWidget(self.shufflecheck,2,2)
        self.setLayout(preflayout)
        self.centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(preflayout)
    def changetheme(self,themenumber):
        if self.darkcheck.isChecked()==True:
            self.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
            MainWindow.setdarktheme(self)
            self.mainwindow = MainWindow()
            self.mainwindow.setdarktheme()
            self.mainwindow.createWidgets(64,1)
            self.mainwindow.initPlayer()
            self.mainwindow.initPlaylist()
            self.mainwindow.init_playpause()
            self.mainwindow.connect_update_media()
            self.mainwindow.createLayoutMain()
            self.mainwindow.createCentralWidget()
            self.mainwindow.createMenus()
            self.mainwindow.createShortcuts()
        if self.lightcheck.isChecked()==True:
            self.setStyleSheet("")
            MainWindow.setlighttheme(self)
            self.mainwindow = MainWindow()
            self.mainwindow.setlighttheme()
            self.mainwindow.createWidgets(64,1)
            self.mainwindow.initPlayer()
            self.mainwindow.initPlaylist()
            self.mainwindow.init_playpause()
            self.mainwindow.connect_update_media()
            self.mainwindow.createLayoutMain()
            self.mainwindow.createCentralWidget()
            self.mainwindow.createShortcuts()          
        if self.lightcheck.isChecked()==True:
            themenumber = 2
            

class MainWindow(QtWidgets.QMainWindow):
    #   -   init: 
    #       -   Call init on super
    #       -   Set geometry variables
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
    #       -   Add media from config, reset lastMediaCount, isTransitioning, isFading and lastVolume variables
    #       -   Set variables for fade out and in rates
    #       -   Show
    def __init__(self):
        super().__init__()
        self.left = 0
        self.top = 0
        self.width = 430
        self.height = 320
        self.title = lib.progName

        self.rate_ms_fadeOut = 200
        self.rate_ms_fadeIn = 200
        
        self.initUI()
    
    def setdarktheme(self):
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    def setlighttheme(self):
        self.setStyleSheet("")

    def initUI(self):
        if darkdetect.isDark()== True:
            self.setdarktheme()
        else:
            self.setlighttheme()
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)

        self.createWidgets(64,1)
        self.initPlayer()
        self.initPlaylist()
        self.init_playpause()
        self.connect_update_media()

        self.createMenus()
        self.createShortcuts()

        self.addMediaFromConfig()
        self.lastMediaCount = 0
        self.isTransitioning = False
        self.isFading = False
        self.lastVolume = self.player.volume()

        self.createLayoutMain()
        self.createCentralWidget()

        self.show()


    def createWidgets(self,width,showart):
        # Create buttons, labels and sliders
        self.control_playpause = QtWidgets.QPushButton()
        self.control_playpause.setFixedWidth(85)
        self.control_previous = QtWidgets.QPushButton(self.tr(""))
        self.control_next = QtWidgets.QPushButton(self.tr(""))

        self.mini_player_button = QtWidgets.QPushButton("Mini Player")
        self.mini_player_button.clicked.connect(self.mini_button_clicked)

        self.main_player_button = QtWidgets.QPushButton("Main Player")
        self.main_player_button.clicked.connect(self.main_button_clicked)

        self.prefbutton = QtWidgets.QPushButton("Preferences")
        self.prefbutton.clicked.connect(self.openpref)

        self.lyricbutton = QtWidgets.QPushButton("Lyrics")
        self.lyricbutton.clicked.connect(self.openlyrics)

        self.control_previous.setIcon(QtGui.QIcon("resources/control_previous"))
        self.control_previous.setIconSize(QtCore.QSize(20,20))
        self.control_next.setIcon(QtGui.QIcon("resources/control_next"))
        self.control_next.setIconSize(QtCore.QSize(20,20))
        
        self.basichelp_label = QtWidgets.QLabel("""Welcome to QMusic, to get started go to File --> Open or Drag and Drop a Song or Folder into the window""")
        self.basichelp_label.hide()
        self.basichelp_label.setWordWrap(True)
        self.volumeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setValue(100)
        
        self.timeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.timePositionLabel = QtWidgets.QLabel(lib.to_hhmmss(0))
        self.totalTimeLabel = QtWidgets.QLabel(lib.to_hhmmss(0))
        self.timePositionLabel.setStyleSheet(
            "QLabel {color: #" + lib.textColour + "}"
        )
        self.totalTimeLabel.setStyleSheet(
            "QLabel {color: #" + lib.textColour + "}"
        )
        
        #self.basichelp_label.hide()
        self.metadata_label = QtWidgets.QLabel()
        self.metadata_label.setStyleSheet(
            "QLabel {color: #" + lib.textColour + "}"
        )
        self.metadata_label.setWordWrap(True)
        self.metadata_label.hide()
        if showart == 1:
            self.coverart_label = QtWidgets.QLabel()
            self.coverart_label.hide()
            self.coverart_width = width

        # Create playlist action buttons and connect pressed signals
        self.control_playlist_moveDown = QtWidgets.QPushButton(self.tr("Move Down"))
        self.control_playlist_moveUp = QtWidgets.QPushButton(self.tr("Move Up"))
        self.control_playlist_clear = QtWidgets.QPushButton(self.tr("Clear"))

        self.control_playlist_moveDown.pressed.connect(self.playlist_moveDown)
        self.control_playlist_moveUp.pressed.connect(self.playlist_moveUp)
        self.control_playlist_clear.pressed.connect(self.playlist_clear)

    def initPlayer(self):
        # Create QMediaPlayer and connect to time and volume sliders value changed members, connect player position/duration changed to update position and duration methods
        self.player = QtMultimedia.QMediaPlayer()
        self.volumeSlider.valueChanged.connect(self.player.setVolume)

        # Note: self.player.setPosition adds pauses to playback
        self.timeSlider.valueChanged.connect(self.setPosition)
        self.player.durationChanged.connect(self.update_duration)
        self.player.positionChanged.connect(self.update_position)

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
        print("Restoring volume")
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
        self.playlist = QtMultimedia.QMediaPlaylist()
        self.player.setPlaylist(self.playlist)
        self.playlistModel = PlaylistModel(self.playlist)
        self.control_previous.pressed.connect(self.previousTrack)
        self.control_next.pressed.connect(self.nextTrack)

        # Create playlist view and set model, create selection model from playlist view and connect playlist selection changed method
        self.playlistView = PlaylistView(self.playlistModel)
        self.playlistViewSelectionModel = self.playlistView.selectionModel()
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

    #
    #   Todo: add comments for playlist move functions
    #

    def playlist_moveDown(self):
        selectedIndexes = self.playlistView.selectedIndexes()
        currentPlaylistIndex = self.playlist.currentIndex()

        if len(selectedIndexes) > 0 and selectedIndexes.__contains__(self.playlistModel.index(currentPlaylistIndex)) == False and selectedIndexes[len(selectedIndexes) - 1].row() + 1 > currentPlaylistIndex:
            firstIndex = selectedIndexes[0].row()
            maxIndex = selectedIndexes[len(selectedIndexes) - 1].row()

            media: List[QtMultimedia.QMediaContent] = []
            for i in range(firstIndex, maxIndex + 1):
                media.append(self.playlist.media(i))
            
            previousSelectedIndexes = self.playlistView.selectedIndexes()

            self.playlist.insertMedia(firstIndex + 2, media)
            self.playlist.removeMedia(firstIndex, maxIndex)
            self.playlistModel.layoutChanged.emit()

            len_previousSelectedIndexes = len(previousSelectedIndexes)
            self.playlistViewSelectionModel.select(QtCore.QItemSelection(previousSelectedIndexes[0], previousSelectedIndexes[len_previousSelectedIndexes - 1]), QtCore.QItemSelectionModel.Deselect)
            self.playlistViewSelectionModel.select(QtCore.QItemSelection(self.playlistModel.index(previousSelectedIndexes[0].row() + 1), self.playlistModel.index(previousSelectedIndexes[len_previousSelectedIndexes - 1].row() + 1)), QtCore.QItemSelectionModel.Select)

    def playlist_moveUp(self):
        selectedIndexes = self.playlistView.selectedIndexes()
        currentPlaylistIndex = self.playlist.currentIndex()
        
        if len(selectedIndexes) > 0 and selectedIndexes.__contains__(self.playlistModel.index(currentPlaylistIndex)) == False and selectedIndexes[0].row() - 1 > currentPlaylistIndex:
            firstIndex = selectedIndexes[0].row()
            maxIndex = selectedIndexes[len(selectedIndexes) - 1].row()

            media: List[QtMultimedia.QMediaContent] = []
            for i in range(firstIndex, maxIndex + 1):
                media.append(self.playlist.media(i))
            
            previousSelectedIndexes = self.playlistView.selectedIndexes()

            self.playlist.insertMedia(firstIndex - 1, media)
            self.playlist.removeMedia(firstIndex + 1, maxIndex + 1)
            self.playlistModel.layoutChanged.emit()

            len_previousSelectedIndexes = len(previousSelectedIndexes)
            self.playlistViewSelectionModel.select(QtCore.QItemSelection(previousSelectedIndexes[0], previousSelectedIndexes[len_previousSelectedIndexes - 1]), QtCore.QItemSelectionModel.Deselect)
            self.playlistViewSelectionModel.select(QtCore.QItemSelection(self.playlistModel.index(previousSelectedIndexes[0].row() - 1), self.playlistModel.index(previousSelectedIndexes[len_previousSelectedIndexes - 1].row() - 1)), QtCore.QItemSelectionModel.Select)

    def playlist_clear(self):
        # Clear the playlist, clear the media config log and emit the playlist model layout changed signal
        self.playlist.clear()
        lib.clearConfigFile(lib.configDir, lib.mediaFileName)
        self.playlistModel.layoutChanged.emit()
    
    #
    #   Revise
    #

    def playlist_position_changed(self, index: QtCore.QModelIndex):
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

    def openpref(self):
        self.preferenceswindow = PrefWindow()
        self.preferenceswindow.show
    
    def openlyrics(self):
        self.lyricswindow = lyricWindow()
        self.lyricswindow.show


    def mini_button_clicked(self):
        
        self.left = 0
        self.top = 0
        self.width = 270
        self.height = 350
        self.title = "QMusic"
        self.setWindowTitle(self.title)
        self.createLayoutMain()
        self.createCentralWidget()
        self.createLayoutMini()
        self.createCentralWidget()
        self.control_playlist_moveDown.hide()
        self.control_playlist_moveUp.hide()
        self.control_playlist_clear.hide()
        self.playlistView.hide()
        self.prefbutton.hide()
        self.lyricbutton.hide()
        self.coverart_label.hide()
        self.createLayoutMain()
        self.createCentralWidget()
        self.createLayoutMini()
        self.createCentralWidget()
        self.setFixedWidth(350)
        self.setFixedHeight(230)
        self.control_playpause.setIcon(QtGui.QIcon("resources/control_play"))
        self.control_playpause.setIconSize(QtCore.QSize(18,18))



    def main_button_clicked(self):
        self.left = 0
        self.top = 0
        self.width = 660
        self.height = 400
        self.title = "QMusic"
        self.setWindowTitle(self.title)
        self.createLayoutMain()
        self.control_playlist_moveDown.show()
        self.control_playlist_moveUp.show()
        self.control_playlist_clear.show()
        self.playlistView.show()
        self.prefbutton.show()
        self.lyricbutton.show()
        self.coverart_label.show()
        self.createCentralWidget()
        self.setMaximumSize(8000,8000)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.control_playpause.setIcon(QtGui.QIcon("resources/control_play"))
        self.control_playpause.setIconSize(QtCore.QSize(20,20))
        self.control_playpause.pressed.connect(self.play)
        
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

    def update_media(self, media: QtMultimedia.QMediaContent):
        # If playing, update the play/pause button to the playing state, otherwise set its properties to the paused state
        self.updatePlayingState()
        
        # Called on media change, update track metadata and cover art
        self.update_metadata(media)
        self.update_coverart(media)

    def connect_update_media(self):
        # Connect cover art update method to playlist current media changed signal
        self.playlist.currentMediaChanged.connect(self.update_media)

    def createLayoutMain(self):
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
        actionsLayout.addWidget(self.control_playlist_clear)
        actionsLayout.addWidget(self.mini_player_button)
        actionsLayout.addWidget(self.main_player_button)
        actionsLayout.addWidget(self.prefbutton)
        actionsLayout.addWidget(self.lyricbutton)
        

        self.vLayout = QtWidgets.QVBoxLayout()
        self.vLayout.addWidget(detailsGroup)
        self.vLayout.addLayout(actionsLayout)
        self.vLayout.addWidget(self.playlistView)
        self.vLayout.addWidget(self.basichelp_label)

    def createLayoutMini(self):
        detailsGroup = QtWidgets.QGroupBox()

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

        hPlaylistLayout = QtWidgets.QHBoxLayout()
        hPlaylistLayout.addWidget(self.playlistView)
        hPlaylistLayout.addWidget(self.coverart_label)
    
        actionsLayout = QtWidgets.QHBoxLayout()
        
        actionsLayout.addWidget(self.control_playlist_moveDown)
        actionsLayout.addWidget(self.control_playlist_moveUp)
        actionsLayout.addWidget(self.control_playlist_clear)
        actionsLayout.addWidget(self.prefbutton)
        actionsLayout.addWidget(self.lyricbutton)

        switchLayoutButtons = QtWidgets.QHBoxLayout()
        switchLayoutButtons.addWidget(self.main_player_button)
        
        switchLayoutButtons.addWidget(self.mini_player_button)

        vDetailsLayout = QtWidgets.QVBoxLayout()
        
        vDetailsLayout.addLayout(hControlLayout)
        vDetailsLayout.addLayout(hVolumeLayout)
        vDetailsLayout.addLayout(hTimeLayout)
        vDetailsLayout.addLayout(actionsLayout)
        vDetailsLayout.addWidget(self.metadata_label)
        vDetailsLayout.addLayout(hPlaylistLayout)

        vDetailsLayout.addLayout(switchLayoutButtons)
        

        
        detailsGroup.setLayout(vDetailsLayout)

        self.vLayout = QtWidgets.QVBoxLayout()
        self.vLayout.addWidget(detailsGroup)
        self.vLayout.addWidget(self.basichelp_label)
    def createCentralWidget(self):
        # Create central widget, call set central widget method and set widget layout
        self.centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.vLayout)
        self.setGeometry(self.left, self.top, self.width, self.height)

    def createMenus(self):
        # Create main menu from menuBar method, use addMenu for submenus and add QActions accordingly with triggered connect method, set shortcut from QKeySequence on QActions
        self.mainMenu = self.menuBar()
        fileMenu = self.mainMenu.addMenu("File")

        openAction = QtWidgets.QAction("Open", self)
        openAction.triggered.connect(self.open_file)
        openAction.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+O", "File|Open")))

        removeAction = QtWidgets.QAction("Remove", self)
        removeAction.triggered.connect(self.removeMedia)

        clearPlaylistAction = QtWidgets.QAction("Clear Playlist", self)
        clearPlaylistAction.triggered.connect(self.playlist_clear)
        clearPlaylistAction.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+Backspace", "File|Clear Playlist")))

        helpMenu = self.mainMenu.addMenu("Help")
        basichelp = QtWidgets.QAction("Basic Help", self)
        basichelp.triggered.connect(self.basic_help)
        basichelp.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+H", "Help|Basic Help")))
        

        windowMenu = self.mainMenu.addMenu("Window")
        miniwindow = QtWidgets.QAction("Mini Player", self)
        miniwindow.triggered.connect(self.mini_button_clicked)
        mainwindow = QtWidgets.QAction("Main Player", self)
        mainwindow.triggered.connect(self.main_button_clicked)

        prefMenu = self.mainMenu.addMenu("Pref")
        pref = QtWidgets.QAction("Preferences", self)
        pref.triggered.connect(self.openpref)
        
        prefMenu.addAction(pref)

        windowMenu.addAction(miniwindow)
        windowMenu.addAction(mainwindow)

        helpMenu.addAction(basichelp)
        
        fileMenu.addAction(openAction)
        fileMenu.addAction(removeAction)
        fileMenu.addAction(clearPlaylistAction)

    def open_file(self):
        # Set last media count for playlist media check later on
        self.lastMediaCount = self.playlist.mediaCount()
        
        # Set paths from QFileDialog getOpenFileNames, filetypes formatted as "Name (*.extension);;Name" etc.
        paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self, self.tr("Open"), "", self.tr("All Files (*.*);;Waveform Audio (*.wav);;mp3 Audio (*.mp3);;m4a Audio (*.m4a)"))

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

        # Write media to config
        self.writeMediaToConfig()

    def addMediaFromConfig(self):
        # If the file exists, read in each line of the media log to a list and add the media content from each path to the playlist
        paths: List[str] = []
        mediaLog = os.path.join(lib.configDir, lib.mediaFileName)

        if os.path.isfile(mediaLog):
            with open(mediaLog, "r") as mediaData:
                paths = mediaData.read().split("\n")

            for path in paths:
                if path != "":
                    self.playlist.addMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(path)))

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
        selectedIndexes = self.playlistView.selectedIndexes()
        if len(selectedIndexes) > 0:
            for index in selectedIndexes:
                self.playlist.removeMedia(index.row(), selectedIndexes[len(selectedIndexes)-1].row())
                self.playlistModel.layoutChanged.emit()

    def createShortcuts(self):
        # Create QShortcuts from QKeySequences with the shortcut and menu item passed as arguments
        shortcut_playpause_space = QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("Space", "")), self)
        shortcut_playpause = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_MediaPlay), self)
        shortcut_playpause_space.activated.connect(self.playpause)
        shortcut_playpause.activated.connect(self.playpause)

        shortcut_delete = QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("Backspace")), self)
        shortcut_delete.activated.connect(self.removeMedia)

        shortcut_previous = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Left), self)
        shortcut_previous.activated.connect(self.playlist.previous)

        shortcut_next = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Right), self)
        shortcut_next.activated.connect(self.playlist.next)

        #if is_admin:
            #keyboard.add_hotkey(0x83, self.playpause)

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
        self.writeMediaToConfig()

    def playNewMedia(self):
        if self.isPlaying() == False and self.lastMediaCount == 0:
            self.pause()

    def switchMedia(self):
        selectedIndexes = self.playlistView.selectedIndexes()
        if len(selectedIndexes) > 0:
            self.playlist.setCurrentIndex(selectedIndexes[0].row())
            self.playNewMedia()
