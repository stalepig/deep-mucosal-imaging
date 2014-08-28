theImage = IJ.getImage()

gd = NonBlockingGenericDialog("Shine Light")
gd.addMessage("Select an ROI to shine light")
gd.showDialog()
doClose = False
continueProg = True
if (gd.wasCanceled()):
	continueProg = False

while (continueProg):
	if (doClose):
		litImage.close()
	nslices = theImage.getNSlices()
	params = "title=dupped duplicate range=1-" + str(nslices)
	IJ.run("Duplicate...", params)
	litImage = WindowManager.getImage("dupped")
	params = "saturated=0.4 normalize process_all"
	IJ.run(litImage,"Enhance Contrast...", params)

	gd = NonBlockingGenericDialog("Shine Light")
	gd.addMessage("Select an ROI to shine light")
	gd.showDialog()
	if (gd.wasCanceled()):
		continueProg = False
	doClose = True
