## Imports
import os
import re
import glob
from ij.io import DirectoryChooser
from ij.gui import GenericDialog
from ij import IJ
from ij import Macro
from ij import WindowManager
from ij.plugin import Memory
from java.lang import Thread


## Function definitions
def check_if_filetype(inputString,extension):
	pattern = u"\." + extension + u"$"
	if re.search(extension,inputString) is not None:
		return True
	else:
		return False

def generate_path(fileName,basePath):
	returnPath = basePath + "/" + fileName
	return returnPath

def run_stitch(filePath):
	basePath,baseName = os.path.split(filePath)
	checkName = basePath + "/" + baseName + "_tiles"
	IJ.log("Stitching " + filePath + "...")
	if (not os.path.isdir(checkName)):
		thread = Thread.currentThread()
		originalThread = thread.getName()
		thread.setName("Run$_stitch_process")
		options = "select=" + filePath
		Macro.setOptions(Thread.currentThread(),options)
		try:
			IJ.run("Make prelim tileconfig file",options)
			IJ.log("succeeded")
			returnVal = 0
		except:
			IJ.log("failed")
			returnVal = 1
		thread.setName(originalThread)
		Macro.setOptions(thread,None)
	else:
		IJ.log("skipped")
		returnVal = 2

	return returnVal

def filter_by_return_status(tupleInput):
	path,status = tupleInput
	if (status == 1):
		return False
	else:
		return True

def get_first_in_tuple(tupleInput):
	first,second = tupleInput
	return first

def run_resize(filePath):
	basePath,baseName = os.path.split(filePath)
	checkName = basePath + "/" + baseName + "_tiles/stitched/"
	activeName = basePath + "/" + baseName + "_tiles"
	IJ.log("Resizing " + filePath + "...")
	if (not os.path.isdir(checkName)):
		thread = Thread.currentThread()
		originalThread = thread.getName()
		thread.setName("Run$_resize_process")
		options = "select=" + filePath
		Macro.setOptions(Thread.currentThread(),options)
		try:
			IJ.run("Resize virtual image",options)
			IJ.log("succeeded")
			returnVal = 0
		except:
			IJ.log("failed")
			returnVal = 1
		thread.setName(originalThread)
		Macro.setOptions(thread,None)
	else:
		IJ.log("skipped")
		returnVal = 2

	return returnVal

def run_metadata(filePath):
	basePath,baseName = os.path.split(filePath)
	activeName = basePath + "/" + baseName + "_tiles"
	IJ.log("Getting metadata for " + filePath + "...")
	thread = Thread.currentThread()
	originalThread = thread.getName()
	thread.setName("Run$_metadata_process")
	options = "select=" + filePath
	Macro.setOptions(Thread.currentThread(),options)
	returnVal = 2
	try:
		IJ.run("Extract metadata",options)
		IJ.log("succeeded")
		returnVal = 0
	except:
		IJ.log("failed")
		returnVal = 1
	thread.setName(originalThread)
	Macro.setOptions(thread,None)

	return returnVal

## Main body of script starts here
dc = DirectoryChooser("Choose root directory")
rootPath = dc.getDirectory()
if rootPath is not None:
	gd = GenericDialog("Batch mode options...")
	gd.addStringField("Filename extension","lsm",6)
	gd.showDialog()
	if (gd.wasOKed()):
		extension = gd.getNextString()
		for root, dirs, files in os.walk(rootPath):
			LSMfiles = filter(lambda x: check_if_filetype(x,extension),files)
			if len(LSMfiles)>0:
				LSMpaths = map(lambda x: generate_path(x,root),LSMfiles)
				stitchStatuses = map(run_stitch,LSMpaths)
				resizePaths = map(get_first_in_tuple,filter(filter_by_return_status,map(lambda x,y:(x,y),LSMpaths,stitchStatuses)))
				if len(resizePaths)>0:
					resizeStatuses = map(run_resize,resizePaths)
					metadataStatuses = map(run_metadata,resizePaths)