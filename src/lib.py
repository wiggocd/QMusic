#
#   lib.py
#   Miscellaneous definitions
#

import os
from typing import Union, List
from PySide2 import QtGui, QtCore, QtWidgets
import json
import mutagen
import lyricsgenius
from shutil import rmtree

# Globals
progName = "QMusic"
textColour = "A7A7A7"
configDir: str = None
execDir: str = None
mainConfigJSONFileName = "config.json"
mediaFileName = "media.txt"
configDict: dict = None
globalStyleIndex = 0
globalStyleSheet = ""
titleSeparator = " - "
defaultLeft = 0
defaultTop = 0
defaultWidth = 460
defaultHeight = 320
miniWidth = 350
miniHeight = 160
maxWidth = 16777215
maxHeight = 16777215
lyrics_defaultWidth = 300
lyrics_defaultHeight = 300
lyricsObject: lyricsgenius.Genius = None
lyricsTokenFileName = "lyricsgenius_token.txt"
QDarkStyleSrcFileName = "QDarkStyle.qss"
config = {}

defaultConfig = {
    "volume": 100,
    "playerSize": 0,
    "style": 0
}

supportedFormats = [
    "wav",
    "mp3",
    "m4a",
    "flac"
]

class Style:
    def __init__(self, name: str, styleSheet: str):
        # Basic class: set attributes from parameters for name and style data
        self.name = name
        self.styleSheet = styleSheet

styles = [
    Style("Default", "")
]

def get_execdir() -> str:
    path = os.path.dirname(os.path.realpath(__file__))
    return path

def get_resourcepath(resourceName: str, execDir: str) -> str:
    # Return the parent directory to the running file directory and concatenate the resource directory to the returned string
    return os.path.join(os.path.realpath(os.path.dirname(execDir)), "resources", resourceName)

def to_hhmmss(ms: int) -> str:
    #   -   s = ms / 1000 rounded
    #   -   m and s = s modulo 60
    #   -   h and m = m modulo 60
    #   -   Return hh:mm:ss formatted/padded string if h, else return mm:ss

    s = round(ms / 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)

    return ("%d:%02d:%02d" % (h, m, s)) if h else ("%d:%02d" % (m, s))

def get_coverart(directoryPath: str) -> Union[str, None]:
    #   -   Loop through directory entries from listdir method, check if extension is an image, if so append to a list
    #   -   Loop through the list and if an entry contains a cover art keyword, return the path to the image

    directory = os.listdir(directoryPath)
    images: List[str] = []
    
    for relativeEntryName in directory:
        split = relativeEntryName.split(os.path.extsep)
        if split[len(split)-1].lower() == "jpg" or "jpeg" or "png":
            images.append(relativeEntryName)

    for relativeEntryName in images:
        lower = relativeEntryName.lower()
        if lower.__contains__("cover") or lower.__contains__("front") or lower.__contains__("folder"):
            return os.path.join(directoryPath, relativeEntryName)

    return None

def urlStringToPath(urlString: str) -> str:
    #   If url begins with the file prefix, return all of the url string after the third slash if there is a colon signifying a Windows environment, otherwise return before the third slash (Unix)

    path = ""
    if urlString.startswith("file://"):
        separator_index = 8 if urlString[9] == ':' else 7
        path = urlString[separator_index:]
    else:
        path = urlString

    return path

#
#   Revise
#

def getAdminStatus() -> bool:
    #   Reminders:
    #   - import ctypes
    #   - if os.getuid == x ...
    #   - ctypes.windll.shell32.IsUserAnAdmin != 0 ...

    import ctypes
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin != 0

    return is_admin

#
#   Todo: comment and revise
#

def get_coverart_pixmap_from_metadata(metadata: dict) -> Union[QtGui.QPixmap, None]:
    apic: str = None
    for k in metadata.keys():
        if k.startswith("APIC"):
            apic = k
    
    if apic != None:
        data = metadata[apic].data
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(QtCore.QByteArray(data))
        return pixmap
    else:
        return None

def get_configDir(progName: str) -> str:
    # Use expanduser with nested config directory
    return os.path.join(os.path.expanduser("~"), ".config", progName)

def create_configDir(configDir: str):
    # Check if the directory exists and create it if not
    if not os.path.isdir(configDir):
        os.makedirs(configDir)

def writeToConfig(configDir: str, configFilename: str, strings: List[str]):
    # Open file and write each string as a line
    with open(os.path.join(configDir, configFilename), "w") as openFile:
        for path in strings:
            openFile.write(path + "\n")

def clearConfigFile(configDir: str, configFilename: str):
    # Open file and write it to empty
    with open(os.path.join(configDir, configFilename), "w") as openFile:
        openFile.write("")

def getLyricsToken(execDir: str):
    # Get the canonical path of the lyrics token from the resource method, and if the file exists open the file for reading and return the first line
    path = get_resourcepath(lyricsTokenFileName, execDir)
    
    if os.path.isfile(path):
        with open(path, "r") as openFile:
            return openFile.read().split("\n")[0]

def setLyricsToken(execDir: str):
    # If the token read from disk is valid, set the global lyrics object to a Genius instance from the lyrics token
    global lyricsObject
    token = getLyricsToken(execDir)
    
    if token != None and len(token) > 1:
        lyricsObject = lyricsgenius.Genius(token)

def setAltLabelStyle(label: QtWidgets.QLabel):
    # Set the alternative properties on the label's stylesheet
    label.setStyleSheet(
        """
        QLabel {color: #""" + textColour + """}
        """
    )

def loadStyleFromSrc(styleFileName: str, execDir: str, styleName: str) -> Style:
    # If the style file exists, using the open function load the style file from the executable directory and read in the data as a string, return a Style instance from the style name and stylesheet string
    styleString = ""
    path = os.path.join(execDir, styleFileName)

    if os.path.isfile(path):
        with open(path, "r") as openFile:
            styleString = openFile.read()
    
    return Style(styleName, styleString)

def loadQDarkStyle(execDir: str) -> Style:
    return loadStyleFromSrc(QDarkStyleSrcFileName, execDir, "QDarkStyle")

def loadConfigJSON(fileName: str, configDirPath: str) -> dict:
    # If the path from the filename and config path exists, read the data from the file as a string and use the JSON load string function to parse the data and return it
    path = os.path.join(configDirPath, fileName)
    data = {}

    if os.path.isfile(path):
        with open(path, "r") as openFile:
            data = json.loads(openFile.read())

    return data

def loadMainConfigJSON():
    return loadConfigJSON(mainConfigJSONFileName, configDir)

def writeToConfigJSON(data: dict, fileName: str, configDirPath: str):
    # Dump the dict to a json string and write it to the file
    string = json.dumps(data)

    with open(os.path.join(configDirPath, fileName), "w") as openFile:
        openFile.write(string)

def writeToMainConfigJSON(data: dict):
    # Write to the main config JSON from the data
    return writeToConfigJSON(data, mainConfigJSONFileName, configDir)

def writeDefaultConfig():
    # If the main config JSON doesn't exist, write the default config
    if not os.path.isfile(os.path.join(configDir, mainConfigJSONFileName)):
        return writeToMainConfigJSON(defaultConfig)

def updateMainConfig(key: str, data: any):
    # Set the key in the config dictionary with the data provided and proceed to write the new config to the main config JSON
    config[key] = data
    writeToMainConfigJSON(config)

def removeConfigDir():
    rmtree(configDir)

class Metadata:
    def __init__(self, mutagen_metadata: dict):
        # Reset title and album attributes
        self.title = None
        self.album = None

        # If the title TIT2 exists in the metadata dictionary, set the title to the text from that dictionary and likewise for TALB corresponding to album title
        if "TIT2" in mutagen_metadata:
            self.title = mutagen_metadata["TIT2"].text[0]
        if "TALB" in mutagen_metadata:
            self.album = mutagen_metadata["TALB"].text[0]
