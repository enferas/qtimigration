## Getting Started ##

Firstly, follow the instructions for [downloading and installing](QTIMigInstall.md) the tool for your platform.

When you launch the migration tool you'll see a splash screen with the tool's icon and then a simple file/folder selection dialog.

To start with, use the "Single QTI v1.2 File" part of the dialog to browse for an input file from your disk.  In the screen shot I've selected mchc\_i\_001.xml, one of the basic examples from the standard set distributed with the [QTI v1.2 specification](http://www.imsglobal.org/question/).

![![](http://qtimigration.googlecode.com/svn/images/screen01thumb.png)](http://qtimigration.googlecode.com/svn/images/screen01.png)
(Click to see the full size screen shot.)

Next, click the "Convert..." button.  By default, the tool prints information about the conversion process to the machine console (shown in the background) but you can select "Show Output Log" under the File menu to open an application window to show the output instead (shown as the frontmost window).

> Warning: if you used the same example file I did the conversion will probably terminate with an error message:

> `IOError: [Errno 2] The system cannot find the file specified: 'ims_qtiasiv1p2.dtd'`

> This is because the basic example file from IMS makes reference to the schema (aka DTD) file but the schema file is missing from the example directory.  For now, locate the schema file in the package from IMS and copy it into the directory containing the example file.

Once you have the tool working you should see output like the following...

```
	Input: C:\dev\testdata\mchc_i_001.xml
	Processing file: C:\dev\testdata\mchc_i_001.xml
	Resolving: PUBLIC None SYSTEM ims_qtiasiv1p2.dtd
	Returning: ims_qtiasiv1p2.dtd
	-- Converting item id="IMS_V01_I_mchc_i_001" --
	Warning: found qticomment on a questestinterop with single item: treating as metadata for the item *not* the content package
	No output set. Parsing complete
```

The first two lines are self-explanatory.  The second two lines concern the process of locating the schema associated with the QTI file (see note above).  At this point, the conversion starts in earnest.  A single item is found in the file with an identifier of "IMS\_V01\_I\_mchc\_i\_001", the conversion generates a single warning about a comment element.  Finally, because no output folder has been set the conversion process terminates.  The status bar in the main dialog refers to this as a "dry run".

To actually see your output, create a new empty directory and use the "Select Directory..." part of the dialog to select it.  Click "Convert..." again and this time your output should end something like this:

```
	Parsing complete
	Writing manifest file: C:\dev\testoutput\imsmanifest.xml
	Writing file: C:\dev\testoutput\IMS_V01_I_mchc_i_001.xml
	Migration completed...
```

The conversion process writes _two_ files even though there is only a single item.  The output directory is treated as a content package, the first file is a manifest file required by the IMS Content Packaging format.  It contains references to the other files in the package.  The second file is the QTI v2 file containing the converted item.