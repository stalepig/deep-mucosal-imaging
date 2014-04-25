def average(pts):
	summer = 0.0
	for pt in pts:
		summer = summer + pt
	return (summer / len(pts))

def is_monotonic_increasing(pts):
	if len(pts) > 1:
		for i in range(1,len(pts)):
			diff = pts[i] - pts[i-1]
			if (diff < 0):
				return False
	return True
		
theImage = IJ.getImage()
stayinloop = True
IJ.run("RGB Color")

injuryfirst = True
injuryLengths = []
totalLengths = []
injuryRatios = []
Xpositions = []
while stayinloop:
	gd = NonBlockingGenericDialog("Pick points...")
	gd.addMessage("Use multipoint tool to pick points along a column (Y-axis).\nAlternate points to mark injured vs uninjured area.")
	gd.setCancelLabel("Quit")
	gd.setOKLabel("Define column")
	gd.addCheckbox("First segment is injury?",injuryfirst)
	gd.showDialog()

	if (gd.wasOKed()):
		roi = theImage.getRoi()
		if roi is None:
			IJ.error("No ROI selected")
		else:		
			polygon = roi.getFloatPolygon()

			if len(polygon.xpoints) % 2 == 0 and is_monotonic_increasing(polygon.ypoints):
				xset = average(polygon.xpoints)
				IJ.setForegroundColor(255,255,0)
				IJ.run("Draw","stack")
				IJ.makeLine(xset,0,xset,theImage.getHeight())
				IJ.setForegroundColor(0,255,255)
				IJ.run("Draw","stack")

				injuryfirst = gd.getNextBoolean()
				if injuryfirst:
					countidx = range(0,len(polygon.xpoints)-1,2)
				else:
					countidx = range(1,len(polygon.xpoints)-1,2)

				injuryLength = 0.0
				for idx in countidx:
					injuryLength = injuryLength + (polygon.ypoints[idx+1]-polygon.ypoints[idx])
				totalLength = polygon.ypoints[-1]-polygon.ypoints[0]
				injuryRatio = injuryLength / totalLength

				injuryLengths.append(injuryLength)
				totalLengths.append(totalLength)
				injuryRatios.append(injuryRatio)
				Xpositions.append(xset)
			else:
				IJ.error("Need an even number of points that go from top to bottom of image!")
			
		stayinloop = True
	else:
		stayinloop = False

if len(Xpositions) > 0:
	sd = SaveDialog("Save data file...",theImage.getShortTitle()+"_injury",".csv")
	filename = sd.getFileName()
	filedir = sd.getDirectory()
	outpath = filedir + filename
	fileobj = open(outpath,"w")
	for i in range(len(Xpositions)):
		fileobj.write(str(Xpositions[i])+","+str(injuryLengths[i])+","+str(totalLengths[i])+","+str(injuryRatios[i])+"\n")
	fileobj.close()