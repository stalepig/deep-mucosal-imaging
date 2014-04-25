theImage = IJ.getImage()

gd = GenericDialog("Set grid size")
gd.addNumericField("Number of rows:",10,0)
gd.addNumericField("Number of columns:",10,0)
gd.showDialog()
if (gd.wasOKed()):
	IJ.run("Colors...","foreground=cyan background=cyan selection=yellow")
	numRows = gd.getNextNumber()
	numCols = gd.getNextNumber()
	colDim = theImage.getWidth() / (numCols)
	rowDim = theImage.getHeight() / (numRows)
	rowStarts = range(rowDim,theImage.getHeight()-numRows,rowDim)
	colStarts = range(colDim,theImage.getWidth()-numCols,colDim)
	rowCenters = list(rowStarts)
	rowCenters.insert(0,0)
	colCenters = list(colStarts)
	colCenters.insert(0,0)
	for i in range(0,len(rowCenters)):
		rowCenters[i] = rowCenters[i] + rowDim - rowDim/8
	for i in range(0,len(colCenters)):
		colCenters[i] = colCenters[i] + colDim/2

	for i in rowStarts:
		IJ.makeLine(0,i,theImage.getWidth(),i)
		IJ.run("Draw","stack")
	for i in colStarts:
		IJ.makeLine(i,0,i,theImage.getHeight())
		IJ.run("Draw","stack")

	numSlices = theImage.getNSlices() * theImage.getNChannels() * theImage.getNFrames()
	for zslice in range(1,numSlices+1):
		theImage.setSliceWithoutUpdate(zslice)
		ip = theImage.getProcessor()
		ip.setColor(255*255)
		for i in range(0,len(colCenters)):
			for j in range(0,len(rowCenters)):
				theString = str(int(j*numCols+i+1))
				ip.drawString(theString,int(colCenters[i]),int(rowCenters[j]))
	theImage.updateAndDraw()
