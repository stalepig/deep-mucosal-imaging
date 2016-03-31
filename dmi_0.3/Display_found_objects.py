from ij.io import OpenDialog
from ij.gui import GenericDialog
from ij.gui import NonBlockingGenericDialog
from ij import IJ
from ij import ImagePlus
from ij import WindowManager
from ij.process import ByteProcessor
from ij.plugin import ImageCalculator
from java.awt.event import ItemListener
from java.awt.event import ItemEvent
import re
import os

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

def cast_field_variable(theField):
	fctns = [int, float, float, int, int, int, float, float, float, int, int, float, float, float, float, float, float, float, float, float, int, int, int, int, int, int, int, float, float, float, float, float, float, str, str, str, str, str, int, str, str, str]
	result = map(lambda x,y: x(y), fctns, theField)
	return (result)

def parse_object_file_into_db(path):
	retList = []
	
	f = open(path,"r")
	fileContents = f.readlines()
	f.close()
	if (len(fileContents) > 1):
		for line in fileContents[1:len(fileContents)-1]:
			line = line.rstrip()
			fields = line.split(",")
			fields = cast_field_variable(fields)
			retList.append(fields)

	return (retList)

def draw_bounding_boxes(objects,title,templateImage):
	drawnIp = ByteProcessor(templateImage.getWidth(),templateImage.getHeight())
	drawnImage = ImagePlus(title,drawnIp)
	drawnImage.show()
	IJ.selectWindow(title)
	for j in range(len(objects)):
		IJ.makeRectangle(objects[j][42],objects[j][43],objects[j][45]-objects[j][42],objects[j][46]-objects[j][43])
		IJ.run("Draw","stack")
	drawnImage.hide()
	return(drawnImage)

## Event handling classes
class CustomCheckboxListener(ItemListener):
	def __init__(self,objectDB,virginImage,boxImages,boxes):
		self.objectDB = objectDB
		self.virginImage = virginImage
		self.boxImages = boxImages
		self.checkboxObjects = []
		for i in range(boxes.size()):
			self.checkboxObjects.append(boxes.elementAt(i))
		
	def addImages(self,img1, img2):
		ic = ImageCalculator()
		sumImage = ic.run("Add create stack",img1,img2)
		return(sumImage)
	
	def itemStateChanged(self,e):
		imgList = []
		imgList.append(virginImage)
		for i in range(len(checkboxObjects)):
			if checkboxObjects[i].getState() == True:
				imgList.append(self.boxImages[i])

		titles = WindowManager.getImageTitles()
		p = re.compile(r'^Result')
		for title in titles:
			m = p.search(title)
			if m is not None:
				computedImage = WindowManager.getImage(title)
				computedImage.close()

		IJ.showStatus("Computing...")
		computedImage = reduce(self.addImages,imgList)
		computedImage.show()
		IJ.showStatus("Ready")


## Main body of script
opener = OpenDialog("Select parent LSM file...")
parentLSMFilePath = opener.getPath()
if (parentLSMFilePath is not None):
	stackInfo = parse_tile_info_file(parentLSMFilePath + "_tiles/tile_info.txt")
	channelTexts = map(lambda x: str(x), filter(lambda x:os.path.isfile(parentLSMFilePath+"_tiles/objects/C"+str(x)+".objects.keep.unique.csv"),range(1,stackInfo[0]+1)))
	gd = GenericDialog("Specify parameters...")
	gd.addChoice("Which_channel",channelTexts,channelTexts[0])
	gd.showDialog()
	if gd.wasOKed():
		channel = int(gd.getNextChoice())

		## Obtains global coordinate system for tiles
		scale_info = estimate_scale_multiplier(parentLSMFilePath+"_tiles/tile_1.ome.tif",parentLSMFilePath+"_tiles/resized/tile_1.tif")

		## Parses each of the object files
		objectDB = [[] for x in range(4)]
		objectDB[0] = parse_object_file_into_db(parentLSMFilePath+"_tiles/objects/C"+str(channel)+".objects.keep.contained.csv")
		objectDB[1] = parse_object_file_into_db(parentLSMFilePath+"_tiles/objects/C"+str(channel)+".objects.keep.duplicated.csv")
		objectDB[2] = parse_object_file_into_db(parentLSMFilePath+"_tiles/objects/C"+str(channel)+".objects.keep.restitched.csv")
		objectDB[3] = parse_object_file_into_db(parentLSMFilePath+"_tiles/objects/C"+str(channel)+".objects.keep.unique.csv")

		## Converts object global coordinates to rescaled coordinates
		for i in range(len(objectDB)):
			for j in range(len(objectDB[i])):
				rescaledTup = [objectDB[i][j][27]/scale_info[0],objectDB[i][j][28]/scale_info[0],objectDB[i][j][29],objectDB[i][j][30]/scale_info[0],objectDB[i][j][31]/scale_info[0],objectDB[i][j][32]]
				objectDB[i][j] = objectDB[i][j] + rescaledTup

		## Draws the bounding boxes in the precomputed way
		virginImage = IJ.getImage()
		theImage = virginImage.duplicate()
		virginImage.hide()
		boxImages = []
		for i in range(len(objectDB)):
			boxImages.append(draw_bounding_boxes(objectDB[i],"image_"+str(i+1),virginImage))
		virginImage.show()
		
		## Sets up main GUI interface for examining found objects
		
		ngd = NonBlockingGenericDialog("Control box")
		ngd.addCheckbox("Contained_objects",False)
		ngd.addCheckbox("Duplicated_objects",False)
		ngd.addCheckbox("Restitched_objects",False)
		ngd.addCheckbox("Unique_objects",False)
		boxes = ngd.getCheckboxes()
		checkboxObjects = []
		for i in range(boxes.size()):
			checkboxObjects.append(boxes.elementAt(i))
		for i in range(len(checkboxObjects)):
			checkboxObjects[i].addItemListener(CustomCheckboxListener(objectDB,virginImage,boxImages,boxes))
		ngd.setCancelLabel("Exit")
		ngd.setOKLabel("Inspect")
		ngd.showDialog()
		if (ngd.wasCanceled()):
			titles = WindowManager.getImageTitles()
			p = re.compile(r'^Result')
			for title in titles:
				m = p.search(title)
				if m is not None:
					theImage = WindowManager.getImage(title)
					theImage.close()

			virginImage.show()
			for img in boxImages:
				img.close()
		else:
			titles = WindowManager.getImageTitles()
			p = re.compile(r'^Result')
			for title in titles:
				m = p.search(title)
				if m is not None:
					theImage = WindowManager.getImage(title)
					roi = theImage.getRoi()

					## Searches which objects could match the selected point on the image
		