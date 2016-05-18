from ij import IJ
from ij.gui import NonBlockingGenericDialog
from ij import WindowManager
from ij.gui import WaitForUserDialog
from ij import ImageStack
from ij import ImagePlus
from ij.process import ByteProcessor
from ij.plugin import ImageCalculator

theImage = IJ.getImage()

if theImage.getNSlices() > 1:
	iStack = ImageStack(theImage.getWidth(),theImage.getHeight())
	for sl in range(theImage.getNSlices()):
		sliceIp = ByteProcessor(theImage.getWidth(),theImage.getHeight())
		iStack.addSlice(sliceIp)
	maskImage = ImagePlus("maskImage",iStack)

	## Gets the user-defined ROIs; user can add in any order to image
	sliceList = []
	gd  = NonBlockingGenericDialog("Select freehand ROI, then hit OK when ready to store")
	gd.showDialog()
	while gd.wasOKed():
		roi = theImage.getRoi()
		if roi is not None:
			currSlice = theImage.getCurrentSlice()
			maskImage.setSlice(currSlice)
			currIp = maskImage.getProcessor()
			currIp.setRoi(roi)
			currIp.setColor(255)
			currIp.fill(currIp.getMask())
			sliceList.append(currSlice)
			theImage.setSlice(currSlice+1)
			
		gd  = NonBlockingGenericDialog("Select freehand ROI, then hit OK when ready to store")
		gd.showDialog()

	## Does simple interpolation of the ROIs through the stack
	if len(sliceList)>0:
		sliceList.sort(reverse=True)
		for sl in range(theImage.getNSlices()):
			if (sl+1) < sliceList[-1]:
				maskImage.setSliceWithoutUpdate(sliceList[-1])
				activeIp = maskImage.getProcessor().duplicate()
			elif (sl+1) > sliceList[0]:
				maskImage.setSliceWithoutUpdate(sliceList[0])
				activeIp = maskImage.getProcessor().duplicate()
			else:
				isFound = False
				for mark in sliceList:
					dist = sl+1 - mark
					if dist >= 0 and not isFound:
						isFound = True
						refSlice = mark
				maskImage.setSliceWithoutUpdate(refSlice)
				activeIp = maskImage.getProcessor().duplicate()
			maskImage.setSliceWithoutUpdate(sl+1)
			maskImage.setProcessor(activeIp)

	## Computes the overlay image
	ic = ImageCalculator()
	resultImage = ic.run("AND create stack",theImage,maskImage)
	resultImage.show()

	maskImage.close()
