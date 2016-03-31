from ij import IJ
from ij.gui import NonBlockingGenericDialog
from ij import WindowManager
from ij.gui import WaitForUserDialog
from ij import ImageStack
from ij import ImagePlus

theImage = IJ.getImage()

sourceImages = []
if theImage.getNChannels() == 1:
	IJ.run("8-bit")
	sourceImages.append(theImage)
else:
	sourceImages = ChannelSplitter.split(theImage)
	sourceNames = []
	for im in sourceImages:
		im.show()
		sourceNames.append(im.getTitle())
	gd0 = NonBlockingGenericDialog("Select source image...")
	gd0.addChoice("Source image",sourceNames,sourceNames[0])
	gd0.showDialog()
	if (gd0.wasOKed()):
		chosenImage = gd0.getNextChoice()
		theImage = WindowManager.getImage(chosenImage)
		IJ.selectWindow(chosenImage)
	else:
		theImage = sourceImages[0]
		IJ.selectWindow(sourceNames[0])
	
gd = NonBlockingGenericDialog("Set slice params...")
gd.addNumericField("Slice start:",1,0)
gd.addNumericField("Slice end:",theImage.getNSlices(),0)
gd.showDialog()

if (gd.wasOKed()):
	## Selecting the ROI over the stack
	startSlice = int(gd.getNextNumber())
	endSlice = gd.getNextNumber()
	width = theImage.getWidth()
	height = theImage.getHeight()

	roiArray = []
	for i in range(startSlice,endSlice+1):
		theImage.setSlice(i)

		bp = theImage.getProcessor().duplicate()
		bp.setColor(0)
		
		doStaySlice = True
		while doStaySlice:
			waiter = WaitForUserDialog("Draw ROI","Draw ROI, then hit OK")
			waiter.show()

			roi = theImage.getRoi()
			if roi is None:
				doStaySlice = True
			else:
				doStaySlice = False
				roiArray.append(roi)

	## Applying the ROI to each channel
	newStacks = []
	castImages = []
	for procImage in sourceImages:
		newStacks.append(ImageStack(width,height))
		ns = newStacks[-1]
		for i in range(startSlice,endSlice+1):
			procImage.setSliceWithoutUpdate(i)
			bp = procImage.getProcessor().duplicate()
			bp.fillOutside(roiArray[i-startSlice])
			ns.addSlice(bp)
		castImages.append(ImagePlus(procImage.getShortTitle()+"_cast",ns))

	## Displays the output
	for castImage in castImages:
		castImage.show()

	## Cleans up the windows
	for sourceImage in sourceImages:
		sourceImage.close()
