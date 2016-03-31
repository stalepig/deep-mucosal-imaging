import re
import os
import shutil
from ij.gui import NonBlockingGenericDialog
from ij.gui import MessageDialog
from ij.io import OpenDialog
from ij import IJ
from ij import WindowManager
from ij import ImagePlus
from ij.plugin import ChannelSplitter
from ij.process import LUT
from java.awt import Color

## Function definitions
def make_image_binary(theImage):
	for z in range(1,theImage.getNSlices()+1):
		theImage.setSlice(z)
		theProcessor = theImage.getProcessor()
		for x in range(theImage.getWidth()):
			for y in range(theImage.getHeight()):
				if theProcessor.getPixel(x,y) > 0:
					theProcessor.putPixel(x,y,255)
	return theImage

## Main body of script
od = OpenDialog("Select parent LSM file to work on...")
parentLSMFilePath = od.getPath()
if (parentLSMFilePath is not None):
	try:
		if not os.path.isdir(parentLSMFilePath + "_tiles/objects/"):
			os.mkdir(parentLSMFilePath + "_tiles/objects/")
		if not os.path.isdir(parentLSMFilePath + "_tiles/surfaces/"):
			os.mkdir(parentLSMFilePath + "_tiles/surfaces/")
		if not os.path.isdir(parentLSMFilePath + "_tiles/maps/"):
			os.mkdir(parentLSMFilePath + "_tiles/maps/")
	except:
		print "Error making output directory"
		
	## Opens a tile to get number of channels in the image
	params = ("open=["+ parentLSMFilePath + "_tiles/tile_1.ome.tif] " + 
			"color_mode=Default view=Hyperstack stack_order=XYCZT")
	IJ.run("Bio-Formats Importer", params)
	testImage = WindowManager.getImage("tile_1.ome.tif")
	nChannels = testImage.getNChannels()
	testImage.close()

	## Gets the maximum number of tiles in the LSM file
	metadata = IJ.openAsString(parentLSMFilePath + "_tiles/tile_info.txt")
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
	nTiles = xtiles*ytiles
	
	## Opens the options dialog box
	gd = NonBlockingGenericDialog("Select channel...")
	gd.addChoice("Analysis_channel",["Channel "+str(i) for i in range(1,nChannels+1)],"Channel 1")
	gd.addChoice("Bleeding_channel",["Channel "+str(i) for i in range(nChannels+1)],"Channel 0")
	gd.addChoice("Refractive_reference_channel",["Channel "+str(i) for i in range(nChannels+1)],"Channel 0")
	gd.addNumericField("Intensity_threshold",128,0)
	gd.addNumericField("Size_threshold",100,0)
	gd.addChoice("Process_filter",["None","Min","Median"],"None")
	gd.addCheckbox("Operate_on_tile_subset",False)
	gd.addStringField("Which_tile_subset","1-4,9,11",12)
	gd.showDialog()

	## Parses the information from the dialog box
	if (gd.wasOKed()):
		analysisChannel = gd.getNextChoiceIndex()+1
		bleedingChannel = gd.getNextChoiceIndex()
		refChannel = gd.getNextChoiceIndex()
		intThreshold = gd.getNextNumber()
		sizeThreshold = gd.getNextNumber()
		processFilter = gd.getNextChoiceIndex()
		doSubset = gd.getNextBoolean()
		whichTiles = gd.getNextString()
		tileList = []
		parsingFailed = False
		if doSubset:
			try: 
				whichTilesDespaced = whichTiles.replace(" ","")
				tilesListed = whichTilesDespaced.split(",")
				for tile in tilesListed:
					tilesExpanded = tile.split("-")
					tilesExpanded = map(int,tilesExpanded)
					if (len(tilesExpanded) == 2):
						tilesExpanded = range(tilesExpanded[0],tilesExpanded[1]+1)
					tileList = tileList + tilesExpanded
				tileList = list(set(tileList))
				tileList = filter(lambda x: True if x<nTiles+1 else False,tileList)
				print tileList
			except:
				IJ.log("Problem parsing your tile subset!")
				parsingFailed = True	
		else:
			tileList = range(1,nTiles+1)

		## Applies corrections to individual tiles, then runs the object counter
		if not parsingFailed:
			for tile in tileList:
				params = ("open=["+ parentLSMFilePath + "_tiles/tile_" + str(tile) + ".ome.tif] " + 
						"color_mode=Default view=Hyperstack stack_order=XYCZT")
				IJ.run("Bio-Formats Importer", params)
				theImage = WindowManager.getImage("tile_" + str(tile) + ".ome.tif")
				calibration = theImage.getCalibration()
				channelImages = ChannelSplitter.split(theImage)
				if (bleedingChannel > 0):
					params = ("bleeding_channel=" + str(bleedingChannel) + " bloodied_channel=" + str(analysisChannel) + " " +
							"allowable_saturation_percent=1.0 rsquare_threshold=0.50")
					IJ.run("Remove Bleedthrough (automatic)", params)
					dataImage = WindowManager.getImage("Corrected_ch" + str(analysisChannel))
					if (refChannel > 0):
						refractCImage = channelImages[refChannel-1].duplicate()
						refractCImage.show()
						IJ.run("Merge Channels...", "c1=" + dataImage.getTitle() + " c2=" + refractCImage.getTitle() + " create ignore")
						mergedImage = WindowManager.getImage("Composite")
						params = ("reference_channel=2 application_channel=1 automatic_operation generate_log " +
								"max_slice=43 surface_slice=87")
						IJ.run(mergedImage,"Refractive Signal Loss Correction",params)
						dataImage = WindowManager.getImage("App Corrected")
						mergedImage.close()
						refCorrectedImage = WindowManager.getImage("Ref Corrected")
						refCorrectedImage.close()
				else:
					dataImage = channelImages[analysisChannel-1]
					if (refChannel > 0):
						params = ("reference_channel=" + str(refChannel) + 
								" application_channel=" + str(analysisChannel) + " automatic_operation" +
								" generate_log max_slice=43 surface_slice=87")
						IJ.run(theImage,"Refractive Signal Loss Correction",params)
						dataImage = WindowManager.getImage("App Corrected")
						refCorrectedImage = WindowManager.getImage("Ref Corrected")
						refCorrectedImage.close()
				dataImage.setLut(LUT.createLutFromColor(Color.WHITE))
				#dataImage.setCalibration(calibration)
				dataImage.show()
				if (processFilter > 0):
					if processFilter == 1:
						IJ.run(dataImage,"Minimum...", "radius=2 stack")
					if processFilter == 2:
						IJ.run(dataImage,"Median...", "radius=2 stack")
				theImage.close()
					
				## Now runs the object counter on the processed tile
				params = ("volume surface nb_of_obj._voxels " + 
						"nb_of_surf._voxels integrated_density mean_gray_value " +
						"std_dev_gray_value median_gray_value minimum_gray_value " +
						"maximum_gray_value centroid mean_distance_to_surface " + 
						"std_dev_distance_to_surface median_distance_to_surface centre_of_mass " +
						"bounding_box dots_size=5 font_size=10 " + 
						"redirect_to=none")
				IJ.run("3D OC Options", params)
				params = ("threshold=" + str(intThreshold) + 
						" slice=1 min.=" + str(sizeThreshold) + " max.=24903680 objects surfaces statistics")
				IJ.redirectErrorMessages(True)
				IJ.run(dataImage, "3D Objects Counter", params)
				dataImage.changes = False
				dataImage.close()

				## Saves the results table, surfaces image output, and run configuration
				surfacesImage = WindowManager.getImage("Surface map of " + dataImage.getTitle())
				IJ.run(surfacesImage,"8-bit","")
				surfacesImage = make_image_binary(surfacesImage)
				IJ.saveAsTiff(surfacesImage,parentLSMFilePath + "_tiles/surfaces/C" + str(analysisChannel) + "-tile_" + str(tile) + ".tif")
				surfacesImage.close()
				objectsImage = WindowManager.getImage("Objects map of " + dataImage.getTitle())
				IJ.run(objectsImage,"8-bit","")
				objectsImage = make_image_binary(objectsImage)
				IJ.saveAsTiff(objectsImage,parentLSMFilePath + "_tiles/maps/C" + str(analysisChannel) + "-tile_" + str(tile) + ".tif")
				objectsImage.close()
				IJ.selectWindow("Results")
				IJ.saveAs("Results",parentLSMFilePath + "_tiles/objects/C" + str(analysisChannel) + "-tile_" + str(tile) + ".csv")
			
			configData = ("Parent LSM file: " + parentLSMFilePath + "\n" +
						"Analysis channel: " + str(analysisChannel) + "\n" +
						"Bleeding channel: " + str(bleedingChannel) + "\n" +
						"Refractive correction reference channel: " + str(refChannel) + "\n" +
						"Intensity threshold (0-255): " + str(intThreshold) + "\n" +
						"Size threshold (voxels): " + str(sizeThreshold) + "\n" +
						"Process filter: " + str(processFilter) + "\n" +
						"Tiles: " + ','.join([str(i) for i in tileList]))
			IJ.saveString(configData,parentLSMFilePath+"_tiles/objects/runData-C" + str(analysisChannel) + ".txt")