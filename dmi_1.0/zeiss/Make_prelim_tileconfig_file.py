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
import datetime

## Adds jar dependencies
sys.path.append("./formats-gpl.jar")
sys.path.append("./Image_stamper-0.1.0-SNAPSHOT.jar")

## Imports external classes
from loci.formats import ImageReader
from loci.formats import MetadataTools
from cambrian.dmi import Image_stamper

## Function definitions
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

def round_coords(coords):
	ret_coords = []
	for i in range(len(coords)):
		ret_coords.append([int(round(coords[i][0])),int(round(coords[i][1])),int(round(coords[i][2]))])
	return(ret_coords)

def write_log_file(path,message):
	dt = datetime.datetime.now()
	try:
		f = open(path, "a")
		f.write("%s" % dt)
		f.write(": " + message + "\n")
	except (IOError,OSError):
		print "Problem writing to log file"
	finally:
		f.close()

def write_scalings_file(path,scale):
	try:
		f = open(path, "w")
		f.write("1 px = " + str(scale) + " µm\n")
	except (IOError,OSError):
		print "Problem writing to scale file"
	finally:
		f.close()

## Main body of script starts here
od = OpenDialog("Select parent LSM file...")
parentLSMFilePath = od.getPath()
if parentLSMFilePath is not None:
	## Makes new directory
	make_destination_directories(parentLSMFilePath+"_tiles/",False)

	## Reads LSM file for metadata
	iReader = ImageReader()
	meta = MetadataTools.createOMEXMLMetadata()
	iReader.setMetadataStore(meta)
	iReader.setId(parentLSMFilePath)
	numChannels = iReader.getSizeC()
	sizeX = iReader.getSizeX()
	sizeY = iReader.getSizeY()
	numZ = iReader.getSizeZ()
	numTiles = iReader.getSeriesCount()

	## Gets the preliminary plane positions from metadata
	coords = []
	scaleFactor = 0
	for i in range(numTiles):
		pos = []
		pos.append(meta.getPlanePositionX(i,0).value()/meta.getPixelsPhysicalSizeX(i).value())
		pos.append(meta.getPlanePositionY(i,0).value()/meta.getPixelsPhysicalSizeY(i).value())
		pos.append(meta.getPlanePositionZ(i,0).value())
		coords.append(pos)
		scaleFactor = meta.getPixelsPhysicalSizeY(i).value()
	coords_normed = round_coords(normalize_coords_in_list(coords))

	## Writes the tileconfig file
	write_tileconfig_file(parentLSMFilePath+"_tiles/TileConfiguration.fullsize.prelim.txt",coords_normed,".ome.tif")
	write_log_file(parentLSMFilePath+"_tiles/analysis.log.txt","Made preliminary tileconfig file")

	## Stitches the output files
	make_destination_directories(parentLSMFilePath+"_tiles/v_img/",True)
	write_scalings_file(parentLSMFilePath+"_tiles/Scalings.fullsize.txt",scaleFactor)
	max_coords = get_max_coordinates(coords_normed)
	for z in range(max_coords[2]+numZ):
		IJ.showStatus("z: "+str(z+1)+" of "+str(max_coords[2]+numZ))
		chIps = []
		resImages = []
		for ch in range(numChannels):
			chIps.append(ByteProcessor(max_coords[0]+sizeX,max_coords[1]+sizeY))
		for ch in range(numChannels):
			resImages.append(ImagePlus("ch"+str(ch+1),chIps[ch]))
		for se in range(numTiles):
			IJ.showProgress(se,numTiles)
			if z >= coords_normed[se][2] and z <= coords_normed[se][2]+numZ-1:
				iReader.setSeries(se)
				for ch in range(numChannels):
					byteArray = iReader.openBytes((z-coords_normed[se][2])*numChannels+ch)
					testIp = ByteProcessor(sizeX,sizeY,byteArray)
					testImage = ImagePlus("tester",testIp)
					Image_stamper.stampStack(testImage,resImages[ch],coords_normed[se][0],coords_normed[se][1],0)			
					activeIp = chIps[ch]
					testImage.close()
					
					
		for ch in range(len(resImages)):
			IJ.saveAsTiff(resImages[ch],parentLSMFilePath+"_tiles/v_img/img_z_"+str(z+1)+"_c_"+str(ch+1)+".tif")
	
	## Closes the LSM file
	iReader.close()

	## Writes to the log file
	write_log_file(parentLSMFilePath+"_tiles/analysis.log.txt","Made virtual image slices in v_img/ with preliminary fileconfig file")