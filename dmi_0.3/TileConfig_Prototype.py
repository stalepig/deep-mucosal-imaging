import re
import sys
import shutil
from ij import IJ
from ij.gui import WaitForUserDialog
from ij.process import FloatPolygon
from ij.gui import PointRoi
from ij import WindowManager

def read_tileconfig_file(path):	
	coords = {}	
	try:
		f = open(path, "r")
		tileConfigContents = f.readlines()
		p = re.compile(r'(tile_.*).tif.*\((.*)\)')
		for line in tileConfigContents:
			m = p.search(line)
			if m is not None:
				tup = re.split(", ",m.group(2))
				tup_float = map(float,tup)
				coords[m.group(1)] = tup_float
	except (IOError,OSError):
		print "Problem opening tile configuration file"
	finally:
		f.close()
	return coords

def get_list_from_dict(keys, the_dict):
	the_list = []
	for key in keys:
		the_list.append(the_dict[key])
	return(the_list)

def normalize_coords_in_list(coord_vals):
	min_x = sys.maxint
	min_y = sys.maxint
	min_z = sys.maxint
	for i in range(0,len(coord_vals)):
		if (coord_vals[i][0] < min_x):
			min_x = coord_vals[i][0]
		if (coord_vals[i][1] < min_y):
			min_y = coord_vals[i][1]
		if (coord_vals[i][2] < min_z):
			min_z = coord_vals[i][2]
	for i in range(0,len(coord_vals)):
		coord_vals[i][0] = coord_vals[i][0] - min_x
		coord_vals[i][1] = coord_vals[i][1] - min_y
		coord_vals[i][2] = coord_vals[i][2] - min_z
	return(coord_vals)
	
def write_tileconfig_file(path, coord_vals, ext):
	try:
		f = open(path, "w")
		f.write("# Define the number of dimensions we are working on\n")
		f.write("dim = 3\n\n")
		f.write("# Define the image coordinates\n")
		for i in range(1,len(coord_vals)+1):
			f.write("tile_"+str(i)+ext+"; ; ("+str(coord_vals[i-1][0])+", "+str(coord_vals[i-1][1])+", "+str(coord_vals[i-1][2])+")\n")
	except (IOError,OSError):
		print "Problem writing to the tile configuration file"
	finally:
		f.close()

def estimate_scale_multiplier(acquisition_path, resized_path):
	resized_image = IJ.openImage(resized_path)
	resized_dim = resized_image.getDimensions()
	resized_image.close()
	acquisition_image = IJ.openImage(acquisition_path)
	acquisition_dim = acquisition_image.getDimensions()
	acquisition_image.close()
	if ((resized_dim[0] == resized_dim[1]) and (acquisition_dim[0] == acquisition_dim[1])):
		scale = float(acquisition_dim[0])/float(resized_dim[0])
	else:
		scale = -1
	
	return([scale,resized_dim[0],acquisition_dim[0]])

def upscale_coords(coords,scale):
	for key in coords.keys():
		coords[key] = [coords[key][0]*scale,coords[key][1]*scale,coords[key][2]]
	return(coords)

def copy_fullsize_tiles(keys,source_dir,dest_dir):
	try:
		for i in range(len(keys)):
			print(source_dir+keys[i]+".ome.tif")
			shutil.copyfile(source_dir+keys[i]+".ome.tif",dest_dir+"tile_"+str(i+1)+".ome.tif")
	except:
		print "Error copying tiles to new directory"

def stitch_from_tileconfig():
	params = ("type=[Positions from file] order=[Defined by TileConfiguration] " +  
			"directory=/Users/cambrian/Documents/work_adj/03-05.lsm_tiles/debug " + 
			"layout_file=TileConfiguration.debug.txt " + 
			"fusion_method=[Linear Blending] regression_threshold=0.30 " +
			"max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 " +
			"subpixel_accuracy computation_parameters=[Save memory (but be slower)] " + 
			"image_output=[Fuse and display]")
	IJ.run("Grid/Collection stitching", params)

def find_containing_tiles(point_tup,normed_coords_vals,resized_tile_length,full_tile_length):
	containing_tiles = []
	for i in range(len(coords_vals)):
		if ((point_tup[0] >= normed_coords_vals[i][0]) and (point_tup[1] >= normed_coords_vals[i][1])):
			if ((point_tup[0]-normed_coords_vals[i][0]) < resized_tile_length and (point_tup[1]-normed_coords_vals[i][1]) < resized_tile_length):
				x_resized_offset = point_tup[0]-normed_coords_vals[i][0]
				y_resized_offset = point_tup[1]-normed_coords_vals[i][1]
				x_full_offset = (x_resized_offset/resized_tile_length) * full_tile_length
				y_full_offset = (y_resized_offset/resized_tile_length) * full_tile_length
				containing_tiles.append([i+1,x_resized_offset,y_resized_offset,x_full_offset,y_full_offset])
	return(containing_tiles)

def draw_roi_on_full_res_tile(containment_tups_superlist,tile_dir,ext):
	tile_dict = {}
	for roi in containment_tups_superlist:
		for tup in roi:
			tile_dict[str(tup[0])] = []
	for roi in containment_tups_superlist:
		for tup in roi:
			tile_dict[str(tup[0])].append(tup)
	
	for key in tile_dict.keys():
		params = "open=["+ tile_dir + "tile_"+key+ext+"] color_mode=Default view=Hyperstack stack_order=XYCZT"
		IJ.run("Bio-Formats Importer", params)
		active_image = WindowManager.getImage("tile_"+key+ext)
		xs = [tup[3] for tup in tile_dict[key]]
		ys = [tup[4] for tup in tile_dict[key]]
		proi = PointRoi(xs,ys)
		active_image.setRoi(proi)

coords = read_tileconfig_file("/Users/cambrian/Documents/work_adj/03-05.lsm_tiles/resized/TileConfiguration.registered.txt")
full_keys = ["tile_"+str(i) for i in range(1,len(coords.keys())+1)]
coords_vals = normalize_coords_in_list(get_list_from_dict(full_keys,coords))
write_tileconfig_file("/Users/cambrian/Documents/work_adj/03-05.lsm_tiles/resized/TileConfiguration.normed.txt",coords_vals,".tif")
scale_info = estimate_scale_multiplier("/Users/cambrian/Documents/work_adj/03-05.lsm_tiles/tile_78.ome.tif","/Users/cambrian/Documents/work_adj/03-05.lsm_tiles/resized/tile_78.tif")
upscaled_coords = upscale_coords(coords,scale_info[0])
# subupcoords_vals = normalize_coords_in_list(get_list_from_dict(["tile_78","tile_79","tile_80"],upscaled_coords))
# copy_fullsize_tiles(["tile_78","tile_79","tile_80"],"/Users/cambrian/Documents/work_adj/03-05.lsm_tiles/","/Users/cambrian/Documents/work_adj/03-05.lsm_tiles/debug/")
# write_tileconfig_file("/Users/cambrian/Documents/work_adj/03-05.lsm_tiles/debug/TileConfiguration.debug.txt",subupcoords_vals,".ome.tif")
# stitch_from_tileconfig()

im = IJ.getImage()
wfud = WaitForUserDialog("Select an ROI, then click here")
wfud.show()
roi = im.getRoi()
if (roi is not None):
	float_poly = roi.getFloatPolygon()
	containing_tiles_superlist = []
	for i in range(float_poly.npoints):
		containing_tiles_superlist.append(find_containing_tiles([float_poly.xpoints[i],float_poly.ypoints[i],0],coords_vals,scale_info[1],scale_info[2]))
draw_roi_on_full_res_tile(containing_tiles_superlist,"/Users/cambrian/Documents/work_adj/03-05.lsm_tiles/",".ome.tif")