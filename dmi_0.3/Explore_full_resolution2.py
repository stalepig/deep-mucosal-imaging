from ij.gui import GenericDialog
from ij.gui import NonBlockingGenericDialog
from ij.io import OpenDialog
from ij import IJ
from ij import WindowManager
from ij import ImageStack
from ij import ImagePlus
from ij.measure import ResultsTable
from ij.gui import WaitForUserDialog
from ij import CompositeImage
from ij.gui import PolygonRoi
from ij.gui import Roi
from java.awt import Color
from ij.process import LUT
from ij.plugin import CompositeConverter
import re
import os
import sys
import shutil
import math
import copy

## Function definitions
def parse_tile_info_file(path):
	metadata = IJ.openAsString(path)
	p = re.compile(r'Num planes per tile: (\d+)')
	m = p.search(metadata)
	if m is None:
		pptile = 0
	else:
		pptile = int(m.group(1))
	p = re.compile(r'Num channels: (\d+)')
	m = p.search(metadata)
	if m is None:
		channels = 0
	else:
		channels = int(m.group(1))
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
	return ([channels,nTiles,xtiles,ytiles,int(pptile/channels)])

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

def estimate_scale_multiplier(acquisition_path, resized_path):
	resized_image = IJ.openImage(resized_path)
	resized_dim = resized_image.getDimensions()
	resized_image.close()
	acquisition_image = IJ.openImage(acquisition_path)
	acquisition_dim = acquisition_image.getDimensions()
	cal = acquisition_image.getCalibration()
	acquisition_image.close()
	if ((resized_dim[0] == resized_dim[1]) and (acquisition_dim[0] == acquisition_dim[1])):
		scale = float(acquisition_dim[0])/float(resized_dim[0])
	else:
		scale = -1

	return([scale,resized_dim[0],acquisition_dim[0],cal])

def rearrange_tile_list(containment_tups_superlist):
	tile_dict = {}
	for roi in containment_tups_superlist:
		for tup in roi:
			tile_dict[str(tup[0])] = []
	for roi in containment_tups_superlist:
		for tup in roi:
			tile_dict[str(tup[0])].append(tup)

	return tile_dict

def upscale_coords(coords,scale):
	ret_coords = copy.deepcopy(coords)
	for key in ret_coords.keys():
		ret_coords[key] = [ret_coords[key][0]*scale,ret_coords[key][1]*scale,ret_coords[key][2]]
	return(ret_coords)

def get_list_from_dict(keys, the_dict):
	the_list = []
	for key in keys:
		the_list.append(the_dict[key])
	return(the_list)

def normalize_coords_in_list(coord_vals):
	ret_coords = [x[:] for x in coord_vals]
	
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
		ret_coords[i][0] = coord_vals[i][0] - min_x
		ret_coords[i][1] = coord_vals[i][1] - min_y
		ret_coords[i][2] = coord_vals[i][2] - min_z
	return(ret_coords)

def normalize_coords_in_dict(coords):
	ret_coords = copy.deepcopy(coords)
	
	min_x = sys.maxint
	min_y = sys.maxint
	min_z = sys.maxint
	for key in ret_coords.keys():
		if ret_coords[key][0] < min_x:
			min_x = ret_coords[key][0]
		if ret_coords[key][1] < min_y:
			min_y = ret_coords[key][1]
		if ret_coords[key][2] < min_z:
			min_z = ret_coords[key][2]
	for key in ret_coords.keys():
		ret_coords[key][0] = ret_coords[key][0] - min_x
		ret_coords[key][1] = ret_coords[key][1] - min_y
		ret_coords[key][2] = ret_coords[key][2] - min_z
	return(ret_coords)

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

def copy_fullsize_tiles(keys,source_dir,dest_dir,ext):
	try:
		if not os.path.isdir(dest_dir):
			os.mkdir(dest_dir)
		if len(os.listdir(dest_dir)) > 0:
			for afile in os.listdir(dest_dir):
				try:
					os.remove(dest_dir+afile)
				except:
					print "Error deleting old files in /subtiles/ directory" 
		for i in range(len(keys)):
			print(source_dir+keys[i]+ext)
			shutil.copyfile(source_dir+keys[i]+ext,dest_dir+"tile_"+str(i+1)+ext)
	except:
		print "Error copying tiles to new directory"


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


def stitch_from_tileconfig(input_dir):
	params = ("type=[Positions from file] order=[Defined by TileConfiguration] " +  
			"directory=" + input_dir + " " + 
			"layout_file=TileConfiguration.subtiles.txt " + 
			"fusion_method=[Linear Blending] regression_threshold=0.30 " +
			"max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 " +
			"subpixel_accuracy computation_parameters=[Save memory (but be slower)] " + 
			"image_output=[Fuse and display]")
	IJ.run("Grid/Collection stitching", params)

def draw_roi_on_full_res_tile(containing_tiles_dict,subupcoords_dict):
	masterXs = []
	masterYs = []
	for key in containing_tiles_dict.keys():
		if (len(containing_tiles_dict.keys())>1):
			active_image = WindowManager.getImage("Fused")
		else:
			active_image = WindowManager.getImage("tile_"+key+".ome.tif")
		for point in containing_tiles_dict[key]:
			masterXs.append(point[3]+subupcoords_dict["tile_"+str(point[0])][0])
			masterYs.append(point[4]+subupcoords_dict["tile_"+str(point[0])][1])
	proi = PolygonRoi(masterXs,masterYs,Roi.FREEROI)
	active_image.setRoi(proi)
	return active_image

## Main body of script starts here
od = OpenDialog("Select parent LSM file...")
parentLSMFilePath = od.getPath()
if parentLSMFilePath is not None:
	tileConfigFilePath = parentLSMFilePath + "_tiles/resized/TileConfiguration.registered.txt"
	scale_info = estimate_scale_multiplier(parentLSMFilePath+"_tiles/tile_1.ome.tif",parentLSMFilePath+"_tiles/resized/tile_1.tif")
	print scale_info
	coords = read_tileconfig_file(tileConfigFilePath)
	full_keys = ["tile_"+str(i) for i in range(1,len(coords.keys())+1)]
	coords_vals = normalize_coords_in_list(get_list_from_dict(full_keys,coords))
	im = IJ.getImage()
	if im.getNChannels() == 1:
		LUTarray = [LUT.createLutFromColor(Color.WHITE)]
	elif im.getNChannels() == 2:
		LUTarray = [LUT.createLutFromColor(Color.RED),LUT.createLutFromColor(Color.WHITE)]
	elif im.getNChannels() == 3:
		LUTarray = [LUT.createLutFromColor(Color.GREEN),LUT.createLutFromColor(Color.RED),LUT.createLutFromColor(Color.WHITE)]
	elif im.getNChannels() == 4:
		LUTarray = [LUT.createLutFromColor(Color.BLUE),LUT.createLutFromColor(Color.RED),LUT.createLutFromColor(Color.GREEN),LUT.createLutFromColor(Color.WHITE)]
	elif im.getNChannels() == 5:
		LUTarray = [LUT.createLutFromColor(Color.BLUE),LUT.createLutFromColor(Color.RED),LUT.createLutFromColor(Color.GREEN),LUT.createLutFromColor(Color.YELLOW),LUT.createLutFromColor(Color.WHITE)]
	else:
		LUTarray = []

	nbgd = NonBlockingGenericDialog("Pick freehand ROI")
	nbgd.setLocation(0,0)
	nbgd.addMessage("OK to run, cancel to exit")
	nbgd.showDialog()
	isContinue = nbgd.wasOKed()
	while isContinue:
		roi = im.getRoi()
		if (roi is not None):
			float_poly = roi.getFloatPolygon()
			containing_tiles_superlist = []
			for i in range(float_poly.npoints):
				containing_tiles_superlist.append(find_containing_tiles([float_poly.xpoints[i],float_poly.ypoints[i],0],coords_vals,scale_info[1],scale_info[2]))
			upscaled_coords = upscale_coords(coords,scale_info[0])
			containing_tiles_dict = rearrange_tile_list(containing_tiles_superlist)
			copy_fullsize_tiles(["tile_"+key for key in containing_tiles_dict.keys()],parentLSMFilePath+"_tiles/",parentLSMFilePath+"_tiles/subtiles/",".ome.tif")
			subupcoords_vals = normalize_coords_in_list(get_list_from_dict(["tile_"+key for key in containing_tiles_dict.keys()],upscaled_coords))
			hadStitched = False
			if len(containing_tiles_dict.keys())>1:
				for i in containing_tiles_dict.keys():
					IJ.log("Opened tile " + str(i))
				write_tileconfig_file(parentLSMFilePath+"_tiles/subtiles/TileConfiguration.subtiles.txt",subupcoords_vals,".ome.tif")
				stitch_from_tileconfig(parentLSMFilePath+"_tiles/subtiles/")
				hadStitched = True		
			else:
				IJ.run("Bio-Formats Importer", "open=" + parentLSMFilePath + "_tiles/tile_" + (containing_tiles_dict.keys())[0] + ".ome.tif color_mode=Default view=Hyperstack stack_order=XYCZT")
				IJ.log("Opened tile " + str((containing_tiles_dict.keys())[0]))
			subupcoords_dict = normalize_coords_in_dict(dict(("tile_"+k,upscaled_coords["tile_"+k]) for k in containing_tiles_dict.keys()))
			activeImage = draw_roi_on_full_res_tile(containing_tiles_dict,subupcoords_dict)
			if len(LUTarray) > 0:
				for ch in range(1,activeImage.getNChannels()+1):
					activeImage.setChannelLut(LUTarray[ch-1],ch)
				activeImage.updateAndDraw()
			if not hadStitched:
				IJ.run(activeImage,"Make Composite","")

		nbgd = NonBlockingGenericDialog("Pick freehand ROI")
		nbgd.setLocation(0,0)
		nbgd.addMessage("OK to run, cancel to exit")
		nbgd.showDialog()
		isContinue = nbgd.wasOKed()
		if activeImage is not None:
			activeImage.setTitle("Old image")