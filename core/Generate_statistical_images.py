squareSize = 10

theImage = IJ.getImage()
theConverter = ImageConverter(theImage)
theConverter.convertToGray8()
imgHeight = theImage.getHeight()
imgWidth = theImage.getWidth()

theAnalyzer = Analyzer(theImage)
theAnalyzer.setMeasurements(Analyzer.AREA | Analyzer.STD_DEV | Analyzer.MEAN)
theResultsTable = theAnalyzer.getResultsTable()

widthIter = range(0,imgWidth,squareSize)
heightIter = range(0,imgHeight,squareSize)
sd_array = []
mean_array = []
for i in widthIter:
	for j in heightIter:
		theResultsTable.reset()
		theRoi = Roi(i,j,squareSize,squareSize)
		theImage.setRoi(theRoi,0)
		theAnalyzer.measure()
		sds = theResultsTable.getColumn(2)
		means = theResultsTable.getColumn(1)
		sd = sds[0]
		mean = means[0]
		sd_array.append(sd)
		mean_array.append(mean)

maxsd = max(sd_array)
minsd = min(sd_array)
maxmean = max(mean_array)
minmean = min(mean_array)
for i in range(len(sd_array)):
	sd_array[i] = ((sd_array[i] - minsd) / maxsd) * 255
	mean_array[i] = ((mean_array[i] - minmean) / maxmean) * 255
sdImage = ImagePlus("Standard Deviation Image", FloatProcessor(imgWidth,imgHeight))
meanImage = ImagePlus("Mean Image", FloatProcessor(imgWidth,imgHeight))
index = 0
for i in widthIter:
	for j in heightIter:
		theRoi = Roi(i,j,squareSize,squareSize)
		theColorSD = int(sd_array[index])
		theColorMean = int(mean_array[index])
		sdImage.getProcessor().setColor(theColorSD)
		sdImage.getProcessor().fill(theRoi)
		meanImage.getProcessor().setColor(theColorMean)
		meanImage.getProcessor().fill(theRoi)
		index = index + 1
sdImage.show()
#meanImage.show()