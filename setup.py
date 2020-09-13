#
#   setup.py
#   Program to setup, build and run different automated tasks in the environment.
#

from setuptools import setup, find_packages, Command

import sys
import io
import os
from shutil import rmtree

# Package metadata
NAME = "QMusic"
DESCRIPTION = "A simple Python Qt application for audio playback."
URL = ""
EMAIL = "cd.wiggins@outlook.com"
AUTHOR = "C. Wiggins"
REQUIRES_PYTHON = ">=3.5.0"
VERSION = "0.1.0"
long_description = DESCRIPTION
about: dict

def get_execpath():
    return os.path.realpath(os.path.dirname(__file__))

def get_realpath(relativePath: str, execPath: str):
    return os.path.join(execPath, relativePath)

def get_buildname(srcfile: str):
    separated = srcfile.split(os.path.sep)
    fname = separated[len(separated) - 1]
    dotseparated = fname.split(".")
    ret = ""

    # Loop through array until extension is reached
    for i in range(len(dotseparated) - 1):
        ret += dotseparated[i]

    return ret

# Packages required for the module to be executed
required = [
    # "package"
]

# Optional packages for features
EXTRAS = {
    # "feature": ["package"]
}

execpath = get_execpath()

PATH_REQUIREMENTS = get_realpath("requirements.txt", execpath)
PATH_README = get_realpath("README.md", execpath)
PATH_VERSION = get_realpath("__version__.py", execpath)

interpreter = "python"
SRCDIR = get_realpath("src", execpath)
SRCFILE = os.path.join(SRCDIR, "main.py")
OUTDIR = get_realpath("dist", execpath)
OUTFILE = OUTDIR + os.path.sep + NAME
OUTAPP = OUTFILE + ".app"
BUILDNAME = get_buildname(SRCFILE)
BUILDDIR_PYTHON = get_realpath("build", execpath)
BUILDDIR_NUITKA = get_realpath(BUILDNAME + os.path.extsep + "build", execpath)
PYINSTALLER_SPEC = BUILDNAME + os.path.extsep + "spec"
RESOURCES = get_realpath("resources", execpath)
SCRIPTSDIR = get_realpath("scripts", execpath)

def get_interpreter():
    if sys.platform.startswith("darwin"):
        ret = "python3"
    else:
        ret = "python"

    return ret

def get_here():
    return os.path.abspath(os.path.dirname(__file__))

def get_requirements():
    here = get_here()
    required = []

    # Import requirements
    try:
        with io.open(os.path.join(here, PATH_REQUIREMENTS)) as f:
            required = f.read().split("\n")
    except FileNotFoundError:
        print("File \"%s\" not found. Exiting...", PATH_REQUIREMENTS)
    
    return required

def get_long_description():

    # Import the README.md as long description
    try:
        with open(PATH_README) as f:
            long_description = f.read()
    except FileNotFoundError:
        long_description = DESCRIPTION

    return long_description

def get_about():
    here = get_here()

    # Load the package"s __version__.py as a dictionary
    about = {}
    if not VERSION:
        with open(os.path.join(here, PATH_VERSION)) as f:
            exec(f.read(), about)
    else:
        about["__version__"] = VERSION

    return about

def run_py():
    os.system(interpreter + " " + SRCFILE)

def run_exec():
    os.system(OUTFILE)

def run_macos():
    os.system("open " + "\"OUTAPP\"")

def clean_build():
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
    fnames = os.listdir(get_here())
    
    for fname in fnames:
        if fname.lower().endswith(os.path.extsep + "egg-info"):
            path = os.path.join(get_here(), fname)
            if os.path.isdir(path):
                rmtree(path)

def clean_all():
    clean_build()
    clean_dist()
    clean_egginfo()

def makeapp():
    os.system(os.path.join(SCRIPTSDIR, "makeapp") + " \"" + OUTFILE + "\" -o \"" + OUTAPP + "\"")


# Custom commands
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
        None

    def run(self):
        if self.exec:
            run_exec()
        elif self.macos:
            run_macos()
        else:
            run_py()

class Compile(Command):
    description = "Compile executable"

    user_options = [
        ("macos", "m", "Build executable and create macOS application package")
    ]

    def initialize_options(self):
        self.macos = None

    def finalize_options(self):
        None

    def run(self):
        # os.system("nuitka3 "+SRCFILE+" -o "+OUTFILE+" --nofollow-imports")
        os.system("nuitka3 "+SRCFILE+" --follow-imports --standalone")
        # os.system("pyinstaller "+SRCFILE+" --onedir")
        
        if self.macos:
            makeapp()

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

class MakeApp(Command):
    description = "Create macOS application package"

    def run(self):
        makeapp()


long_description = get_long_description()
about = get_about()
required = get_requirements()
interpreter = get_interpreter()

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
        "compile": Compile,
        "makeapp": MakeApp,
        "clean": Clean
    }
)
