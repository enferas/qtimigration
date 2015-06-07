## Downloading and Installing ##

This page contains information about downloading and installing the migration tool.  Once you have done this, move on to [Getting Started](MigGettingStarted.md).

### Windows ###

Users of Windows should download the Windows installer executable (.exe) featured in the [downloads section of the site](http://code.google.com/p/qtimigration/downloads/list).  The installer works in the usual way and will install the QTI Migration Tool executable and supporting files.

#### Troubleshooting the Windows Installation ####

The Windows installer is missing an important DLL (due to a licensing issue).  In most cases, this DLL will already be on your system and you won't have a problem but if you do have an unexpected problem running the tool you may need to download and install the [Microsoft Visual C++ 2008 Redistributable Package (x86)](http://www.microsoft.com/downloads/en/details.aspx?FamilyID=9b2da534-3e03-4391-8a4d-074b9f2bc1bf&displaylang=en).

### Mac OS X ###

Users of Mac OS X should download the Mac OS X disk image file (.dmg) featured in the [downloads section of the site](http://code.google.com/p/qtimigration/downloads/list).

The disk image contains the QTI Migration Tool application which can be dropped into the Applications folder in the normal way.

### Source Package (all other platforms) ###

Other UNIX-based platforms should use the source distribution instead by downloading the QTIMigrationTool tgz package featured in [downloads section of the site](http://code.google.com/p/qtimigration/downloads/list).  (You can use the source package on Mac and Windows-based systems too, Windows users may find the [FAQ on running python programs under Windows](http://docs.python.org/faq/windows#how-do-i-run-a-python-program-under-windows) useful.)

The tool is written in the [Python programming language](http://www.python.org/).  In most cases you'll already have python installed but if not, download and install the latest Python 2.7 from the main python website.  (The migration tool should work just fine with newer versions of Python 2, however it is not compatible with Python 3 at this point.)

Once you have python installed you will need to install some additional packages.  If you are not sure if you already have a package and/or what version you already have installed you can use the python interpreter to tell you.  Start the python interpreter (e.g., by typing 'python' at the terminal prompt) and the use a command like this:

```
>>> import pkg_resources
>>> pkg_resources.get_distribution("wxPython").version
'2.8.12.0'
```

In this case we asked the interpreter for the installed version of the wxPython package.  (The '>>>' is the python interpreter's prompt by the way.)  If you get an error ending in something like: `pkg_resources.DistributionNotFound` then the package in question isn't installed yet.  Although less likely, you may get an error when typing the first command `import pkg_resources`, if you do then you need to install setuptools too (the first one in the list below).

The list of packages you need, and the suggested order to install them, is given here (each one links to the place you need to download the package from):

  1. [setuptools](http://pypi.python.org/pypi/setuptools)
  1. [python-dateutil](http://pypi.python.org/pypi/python-dateutil/1.5)
  1. [vobject](http://pypi.python.org/pypi/vobject/0.8.1c)
  1. [oauth](http://pypi.python.org/pypi/oauth/1.0.1)
  1. [pyslet](http://code.google.com/p/qtimigration/downloads/list) - available from the QTIMigration website
  1. [wxPython](http://wxpython.org/) - (optional, but required if you want to use the graphical user interface: use the latest stable 2.8 release.)

If you have to install setuptools yourself, follow the instructions given.  Likewise when installing wxPython you'll need to choose an appropriate download for your system and follow the instructions given on the wxPython website.  For all the other modules you can just download the source in the form of a compressed tar archive; expand it to a directory on your computer, change to the package's directory and type the following command at the terminal:

`python setup.py install`

Once you have all the prerequisites installed you can navigate to the directory you expanded the migration tool itself into and simple type the command:

`python migrate.py`

If you have installed wxPython then the tool will start the graphical user interface, otherwise it will run in command-line mode.  In the latter case, it will print a brief message to the console and exit.  For a brief summary of the available options pass "--help" when launching:

`python migrate.py --help`


---


Now move on to [Getting Started](MigGettingStarted.md).