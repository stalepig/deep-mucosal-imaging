import os
import glob

table = ResultsTable()
pa = ParticleAnalyzer(ParticleAnalyzer.SHOW_NONE, Measurements.AREA, table, 0, Double.POSITIVE_INFINITY, 0.0, 1.0)

theDirChooser = DirectoryChooser("Choose directory of files to analyze")
dirPath = theDirChooser.getDirectory()

theSaveDialog = SaveDialog("Choose file to save analysis results","analyzed_particles",".csv")
saveDir = theSaveDialog.getDirectory()
savePath = saveDir + theSaveDialog.getFileName()
print savePath
theFile = open(savePath,"w")

filecollection = glob.glob(os.path.join(dirPath, '*.tif'))
if (len(filecollection)<1):
	filecollection = glob.glob(os.path.join(dirPath, '*.TIF'))
numFiles = len(filecollection)
print numFiles
count = 0

gd = GenericDialog("Options...")
gd.addCheckbox("Run optimal min/max normalization:",False)
gd.addCheckbox("Equalize histogram",False)
gd.showDialog()
doNorm = gd.getNextBoolean()
doEqualize = gd.getNextBoolean()

for imagePath in filecollection:
	print("current file is: " + imagePath)

	progress = count / (numFiles * 1.0)
	IJ.showProgress(progress)
	theImage = IJ.openImage(imagePath)
	theConverter = ImageConverter(theImage)
	theConverter.convertToGray8()
	if (doNorm):
		IJ.run(theImage,"Enhance Contrast...","saturated=0.4 normalize")
	if (doEqualize):
		IJ.run(theImage,"Enhance Contrast...","saturated=0.4 normalize equalize")
	theProcessor = theImage.getChannelProcessor()
	theProcessor.invert()

	theFile.write("\"" + imagePath + "\",")
	for i in range(254):
		testerImage = ImagePlus("TesterImage", theImage.getImage())
		IJ.setThreshold(testerImage,0,254-i)
		#print i
	
		pa.analyze(testerImage)
	
		numSpots = table.getCounter()
		
		theFile.write(str(numSpots)+",")
		table.reset()

	theFile.write("\n")
	count = count + 1
	
theFile.close()
IJ.showProgress(1)