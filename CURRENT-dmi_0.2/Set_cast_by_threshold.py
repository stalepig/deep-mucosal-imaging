from ij import IJ
from ij.gui import NonBlockingGenericDialog
from ij import ImageStack
from ij.gui import WaitForUserDialog
from ij import ImagePlus
from ij.process import ImageProcessor

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

	t_line = 240
	for i in range(startSlice,endSlice+1):
		theImage.setSlice(i)
		waiter = WaitForUserDialog("Set ROI","Set ROI for thresholding region")
		waiter.show()

		roi = theImage.getRoi()
		newip = theImage.getProcessor().duplicate()
		newip.setColor(0)
		newip.fillOutside(roi)
		newip.snapshot()
		newip.setThreshold(0,t_line,ImageProcessor.BLACK_AND_WHITE_LUT)
		newImage = ImagePlus("toggler",newip)
		newImage.show()

		doSameSlice = True
		while (doSameSlice):
			accept_waiter = NonBlockingGenericDialog("Thresholding...")
			accept_waiter.addNumericField("Threshold:",t_line,0)
			accept_waiter.setCancelLabel("Apply new threshold")
			accept_waiter.setOKLabel("Accept threshold")
			accept_waiter.showDialog()
			if (accept_waiter.wasCanceled()):
				newip.reset()
				newip.snapshot()
				t_line = accept_waiter.getNextNumber()
#				if (t_line > 10):
#					t_line = t_line - 5
#				else:
#					t_line = 5
				newip.setThreshold(0,t_line,ImageProcessor.BLACK_AND_WHITE_LUT)
				newImage.updateAndDraw()
			else:
				doSameSlice = False
				for i in range(newImage.getWidth()):
					for j in range(newImage.getHeight()):
						if (newip.getPixel(i,j) > newip.getMaxThreshold()):
							newip.putPixel(i,j,254)
						else:
							newip.putPixel(i,j,0)
				newnewip = newip.duplicate()
				newStack.addSlice(newnewip)
				newImage.close()

	castImage = ImagePlus("cast",newStack)
	castImage.show()
			
