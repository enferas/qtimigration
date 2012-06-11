#!/usr/bin/env python

import pyslet.info as info
import pyslet.imscpv1p2 as cp
import pyslet.imsqtiv1p2p1 as qti1
import pyslet.imsqtiv2p1 as qti2
import pyslet.rfc2396 as uri
import pyslet.iso8601 as iso

import wx
import traceback
import os.path
import sys
import string

QTIMIGRATION_NAME="QTI Migration Tool"
QTIMIGRATION_VERSION="2.0"
QTIMIGRATION_BUILD="2.0.20120605"
QTIMIGRATION_HOME="http://code.google.com/p/qtimigration/"
QTIMIGRATION_DOCS="http://code.google.com/p/qtimigration/wiki/Home"
QTIMIGRATION_COPYRIGHT="""Copyright (c) 2011-2012, Steve Lay.
Adapted from code Copyright (c) 2004 - 2008, University of Cambridge.
Incorporating GUI Code Copyright (c) 2004 - 2008, Pierre Gorissen.
All Rights Reserved"""


class ResourceController:
	
	def __init__(self,resource,logs):
		self.resource=resource		#: the cp.Resource instance
		self.logs=logs
		
	def GetID(self):
		if self.resource.id:
			return self.resource.id
		else:
			return EMPTY
	
	def GetType(self):
		if self.resource.type:
			return self.resource.type
		else:
			return EMPTY
	
	def GetHREF(self):
		if self.resource.href:
			return str(self.resource.href)
		else:
			return EMPTY

	def GetWarnings(self):
		if self.logs[0]:
			return self.logs[0]
		else:
			return ""

	def GetErrors(self):
		if self.logs[1]:
			return self.logs[1]
		else:
			return ""


class FileController:
	
	def __init__(self,relPath,fullPath,fileElement):
		self.relPath=relPath		#: the package relative file path
		self.fullPath=fullPath		#: the operating system absolute path
		self.file=fileElement		#: the cp.File instance

	def GetPath(self):
		return self.relPath
	
	def GetMissing(self):
		return not os.path.exists(self.fullPath)
	
	def GetResourceID(self):
		if self.file:
			resource=self.file.parent
			if resource and resource.id:
				return resource.id				
		return EMPTY


class MainController:

	def __init__(self):
		self.pkg=cp.ContentPackage()
		self.xmlTypes={".xml":True}
		self.migrationLogs={}
		
	def GetPackageName(self):
		return self.pkg.GetPackageName()
	
	def GetItems(self):
		return [['1','Hello World','Resource: X',True]]
	
	def GetResources(self):
		resources=[]
		for r in self.pkg.manifest.root.Resources.Resource:
			resources.append(ResourceController(r,self.migrationLogs.get(r.id,('',''))))
		return resources
		
	def GetFiles(self):
		files=[]
		for fPath in self.pkg.fileTable.keys():
			osPath=os.path.join(self.pkg.dPath,fPath)
			fList=self.pkg.fileTable[fPath]
			if fList:
				for f in fList:
					files.append(FileController(fPath,osPath,f))
			else:
				files.append(FileController(fPath,osPath,None))			
		return files
		
	def Import(self,fPath):
		result=[]
		if os.path.isdir(fPath):
			os.path.walk(fPath,self.SearchQTIv1,result)
		else:
			head,tail=os.path.split(fPath)
			self.SearchQTIv1(result,head,[tail])
		if len(result):
			for fName,fPath,doc in result:
				self.Log("Importing: %s"%fPath)
				try:
					results=doc.MigrateV2(self.pkg)
					for doc,metadata,log,resource in results:
						if isinstance(doc.root,qti2.QTIAssessmentItem):
							self.Log("Found AssessmentItem: %s"%doc.root.identifier)
						else:
							self.Log("Found <%s>"%doc.root.xmlname)
						if log:
							errorList=[]
							warnList=[]
							for line in log:
								if line.lower().startswith("warning"):
									warnList.append(line)
								else:
									errorList.append(line)
								self.Log("\t%s"%line)
							self.migrationLogs[resource.id]=(string.join(warnList,'\n'),string.join(errorList,'\n'))
				except:
					self.LogException()
					
					
		return len(result)

	def SearchQTIv1(self,result,dirname,names):
		"""Search function called by walk to identify and load QTIv1 files."""
		for fName in names:
			stem,ext=os.path.splitext(fName)
			fPath=os.path.join(dirname,fName)
			if os.path.isfile(fPath) and self.xmlTypes.has_key(ext.lower()):
				self.Log("Examining file: %s"%fPath)
				doc=self.LoadQTIv1(fPath)
				if doc is not None:
					# success; add the file name to result
					result.append((fName,fPath,doc))
	
	def LoadQTIv1(self,fPath):
		"""Loads a QTI v1 file from the given file path."""
		doc=qti1.QTIDocument(baseURI=str(uri.URIFactory.URLFromPathname(fPath)))
		try:
			doc.Read()
		except:
			self.LogException()
		if isinstance(doc.root,qti1.QTIQuesTestInterop):
			return doc
		else:
			return None

	def Export(self,fPath):
		if os.path.exists(fPath):
			if not os.path.isfile(fPath):
				raise ValueError("Can't overwrite a directory or special file")
		try:
			self.pkg.ExportToPIF(fPath)
			return True
		except imscp.CPException:
			self.LogException()
			return False
		except IOError,e:
			self.LogException()
			return False
		
	def Close(self):
		if self.pkg:
			self.pkg.Close()

	def Log(self,msg):
		print msg
	
	def LogException(self):
		now=iso.TimePoint()
		now.Now()
		e=str(sys.exc_info()[1])
		if e:
			e="%s::%s"%(str(sys.exc_info()[0]),e)
		else:
			e=str(sys.exc_info()[0])
		self.Log("%s::ERROR::"%str(now)+e) 
		self.Log(string.join(traceback.format_tb(sys.exc_info()[2]),'\n'))


# Constants used for awkward unicode characters
UP_TRIANGLE=u"\u25B2"
DOWN_TRIANGLE=u"\u25BC"
CHECK_MARK=u"\u2713"
CROSS_MARK=u"\u2717"
EMPTY=u"\u2205"
BLACK_CIRCLE=u"\u25CF"

class QTIMigrationWX(wx.Frame):
	def __init__(self, parent):
		wx.Frame.__init__(self, parent, title="QTIMigration WX", size=(640,480), pos=(30,30))
		#self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
		# A Statusbar in the bottom of the window
		self.CreateStatusBar()
		# Setting up the menu.
		filemenu=wx.Menu()
		helpmenu=wx.Menu()
		# wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets.
		menuAbout=helpmenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
		menuDocs=helpmenu.Append(wx.NewId(),"Documentation")
		menuHome=helpmenu.Append(wx.NewId(),"QTI Migration Home")
		menuImport=filemenu.Append(wx.NewId(),"Import File...")
		menuImportDir=filemenu.Append(wx.NewId(),"Import Multiple...")
		filemenu.AppendSeparator()
		menuShowDetails=filemenu.Append(wx.NewId(),"Show Details")
		menuShowLog=filemenu.Append(wx.NewId(),"Show Activity Log")
		filemenu.AppendSeparator()
		menuExport=filemenu.Append(wx.NewId(),"Export to PIF...")
		menuExit=filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
		# Creating the menubar.
		menuBar = wx.MenuBar()
		menuBar.Append(filemenu,"&File")
		menuBar.Append(helpmenu,"&Help")
		self.SetMenuBar(menuBar)
		self.controller=MainController()
		self.pages=wx.Notebook(self,wx.ID_ANY)	
		# self.itemList=ItemPanel(self.pages,self)
		self.resourceList=ResourcePanel(self.pages,self)
		self.fileList=FilePanel(self.pages,self)
		# self.pages.AddPage(self.itemList,"Items")
		self.pages.AddPage(self.resourceList,"Resources")
		self.pages.AddPage(self.fileList,"Files")
		self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
		self.Bind(wx.EVT_MENU, self.OnDocumentation, menuDocs)
		self.Bind(wx.EVT_MENU, self.OnHome, menuHome)
		self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
		self.Bind(wx.EVT_MENU, self.OnImport,menuImport)
		self.Bind(wx.EVT_MENU, self.OnImportDir,menuImportDir)
		self.Bind(wx.EVT_MENU, self.OnShowDetails,menuShowDetails)
		self.Bind(wx.EVT_MENU, self.OnShowLog,menuShowLog)
		self.Bind(wx.EVT_MENU, self.OnExport,menuExport)
		self.Show(True)
		self.UpdateStatus()
		self.UpdateLists()
		wx.GetApp().SetOutputWindowAttributes(title="Activity Log",size=(640,300),pos=(100,100))
		self.OnShowLog(None)
		
	def UpdateStatus(self):
		pName=self.controller.GetPackageName()
		self.SetStatusText("%s: Ready"%pName)
		self.SetTitle(pName)
	
	def UpdateLists(self):
		# self.itemList.list.Update()
		self.resourceList.list.Update()
		self.fileList.list.Update()

	def OnImport(self,event):
		dialog = wx.FileDialog (self,message = "Select file to import...", style = wx.FD_OPEN)
		if dialog.ShowModal()==wx.ID_OK:
			fPath=dialog.GetPath()
		else:
			fPath=None
		dialog.Destroy()
		if fPath:
			self.SetStatusText("Importing %s"%fPath)
			self.controller.Import(fPath)
			self.UpdateLists()
			self.UpdateStatus()

	def OnImportDir(self,event):
		dialog = wx.DirDialog (self,message = "Select a directory to scan for imports...", style = wx.DD_DIR_MUST_EXIST)
		if dialog.ShowModal()==wx.ID_OK:
			dPath=dialog.GetPath()
		else:
			dPath=None
		dialog.Destroy()
		if dPath:
			self.SetStatusText("Importing all files from %s"%dPath)
			self.controller.Import(dPath)
			self.UpdateLists()
			self.UpdateStatus()

	def OnShowDetails(self,event):
		if self.pages.GetCurrentPage() is self.resourceList:
			self.resourceList.ShowDetails()
		else:
			pass
	
	def OnShowLog(self,event):
		wx.GetApp().RedirectStdio()
		print "Application logs will appear here:\n"
	
	def OnExport(self,event):
		filterStr="%s.zip"%self.controller.GetPackageName()
		dialog = wx.FileDialog (self,message = "Save exported PIF file as...",defaultFile=filterStr,
			style = wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT|wx.FD_CHANGE_DIR)
		if dialog.ShowModal()==wx.ID_OK:
			fPath=dialog.GetPath()
		else:
			fPath=None
		dialog.Destroy()
		if fPath:
			self.controller.Export(fPath)
		
	def OnHome (self,event):
		wx.LaunchDefaultBrowser(QTIMIGRATION_HOME)
	
	def OnDocumentation(self,event):
		wx.LaunchDefaultBrowser(QTIMIGRATION_DOCS)
		
	def OnAbout (self,event):
		description="""QTIMigration %s
%s
		
A tool for migrating content from IMS QTI 1.x to 2.1

Incorporating %s version %s
%s

Built with wxPython %s"""%(QTIMIGRATION_BUILD,QTIMIGRATION_HOME,info.name,info.version,info.home,wx.version())
		about=wx.AboutDialogInfo()
		about.SetName(QTIMIGRATION_NAME)
		about.SetVersion(QTIMIGRATION_VERSION)
		about.SetDescription(description)
		about.SetCopyright(QTIMIGRATION_COPYRIGHT)
		# about.SetWebSite(QTIMIGRATION_HOME)
		# about.SetLicense("See README file for licensing information")
		about.AddDeveloper("Steve Lay")
		wx.AboutBox(about)

	def OnExit(self,event):
		self.controller.Close()
		self.Close(1)


class ItemPanel(wx.Panel):

	def __init__(self,parent,mainView):
		self.mainView=mainView
		self.controller=mainView.controller
 		wx.Panel.__init__(self,parent,wx.ID_ANY)
 		self.list=ItemList(self,self.mainView)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizerH = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.list, 1, wx.ALL|wx.EXPAND, 5)
		sizer.Add(sizerH,0,wx.ALL|wx.EXPAND,5)
		self.SetSizer(sizer)


class ResourcePanel(wx.Panel):

	def __init__(self,parent,mainView):
		self.mainView=mainView
		self.controller=mainView.controller
 		wx.Panel.__init__(self,parent,wx.ID_ANY)
 		self.list=ResourceList(self,self.mainView)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizerH = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.list, 1, wx.ALL|wx.EXPAND, 5)
		sizer.Add(sizerH,0,wx.ALL|wx.EXPAND,5)
		self.SetSizer(sizer)

	def ShowDetails(self):
		self.list.ShowDetails()

		
class FilePanel(wx.Panel):

	def __init__(self,parent,mainView):
		self.mainView=mainView
		self.controller=mainView.controller
 		wx.Panel.__init__(self,parent,wx.ID_ANY)
 		self.list=FileList(self,self.mainView)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizerH = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.list, 1, wx.ALL|wx.EXPAND, 5)
		sizer.Add(sizerH,0,wx.ALL|wx.EXPAND,5)
		self.SetSizer(sizer)


class PanelList(wx.ListCtrl):
	HEADERS=[]
	
	def __init__(self,parent,mainView):
		self.mainView=mainView
		self.controller=mainView.controller
		wx.ListCtrl.__init__(self,parent,size=(-1,100),style=wx.LC_REPORT|wx.BORDER_SUNKEN|wx.LC_VIRTUAL|wx.LC_SINGLE_SEL)
		self.sorting=[]
		self.selection=0
		self.Bind(wx.EVT_LIST_COL_CLICK,self.OnSort)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED,self.OnSelect)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED,self.OnDeselect)
		self.Bind(wx.EVT_LIST_KEY_DOWN,self.OnKey)
		
	def OnSelect(self,event):
		self.selection=event.GetIndex()
		
	def OnDeselect(self,event):
		self.selection=-1
		
	def OnKey(self,event):
		key=event.GetKeyCode()
		if key in (wx.WXK_DELETE,wx.WXK_BACK):
			self.DeleteSelection()
		else:
			event.Skip()

	def DeleteSelection(self):
		pass
		
	def OnSort(self,event):
		column=event.GetColumn()
		c,d=self.sorting[0]
		if c==column:
			# reverse the direction of sort and we're done
			self.sorting[0]=(c,-d)
		elif column>=0:
			# remove any previous sorting
			for i in xrange(len(self.sorting)):
				c,d=self.sorting[i]
				if c==column:
					del self.sorting[i]
					break
			# and sort by this column ascending
			self.sorting=[(column,1)]+self.sorting
		# Now set the column headings
		self.SetColumnHeads()
		self.Update()	
	
	def SetColumnHeads(self):
		c,d=self.sorting[0]
		if d<0:
			sortIcon=DOWN_TRIANGLE
		else:
			sortIcon=UP_TRIANGLE
		for i in xrange(len(self.HEADERS)):
			colInfo=self.GetColumn(i)
			if c==i:
				colInfo.SetText("%s %s"%(self.HEADERS[i],sortIcon))
			else:
				colInfo.SetText(self.HEADERS[i])
			self.SetColumn(i,colInfo)


class ItemList(PanelList):
	HEADERS=['ID','Title','Target','Visible']
	
	def __init__(self,parent,mainView):
		PanelList.__init__(self,parent,mainView)
		self.InsertColumn(0, "1", width=150)
		self.InsertColumn(1, "2", width=210)
		self.InsertColumn(2, "3", width=200)
 		self.InsertColumn(3, "4",wx.LIST_FORMAT_CENTER, width=50)
 		self.items=[]
		self.sorting=[(0,-1)]
		self.SetColumnHeads()
		self.Update()

	def OnGetItemText(self,row,column):
		item=self.items[row]
		if column==3:
			return CHECK_MARK if item[3] else CROSS_MARK
		elif column>=0 and column<3:
			return item[column]
		else:
			return ""

	def Update(self):
		self.items=self.controller.GetItems()
		self.items.sort(lambda a,b:self.CompareItems(a,b))
		self.SetItemCount(len(self.items))

	def CompareItems(self,itemA,itemB):
		result=0
		for c,d in self.sorting:
			result=cmp(itemA[c],itemB[c])
			result=d*result
			if result:
				break
		return result


class ResourceList(PanelList):
	HEADERS=['ID','Type','Entry Point','Warnings','Errors']
	
	def __init__(self,parent,mainView):
		PanelList.__init__(self,parent,mainView)
		self.InsertColumn(0, "1", width=145)
		self.InsertColumn(1, "2", width=140)
		self.InsertColumn(2, "3", width=205)
		self.InsertColumn(3, "4", wx.LIST_FORMAT_CENTER, width=60)
		self.InsertColumn(4, "5", wx.LIST_FORMAT_CENTER, width=60)
 		self.resources=[]
 		self.details={}		#: a mapping from resource ID to window showing the details
		self.sorting=[(0,-1)]
		self.SetColumnHeads()
		self.Update()
		
	def OnGetItemText(self,row,column):
		resource=self.resources[row]
		return self.GetItemText(resource,column)
				
	def Update(self):
		self.resources=self.controller.GetResources()
		self.resources.sort(lambda a,b:self.CompareResources(a,b))
		self.SetItemCount(len(self.resources))
		# now remove any defunct windows
		idTable={}
		for r in self.resources:
			id=r.GetID()
			if id:
				idTable[id]=True
		for id in self.details.keys():
			if not idTable.has_key(id):
				# We need to remove this defunct window
				self.details[id].Destroy()
				del details[id]
				
	def ShowDetails(self):
		if self.selection>=0:
			r=self.resources[self.selection]
			id=r.GetID()
			# Note that a window that is in the table but has been closed behaves as per None
			if self.details.get(id,None):
				self.details[id].Raise()
			else:
				self.details[r.GetID()]=ResourceDetails(r,self.mainView)
			
	def CompareResources(self,resourceA,resourceB):
		result=0
		for c,d in self.sorting:
			result=cmp(self.GetItemText(resourceA,c),self.GetItemText(resourceB,c))
			result=d*result
			if result:
				break
		return result

	def GetItemText(self,resource,column):
		if column==0:
			return resource.GetID()
		elif column==1:
			return resource.GetType()
		elif column==2:
			return resource.GetHREF()
		elif column==3:
			if resource.GetWarnings():
				return BLACK_CIRCLE
			else:
				return ""
		elif column==4:
			if resource.GetErrors():
				return UP_TRIANGLE
			else:
				return ""
		else:
			return ""


class ResourceDetails(wx.Frame):
	"""We simply derive a new class of Frame. """
	def __init__(self, resource, mainView):
		self.mainView=mainView
		self.resource=resource
		titleStr="Resource: %s"%self.resource.GetID()
		wx.Frame.__init__(self, None, title=titleStr, size=(700,300))
		sizerV = wx.BoxSizer(wx.VERTICAL)
		sizerG=wx.FlexGridSizer(2,2)
		eTxt=self.resource.GetErrors()
		if not eTxt:
			eTxt="None"
		errors=wx.StaticText(self,wx.ID_ANY,"Errors: ")
		errorsValue=wx.StaticText(self,wx.ID_ANY,eTxt)
		wTxt=self.resource.GetWarnings()
		if not wTxt:
			wTxt="None"		
		warnings=wx.StaticText(self,wx.ID_ANY,"Warnings: ")
		warningsValue=wx.StaticText(self,wx.ID_ANY,wTxt)
		sizerG.Add(errors, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
		sizerG.Add(errorsValue, 1, wx.ALL|wx.ALIGN_LEFT|wx.EXPAND, 5)
		sizerG.Add(warnings, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
		sizerG.Add(warningsValue, 1, wx.ALL|wx.ALIGN_LEFT|wx.EXPAND, 5)
		sizerG.AddGrowableCol(1,1)
		sizerV.Add(sizerG, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER, 5)
		# self.textValue=wx.TextCtrl(self,wx.ID_ANY,project.text,style=wx.TE_MULTILINE)
		# sizerV.Add(self.textValue, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER, 5)
		# sizerV.Add(btnSizer, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
		self.SetSizer(sizerV)	
   		self.Show(True)


class FileList(PanelList):
	HEADERS=['Path','Present','Resource']
	
	def __init__(self,parent,mainView):
		PanelList.__init__(self,parent,mainView)
		self.InsertColumn(0, "1", width=260)
		self.InsertColumn(1, "2", wx.LIST_FORMAT_CENTER, width=90)
		self.InsertColumn(2, "3", width=260)
 		self.files=[]
		self.sorting=[(0,-1)]
		self.SetColumnHeads()
		self.Update()

	def OnGetItemText(self,row,column):
		f=self.files[row]
		return self.GetItemText(f,column)
				
	def Update(self):
		self.files=self.controller.GetFiles()
		self.files.sort(lambda a,b:self.CompareFiles(a,b))
		self.SetItemCount(len(self.files))

	def CompareFiles(self,fileA,fileB):
		result=0
		for c,d in self.sorting:
			result=cmp(self.GetItemText(fileA,c),self.GetItemText(fileB,c))
			result=d*result
			if result:
				break
		return result

	def GetItemText(self,f,column):
		if column==0:
			return f.GetPath()
		elif column==1:
			return CROSS_MARK if f.GetMissing() else CHECK_MARK
		elif column==2:
			return f.GetResourceID()
		else:
			return ""



if __name__=="__main__":
	# Create a new app, don't redirect stdout/stderr to a window.
	app = wx.App(False)
	# A Frame is a top-level window.
	mainWindow=QTIMigrationWX(None)
	app.MainLoop()

