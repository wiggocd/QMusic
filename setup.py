#
#   setup.py
#   Program to setup, build and run different automated tasks in the environment with setuptools/distutils
#

#
#   Todo: add comments and look back over
#

from setuptools import setup, find_packages, Command
import sys
import os
from shutil import rmtree
import subprocess

# Package metadata, capitalised for constants
NAME = "QMusic"
DESCRIPTION = "A simple Python Qt application for audio playback."
URL = ""
EMAIL = "cd.wiggins@outlook.com"
AUTHOR = "C. Wiggins"
REQUIRES_PYTHON = ">=3.5.0"
VERSION = "0.1.0"
long_description = DESCRIPTION
about: dict
resourcesPath = "resources"
iconPath = os.path.join(resourcesPath, "icons", "icon_default.icns")

darwin = False
win32 = False
unix_other = False

def setOS():
    # Use sys.platform to derive OS details
    global darwin, win32, unix_other
    if sys.platform.startswith("darwin"):
        darwin = True
    elif sys.platform.startswith("win32"):
        win32 = True
    else:
        unix_other = True

setOS()

def get_execDir() -> str:
    # Return real path of the parent directory of this file
    return os.path.realpath(os.path.dirname(__file__))

def get_relativeToRealPath(relativePath: str, execDir: str) -> str:
    # Return the path of the relative path within the executable directory
    return os.path.join(execDir, relativePath)

def get_buildName(srcfile: str) -> str:
    # Separate the path from the parent directories, get the filename and separate the filename by the extension separator
    separated = srcfile.split(os.path.sep)
    fname = separated[len(separated) - 1]
    extSeparated = fname.split(os.path.extsep)
    ret = ""

    # Loop through array appending the filename parts to the return string until the real extension is reached
    for i in range(len(extSeparated) - 1):
        ret += extSeparated[i]
    
    # Return the final filename without its extension
    return ret

# Packages required for the module to be executed
required = [
    # "package"
]

# Optional packages for features
EXTRAS = {
    # "feature": ["package"]
}

# Get the current executable directory, set calculated paths to relative resources
execDir = get_execDir()

PATH_REQUIREMENTS = get_relativeToRealPath("requirements.txt", execDir)
PATH_README = get_relativeToRealPath("README.md", execDir)
PATH_VERSION = get_relativeToRealPath("__version__.py", execDir)

interpreter = "python"
SRCDIRNAME = get_relativeToRealPath("src", execDir)
mainScriptRelativePath = os.path.join(SRCDIRNAME, "main.py")
OUTDIR = get_relativeToRealPath("dist", execDir)
OUTFILE = OUTDIR + os.path.sep + NAME
OUTAPP = OUTFILE + ".app"
BUILDNAME = get_buildName(mainScriptRelativePath)
BUILDDIR_PYTHON = get_relativeToRealPath("build", execDir)
BUILDDIR_NUITKA = get_relativeToRealPath(BUILDNAME + os.path.extsep + "build", execDir)
PYINSTALLER_SPEC = BUILDNAME + os.path.extsep + "spec"
RESOURCES = get_relativeToRealPath("resources", execDir)
SCRIPTSDIR = get_relativeToRealPath("scripts", execDir)
linkScriptPath = "/usr/local/bin/qmusic"

def get_interpreter():
    # If the platform is macOS (darwin), use python3, otherwise use standard python and assume it's Python 3
    if darwin:
        ret = "python3"
    else:
        ret = "python"

    return ret

def get_requirements():
    # Import requirements, add the lines split by newline from the opened file to the return list
    required = []

    try:
        with open(get_relativeToRealPath(PATH_REQUIREMENTS, execDir), "r") as f:
            required = f.read().split("\n")
    except FileNotFoundError:
        print("File \"%s\" not found. Exiting...", PATH_REQUIREMENTS)
    
    return required

def get_long_description():
    # Import the README.md as long description by reading from disk, set the long description to the standard description if the file is not found
    try:
        with open(PATH_README, "r") as f:
            long_description = f.read()
    except FileNotFoundError:
        long_description = DESCRIPTION

    return long_description

def get_about():
    # Load the package"s __version__.py as a dictionary by using the exec method with the dictionary and open file read return
    about = {}
    if not VERSION:
        with open(get_relativeToRealPath(PATH_VERSION, execDir), "r") as f:
            exec(f.read(), about)
    else:
        about["__version__"] = VERSION

    return about

def run_py():
    # Run the python file with the interpreter using system
    os.system(interpreter + " \"" + mainScriptRelativePath + "\"")

def run_exec():
    # Run the executable
    os.system(OUTFILE)

def run_macos():
    # Use the darwin specific open shell command
    os.system("open " + "\"OUTAPP\"")

def clean_build():
    # rmtree on each of the build directories
    if os.path.isdir(BUILDDIR_PYTHON):
        rmtree(BUILDDIR_PYTHON)

    if os.path.isdir(BUILDDIR_NUITKA):
        rmtree(BUILDDIR_NUITKA)

    if os.path.isfile(PYINSTALLER_SPEC):
        os.remove(PYINSTALLER_SPEC)

def clean_dist():
    if os.path.isdir(OUTDIR):
        rmtree(OUTDIR)

def clean_egginfo():
    # For each filename from the listed contents of the executable directory, if the filename ends with the egg-info extension with separator, rmtree on that path
    fnames = os.listdir(execDir)
    
    for fname in fnames:
        if fname.lower().endswith(os.path.extsep + "egg-info"):
            path = get_relativeToRealPath(fname, execDir)
            if os.path.isdir(path):
                rmtree(path)

def clean_all():
    # Run all the clean functions
    clean_build()
    clean_dist()
    clean_egginfo()

def makeapp():
    # Run the concatenated path to the makeapp script and pass the executable and output path parameters
    os.system(os.path.join(SCRIPTSDIR, "makeapp") + " \"" + OUTFILE + "\" -o \"" + OUTAPP + "\"")

def generateLaunchScript():
    return """
    #!/bin/sh
    python """ + os.path.join(execDir, mainScriptRelativePath) + """
    """

#
#   Revise
#

def sudo():
    # Not working, for now we will just request the user to run sudo with the script for operations that require it
    
    # Use subprocess.call with shlex.split of "sudo id -nu" until the return is 0 and we have superuser

    sudo = 1
    attempts = 0

    while sudo != 0 and attempts < 3:
        subprocess.call(shlex.split("sudo id -nu"), stdout=os.devnull) != 0
        attempts += 1

    return sudo

def createLaunchScript():
    # sudo()

    # Open the path to the script for writing at write the link script, make the file executable with chmod
    with open(linkScriptPath, "w") as openFile:
        openFile.write(generateLinkScript())

    os.chmod(linkScriptPath, 755)

def removeLaunchScript():
    # sudo()

    # If the link script exists, remove it
    if os.path.isfile(linkScriptPath):
        os.remove(linkScriptPath)

#   Custom setup commands
#   For each extension of the Command class from setuptools, provide:
#       -   description
#       -   user_options list of tuples with names, shortcuts and descriptions
#       -   initialize_options and finalize_options
#       -   the main function: run, running the required functions

class Run(Command):
    description = "Run program"

    user_options = [
        ("interpreter", "i", "Run program from the Python interpreter"),
        ("exec", "e", "Run the built executable"),
        ("macos", "m", "Run the built macOS application package")
    ]

    def initialize_options(self):
        self.interpreter = None
        self.exec = None
        self.macos = None

    def finalize_options(self):
        ...

    def run(self):
        if self.exec:
            run_exec()
        elif self.macos:
            run_macos()
        else:
            run_py()

class Clean(Command):
    description = "Clean the build environment"

    user_options = [
        ("build", "b", "Clean only the build directories"),
        ("dist", "d", "Clean only the dist directory")
    ]

    def initialize_options(self):
        self.build = None
        self.dist = None

    def finalize_options(self):
        None

    def run(self):
        if self.build:
            clean_build()
        elif self.dist:
            clean_dist()
        else:
            clean_all()

class InstallUnix(Command):
    description = "Create or remove a script in /usr/bin as a link to launch your local copy of the application"

    user_options = [
        ("create", "c", "Create a script in /usr/bin as a link to launch your local copy of the application"),
        ("remove", "r", "Remove the launcher script")
    ]

    def initialize_options(self):
        self.create = None
        self.remove = None

    def finalize_options(self):
        ...

    def run(self):
        if not win32:
            if self.remove:
                removeLaunchScript()
            else:
                createLaunchScript()

class Compile(Command):
    description = "Compile executable"

    user_options = [
        ("macos", "m", "Build executable and create macOS application package")
    ]

    def initialize_options(self):
        self.macos = None

    def finalize_options(self):
        ...

    def run(self):
        # os.system("nuitka3 "+mainScriptRelativePath+" -o "+mainScriptRelativePath+" --follow-imports --standalone")
        # os.system("pyinstaller "+mainScriptRelativePath+" --onedir")
        
        if self.macos:
            makeapp()

class MakeApp(Command):
    description = "Create macOS application package"

    def run(self):
        makeapp()

long_description = get_long_description()
about = get_about()
required = get_requirements()
interpreter = get_interpreter()

# py2app/py2exe
APP = [mainScriptRelativePath]
DATA_FILES = []
OPTIONS = {
    "py2app": {
        "iconfile": iconPath
    }
}

# OS specific functions. For all Unix-like systems, import shlex for sudo. If Mac, use py2app in the setup with app, data files and options provided, otherwise if Windows, use py2exe with the app passed
if darwin:
    import shlex
    setup_requires=["py2app"]
elif win32:
    setup_requires=["py2exe"]
else:
    # Other/Unix
    import shlex

#   Call the setuptools main setup function with all metadata and commands passed as parameters:
#       - name, version, description, long description and content type, author details, url, included packages from find_packages, install_requires for pip packages, exxtras, classifiers and cmdclass for command options amongst others
if darwin or win32:
    setup(  
        name=NAME,
        version=about["__version__"],
        description=DESCRIPTION,
        long_description=long_description,
        long_description_content_type="text/markdown",
        author=AUTHOR,
        author_email=EMAIL,
        python_requires=REQUIRES_PYTHON,
        url=URL,
        packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
        install_requires=required,
        extras_require=EXTRAS,
        include_package_data=True,
        license="ISC",
        classifiers=[
            # Trove classifiers
            # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
            "License :: OSI Approved :: ISC License (ISCL)",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.5"
        ],
        cmdclass={
            "run": Run,
            "clean": Clean,
            "install_unix": InstallUnix,
            "compile": Compile,
            "makeapp": MakeApp,
        },
        app=APP,
        data_files=DATA_FILES,
        options=OPTIONS
    )
else:
    setup(  
        name=NAME,
        version=about["__version__"],
        description=DESCRIPTION,
        long_description=long_description,
        long_description_content_type="text/markdown",
        author=AUTHOR,
        author_email=EMAIL,
        python_requires=REQUIRES_PYTHON,
        url=URL,
        packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
        install_requires=required,
        extras_require=EXTRAS,
        include_package_data=True,
        license="ISC",
        classifiers=[
            # Trove classifiers
            # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
            "License :: OSI Approved :: ISC License (ISCL)",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.5"
        ],
        cmdclass={
            "run": Run,
            "clean": Clean,
            "install_unix": InstallUnix,
            "compile": Compile,
            "makeapp": MakeApp,
        }
    )
