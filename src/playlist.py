#
#   playlist.py
#   Classes and functions for the playlist
#

from PySide2 import QtCore, QtMultimedia, QtWidgets, QtGui

#
#   Revise
#

#
#   Todo: add playlist drag and drop reordering support
#

class PlaylistModel(QtCore.QAbstractListModel):
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

    def data(self, index: QtCore.QModelIndex, role):
        if role == QtCore.Qt.DisplayRole:
            media = self.playlist.media(index.row())
            return media.canonicalUrl().fileName()

    def rowCount(self, index: QtCore.QModelIndex):
        return self.playlist.mediaCount()

    def flags(self, index: QtCore.QModelIndex):
        if index.isValid():
            flags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled | QtCore.Qt.ItemIsEnabled
        else:
            flags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled
        
        return flags


class PlaylistView(QtWidgets.QListView):
    def __init__(self, model: QtCore.QAbstractListModel, parent: QtWidgets.QWidget = None):
        super().__init__(parent)

        self.setModel(model)
        self.setMovement(QtWidgets.QListView.Snap)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setDragDropOverwriteMode(False)
