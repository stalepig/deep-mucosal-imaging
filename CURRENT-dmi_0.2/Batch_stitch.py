import glob
import os
from ij import IJ
from ij.io import DirectoryChooser

dc = DirectoryChooser("Choose directory of LSM files...")
dirPath = dc.getDirectory()
if dirPath is not None:
	fileList = glob.glob(dirPath+"*.lsm")

	for path in fileList:
		basename = os.path.splitext(os.path.basename(path))[0]
		outputPath = dirPath + basename + "_stitched"
		if not os.path.exists(outputPath):
			os.mkdir(outputPath)

		params = "type=[Positions from file] order=[Defined by image metadata] browse=[" + path + "] multi_series_file=[" + path + "] fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 compute_overlap ignore_z_stage increase_overlap=10 subpixel_accuracy computation_parameters=[Save memory (but be slower)] image_output=[Write to disk] output_directory=[" + outputPath + "]";
		IJ.run("Grid/Collection stitching", params)
