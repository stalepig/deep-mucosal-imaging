## Imports
import os
import os.path
import re
import glob
import math
import datetime
from ij.io import DirectoryChooser
from ij.gui import GenericDialog
from ij import IJ
from ij import Macro
from ij import WindowManager
from ij import ImagePlus
from ij import ImageStack

## Caliber-specific channel dictionaries
channelDict = {
	"405": "c3",
	"488": "c2",
	"561": "c1",
	"640": "c4"
}

## Function definitions
def make_destination_directories(dest_dir,isDeleteContents):
	try:
		if not os.path.isdir(dest_dir):
			os.makedirs(dest_dir)
		if isDeleteContents and len(os.listdir(dest_dir)) > 0:
			for afile in os.listdir(dest_dir):
				try:
					os.remove(dest_dir+afile)
				except:
					print "Error deleting old files in " + dest_dir + " directory" 
	except:
		print "Error preparing output directory"


## Main body of script starts here
dc = DirectoryChooser("Choose root directory")
rootPath = dc.getDirectory()
if rootPath is not None:
	subDirs = next(os.walk(rootPath))[1]
	print(subDirs)
	gd = GenericDialog("Select directories to process...")
	gd.addCheckboxGroup(len(subDirs),1,subDirs,[True]*len(subDirs))
	gd.showDialog()
	if (gd.wasOKed()):
		subDirsToProcess = [subDirs[count] for count,cbox in enumerate(gd.getCheckboxes()) if cbox.state == True]
		print(subDirsToProcess)
		
		for currentDir in subDirsToProcess:
			currentPath = rootPath + currentDir + "/composites"
			IJ.log(currentPath)
			channelDirs = next(os.walk(currentPath))[1]
			channelDirstoProcess = [di for di in channelDirs if di in channelDict.keys()]
			
			## accounts situation where there is only one channel and no divided subdirectories
			if (len(channelDirstoProcess) == 0):
				channelDirstoProcess.append("")
	
			## Prepares 16-bit directories
			for channelDir in channelDirstoProcess:
				make_destination_directories(currentPath+"/16bit/"+channelDir+"/",False)

			for channelDir in channelDirstoProcess:
				files = glob.glob(os.path.join(currentPath+"/"+channelDir,'*.tif'))
				outDir16bit = currentPath+"/16bit/"+channelDir
				for theFile in files:
					IJ.showStatus(theFile)
					theImage16 = IJ.openImage(theFile)
					if (theImage16.getType() == ImagePlus.GRAY16):
						if (not os.path.exists(outDir16bit+"/"+os.path.basename(theFile))):
							IJ.saveAsTiff(theImage16,outDir16bit+"/"+os.path.basename(theFile))
						ip = theImage16.getProcessor()
						theImage16.setProcessor(ip.convertToByte(True))
						theImage16.setCalibration(theImage16.getCalibration())
						IJ.saveAsTiff(theImage16,theFile)
					else:
						IJ.log(theFile + " is not 16-bit grayscale image")
					theImage16.close()	