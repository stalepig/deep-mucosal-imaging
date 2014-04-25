from array import zeros

theImage = IJ.getImage()
gd = NonBlockingGenericDialog("Set slice params...")
gd.addNumericField("Slice start:",1,0)
gd.addNumericField("Slice end:",theImage.getNSlices(),0)
gd.showDialog()

if (gd.wasOKed()):
	startSlice = gd.getNextNumber()
	endSlice = gd.getNextNumber()
	width = theImage.getWidth()
	height = theImage.getHeight()
	newStack = ImageStack(width,height)

	for i in range(startSlice,endSlice+1):
		theImage.setSlice(i)
		theImage.killRoi()

		pixels = zeros('b',width*height)
		bp = ByteProcessor(width,height,pixels)
		bp.setColor(127)
		
		doStaySlice = True
		while doStaySlice:
			waiter = NonBlockingGenericDialog("Set cast")
			waiter.addMessage("Pick 2D ROI")
			waiter.setOKLabel("Save and advance")
			waiter.setCancelLabel("Save")
			waiter.showDialog()

			if (waiter.wasOKed()):
				roi = theImage.getRoi()
				if (roi is None):
					doStaySlice = True
				else:
					bp.fill(roi)
					doStaySlice = False
			else:
				roi = theImage.getRoi()
				if (roi is None):
					doStaySlice = True
				else:
					bp.fill(roi)
					doStaySlice = True	
		newStack.addSlice(bp)
		
	castImage = ImagePlus("cast",newStack)
	castImage.show()	
