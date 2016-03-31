from ij import IJ
from ij import ImagePlus
from ij.gui import NonBlockingGenericDialog
from ij.gui import WaitForUserDialog
from ij.plugin import ChannelSplitter
from ij.plugin import ImageCalculator
from ij.measure import ResultsTable
from ij.measure import Measurements
from ij.plugin.filter import Analyzer

## Main body of script
theImage = IJ.getImage()
gd = NonBlockingGenericDialog("Pick parameters...")
gd.addChoice("Analysis_channel",["Channel "+str(i+1) for i in range(theImage.getNChannels())],"Channel 1")
gd.addNumericField("Pick_threshold",50,0)
gd.addCheckbox("Apply_min",True)
gd.showDialog()
if (gd.wasOKed()):
	analysisChannel = gd.getNextChoiceIndex() + 1
	intensityThreshold = gd.getNextNumber()
	doMin = gd.getNextBoolean() 
	splitImage = ChannelSplitter.split(theImage)
	dataImage = splitImage[analysisChannel-1].duplicate()
	if doMin:
		IJ.run(dataImage,"Minimum...", "radius=2 stack")
	goRun = True
	rt = ResultsTable()
	while goRun:
		wfud = WaitForUserDialog("Pick freehand ROI, then hit OK to analyze")
		wfud.show()
		roi = theImage.getRoi()
		if roi is None:
			goRun = False
		else:
			dataImage.setRoi(roi)
			subImage = dataImage.duplicate()
			dataIp = dataImage.getProcessor()
			dataIp.setRoi(roi)
			maskIp = dataIp.getMask()
			maskImage = ImagePlus("Mask Image",maskIp)
			ic = ImageCalculator()
			countingImage = ic.run("AND create stack",subImage,maskImage)
			pixelCount = 0
			for i in range(1,countingImage.getNSlices()+1):
				countingImage.setSlice(i)
				countingIp = countingImage.getProcessor()
				for x in range(0,countingImage.getWidth()):
					for y in range(0,countingImage.getHeight()):
						if (countingIp.getPixel(x,y) >= intensityThreshold):
							pixelCount = pixelCount + 1
			totAvailablePixels = countingImage.getWidth() * countingImage.getHeight() * countingImage.getNSlices()
			#IJ.log("Pixel count: " + str(pixelCount) + " of " + str(totAvailablePixels))
			countingImage.close()
			rt.incrementCounter()
			rt.addValue("PosPixels",pixelCount)
			rt.addValue("TotPixels",totAvailablePixels)
			rt.show("DMI Results")
	