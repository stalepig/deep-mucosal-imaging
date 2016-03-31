import re
import os
import shutil
from ij.io import DirectoryChooser
from ij.gui import NonBlockingGenericDialog
from ij.gui import GenericDialog
from ij import IJ
from ij import WindowManager

#### Function definitions ########
def find_index_greater_zero(arr):
	for i in range(len(arr)):
		if (arr[i] >= 0):
			return i
	return len(arr)

def find_tile_range(mi,ma,arr):
	arr1 = [x - mi for x in arr]
	arr2 = [x - ma for x in arr]
	start = find_index_greater_zero(arr1)
	end = find_index_greater_zero(arr2)
	length = end-start+1
	return [start,end,length]

def make_tile_series(xs,ys,xlen,ylen):
	arr = []
	for y in range(ys[0],ys[1]+1):
		arr.extend(range(xlen*y+xs[0],xlen*y+xs[1]+1))
	arr = [m+1 for m in arr]
	return arr

##### Sets directory of full-res tiles and gets metadata ######
dc = DirectoryChooser("Choose directory where full-res tiles are stored...")
imgDir = dc.getDirectory()
metadata = IJ.openAsString(imgDir+"tile_info.txt")
p = re.compile(r'X Tiles: (\d+)')
m = p.search(metadata)
if m is None:
	xtiles = 0
else:
	xtiles = int(m.group(1))
p = re.compile(r'Y Tiles: (\d+)')
m = p.search(metadata)
if m is None:
	ytiles = 0
else:
	ytiles = int(m.group(1))
if not os.path.exists(imgDir + "temp"):
	os.mkdir(imgDir + "temp")
if not os.path.exists(imgDir + "substitched"):
	os.mkdir(imgDir + "substitched")
fileList = os.listdir(imgDir + "substitched")
for f in fileList:
	if (os.path.isdir(imgDir+"substitched/"+f) == False):
		os.unlink(imgDir+"substitched/"+f)

#### Draw grid #####
theImage = IJ.getImage()
visSlice = theImage.getSlice()
IJ.run("Colors...","foreground=cyan background=cyan selection=yellow")
colDim = theImage.getWidth() / (xtiles)
rowDim = theImage.getHeight() / (ytiles)
rowStarts = range(rowDim,theImage.getHeight()-xtiles,rowDim)
colStarts = range(colDim,theImage.getWidth()-ytiles,colDim)
rowCenters = list(rowStarts)
rowCenters.insert(0,0)
colCenters = list(colStarts)
colCenters.insert(0,0)
for i in range(0,len(rowCenters)):
	rowCenters[i] = rowCenters[i] + rowDim - rowDim/8
for i in range(0,len(colCenters)):
	colCenters[i] = colCenters[i] + colDim/2

for i in rowStarts:
	IJ.makeLine(0,i,theImage.getWidth(),i)
	IJ.run("Draw","stack")
for i in colStarts:
	IJ.makeLine(i,0,i,theImage.getHeight())
	IJ.run("Draw","stack")

numSlices = theImage.getNSlices() * theImage.getNChannels() * theImage.getNFrames()
for zslice in range(1,numSlices+1):
	theImage.setSliceWithoutUpdate(zslice)
	ip = theImage.getProcessor()
	ip.setColor(255*255)
	for i in range(0,len(colCenters)):
		for j in range(0,len(rowCenters)):
			theString = str(int(j*xtiles+i+1))
			ip.drawString(theString,int(colCenters[i]),int(rowCenters[j]))
theImage.updateAndDraw()
theImage.setSlice(visSlice)

### Sets up main interface for visualization #####
gd = NonBlockingGenericDialog("Explore full resolution...")
gd.addMessage("Select ROI for visualization at full resolution")
gd.showDialog()
doContinue = gd.wasOKed()
while (doContinue):
	roi = theImage.getRoi()
	boundRect = roi.getBounds()
	xmin = boundRect.getX()
	xmax = xmin + boundRect.getWidth()
	ymin = boundRect.getY()
	ymax = ymin + boundRect.getHeight()
	xs = find_tile_range(xmin,xmax,colStarts)
	ys = find_tile_range(ymin,ymax,rowStarts)
	tiles = make_tile_series(xs,ys,xtiles,ytiles)
	print tiles

	# Copies tiles for stitching into temp directory and stitches, if necessary
	if len(tiles)==1:
		params = "open=["+ imgDir +"tile_"+str(tiles[0])+".ome.tif] color_mode=Default view=Hyperstack stack_order=XYCZT"
		IJ.run("Bio-Formats Importer", params);
		tileImage = WindowManager.getImage("tile_"+str(tiles[0])+".ome.tif")
		tileImage.setSlice(int(tileImage.getNSlices()/2))
	else:
		ind = 1
		tileDiskSize = os.path.getsize(imgDir+"tile_"+str(tiles[0])+".ome.tif")
		totalDiskSize = tileDiskSize * len(tiles)
		totalDiskSizeMB = totalDiskSize / 1048576
		sizeGD = GenericDialog("Warning")
		sizeGD.addMessage("Memory used by selected tiles is " + str(totalDiskSizeMB) + "MB. Continue?")
		sizeGD.addCheckbox("Compute overlap",False)
		sizeGD.addNumericField("Tile overlap percentage",10,0)
		sizeGD.addCheckbox("Write fused image sequence to disk",False)
		sizeGD.showDialog()
		doComputeOverlap = sizeGD.getNextBoolean()
		overlapPctStr = str(sizeGD.getNextNumber())
		doWriteToDisk = sizeGD.getNextBoolean()
		if (doComputeOverlap):
			overlapText = "compute_overlap ignore_z_stage"
		else:
			overlapText = ""
		if (doWriteToDisk):
			outputPath = imgDir + "substitched"
			diskWriteText = "image_output=[Write to disk] output_directory=[" + outputPath + "]"
		else:
			diskWriteText = "image_output=[Fuse and display]"
		if (sizeGD.wasOKed()):
			for t in tiles:
				shutil.copyfile(imgDir+"tile_"+str(t)+".ome.tif",imgDir+"temp/tile_"+str(ind)+".ome.tif")
				ind = ind + 1
			IJ.showStatus("Beginning stitch...")
			params = ("type=[Grid: row-by-row] order=[Right & Down                ] grid_size_x=" + 
				str(xs[2]) + " grid_size_y=" + str(ys[2]) + " tile_overlap=" + overlapPctStr + " first_file_index_i=1 directory=[" + 
				imgDir + "temp] file_names=tile_{i}.ome.tif output_textfile_name=TileConfiguration.txt " + 
				"fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 " +
				"absolute_displacement_threshold=3.50 " + overlapText + " subpixel_accuracy " + 
				"computation_parameters=[Save memory (but be slower)] " + diskWriteText)
			IJ.run("Grid/Collection stitching", params)
	
	gd = NonBlockingGenericDialog("Explore full resolution...")
	gd.addMessage("Select ROI for visualization at full resolution")
	gd.showDialog()
	doContinue = gd.wasOKed()

##### Removes temporary tile files ######
# filelist = [f for f in os.listdir(imgDir+"temp") if f.endswith(".tif")]
# for f in filelist:
#	os.remove(f)