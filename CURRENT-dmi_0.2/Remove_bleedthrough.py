from ij import WindowManager
from ij import IJ
from ij.gui import GenericDialog
from ij.measure import ResultsTable
from ij.gui import WaitForUserDialog
from ij.plugin.filter import Analyzer
from ij import ImagePlus
from ij.plugin import ImageCalculator

wList = WindowManager.getIDList()
if (wList):
	theImage = IJ.getImage()
	titles = []
	for i in range(len(wList)):
		imp = WindowManager.getImage(wList[i])
		titles.append(imp.getTitle())

	gd = GenericDialog("Pick images")
	gd.addChoice("Main channel:",titles,titles[0])
	gd.addChoice("Subtracted channel:",titles,titles[1])
	gd.showDialog()

	if (gd.wasCanceled()): 
		quit()

	index1 = gd.getNextChoiceIndex()
	index2 = gd.getNextChoiceIndex()
	image1 = WindowManager.getImage(wList[index1])
	image2 = WindowManager.getImage(wList[index2])
	IJ.selectWindow(wList[index1])

	rt = ResultsTable.getResultsTable()
	rt.reset()
	gd = WaitForUserDialog("Pick region with only bleedthrough")
	gd.show()
	al1 = Analyzer(image1)
	theSlice = image1.getSlice()
	al1.measure()
	al1.displayResults()
	theRoi = image1.getRoi()
	al2 = Analyzer(image2)
	image2.setSlice(theSlice)
	image2.setRoi(theRoi)
	al2.measure()
	al2.displayResults()
	gd = WaitForUserDialog("Pick autofluorescent tissue region")
	gd.show()
	al1.measure()
	al1.displayResults()
	theRoi = image1.getRoi()
	image2.setRoi(theRoi)
	al2.measure()
	al2.displayResults()
	image1.deleteRoi()
	image2.deleteRoi()

	val_high = rt.getValueAsDouble(1,0)
	val_bleed = rt.getValueAsDouble(1,1)
	val_low = rt.getValueAsDouble(1,2)
	val_zero = rt.getValueAsDouble(1,3)
	val_target = val_high - val_low
#	scale_target = val_target / val_bleed
	scale_target = val_target / (val_bleed - val_zero)
	print scale_target

	gd = GenericDialog("Scale factor")
	gd.addNumericField("Scale factor on subtraction:",scale_target,3)
	gd.showDialog()

	if (gd.wasCanceled()): 
		quit()

	scale = gd.getNextNumber()

	tempImage = image2.duplicate()
	for i in range(tempImage.getNSlices()):
		tempImage.setSliceWithoutUpdate(i+1)
		ip = tempImage.getProcessor()
		ip.subtract(val_zero)
		ip.multiply(scale)
	ic = ImageCalculator()
	newImage = ic.run("Subtract create stack",image1,tempImage)
	newImage.show()
	
else:
	IJ.error("No images are open.")
