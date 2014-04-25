theImage = IJ.getImage()

gd = GenericDialog("Expand stack...")
gd.addNumericField("Multiple (natural number):",4,0)
gd.showDialog()

if (gd.wasOKed()):
	newStack = ImageStack(theImage.getWidth(),theImage.getHeight())
	multiple = int(gd.getNextNumber())

	for i in range(1,theImage.getNSlices()):
		theImage.setSlice(i)
		ip = theImage.getProcessor()
		for j in range(multiple):
			newip = ip.duplicate()
			newStack.addSlice(newip)

	resultImage = ImagePlus("stack_exp",newStack)
	resultImage.show()