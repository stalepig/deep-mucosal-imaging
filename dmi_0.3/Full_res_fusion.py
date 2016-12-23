## Imports
from ij.io import OpenDialog
from ij import IJ
from ij import ImagePlus
from ij.process import ByteProcessor
from ij.plugin import RGBStackMerge
import re
import sys
import copy
import os

## Adds jar dependencies
sys.path.append("./formats-gpl.jar")
sys.path.append("./Image_stamper-0.1.0-SNAPSHOT.jar")

## Imports external classes
from loci.formats import ImageReader
from cambrian.dmi import Image_stamper

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


def make_destination_directories(dest_dir):
	try:
		if not os.path.isdir(dest_dir):
			os.mkdir(dest_dir)
		if len(os.listdir(dest_dir)) > 0:
			for afile in os.listdir(dest_dir):
				try:
					os.remove(dest_dir+afile)
				except:
					print "Error deleting old files in /v_img/ directory" 
	except:
		print "Error preparing output directory"

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

	coords_list = []
	for i in range(len(coords.keys())):
		coords_list.append(coords["tile_"+str(i+1)])
	return coords_list

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

def upscale_coords(coords,scale):
	ret_coords = copy.deepcopy(coords)
	for i in range(len(coords)):
		ret_coords[i] = [ret_coords[i][0]*scale,ret_coords[i][1]*scale,ret_coords[i][2]]
	return(ret_coords)

def round_coords(coords):
	ret_coords = []
	for i in range(len(coords)):
		ret_coords.append([int(round(coords[i][0])),int(round(coords[i][1])),int(round(coords[i][2]))])
	return(ret_coords)

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

def get_max_coordinates(coords):
	max_x = 0
	max_y = 0
	max_z = 0

	for i in range(0,len(coords)):
		if (coords[i][0] > max_x):
			max_x = coords[i][0]
		if (coords[i][1] > max_y):
			max_y = coords[i][1]
		if (coords[i][2] > max_z):
			max_z = coords[i][2]

	return([max_x,max_y,max_z])

## Main body of script starts here
od = OpenDialog("Select parent LSM file...")
parentLSMFilePath = od.getPath()
if parentLSMFilePath is not None:
	## Collects info about the image stack
	basic_info = parse_tile_info_file(parentLSMFilePath+"_tiles/tile_info.txt")
	make_destination_directories(parentLSMFilePath+"_tiles/v_img/")
	tileConfigFilePath = parentLSMFilePath + "_tiles/resized/TileConfiguration.registered.txt"
	scale_info = estimate_scale_multiplier(parentLSMFilePath+"_tiles/tile_1.ome.tif",parentLSMFilePath+"_tiles/resized/tile_1.tif")
	print scale_info
	coords_list = read_tileconfig_file(tileConfigFilePath)
	coords_normed = normalize_coords_in_list(coords_list)
	coords_upscaled = round_coords(upscale_coords(coords_normed,scale_info[0]))
	write_tileconfig_file(parentLSMFilePath+"_tiles/v_img/TileConfiguration.fullsize.txt",coords_upscaled,".ome.tif")
	max_coords = get_max_coordinates(coords_upscaled)
	print max_coords
	print basic_info

	## Outputs each stitched z plane as a separate file
	iReader = ImageReader()
	iReader.setId(parentLSMFilePath)
	for z in range(max_coords[2]+basic_info[4]):
	## for z in range(50,51):
		IJ.showStatus("z: "+str(z+1)+" of "+str(max_coords[2]+basic_info[4]))
		chIps = []
		resImages = []
		for ch in range(basic_info[0]):
			chIps.append(ByteProcessor(max_coords[0]+scale_info[2],max_coords[1]+scale_info[2]))
		for ch in range(basic_info[0]):
			resImages.append(ImagePlus("ch"+str(ch+1),chIps[ch]))
		for se in range(basic_info[1]):
			IJ.showProgress(se,basic_info[1])
			if z >= coords_upscaled[se][2] and z <= coords_upscaled[se][2]+basic_info[4]-1:
				iReader.setSeries(se)
				for ch in range(basic_info[0]):
					byteArray = iReader.openBytes((z-coords_upscaled[se][2])*basic_info[0]+ch)
					testIp = ByteProcessor(scale_info[2],scale_info[2],byteArray)
					testImage = ImagePlus("tester",testIp)
					Image_stamper.stampStack(testImage,resImages[ch],coords_upscaled[se][0],coords_upscaled[se][1],0)			
					activeIp = chIps[ch]
					testImage.close()
					
					
		for ch in range(len(resImages)):
			IJ.saveAsTiff(resImages[ch],parentLSMFilePath+"_tiles/v_img/img_z_"+str(z+1)+"_c_"+str(ch+1)+".tif")
		#outPlaneImage = RGBStackMerge.mergeChannels(resImages,False)
		#IJ.saveAsTiff(outPlaneImage,parentLSMFilePath+"_tiles/v_img/img_z_"+str(z+1)+".tif")
		#outPlaneImage.close()