#
#   lib.py
#   Miscellaneous functions
#

import os
from typing import Union, List

def get_execpath() -> str:
    return os.path.dirname(os.path.realpath(__file__))

def get_resourcepath(resourceName: str, execpath: str) -> str:
    return os.path.join(os.path.dirname(execpath), "resources", resourceName)

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

def get_admin_status() -> bool:
    import ctypes
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin != 0

    return is_admin

def importKeyboard(is_admin: bool) -> any:
    if is_admin:
        import keyboard
        return keyboard
