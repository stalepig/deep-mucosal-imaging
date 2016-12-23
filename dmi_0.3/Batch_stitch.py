import glob
import os
from ij import IJ
from ij.io import DirectoryChooser
from ij.plugin import Memory

dc = DirectoryChooser("Choose directory of LSM files...")
dirPath = dc.getDirectory()
if dirPath is not None:
	fileList = glob.glob(dirPath+"*.lsm")

	for path in fileList:
		processImage = False
		theSize = os.path.getsize(path) / 1048576.0
		print theSize
		totFijiMem = Memory().maxMemory() / 1048576.0
		print totFijiMem
		if (theSize < totFijiMem/3.0):
			basename = os.path.splitext(os.path.basename(path))[0]
			outputPath = dirPath + basename + ".tif"
			if not os.path.exists(outputPath):
				processImage = True

			params = "type=[Positions from file] order=[Defined by image metadata] browse=[" + path + "] multi_series_file=[" + path + "] fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 compute_overlap ignore_z_stage increase_overlap=10 subpixel_accuracy computation_parameters=[Save memory (but be slower)] image_output=[Fuse and display]"
			print params
			if (processImage):
				try:
					IJ.run("Grid/Collection stitching", params)
					stitchedImage = IJ.getImage()
					IJ.saveAsTiff(stitchedImage,outputPath)
					stitchedImage.close()
				except:
					IJ.log("Failed to stitch and save " + path)
