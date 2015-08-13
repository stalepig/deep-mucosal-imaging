from ij import IJ

theImage = IJ.getImage()
setterCal = theImage.getCalibration()

sourceImage = IJ.openImage()
if sourceImage is not None:
	sourceCal = sourceImage.getCalibration()

	setterCal.pixelWidth = sourceCal.pixelWidth
	setterCal.pixelHeight = sourceCal.pixelHeight
	setterCal.pixelDepth = sourceCal.pixelDepth
	setterCal.setUnit(sourceCal.getUnit())

	theImage.repaintWindow()
