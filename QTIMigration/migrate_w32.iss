[Setup]
InternalCompressLevel=max
VersionInfoVersion=1.9.20110609
VersionInfoDescription=QTI Migration Tool for QTI 1.2.1 to 2.1
AppCopyright=University of Camebridge
AppName=IMS QTI Migration tool
AppVerName=IMS QTI Migration tool GUI
DisableDirPage=false
DefaultDirName={pf}\MigrationTool
DefaultGroupName=IMS QTI migration Tool
AlwaysShowComponentsList=false
ShowLanguageDialog=no
Uninstallable=true
CreateUninstallRegKey=true
UninstallDisplayIcon={app}\uninstall.ico
UninstallDisplayName=IMS QTI Migration Tool (remove only)
SolidCompression=true
Compression=bzip
DontMergeDuplicateFiles=true
DisableProgramGroupPage=true
LicenseFile=LICENSE.txt
[UninstallDelete]
Name: {app}; Type: filesandordirs
[Icons]
Name: {group}\Read Me!; Filename: {app}\README.txt; IconFilename: {app}\readme.ico; IconIndex: 0
Name: {group}\Migrate QTIv1.2 to QTIv2; Filename: {app}\migrate.exe; WorkingDir: {app}; IconFilename: {app}\migrate.exe; IconIndex: 0
[Run]
Filename: {app}\readme.txt; Description: Show Readme File; Flags: postinstall shellexec; WorkingDir: {app}
[Files]
Source: dist\bz2.pyd; DestDir: {app}
Source: dist\Splash.bmp; DestDir: {app}
Source: dist\library.zip; DestDir: {app}
Source: dist\migrate.exe; DestDir: {app}
Source: dist\pyexpat.pyd; DestDir: {app}
Source: dist\python27.dll; DestDir: {app}
Source: dist\select.pyd; DestDir: {app}
Source: dist\unicodedata.pyd; DestDir: {app}
Source: dist\w9xpopen.exe; DestDir: {app}
Source: dist\wx._controls_.pyd; DestDir: {app}
Source: dist\wx._core_.pyd; DestDir: {app}
Source: dist\wx._gdi_.pyd; DestDir: {app}
Source: dist\wx._misc_.pyd; DestDir: {app}
Source: dist\wx._windows_.pyd; DestDir: {app}
Source: dist\wxbase28uh_net_vc.dll; DestDir: {app}
Source: dist\wxbase28uh_vc.dll; DestDir: {app}
Source: dist\wxmsw28uh_adv_vc.dll; DestDir: {app}
Source: dist\wxmsw28uh_core_vc.dll; DestDir: {app}
Source: dist\wxmsw28uh_html_vc.dll; DestDir: {app}
Source: dist\_hashlib.pyd; DestDir: {app}
Source: dist\_socket.pyd; DestDir: {app}
Source: dist\_ssl.pyd; DestDir: {app}
Source: README.txt; DestDir: {app}
Source: readme.ico; DestDir: {app}
