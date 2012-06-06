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

QTIMIGRATION_NAME="QTI Migration Tool"
QTIMIGRATION_VERSION="2.0"
QTIMIGRATION_BUILD="2.0.20120605"
QTIMIGRATION_HOME="http://code.google.com/p/qtimigration/"
QTIMIGRATION_DOCS="http://code.google.com/p/qtimigration/wiki/Home"
QTIMIGRATION_COPYRIGHT="""Copyright (c) 2011-2012, Steve Lay.
Adapted from code Copyright (c) 2004 - 2008, University of Cambridge.
Incorporating GUI Code Copyright (c) 2004 - 2008, Pierre Gorissen.
All Rights Reserved"""

class MainController:

	def __init__(self):
		self.pkg=cp.ContentPackage()
		self.xmlTypes={".xml":True}
		
	def GetPackageName(self):
		return self.pkg.GetPackageName()
	
	def GetItems(self):
		return [['1','Hello World','Resource: X',True]]
	
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
					for doc,metadata,log in results:
						if isinstance(doc.root,qti2.QTIAssessmentItem):
							self.Log("Found AssessmentItem: %s"%doc.root.identifier)
						else:
							self.Log("Found <%s>"%doc.root.xmlname)
						for line in log:
							self.Log("\t%s"%line)
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
		self.Log(traceback.format_tb(sys.exc_info()[2]))


# Constants used for awkward unicode characters
UP_TRIANGLE=u"\u25B2"
DOWN_TRIANGLE=u"\u25BC"
CHECK_MARK=u"\u2713"
CROSS_MARK=u"\u2717"


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
		filemenu.AppendSeparator()
		menuExit=filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
		# Creating the menubar.
		menuBar = wx.MenuBar()
		menuBar.Append(filemenu,"&File")
		menuBar.Append(helpmenu,"&Help")
		self.SetMenuBar(menuBar)
		self.controller=MainController()
		self.pages=wx.Notebook(self,wx.ID_ANY)			
		self.itemList=ItemPanel(self.pages,self)
		#self.resourceList=ResourcePanel(self.pages,self)
		self.resourceList=ItemPanel(self.pages,self)
		#self.fileList=FilePanel(self.pages,self)
		self.fileList=ItemPanel(self.pages,self)
		self.pages.AddPage(self.itemList,"Items")
		self.pages.AddPage(self.resourceList,"Resources")
		self.pages.AddPage(self.fileList,"Files")
		self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
		self.Bind(wx.EVT_MENU, self.OnDocumentation, menuDocs)
		self.Bind(wx.EVT_MENU, self.OnHome, menuHome)
		self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
		self.Bind(wx.EVT_MENU, self.OnImport,menuImport)
		self.Show(True)
		self.UpdateStatus()
		self.UpdateLists()
					
	def UpdateStatus(self):
		pName=self.controller.GetPackageName()
		self.SetStatusText("%s: Ready"%pName)
		self.SetTitle(pName)
	
	def UpdateLists(self):
		self.itemList.list.Update()
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

	def CompareEntries(self,itemA,itemB):
		result=0
		for c,d in self.sorting:
			result=cmp(itemA[c],itemB[c])
			result=d*result
			if result:
				break
		return result




if __name__=="__main__":
	# Create a new app, don't redirect stdout/stderr to a window.
	app = wx.App(False)
	# A Frame is a top-level window.
	mainWindow=QTIMigrationWX(None)
	app.MainLoop()

