gd = GenericDialog("Parameters to subtract local background...")
gd.addNumericField("Window Size (pixels):",512,0)
gd.addNumericField("Window overlap factor (>1):",2,0)
gd.addNumericField("Standard deviation limit:",1.0,1)
gd.addNumericField("Pixel ignore threshold (higher is faster):",10,0)
gd.showDialog()

if (gd.wasOKed()):
	windowSize = gd.getNextNumber()
	windowMultiple = gd.getNextNumber()
	sdMultiple = gd.getNextNumber()
	ignoreIntensity = gd.getNextNumber()
	
	IJ.run("Set Measurements...", "  mean standard redirect=None decimal=3")
	originalImage = IJ.getImage()
	startSlice = originalImage.getSlice()
	theImage = originalImage.duplicate()
	writeImage = originalImage.duplicate()
	analyzer = Analyzer(theImage)
	rt = ResultsTable.getResultsTable()
	rt.reset()
	
	for i in range(1,theImage.getNSlices()+1):
		theImage.setSliceWithoutUpdate(i)
		writeImage.setSliceWithoutUpdate(i)
		lefts = range(0,theImage.getWidth(),windowSize/windowMultiple)
		tops = range(0,theImage.getHeight(),windowSize/windowMultiple)
		ip = writeImage.getProcessor()
		
		for left in lefts:
			for top in tops:
				if (left+windowSize>theImage.getWidth()):
					miniWidth = theImage.getWidth()-left
				else:
					miniWidth = windowSize
	
				if (top+windowSize>theImage.getHeight()):
					miniHeight = theImage.getHeight()-top
				else:
					miniHeight = windowSize
					
				roi = Roi(left,top,miniWidth,miniHeight)
				theImage.setRoi(roi,False)
				analyzer.measure()
				meanvalue = rt.getValueAsDouble(ResultsTable.MEAN,rt.getCounter()-1)
				sdvalue = rt.getValueAsDouble(ResultsTable.STD_DEV,rt.getCounter()-1)
				threshold = meanvalue + sdMultiple*sdvalue
	
				if (threshold > ignoreIntensity):
					for x in range(left,left+miniWidth):
						for y in range(top,top+miniHeight):
							if (ip.get(x,y) < threshold):
								ip.set(x,y,0)
	
		IJ.showProgress(i,theImage.getNSlices()+1)
				
	writeImage.show()
	writeImage.setSlice(startSlice)