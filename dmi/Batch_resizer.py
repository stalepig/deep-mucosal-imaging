import os
import glob
import math

def get_directory_size(sourceDir):
	sumSize = 0
	files = glob.glob(os.path.join(sourceDir,'*.ome.tif'))
	for theFile in files:
		theSize = os.path.getsize(theFile)
		sumSize = sumSize + theSize
	return sumSize

def calculate_memory_recs(dirsize,maxmem):
	values = []
	maxchannel = maxmem / 10
	maxtot = long(maxmem * 0.3)
	for i in range(1,6):
		if (maxtot/i > maxchannel):
			values.append((maxchannel*i)/1048576)
		else:
			values.append(maxtot/1048576)
	return values

dc = DirectoryChooser("Choose directory with OME.TIF files...")
sourceDir = dc.getDirectory()

if not(sourceDir is None):
	if not os.path.exists(sourceDir + "resized"):
		os.mkdir(sourceDir + "resized")

	dirSize = get_directory_size(sourceDir)
	dirSizeMB = dirSize / 1048576
	memoryObj = Memory()
	memFiji = memoryObj.maxMemory()
	memFijiMB = memFiji / 1048576

	gd = GenericDialog("Set Parameters...")
	gd.addNumericField("Final disk space / Initial disk space:",0.25,2)
	gd.addMessage("Directory size: " + str(dirSizeMB) + "MB")
	gd.addMessage("Maximum memory: " + str(memFijiMB) + "MB")
	mem_recs = calculate_memory_recs(dirSize,memFiji)
	print mem_recs
	for i in range(0,len(mem_recs)):
		ratio_rec = float(mem_recs[i]) / dirSizeMB
		print ratio_rec
		ratio_rec_str = "%.3f" % ratio_rec
		gd.addMessage(str(i+1)+"-channel: " + str(mem_recs[i]) + "MB; Ratio: " + ratio_rec_str)
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
