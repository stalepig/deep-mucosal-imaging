from array import array,zeros
import math as math
import os
import glob

theDirChooser = DirectoryChooser("Choose directory of images to rotate")
dirPath = theDirChooser.getDirectory()

theDirChooserSave = DirectoryChooser("Choose directory to save rotated images")
saveDir = theDirChooserSave.getDirectory()

theSaveDialog = SaveDialog("Choose file to save analysis results","rotate_angles",".csv")
saveDirCSV = theSaveDialog.getDirectory()
savePathCSV = saveDirCSV + theSaveDialog.getFileName()

filecollection = glob.glob(os.path.join(dirPath, '*.tif'))
if (len(filecollection)<1):
	filecollection = glob.glob(os.path.join(dirPath, '*.TIF'))
numFiles = len(filecollection)
count = 0
for imagePath in filecollection:
	imageName = os.path.basename(imagePath)
	savePath = saveDir + "rotated-" + imageName
	progress = count / (numFiles * 1.0)
	IJ.showProgress(progress)
	
	theImage = IJ.openImage(imagePath)
	theImage.show()
	IJ.run("Select None")
	IJ.run(theImage,"Enhance Contrast","saturated=0.4 normalize")

	gd = WaitForUserDialog("Hit OK after having picked reference edge with multi-point ROI tool")
	gd.show()
	
	theAnalyzer = Analyzer(theImage)
	theResultsTable = theAnalyzer.getResultsTable()
	theResultsTable.reset()
	theAnalyzer.measure()
	
	#print theResultsTable.getColumnHeadings()
	xpts = theResultsTable.getColumn(6)
	ypts = theResultsTable.getColumn(7)
	xptsNative = zeros('d',len(xpts))
	yptsNative = zeros('d',len(ypts))
	for i in range(len(xpts)):
		xptsNative[i] = xpts[i]
	for i in range(len(ypts)):
		yptsNative[i] = ypts[i]
	theCurveFitter = CurveFitter(xptsNative,yptsNative)
	theCurveFitter.doFit(theCurveFitter.STRAIGHT_LINE)
	print theCurveFitter.getRSquared()
	fitParams = theCurveFitter.getParams()
	print fitParams[0]
	print fitParams[1]
	angle = math.atan(fitParams[1])
	
	theImage.getProcessor().rotate(-1*math.degrees(angle))
	theFile = open(savePathCSV,"a")
	theFile.write(imageName+","+str(-1*math.degrees(angle))+"\n")
	theFile.close()
	theImage.updateAndDraw()
	
	IJ.save(theImage,savePath)
	theImage.close()
	count = count + 1

IJ.showProgress(1)

#gd = WaitForUserDialog("Hit OK after have outlined edges")
#gd.show()
#theRoi = theImage.getRoi()
#print type(theRoi)
#print theRoi.getNCoordinates()
