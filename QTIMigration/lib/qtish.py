#! /usr/bin/env python

import cmd, getopt
import os, os.path, sys, urllib
from xml.sax import SAXException
import string

import pyslet.imscpv1p2 as imscp
import pyslet.imsqtiv1p2p1 as qti1
import pyslet.imsqtiv2p1 as qti2

VERSION="20110129"

BANNER="QTIMigration Shell version %s, Steve Lay, 2010"%VERSION
NEW_PACKAGE="new_package"
	
try:
	import readline
	print "Running with readline support..."
	readline.parse_and_bind("tab: complete")
except ImportError:
	pass

def OptionBoolean(valueStr):
	valueStr=valueStr.strip().lower()
	if valueStr in ['true','t','yes','1','on']:
		return True
	elif valueStr in ['false','f','no','0','off']:
		return False
	else:
		return None

def OptionString(valueStr):
	return valueStr

DEFAULT_OPTIONS={
	'searchzips':[OptionBoolean,False],
	'filemagic':[OptionBoolean,False],
	'xmltypes':[OptionString,".xml"],
	'ziptypes':[OptionString,".zip"]
	}

class QTIMigrationShell(cmd.Cmd):
	def __init__(self):
		cmd.Cmd.__init__(self)
		self.cp=imscp.ContentPackage()
		self.prompt="%s.%s$ "%(self.cp.GetPackageName(),self.cp.manifest.root.id)
		# paging controls
		self.ClearPages()
		self.pageSize=30
		# options and settings; very complex so use a dictionary
		self.options=DEFAULT_OPTIONS
		
	def ClearPages(self):
		self.header=[]
		self.list=[]
		self.pageNum=0
	
	def PrintException(self,e):
		print e
	
	def AutoFormat(self,heads,results):
		widths=[]
		for h in heads:
			widths.append(len(h))
		for r in results:
			for i in xrange(len(widths)):
				if len(r[i])>widths[i]:
					widths[i]=len(r[i])
		format=[]
		for i in xrange(len(widths)):
			if heads[i] and heads[i][0]==' ':
				format.append("%%%is"%widths[i])
			else:
				format.append("%%-%is"%widths[i])
		format=string.join(format,'  ')
		return format
		
	def PrintPage(self):
		if self.list:
			nPages=(len(self.list)-1)/self.pageSize+1
			if self.pageNum>=nPages:
				self.pageNum=nPages-1
			elif self.pageNum<0:
				self.pageNum=0
		else:
			nPages=0
			self.pageNum=0
		start=self.pageNum*self.pageSize
		for line in self.header:
			print line
		for line in self.list[start:start+self.pageSize]:
			print line
		if nPages>1:
			print ">>> Page %i of %i"%(self.pageNum+1,nPages)
			
	def do_n(self,args):
		self.do_next(args)
	
	def help_n(self):
		self.help_next()

	def do_next(self,args):
		self.pageNum=self.pageNum+1
		self.PrintPage()

	def help_next(self):
		print """n | next

View next page of output"""

	def do_b(self,args):
		self.do_back(args)
	
	def help_b(self):
		self.help_back()

	def do_back(self,args):
		self.pageNum=self.pageNum-1
		self.PrintPage()

	def help_back(self):
		print """b | back

View previous page of output"""

	def do_options(self,args):
		self.ClearPages()
		format="%-16s  %s"
		if self.options:
			self.header=["Current settings","",format%("Name","Value"),"-"*80]
			opts=self.options.keys()
			opts.sort()
			for opt in opts:
				self.list.append(format%(opt,self.options[opt][1]))
			self.PrintPage()
		else:
			print "No options available, sorry"
			
	def help_options(self):
		print """options

List all the current setting of all available options.  To change
the value of an option use the 'set' command."""

	def do_set(self,args):
		self.ClearPages()
		if self.options:
			args=args.split(' ',1)
			args[0]=args[0].strip().lower()
			if len(args)<2:
				args.append('True')
			else:
				args[1]=args[1].strip()
			optInfo=self.options.get(args[0],None)
			if optInfo is None:
				print "Unknown option: %s"%args[0]
			else:
				optValue=optInfo[0](args[1])
				if optValue is None:
					print "%s is not a valid setting for option %s"%(args[1],args[0])
				else:
					self.options[args[0]][1]=optValue
		else:
			print "No options available, sorry"
			
	def help_set(self):
		print """set <option> [value]

Sets the value of <option>.  If value is omitted it is assumed
to be "True"."""

	def do_pwd(self,args):
		self.ClearPages()
		print os.getcwd()

	def help_pwd(self):
		print """pwd

Print current working direcorty"""
	
	def do_cd(self,args):
		self.ClearPages()
		try:
			os.chdir(args)
			print "New working directory:\n%s"%os.getcwd()
		except OSError,e:
			self.PrintException(e)

	def help_cd(self):
		print """cd <path to new directory>

Change current working directory"""

	def do_ls(self,args):
		self.ClearPages()
		self.header=["Listing contents of: os.getcwd()","","%6s  %s"%(" Type ","Name"),"-"*80]
		for fname in os.listdir(os.getcwd()):
			if os.path.islink(fname):
				link='->'
				type="FILE"
			else:
				link='  '
				type="    "
			if os.path.isdir(fname):
				type="DIR "
			elif not os.path.isfile(fname):
				type="SYS "
			self.list.append("%6s  %s"%(link+type,fname))
		self.PrintPage()
		
	def help_ls(self):
		print """ls

List the contents of the current directory"""

	def do_open(self,args):
		self.ClearPages()
		if not os.path.exists(args):
			print "Warning: file or directory does not exist."
			reply=raw_input("Create a content package directory at %s? (Yes/No)> "%args)
			if reply.lower()!="yes"[0:len(reply)]:
				return			
		try:
			newCP=imscp.ContentPackage(args)
		except imscp.CPException,e:
			self.PrintException(e)			
		except IOError,e:
			self.PrintException(e)
		self.cp.Close()
		self.cp=newCP
		self.prompt="%s.%s$ "%(self.cp.GetPackageName(),self.cp.manifest.root.id)
	
	def help_open(self):
		print """open <path to PIF file, directory or manifest>

zip is the only format of PIF file supported.  The file is expanded to a temporary
working directory and will not be modified by other shell operations.

If you specify a directory it is worked on in place, a manifest file is created
automatically if it is missing.

If you specify a manifest file then the containing directory is treated as the
package directory and worked on in place."""

	def do_search(self,args):
		self.ClearPages()
		type=args.strip().lower()
		result=[]
		if type=="qti1":
			os.path.walk('.',self.SearchQTI1,result)
			heads=('File name','File Path')
			body=map(lambda x: x[0:2],result)
			format=self.AutoFormat(heads,body)
			heads=format%heads
			self.header=['Search of %s for QTI v1 data, restuls:'%os.getcwd(),heads,"-"*(len(heads))]
			for r in body:
				self.list.append(format%r)
			self.PrintPage()
		else:
			print "Unknown search type: %s"%type
		
	def SearchQTI1(self,result,dirname,names):
		# Search through names for QTI1 files
		filter=self.options['xmltypes'][1].split()
		for fName in names:
			stem,ext=os.path.splitext(fName)
			fPath=os.path.join(dirname,fName)
			if os.path.isfile(fPath) and ext.lower() in filter:
				doc=self.LoadQTI1(fPath)
				if doc is not None:
					# success; add the file name to result
					result.append((fName,fPath,doc))
	
	def help_search(self):
		print """search qti1

Performs a recursive search from the current directory looking for objects
that match the given search type.  For each object it prints information
about the location where it was found."""

	def do_import(self,args):
		self.ClearPages()
		result=[]
		fPath=args
		if os.path.isdir(fPath):
			os.path.walk(fPath,self.SearchQTI1,result)
		else:
			head,tail=os.path.split(fPath)
			self.SearchQTI1(result,head,[tail])
		if len(result)==0:
			print "No QTI v1 files found in %s"%fPath
		else:
			for fName,fPath,doc in result:
				print "Processing: %s"%fPath
				try:
					results=doc.MigrateV2(self.cp)
					for doc,metadata,log in results:
						if isinstance(doc.root,qti2.QTIAssessmentItem):
							print "AssessmentItem: %s"%doc.root.identifier
						else:
							print "<%s>"%doc.root.xmlname
						for line in log:
							print "\t%s"%line
				except:
					print "Unexpected error: %s (%s)\n%s"%sys.exc_info()
			
	def help_import(self,args):
		print """import <path to file or directory>

Imports QTI files into the current content package.  The current implementation
will only work for QTI version 1 files, on import, they are converted to QTI
version 2 before being added to the content package.

If the argument is the path to a directory then it is recursively scanned for
QTI v1 files."""

			
	def do_export(self,args):
		self.ClearPages()
		fPath=args
		if os.path.exists(fPath):
			if not os.path.isfile(fPath):
				print "Can't overwrite a directory or system file"
			reply=raw_input("Warning: %s already exists, overwrite? (Yes/No)> "%fPath)
			if reply.lower()!="yes":
				return
		try:
			self.cp.ExportToPIF(fPath)
		except imscp.CPException,e:
			self.PrintException(e)			
		except IOError,e:
			self.PrintException(e)
				
	def help_export(self):
		print """export <path to PIF file>

Exports the content package to a Package Interchange File (PIF). The format used
is a zip file, you are advised to use the ".zip" file extension but this is not
enforced.  If you attempt to overwrite an existing file then you are prompted
for confirmation."""


	def do_lsr(self,args):
		self.ClearPages()
		idw=0
		typew=0
		hrefw=0
		output=[]
		resources=self.cp.manifest.root.resources
		for r in resources.GetChildren():
			if len(r.id)>idw: idw=len(r.id)
			if len(r.type)>typew: typew=len(r.type)
			if r.href is None:
				href=''
			else:
				href=r.href
			if len(href)>hrefw: hrefw=len(href)
			output.append((r.id,r.type,href))
		format="%%%is   %%-%is  %%-%is"%(idw,typew,hrefw)
		self.header=["Resources:","",format%("identifier","type","href"),"-"*130]
		for r in output:
			self.list.append(format%r)
		self.PrintPage()
		
	def help_lsr(self):
		print """lsr

List the resources in the content package"""
	def do_quit(self,arg):
		self.cp.Close()
		print "Good-bye!"
		return 1
	
	def help_quit(self):
		print """Quit the QTIMigration Shell"""
		
	def do_EOF(self,arg):
		print
		self.do_quit(arg)
		return 1

	def LoadQTI1(self,fPath):
		"""Loads a QTI v1 file from the given file path."""
		doc=qti1.QTIDocument(baseURI=urllib.pathname2url(fPath))
		try:
			doc.Read()
		except SAXException, e:
			print "Warning: SAXException while parsing %s, error follows:"%fPath
			print e
		except LookupError, e:
			print "Warning: character encoding error while parsing %s:"%fPath
			print e
		if isinstance(doc.root,qti1.QTIQuesTestInterop):
			return doc
		else:
			return None
					

def main():
	print BANNER
	print "Adding fix up for CN-BIG5..."
	qti1.FixupCNBig5()
	print "Starting interactive shell..."
	sh=QTIMigrationShell()
	sh.cmdloop("Working directory set to: %s"%os.getcwd())

if __name__ == '__main__':
	main()
