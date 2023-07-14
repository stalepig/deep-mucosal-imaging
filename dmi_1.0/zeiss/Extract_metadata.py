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
	iReader.setSeries(0)
	mHash = iReader.getSeriesMetadata()
	hashKeys = mHash.keys()
	try:
		f = open(parentLSMFilePath+"_tiles/metadata.txt", "w")
		f.write("CurrentFile\t" + iReader.getCurrentFile() + "\n")
		f.write("BitsPerPixel\t" + str(iReader.getBitsPerPixel()) + "\n")
		f.write("DimensionOrder\t" + iReader.getDimensionOrder() + "\n")
		f.write("Format\t" + iReader.getFormat() + "\n")
		f.write("ImageCount\t" + str(iReader.getImageCount()) + "\n")
		f.write("PixelType\t" + str(iReader.getPixelType()) + "\n")
		f.write("SeriesCount\t" + str(iReader.getSeriesCount()) + "\n")
		f.write("SizeC\t" + str(iReader.getSizeC()) + "\n")
		f.write("SizeT\t" + str(iReader.getSizeT()) + "\n")
		f.write("SizeX\t" + str(iReader.getSizeX()) + "\n")
		f.write("SizeY\t" + str(iReader.getSizeY()) + "\n")
		f.write("SizeZ\t" + str(iReader.getSizeZ()) + "\n")
		f.write("PixelsPhysicalSizeX\t" + str(meta.getPixelsPhysicalSizeX(0).value()) + "\n")
		f.write("PixelsPhysicalSizeY\t" + str(meta.getPixelsPhysicalSizeY(0).value()) + "\n")
		f.write("PixelsPhysicalSizeZ\t" + str(meta.getPixelsPhysicalSizeZ(0).value()) + "\n")
		pythonKeys = []
		while hashKeys.hasMoreElements():
			pythonKeys.append(hashKeys.nextElement())
		pythonKeys.sort()
		for k in pythonKeys:
			f.write(k + "\t" + str(mHash.get(k)) + "\n")
	except (IOError,OSError):
		print "Problem writing to output metadata file"
	finally:
		f.close()
	
	## Closes the LSM file
	iReader.close()