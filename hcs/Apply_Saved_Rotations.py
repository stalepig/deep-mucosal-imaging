import os
import glob
import math

theOpenDialog = OpenDialog("Choose existing rotation file","")
dirPath = theOpenDialog.getDirectory()
fileName = theOpenDialog.getFileName()
openPath = dirPath + fileName
anglesFile = open(openPath,"r")
anglesLines = anglesFile.readlines()
angles = []
fnames = []
for line in anglesLines:
	line = line.rstrip('\n')
	[fname,angle] = line.split(',')
	fnames.append(fname)
	angles.append(float(angle))
anglesFile.close()

theDirChooser = DirectoryChooser("Choose directory of images to rotate")
dirPath = theDirChooser.getDirectory()
filecollection = glob.glob(os.path.join(dirPath, '*.tif'))
if (len(filecollection)<1):
	filecollection = glob.glob(os.path.join(dirPath, '*.TIF'))

theDirChooserSave = DirectoryChooser("Choose directory to save rotated images")
saveDir = theDirChooserSave.getDirectory()

numFiles = len(filecollection)
count = 0
for imagePath in filecollection:
	imageName = os.path.basename(imagePath)
	savePath = saveDir + "rotated-" + imageName

	progress = count / (numFiles * 1.0)
	IJ.showProgress(progress)

	theImage = IJ.openImage(imagePath)
	IJ.run(theImage,"Enhance Contrast","saturated=0.4 normalize")

	foundIndex = -1
	for i in range(len(fnames)):
		if (fnames[i] == imageName):
			foundIndex = i
	if (foundIndex == -1):
		print "No angle found for file " + imageName
	else:
		theAngle = angles[foundIndex]
		theImage.getProcessor().rotate(theAngle)
		IJ.save(theImage,savePath)

	count = count+1

IJ.showProgress(1)
