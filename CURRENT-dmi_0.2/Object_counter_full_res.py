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

od = OpenDialog("Select LSM file to work on...")
imagePath = od.getPath()
if (imagePath is not None):
	tileDir = imagePath + "_tiles/"
	if (os.path.exists(tileDir)):
		metadata = IJ.openAsString(tileDir+"tile_info.txt")

		## Creates directory to store analysis files
		if not os.path.exists(tileDir + "objects"):
			os.mkdir(tileDir + "objects")
	
		## Analyzes the tile metadata
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

		## Opens a tile in the middle of the stitched image
		tileToOpen = int(xtiles/2) * int(ytiles/2)
		windowName = "tile_" + str(tileToOpen) + ".ome.tif"
		params = "open=["+ tileDir +"tile_"+str(tileToOpen)+".ome.tif] color_mode=Default view=Hyperstack stack_order=XYCZT"	
	
		## Gets the number of channels in the image
		IJ.run("Bio-Formats Importer", params);
		testTile = WindowManager.getImage(windowName)
		numTotalChannels = testTile.getNChannels()
		labels = ["" for x in range(numTotalChannels)]
		defaultValues = [False for x in range(numTotalChannels)]
		for i in range(1,numTotalChannels+1):
			labels[i-1] = "Channel" + str(i)
			defaultValues[i-1] = False
	
		## Allows user to choose which channels to analyze
		gd = NonBlockingGenericDialog("Select channel...")
		gd.addCheckboxGroup(numTotalChannels,1,labels,defaultValues)
		gd.showDialog()
		runOnChannel = [False for x in range(numTotalChannels)]
		for i in range(numTotalChannels):
			runOnChannel[i] = gd.getNextBoolean()

		## Runs the 3D object counter on all the tiles and saves the results to disk
		IJ.run("3D OC Options", "volume surface nb_of_obj._voxels nb_of_surf._voxels integrated_density mean_gray_value std_dev_gray_value median_gray_value minimum_gray_value maximum_gray_value centroid mean_distance_to_surface std_dev_distance_to_surface median_distance_to_surface centre_of_mass bounding_box dots_size=5 font_size=10 show_numbers white_numbers store_results_within_a_table_named_after_the_image_(macro_friendly) redirect_to=none");
		channelImage = ChannelSplitter.split(testTile)
		testTile.close()
		for i in range(numTotalChannels):
			if (runOnChannel[i]):
				channelImage[i].show()
				IJ.run(channelImage[i], "3D Objects Counter", "threshold=42 slice=47 min.=300 max.=24903680 statistics")
				IJ.saveAs("Results", "/Volumes/DUNCAN/2015/03_12_15 ERT2 Confetti DSS earlier trace/A5/9396-abluminal.lsm_tiles/objects/C" + str(i+1) + "-tile_45.csv")
				channelImage[i].close()

		resultsWindows = WindowManager.getAllNonImageWindows()
		for i in range(len(resultsWindows)):
			resultsWindows[i].dispose()
