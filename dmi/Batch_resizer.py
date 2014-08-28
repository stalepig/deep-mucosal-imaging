import os
import glob
import math

dc = DirectoryChooser("Choose directory with OME.TIF files...")
sourceDir = dc.getDirectory()

if not(sourceDir is None):
	if not os.path.exists(sourceDir + "resized"):
		os.mkdir(sourceDir + "resized")

	gd = GenericDialog("Set Parameters...")
	gd.addNumericField("Final disk space / Initial disk space:",0.25,2)
	gd.showDialog()
	ratioRaw = gd.getNextNumber()
	ratio = math.sqrt(ratioRaw)

	if (gd.wasOKed()):		
		filecollection = glob.glob(os.path.join(sourceDir, '*.ome.tif'))
		numFiles = len(filecollection)
		count = 1
		for f in filecollection:
			bname1 = os.path.basename(f)
			bname2 = os.path.splitext(bname1)[0]
			bname3 = os.path.splitext(bname2)[0]
			print bname3
		
			params = "open=[" + f + "] color_mode=Default view=Hyperstack stack_order=XYCZT"
			IJ.run("Bio-Formats Importer",params)
		
			theImage = WindowManager.getCurrentImage()
	
			params2 = "x=" + str(ratio) + " y=" + str(ratio) + " z=1.0 interpolation=Bilinear average process create title=doggie"
			IJ.run(theImage,"Scale...",params2)
			theImage.close()
			saveImage = WindowManager.getImage("doggie")
			savePath = sourceDir+"resized/"+bname3+".tif"
			IJ.saveAsTiff(saveImage,sourceDir+"resized/"+bname3+".tif")
			saveImage.close()
			IJ.showStatus("Tile: " + str(count) + "/" + str(numFiles))
			count = count + 1
