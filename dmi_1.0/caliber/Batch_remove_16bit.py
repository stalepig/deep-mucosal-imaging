import os
import glob
import shutil
from ij.io import DirectoryChooser
from ij.gui import GenericDialog
from ij import IJ

## Main body of script starts here
dc = DirectoryChooser("Choose image directory")
parentPath = dc.getDirectory()
if parentPath is not None:
	# imageDirs = next(os.walk(parentPath))[1]
	imageDirs = glob.glob(parentPath + "/**/composites/16bit")
	print(imageDirs)
	gd = GenericDialog("Select directories to remove...")
	gd.addCheckboxGroup(len(imageDirs),1,imageDirs,[True]*len(imageDirs))
	gd.showDialog()
	if (gd.wasOKed()):
		imageDirsToProcess = [imageDirs[count] for count,cbox in enumerate(gd.getCheckboxes()) if cbox.state == True]
		print(imageDirsToProcess)
		for targetDir in imageDirsToProcess:
			try:
				shutil.rmtree(targetDir)
			except OSError as e:
				IJ.log("Error: %s : %s" % (targetDir, e.strerror))