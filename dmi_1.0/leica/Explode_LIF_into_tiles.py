from loci.formats import ImageReader
from loci.formats import ImageWriter
from loci.formats import MetadataTools
from loci.formats.meta import IMetadata
from ij import IJ
import os
from ij.process import ByteProcessor
from ij import ImageStack
from ij import ImagePlus
from ij import CompositeImage
from ij.measure import Calibration
from ij.plugin import ZProjector
from ij.plugin import Memory
from ij.process import LUT
from java.awt import Color
import math
from ij.io import OpenDialog

def make_destination_directories(dest_dir,isDeleteContents):
	try:
		if not os.path.isdir(dest_dir):
			os.mkdir(dest_dir)
		if isDeleteContents and len(os.listdir(dest_dir)) > 0:
			for afile in os.listdir(dest_dir):
				try:
					os.remove(dest_dir+afile)
				except:
					print "Error deleting old files in " + dest_dir + " directory" 
	except:
		print "Error preparing output directory"

## allows user to select LIF file for analysis
od = OpenDialog("Select parent LIF file...")
currFilePath = od.getPath()
if (currFilePath is not None):
	outDirPath = currFilePath + "_exploded/"
	make_destination_directories(outDirPath,False)
	
	## initializes common variables
	omeMeta = MetadataTools.createOMEXMLMetadata()
	theReader = ImageReader()
	theReader.setMetadataStore(omeMeta)
	theReader.setId(currFilePath)
	print(theReader.getSeriesCount())
	theWriter = ImageWriter()
	tileCountDict = {}
	planeCountDict = {}
	downRatioDict = {}
	
	startPos = 0
	currPos = 0
	numX = 1
	numY = 1
	
	endedImage = False
	oldImageName = ""
	tileDimXDict = {}
	tileDimYDict = {}
	calAdjXDict = {}
	calAdjZDict = {}
	
	doIO = True

	## gets image size estimates for downsampling
	mem = Memory()
	memToUse = mem.maxMemory() / 4.0
	for ser in range(0,theReader.getSeriesCount()):
		theReader.setSeries(ser)
		seriesParentImage = omeMeta.getImageName(ser)
		if seriesParentImage in planeCountDict.keys():
			planeCountDict[seriesParentImage] = planeCountDict[seriesParentImage]+(theReader.getSizeC()*theReader.getSizeZ()*theReader.getSizeX()*theReader.getSizeY())	
		else:
			planeCountDict[seriesParentImage] = theReader.getSizeC()*theReader.getSizeZ()*theReader.getSizeX()*theReader.getSizeY()
			IJ.log("Assessing image " + seriesParentImage)
	
	## calculates the downsampling ratios
	for seriesParentImage in planeCountDict.keys():
		if (planeCountDict[seriesParentImage] < memToUse):
			downRatioDict[seriesParentImage] = 1.0
		else:
			downRatioDict[seriesParentImage] = memToUse / planeCountDict[seriesParentImage]
	print(downRatioDict)
	
	## writes the individual tiles to disk
	if (doIO):
		for ser in range(0,theReader.getSeriesCount()):
			cal = Calibration()
			cal.setXUnit("micron")
			cal.setYUnit("micron")
			cal.setZUnit("micron")
			
			theReader.setSeries(ser)
			seriesParentImage = omeMeta.getImageName(ser)
			if (seriesParentImage is not None):
				
				## these things you do after moving onto the next image
				if (seriesParentImage != oldImageName and ser > 0):
					tileDimXDict[oldImageName] = tileDimX
					tileDimYDict[oldImageName] = numY
				
				## these things you do when either continuing or starting a new image
				if seriesParentImage in tileCountDict.keys():
					tileCountDict[seriesParentImage] = tileCountDict[seriesParentImage]+1
					if (omeMeta.getPlanePositionX(ser,0).value() - startPos == 0):
						numX = numX + 1
					else:
						tileDimX = numX
						numX = 1
						numY = numY + 1
						# print("X: " + str(tileDimX) + ", Y: " + str(numY))
						startPos = omeMeta.getPlanePositionX(ser,0).value()
				else:
					tileCountDict[seriesParentImage] = 0
					startPos = omeMeta.getPlanePositionX(ser,0).value()
					numX = 1
					numY = 1
					
				seriesOutDirPath = outDirPath + seriesParentImage + "/"
				make_destination_directories(seriesOutDirPath,False)
				seriesOutFilePath = seriesOutDirPath + "tile_" + str(tileCountDict[seriesParentImage]+1) + ".tif"
				
				## generates resized tiles for stitching
				newDim = int(math.sqrt(downRatioDict[seriesParentImage])*theReader.getSizeX())
				cal.pixelWidth = omeMeta.getPixelsPhysicalSizeX(ser).value() / math.sqrt(downRatioDict[seriesParentImage])
				cal.pixelHeight = omeMeta.getPixelsPhysicalSizeY(ser).value() / math.sqrt(downRatioDict[seriesParentImage])
				cal.pixelDepth = omeMeta.getPixelsPhysicalSizeZ(ser).value()
				calAdjXDict[seriesParentImage] = cal.pixelWidth
				calAdjZDict[seriesParentImage] = cal.pixelDepth
				iStack = ImageStack(newDim,newDim)
				for z in range(0,theReader.getSizeZ()):
					for c in range(0,theReader.getSizeC()):	
						j = c*theReader.getSizeZ()+z
						bp = ByteProcessor(theReader.getSizeX(),theReader.getSizeY(),theReader.openBytes(j))
						bpsmall = bp.resize(newDim)
						iStack.addSlice("plane_" + str(j+1) + "_z_" + str(z) + "_c_" + str(c),bpsmall)
				
				theImage = ImagePlus(seriesParentImage+"_tile_"+str(tileCountDict[seriesParentImage]),iStack)
				theImage.setDimensions(theReader.getSizeC(),theReader.getSizeZ(),1)
				theImage.setCalibration(cal)
				compImage = CompositeImage(theImage,CompositeImage.COMPOSITE)
				IJ.saveAsTiff(compImage,seriesOutFilePath)
				IJ.log("tile_" + str(tileCountDict[seriesParentImage]+1) + ":" + seriesParentImage + " (" + str(ser+1) + " of " + str(theReader.getSeriesCount()) + ")")
				oldImageName = seriesParentImage
				
		tileDimXDict[oldImageName] = tileDimX
		tileDimYDict[oldImageName] = numY
		
		## performs stitching
		for seriesParentImage in tileCountDict.keys():
			params = "type=[Grid: snake by rows] order=[Right & Down                ]"
			params = params + " grid_size_x=" + str(tileDimXDict[seriesParentImage])
			params = params + " grid_size_y=" + str(tileDimYDict[seriesParentImage])
			params = params + " tile_overlap=10 first_file_index_i=1"
			params = params + " directory=" + outDirPath + seriesParentImage
			params = params + " file_names=tile_{i}.tif output_textfile_name=TileConfiguration.txt fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50"
			params = params + " absolute_displacement_threshold=3.50 compute_overlap ignore_z_stage computation_parameters=[Save memory (but be slower)] image_output=[Fuse and display]"
			IJ.run("Grid/Collection stitching", params)
			stitchedImage = IJ.getImage()
			
			cal = Calibration()
			cal.setXUnit("micron")
			cal.setYUnit("micron")
			cal.setZUnit("micron")
			cal.pixelWidth = calAdjXDict[seriesParentImage]
			cal.pixelHeight = calAdjXDict[seriesParentImage]
			cal.pixelDepth = calAdjZDict[seriesParentImage]
			stitchedImage.setCalibration(cal)
			
			if stitchedImage.getNChannels() == 1:
				LUTarray = [LUT.createLutFromColor(Color.WHITE)]
			elif stitchedImage.getNChannels() == 2:
				LUTarray = [LUT.createLutFromColor(Color.RED),LUT.createLutFromColor(Color.WHITE)]
			elif stitchedImage.getNChannels() == 3:
				LUTarray = [LUT.createLutFromColor(Color.GREEN),LUT.createLutFromColor(Color.RED),LUT.createLutFromColor(Color.WHITE)]
			elif stitchedImage.getNChannels() == 4:
				LUTarray = [LUT.createLutFromColor(Color.BLUE),LUT.createLutFromColor(Color.GREEN),LUT.createLutFromColor(Color.RED),LUT.createLutFromColor(Color.WHITE)]
			else:
				LUTarray = [LUT.createLutFromColor(Color.BLUE),LUT.createLutFromColor(Color.GREEN),LUT.createLutFromColor(Color.YELLOW),LUT.createLutFromColor(Color.RED),LUT.createLutFromColor(Color.WHITE)]
			
			if (stitchedImage.getNChannels() <= 5):
				for ch in range(1,stitchedImage.getNChannels()+1):
					stitchedImage.setChannelLut(LUTarray[ch-1],ch)
				stitchedImage.updateAndDraw()
							
			IJ.saveAsTiff(stitchedImage,outDirPath + seriesParentImage + "_composite.tif")
			
			zImage = ZProjector.run(stitchedImage,"max")
			IJ.saveAsTiff(zImage,outDirPath + seriesParentImage + "_composite_mip.tif")
			
			stitchedImage.close()
			zImage.close()
			