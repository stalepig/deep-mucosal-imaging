openImgs = WindowManager.getIDList()
openImgTitles = []
if len(openImgs) > 1:
	for theID in openImgs:
		img = WindowManager.getImage(theID)
		openImgTitles.append(img.getTitle())

	gd = NonBlockingGenericDialog("Pairwise montage parameters...")
	gd.addChoice("Image 1:",openImgTitles,openImgTitles[0])
	gd.addNumericField("Image 1, start slice:",1,0)
	gd.addNumericField("Image 1, end slice:",100,0)
	gd.addChoice("Image 2:",openImgTitles,openImgTitles[1])
	gd.addNumericField("Image 2, start slice:",1,0)
	gd.addNumericField("Image 2, end slice:",100,0)
	gd.addRadioButtonGroup("Keep:",["interval", "number of slices"],2,1,"interval")
	gd.addNumericField("interval/number of slices",5,0)
	gd.showDialog()

	if (gd.wasOKed()):
		img1_idx = gd.getNextChoiceIndex()
		img1 = WindowManager.getImage(openImgs[img1_idx])
		startSlice1 = int(gd.getNextNumber())
		endSlice1 = int(gd.getNextNumber())
		img2_idx = gd.getNextChoiceIndex()
		img2 = WindowManager.getImage(openImgs[img2_idx])
		startSlice2 = int(gd.getNextNumber())
		endSlice2 = int(gd.getNextNumber())
		choice = gd.getNextRadioButton()
		skipstack = int(gd.getNextNumber())
		if (startSlice1 >= 1 and endSlice1 <= img1.getNSlices()):
			if (choice == "interval"):
				params = "slices="+str(startSlice1)+"-"+str(endSlice1)+"-"+str(skipstack)
			else:
				interval = int((endSlice1-startSlice1+1)/float(skipstack))
				params = "slices="+str(startSlice1)+"-"+str(endSlice1-interval)+"-"+str(interval)
			IJ.run(img1,"Make Substack...",params)
#			img1_cut = WindowManager.getImage(img1.getTitle()+"-1")
#			params = "columns=" + str(img1_cut.getNSlices()) + " rows=1 scale=0.25 increment=1 border=1 font=12"
#			IJ.run(img1_cut,"Make Montage...",params)
#			img1_cut.close()
		if (startSlice2 >= 1 and endSlice2 <= img2.getNSlices()):
			if (choice == "interval"):
				params = "slices="+str(startSlice2)+"-"+str(endSlice2)+"-"+str(skipstack)
			else:
				interval = int((endSlice2-startSlice2+1)/float(skipstack))
				params = "slices="+str(startSlice2)+"-"+str(endSlice2-interval)+"-"+str(interval)
				print params
			IJ.run(img2,"Make Substack...",params)
#			img2_cut = WindowManager.getImage(img2.getTitle()+"-1")
#			params = "columns=" + str(img2_cut.getNSlices()) + " rows=1 scale=0.25 increment=1 border=1 font=12"
#			IJ.run(img2_cut,"Make Montage...",params)
#			img2_cut.close()
		