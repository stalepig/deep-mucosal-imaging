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

def check_if_filetype(inputString,extension):
	pattern = u"\." + extension + u"$"
	if re.search(extension,inputString) is not None:
		return True
	else:
		return False

def generate_path(fileName,basePath):
	returnPath = basePath + "/" + fileName
	return returnPath

def run_explode(filePath):
	basePath,baseName = os.path.split(filePath)
	checkName = basePath + "/" + baseName + "_tiles"
	IJ.log("Exploding " + filePath + "...")
	if (not os.path.isdir(checkName)):
		thread = Thread.currentThread()
		originalThread = thread.getName()
		thread.setName("Run$_explode_process")
		options = "open=" + filePath
		Macro.setOptions(Thread.currentThread(),options)
		try:
			IJ.run("Explode Into Tiles",options)
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

def get_directory_size(sourceDir):
	sumSize = 0
	files = glob.glob(os.path.join(sourceDir,'*.ome.tif'))
	for theFile in files:
		theSize = os.path.getsize(theFile)
		sumSize = sumSize + theSize
	return sumSize

def run_resize(filePath):
	basePath,baseName = os.path.split(filePath)
	checkName = basePath + "/" + baseName + "_tiles/resized/"
	activeName = basePath + "/" + baseName + "_tiles"
	IJ.log("Resizing " + filePath + "...")
	if (not os.path.isdir(checkName)):
		thread = Thread.currentThread()
		originalThread = thread.getName()
		thread.setName("Run$_resize_process")
		totFileSize = get_directory_size(activeName) / 1048576.0
		totFijiMem = Memory().maxMemory() / 1048576.0 
		IJ.run("Bio-Formats Importer", "open=["+ activeName +"/tile_1.ome.tif] color_mode=Default view=Hyperstack stack_order=XYCZT");
		tileImage = WindowManager.getImage("tile_1.ome.tif")
		nChannels = tileImage.getNChannels()
		tileImage.close()
		allowedMem = min(nChannels * totFijiMem/10.0, totFijiMem/3.0)
		ratio = allowedMem / totFileSize
		if (ratio < 1):
			options = "choose=" + activeName + " sizing_ratio=" + str(ratio)
		else:
			options = "choose=" + activeName + " sizing_ratio=1.00"
		Macro.setOptions(Thread.currentThread(),options)
		try:
			IJ.run("Batch resizer",options)
			IJ.log("succeeded with sizing ratio=" + str(ratio))
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

def run_stitch(filePath):
	basePath,baseName = os.path.split(filePath)
	imagePrefix = os.path.splitext(baseName)[0]
	resizeName = basePath + "/" + baseName + "_tiles/resized/"
	checkName = basePath + "/" + baseName + "_tiles/resized/" + imagePrefix + "_seq/"
	activeName = basePath + "/" + baseName + "_tiles"
	IJ.log("Stitching " + filePath + "...")
	if (not os.path.isdir(checkName)):
		thread = Thread.currentThread()
		originalThread = thread.getName()
		thread.setName("Run$_stitch_process")
		options = "choose=" + resizeName + " select=" + activeName + "/tile_info.txt image_prefix=" + imagePrefix
		Macro.setOptions(Thread.currentThread(),options)
		try:
			IJ.run("Stitch wrapper",options)
			IJ.log("succeeded")
			returnVal = 0
		except:
			IJ.log("failed")
			os.rmdir(checkName)
			returnVal = 1
		thread.setName(originalThread)
		Macro.setOptions(thread,None)
	else:
		IJ.log("skipped")
		returnVal = 2

	return returnVal

def run_combine(filePath):
	basePath,baseName = os.path.split(filePath)
	imagePrefix = os.path.splitext(baseName)[0]
	resizeName = basePath + "/" + baseName + "_tiles/resized/"
	checkName = basePath + "/" + baseName + "_tiles/resized/" + imagePrefix + "_seq/"
	activeName = basePath + "/" + baseName + "_tiles"
	outputName = basePath + "/stitched/" + imagePrefix + "/"
	IJ.log("Combining " + filePath + "...")
	if (not os.path.isdir(outputName)):
		try:
			os.makedirs(outputName)
			if (not os.path.isdir(checkName)):
				raise ValueError("Stitched image directory not found")
			for dirpath, dirnames, files in os.walk(checkName):
				if not files:
					raise ValueError("Stitched image directory is empty")
			IJ.run("Bio-Formats Importer", "open=["+ activeName +"/tile_1.ome.tif] color_mode=Default view=Hyperstack stack_order=XYCZT");
			tileImage = WindowManager.getImage("tile_1.ome.tif")
			nChannels = tileImage.getNChannels()
			tileImage.close()
			options = "open=[" + checkName + "] starting=1 increment=1 scale=100 file=[] sort"
			IJ.run("Image Sequence...", options)
			theImage = IJ.getImage()
			for i in range(1,nChannels+1):
				params = "slices=" + str(i) + "-" + str(theImage.getNSlices()) + "-" + str(nChannels)
				IJ.run(theImage,"Make Substack...",params)
			theImage.close()
			wList = WindowManager.getIDList()
			for i in range(len(wList)):
				currImage = WindowManager.getImage(wList[i])
				currImage.setTitle("image"+str(i+1))
				IJ.save(currImage,outputName+imagePrefix+"_ch"+str(i+1)+".tif")
			if nChannels > 1 and not os.path.isfile(outputName+imagePrefix+"_composite.tif"):
				if nChannels == 2:
					params = ("c1=" + WindowManager.getImage(wList[0]).getTitle() + 
							" c4=" + WindowManager.getImage(wList[1]).getTitle() + " create ignore")
				elif nChannels == 3:
					params = ("c1=" + WindowManager.getImage(wList[1]).getTitle() +
							" c2=" + WindowManager.getImage(wList[0]).getTitle() +
							" c4=" + WindowManager.getImage(wList[2]).getTitle() + " create ignore")
				elif nChannels == 4:
					params = ("c1=" + WindowManager.getImage(wList[1]).getTitle() +
							" c2=" + WindowManager.getImage(wList[2]).getTitle() +
							" c3=" + WindowManager.getImage(wList[0]).getTitle() +
							" c4=" + WindowManager.getImage(wList[3]).getTitle() + " create ignore")
				elif nChannels == 5:
					params = ("c1=" + WindowManager.getImage(wList[1]).getTitle() +
							" c2=" + WindowManager.getImage(wList[2]).getTitle() +
							" c3=" + WindowManager.getImage(wList[0]).getTitle() +
							" c4=" + WindowManager.getImage(wList[4]).getTitle() + 
							" c7=" + WindowManager.getImage(wList[3]).getTitle() +
							" create ignore")
				else:
					IJ.log("No composite image created due to excess channels (>4)")
				IJ.run("Merge Channels...", params)
				compositeImage = IJ.getImage()
				IJ.save(compositeImage,outputName+imagePrefix+"_composite.tif")			
			wList = WindowManager.getIDList()
			for i in range(len(wList)):
				currImage = WindowManager.getImage(wList[i])						
				currImage.close()
			IJ.log("succeeded")
			returnVal = 0
		except:
			IJ.log("failed")
			os.rmdir(outputName)
			wList = WindowManager.getIDList()
			for i in range(len(wList)):
				currImage = WindowManager.getImage(wList[i])
				currImage.close()
			returnVal = 1
	else:
		IJ.log("skipped")
		returnVal = 2

	return returnVal
	

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
				explodeStatuses = map(run_explode,LSMpaths)
				resizePaths = map(get_first_in_tuple,filter(filter_by_return_status,map(lambda x,y:(x,y),LSMpaths,explodeStatuses)))
				if len(resizePaths)>0:
					resizeStatuses = map(run_resize,resizePaths)
					stitchPaths = map(get_first_in_tuple,filter(filter_by_return_status,map(lambda x,y:(x,y),resizePaths,resizeStatuses)))
					if len(stitchPaths)>0:
						stitchStatuses = map(run_stitch,stitchPaths)
						combinePaths = map(get_first_in_tuple,filter(filter_by_return_status,map(lambda x,y:(x,y),stitchPaths,stitchStatuses)))
						if len(combinePaths)>0:
							combineStatuses = map(run_combine,combinePaths)
					