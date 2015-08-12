import re
import os

dc = DirectoryChooser("Choose directory with image tiles you want to stitch...")
sourceDir = dc.getDirectory()

opener = OpenDialog("Select DMI metadata file...",sourceDir,"tile_info.txt")
metadata_file = opener.getPath()

gd = GenericDialog("Input image name...")
gd.addStringField("Name your image (write a prefix):","IMGid")
gd.addMessage("Input directory: " + sourceDir)
gd.showDialog()
img_name = gd.getNextString()
outputPath = sourceDir + img_name + "_seq"

if sourceDir is not None and metadata_file is not None:
	
	## computes tiling information from DMI metadata
	metadata = IJ.openAsString(metadata_file)
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
	
	## Creates output directory if it doesn't already exist
	if not os.path.exists(outputPath):
		os.mkdir(outputPath)

	## Performs stitching
	if xtiles > 0 and ytiles > 0:
		params = ("type=[Grid: row-by-row] order=[Right & Down                ] grid_size_x=" +
			str(xtiles) + " grid_size_y=" + str(ytiles) + " tile_overlap=10 first_file_index_i=1 " +
			"directory=[" + sourceDir + "] file_names=tile_{i}.tif output_textfile_name=TileConfiguration.txt" +
			" fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50" + 
			" compute_overlap ignore_z_stage subpixel_accuracy computation_parameters=[Save memory (but be slower)]" + 
			" image_output=[Write to disk] output_directory=[" + outputPath + "]")
		print params
		IJ.run("Grid/Collection stitching", params)