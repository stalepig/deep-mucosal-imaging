import os
import math


# Gets the input LSM image
theOpenDialog = OpenDialog("Choose large LSM file to open...")
theFilePath = theOpenDialog.getPath()
if not(theFilePath is None):
	theDirectory = theOpenDialog.getDirectory()
	theFileName = theOpenDialog.getFileName()
	baseName = os.path.splitext(theFileName)[0]
		
	# Creates the output directory
	if not os.path.exists(theDirectory + baseName + "_resized"):
		os.mkdir(theDirectory + baseName + "_resized")

	# Asks for parameters
	gd = GenericDialog("Set Parameters...")
	gd.addNumericField("Start tile:",1,0)
	gd.addNumericField("Finish tile:",9,0)
	gd.addNumericField("Final disk space / Initial disk space:",0.25,2)
	gd.addNumericField("Step size (higher is faster but uses more memory):",10,0)
	gd.showDialog()
	startTile = int(gd.getNextNumber())
	finishTile = int(gd.getNextNumber())
	ratioRaw = gd.getNextNumber()
	ratio = math.sqrt(ratioRaw)
	stepSize = int(gd.getNextNumber())
	
	# Performs scaling
	if (gd.wasOKed()):
		anchorTiles = range(startTile,finishTile+1,stepSize)
		print anchorTiles
		for i in anchorTiles:
			if (i+stepSize-1 > finishTile):
				lastAnchorTile = finishTile
			else:
				lastAnchorTile = i+stepSize-1
			
			iterTiles = range(i,lastAnchorTile+1)
			params = "open=[" + theFilePath + "] color_mode=Default view=Hyperstack stack_order=XYCZT series_list=" + str(i) + "-" + str(lastAnchorTile)
			print params
			IJ.run("Bio-Formats Importer", params)
			imageIDList = WindowManager.getIDList()
			if (len(imageIDList) == len(iterTiles)):
				count = 0
				for j in imageIDList:
					theImage = WindowManager.getImage(j)
					print theImage.getTitle()
					params2 = "x=" + str(ratio) + " y=" + str(ratio) + " z=1.0 interpolation=Bilinear average create title=doggie"
					IJ.run(theImage,"Scale...",params2)
					theImage.close()
					saveImage = WindowManager.getImage("doggie")
					IJ.saveAsTiff(saveImage,theDirectory+baseName+"_resized/tile_"+str(iterTiles[count])+".tif")
					saveImage.close()
					count = count + 1
			else:
				print "Open image count does not match tile count!"	
