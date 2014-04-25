from array import array,zeros
import math as math
import glob as glob
import os as os

theDirChooser = DirectoryChooser("Choose directory of files to analyze")
dirPath = theDirChooser.getDirectory()

filecollection = glob.glob(os.path.join(dirPath, '*.tif'))
if (len(filecollection)<1):
	filecollection = glob.glob(os.path.join(dirPath, '*.TIF'))

for imagePath in filecollection:
	
	theImage = IJ.openImage(imagePath)
	theImage.show()
	theConverter = ImageConverter(theImage)
	theConverter.convertToGray8()

	IJ.run("Select None")
	gd = WaitForUserDialog("Use freeform tool to select edge 1")
	gd.show()
	
	theRoi = theImage.getRoi()
	theFP1 = theRoi.getFloatPolygon()
	#xptsNative = zeros('d',len(theFP.xpoints))
	#yptsNative = zeros('d',len(theFP.ypoints))
	#for i in range(len(theFP.xpoints)):
	#	xptsNative[i] = theFP.xpoints[i]
	#for i in range(len(theFP.ypoints)):
	#	yptsNative[i] = theFP.ypoints[i]
	
	IJ.run("Select None")
	gd = WaitForUserDialog("Use freeform tool to select edge 2")
	gd.show()
	
	theRoi = theImage.getRoi()
	theFP2 = theRoi.getFloatPolygon()

	theBasename = os.path.basename(imagePath)
	theBasename = theBasename.rstrip('.tif')
	savePath = dirPath + theBasename + "-roi.csv"
	theFile = open(savePath,"w")

	for i in range(len(theFP1.xpoints)):
		theOut = "%0.1f" % theFP1.xpoints[i]
		theFile.write(theOut + ",")
	theFile.write("\n")
	for i in range(len(theFP1.ypoints)):
		theOut = "%0.1f" % theFP1.ypoints[i]
		theFile.write(theOut + ",")
	theFile.write("\n")
	for i in range(len(theFP2.xpoints)):
		theOut = "%0.1f" % theFP2.xpoints[i]
		theFile.write(theOut + ",")
	theFile.write("\n")
	for i in range(len(theFP2.ypoints)):
		theOut = "%0.1f" % theFP2.ypoints[i]
		theFile.write(theOut + ",")
	theFile.write("\n")
	
	theFile.close()

	theImage.close()
