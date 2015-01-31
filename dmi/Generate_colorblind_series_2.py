wList = WindowManager.getIDList()
titles = []

dc = DirectoryChooser("Select directory to save files...")
theDir = dc.getDirectory()
if (theDir is not None):

	# Performs "Save all" feature
	for imageid in wList:
		theImage = WindowManager.getImage(imageid)
		titles.append(theImage.getTitle())
		IJ.run(theImage,"8-bit","")
		IJ.save(theImage,theDir+"/"+theImage.getShortTitle()+".tif")

	if len(titles) >= 3:
		# Dialog box to ask which images to "OR"
		gd = GenericDialog("Pick images...")
		gd.addChoice("Green image:",titles,titles[0])
		gd.addChoice("Magenta image 1:",titles,titles[1])
		gd.addChoice("Magenta image 2:",titles,titles[2])
		gd.addStringField("Composite label:","gene")
		gd.showDialog()

		if (gd.wasOKed()):
			greenImage_idx = gd.getNextChoiceIndex()
			magentaImage1_idx = gd.getNextChoiceIndex()
			magentaImage2_idx = gd.getNextChoiceIndex()
			labelattach = gd.getNextString()

			greenImage = WindowManager.getImage(wList[greenImage_idx])
			magentaImage1 = WindowManager.getImage(wList[magentaImage1_idx])
			magentaImage2 = WindowManager.getImage(wList[magentaImage2_idx])

			ic = ImageCalculator()
			magentaImage = ic.run("Max create",magentaImage1,magentaImage2)
			magentaImage.show()			

			# Performs color conversion
			magentaImage1.close()
			magentaImage2.close()
			params = "c2=["+greenImage.getTitle()+"] c6=["+magentaImage.getTitle()+"] create ignore"
			IJ.run("Merge Channels...", params)
			compositeImage = WindowManager.getImage(WindowManager.getIDList()[-1])
			IJ.save(compositeImage,theDir+"/Composite-"+labelattach+".tif")
	