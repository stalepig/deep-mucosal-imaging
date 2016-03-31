from ij.gui import GenericDialog
from ij.io import OpenDialog
from ij import IJ
from ij import WindowManager
from ij import ImageStack
from ij import ImagePlus
from ij.measure import ResultsTable
import re
import os
import sys
import shutil
import math

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

def upscale_coords(coords,scale):
	for key in coords.keys():
		coords[key] = [coords[key][0]*scale,coords[key][1]*scale,coords[key][2]]
	return(coords)

def normalize_coords_in_dict(coords):
	min_x = sys.maxint
	min_y = sys.maxint
	min_z = sys.maxint
	for key in coords.keys():
		if coords[key][0] < min_x:
			min_x = coords[key][0]
		if coords[key][1] < min_y:
			min_y = coords[key][1]
		if coords[key][2] < min_z:
			min_z = coords[key][2]
	for key in coords.keys():
		coords[key][0] = coords[key][0] - min_x
		coords[key][1] = coords[key][1] - min_y
		coords[key][2] = coords[key][2] - min_z
	return(coords)

def cast_field_variable(theField):
	fctns = [int, float, float, int, int, int, float, float, float, int, int, float, float, float, float, float, float, float, float, float, int, int, int, int, int, int]
	result = map(lambda x,y: x(y), fctns, theField)
	return (result)

def find_containing_tiles(point_tup,coords,tile_length):
	containing_tiles = []
	for key in coords.keys():
		if ((point_tup[0] >= coords[key][0]) and (point_tup[1] >= coords[key][1])):
			if ((point_tup[0]-coords[key][0]) < tile_length and (point_tup[1]-coords[key][1]) < tile_length):
				containing_tiles.append(int(key[5:]))
	return(containing_tiles)

def write_object_db(objectDB, path):
	try:
		f = open(path,"w")
		for tile in objectDB:
			for obj in tile:
				stringVersion = [str(x) for x in obj]
				cereal = ','.join(stringVersion)
				#print cereal
				f.write(cereal+"\n")
	except:
		IJ.log("Could not write updated object file")
	finally:
		f.close()
			
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

def stitch_from_tileconfig(input_dir):
	params = ("type=[Positions from file] order=[Defined by TileConfiguration] " +  
			"directory=" + input_dir + " " + 
			"layout_file=TileConfiguration.subtiles.txt " + 
			"fusion_method=[Linear Blending] regression_threshold=0.30 " +
			"max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 " +
			"subpixel_accuracy computation_parameters=[Save memory (but be slower)] " + 
			"image_output=[Fuse and display]")
	IJ.run("Grid/Collection stitching", params)

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

def get_coordinate_offsets(coord_vals):
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

	return([min_x,min_y,min_z])

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

def compute_volume_overlap_bboxes(bbox1,bbox2):
	xOverlap = 0.0
	yOverlap = 0.0
	zOverlap = 0.0
	
	if (bbox1[3] < bbox2[0] or bbox2[3] < bbox1[0]):
		xOverlap = 0.0
	elif (bbox1[0] > bbox2[0] and bbox1[3] < bbox2[3]):
		xOverlap = bbox1[3] - bbox1[0]
	elif (bbox1[0] > bbox2[0] and bbox1[3] > bbox2[3]):
		xOverlap = bbox2[3] - bbox1[0]
	elif (bbox1[0] < bbox2[0] and bbox1[3] < bbox2[3]):
		xOverlap = bbox1[3] - bbox2[0]
	elif (bbox1[0] < bbox2[0] and bbox1[3] > bbox2[3]):
		xOverlap = bbox2[3] - bbox2[0]
	elif (bbox2[0] > bbox1[0] and bbox2[3] < bbox1[3]):
		xOverlap = bbox2[3] - bbox2[0]
	elif (bbox2[0] > bbox1[0] and bbox2[3] > bbox1[3]):
		xOverlap = bbox1[3] - bbox2[0]
	elif (bbox2[0] < bbox1[0] and bbox2[3] < bbox1[3]):
		xOverlap = bbox2[3] - bbox1[0]
	elif (bbox2[0] < bbox1[0] and bbox2[3] > bbox1[3]):
		xOverlap = bbox1[3] - bbox1[0]
	else:
		xOverlap = -1.0
		
	if (bbox1[4] < bbox2[1] or bbox2[4] < bbox1[1]):
		yOverlap = 0.0
	elif (bbox1[1] > bbox2[1] and bbox1[4] < bbox2[4]):
		yOverlap = bbox1[4] - bbox1[1]
	elif (bbox1[1] > bbox2[1] and bbox1[4] > bbox2[4]):
		yOverlap = bbox2[4] - bbox1[1]
	elif (bbox1[1] < bbox2[1] and bbox1[4] < bbox2[4]):
		yOverlap = bbox1[4] - bbox2[1]
	elif (bbox1[1] < bbox2[1] and bbox1[4] > bbox2[4]):
		yOverlap = bbox2[4] - bbox2[1]
	elif (bbox2[1] > bbox1[1] and bbox2[4] < bbox1[4]):
		yOverlap = bbox2[4] - bbox2[1]
	elif (bbox2[1] > bbox1[1] and bbox2[4] > bbox1[4]):
		yOverlap = bbox1[4] - bbox2[1]
	elif (bbox2[1] < bbox1[1] and bbox2[4] < bbox1[4]):
		yOverlap = bbox2[4] - bbox1[1]
	elif (bbox2[1] < bbox1[1] and bbox2[4] > bbox1[4]):
		yOverlap = bbox1[4] - bbox1[1]
	else:
		yOverlap = -1.0
	
	if (bbox1[5] < bbox2[2] or bbox2[5] < bbox1[2]):
		zOverlap = 0.0
	elif (bbox1[2] > bbox2[2] and bbox1[5] < bbox2[5]):
		zOverlap = bbox1[5] - bbox1[2]
	elif (bbox1[2] > bbox2[2] and bbox1[5] > bbox2[5]):
		zOverlap = bbox2[5] - bbox1[2]
	elif (bbox1[2] < bbox2[2] and bbox1[5] < bbox2[5]):
		zOverlap = bbox1[5] - bbox2[2]
	elif (bbox1[2] < bbox2[2] and bbox1[5] > bbox2[5]):
		zOverlap = bbox2[5] - bbox2[2]
	elif (bbox2[2] > bbox1[2] and bbox2[5] < bbox1[5]):
		zOverlap = bbox2[5] - bbox2[2]
	elif (bbox2[2] > bbox1[2] and bbox2[5] > bbox1[5]):
		zOverlap = bbox1[5] - bbox2[2]
	elif (bbox2[2] < bbox1[2] and bbox2[5] < bbox1[5]):
		zOverlap = bbox2[5] - bbox1[2]
	elif (bbox2[2] < bbox1[2] and bbox2[5] > bbox1[5]):
		zOverlap = bbox1[5] - bbox1[2]
	else:
		zOverlap = -1.0

	totOverlap= xOverlap * yOverlap * zOverlap
	if totOverlap < 0:
		IJ.log("Error in object overlap calculation")
		print bbox1, bbox2
	
	return(totOverlap)

def get_bounding_box(toplefts,bottomrights):
	min_x = sys.maxint
	min_y = sys.maxint
	min_z = sys.maxint
	max_x = -10000
	max_y = -10000
	max_z = -10000

	for tup in toplefts:
		if tup[0] < min_x:
			min_x = tup[0]
		if tup[1] < min_y:
			min_y = tup[1]
		if tup[2] < min_z:
			min_z = tup[2]

	for tup in bottomrights:
		if tup[0] > max_x:
			max_x = tup[0]
		if tup[1] > max_y:
			max_y = tup[1]
		if tup[2] > max_z:
			max_z = tup[2]

	retVal = [math.floor(min_x)-1,math.floor(min_y)-1,math.floor(min_z)-1,math.ceil(max_x)+1,math.ceil(max_y)+1,math.ceil(max_z)+1]
	return([int(x) for x in retVal])

def get_substack(theImage,startSlice,endSlice):
	retStack = ImageStack(theImage.getWidth(),theImage.getHeight())
	
	for i in range(startSlice,endSlice+1):
		theImage.setSliceWithoutUpdate(i)
		ip = theImage.getProcessor()
		newip = ip.duplicate()
		retStack.addSlice(newip)

	return(ImagePlus("dataimage",retStack))

def select_best_object(theObjects):
	min_summer = sys.maxint
	min_ind = -1
	
	for i in range(len(theObjects)):
		summer = theObjects[i][20] + theObjects[i][21] + theObjects[i][22]
		if summer < min_summer:
			min_summer = summer
			min_ind = i

	return(theObjects[min_ind])

## Main body of script
## Gets the channel to work on
opener = OpenDialog("Select parent LSM file...")
parentLSMFilePath = opener.getPath()
if (parentLSMFilePath is not None):
	stackInfo = parse_tile_info_file(parentLSMFilePath + "_tiles/tile_info.txt")
	channelTexts = map(lambda x: str(x), filter(lambda x:os.path.isfile(parentLSMFilePath+"_tiles/objects/C"+str(x)+"-tile_1.csv"),range(1,stackInfo[0]+1)))
	gd = GenericDialog("Specify parameters...")
	gd.addChoice("Which_channel",channelTexts,channelTexts[0])
	gd.addNumericField("Linear_pixel_num",512,0)
	gd.showDialog()
	if gd.wasOKed():
		channel = int(gd.getNextChoice())
		pixelLimit = int(gd.getNextNumber())

		## Obtains global coordinate system for tiles
		scale_info = estimate_scale_multiplier(parentLSMFilePath+"_tiles/tile_1.ome.tif",parentLSMFilePath+"_tiles/resized/tile_1.tif")
		coords = read_tileconfig_file(parentLSMFilePath+"_tiles/resized/TileConfiguration.registered.txt")
		upscaled_coords = normalize_coords_in_dict(upscale_coords(coords,scale_info[0]))
		#print upscaled_coords

		## Parses each of the object files and converts coordinates to global coordinates
		objectDB = [[] for i in range(stackInfo[1])]
		filteredObjectDB = [[] for i in range(stackInfo[1])]
		duplicatedObjectDB = [[] for i in range(stackInfo[1])]
		uniqueDuplicatedObjectDB = [[] for i in range(stackInfo[1])]
		edgeOnlyObjectDB = [[] for i in range(stackInfo[1])]
		edgeContainedObjectDB = [[] for i in range(stackInfo[1])]
		containedMultipleObjectDB = [[] for i in range(stackInfo[1])]
		restitchedObjectDB = [[] for i in range(stackInfo[1])]
		for i in range(1,stackInfo[1]+1):
			f = open(parentLSMFilePath+"_tiles/objects/C"+str(channel)+"-tile_"+str(i)+".csv","r")
			fileContents = f.readlines()
			f.close()
			if (len(fileContents) > 1):
				for line in fileContents[1:len(fileContents)-1]:
					line = line.rstrip()
					fields = line.split(",")
					fields = cast_field_variable(fields)
					normedCoords = [i,upscaled_coords["tile_"+str(i)][0]+fields[20],upscaled_coords["tile_"+str(i)][1]+fields[21],upscaled_coords["tile_"+str(i)][2]+fields[22]]
					boundingCoords = [normedCoords[1]+fields[23],normedCoords[2]+fields[24],normedCoords[3]+fields[25]]
					fields = fields + normedCoords
					fields = fields + boundingCoords					
					objectDB[i-1].append(fields)
		
		## Finds containing tiles for each object
		globalCounter = 1
		for tile in objectDB:
			for j in range(len(tile)):
				upperLeftCoord = [tile[j][27],tile[j][28]]
				lowerLeftCoord = [tile[j][27],tile[j][31]]
				upperRightCoord = [tile[j][30],tile[j][28]]
				lowerRightCoord = [tile[j][30],tile[j][31]]
				upperLeftContainers = [str(x) for x in find_containing_tiles(upperLeftCoord,upscaled_coords,pixelLimit)]
				lowerLeftContainers = [str(x) for x in find_containing_tiles(lowerLeftCoord,upscaled_coords,pixelLimit)]
				upperRightContainers = [str(x) for x in find_containing_tiles(upperRightCoord,upscaled_coords,pixelLimit)]
				lowerRightContainers = [str(x) for x in find_containing_tiles(lowerRightCoord,upscaled_coords,pixelLimit)]
				contDict = {}
				for x in upperLeftContainers:
					contDict[x] = False
				for x in lowerLeftContainers:
					contDict[x] = False
				for x in upperRightContainers:
					contDict[x] = False
				for x in lowerRightContainers:
					contDict[x] = False
				record = ['-'.join(upperLeftContainers),'-'.join(lowerLeftContainers),'-'.join(upperRightContainers),'-'.join(lowerRightContainers),'-'.join(contDict.keys()),globalCounter]
				tile[j] = tile[j] + record
				globalCounter = globalCounter + 1

		## Finds unique (fully single-tile) objects from source DB and writes to filtered DB
		objectCounter = 0
		counter = 0
		for i in range(len(objectDB)):
			deleteIndices = []
			for j in range(len(objectDB[i])):
				containingTiles = objectDB[i][j][37].split("-")
				if len(containingTiles) == 1:
					filteredObjectDB[i].append(list(objectDB[i][j])+["","contained",""])
					deleteIndices.append(j)
				objectCounter = objectCounter + 1
			for k in range(len(objectDB[i])-1,-1,-1):
				if k in deleteIndices:
					objectDB[i].pop(k)
					counter = counter + 1
		IJ.log(str(objectCounter) + " objects on stack")
		IJ.log("Pass 1: Kept " + str(counter) + " objects whose coordinates were fully within a single tile")

		## Connects objects across tiles, finding objects fully encompassed in 2+ tiles
		objectCounter = 0
		counter = 0
		counter2 = 0
		for i in range(len(objectDB)):
			delList = []
			for j in range(len(objectDB[i])):
				connectedObjects = []
				containingTiles = [int(x) for x in objectDB[i][j][37].split("-")]
				foundMatch = False
				for k in containingTiles:
					if (i+1 != k):
						deleteIndices = []
						for m in range(len(objectDB[k-1])):
							if (abs(objectDB[i][j][27] - objectDB[k-1][m][27]) < 5) and (abs(objectDB[i][j][28] - objectDB[k-1][m][28]) < 5) and (abs(objectDB[i][j][30] - objectDB[k-1][m][30]) < 5) and (abs(objectDB[i][j][31] - objectDB[k-1][m][31]) < 5):
								connectedObjects.append(objectDB[k-1][m][38])
								duplicatedObjectDB[i].append(list(objectDB[k-1][m]))
								deleteIndices.append(m)
								foundMatch = True
						for n in range(len(objectDB[k-1])-1,-1,-1):
							if n in deleteIndices:
								objectDB[k-1].pop(n)
								counter = counter + 1
				connectedObjects = [str(x) for x in connectedObjects]
				objectDB[i][j] = objectDB[i][j] + ['-'.join(connectedObjects)]
				if foundMatch:
					uniqueDuplicatedObjectDB[i].append(list(objectDB[i][j])+["contained",""])
					delList.append(j)
			for l in range(len(objectDB[i])-1,-1,-1):
				if l in delList:
					objectDB[i].pop(l)
					counter2 = counter2 + 1
		IJ.log("Pass 2/3: Kept " + str(counter2) + " unique objects with full representation in 2+ tiles")
		IJ.log("Pass 2/3: Removed " + str(counter) + " duplicate objects to the trash")
		
		## Finds objects that are on the edge of tiles and connects them to neighbors
		for i in range(len(objectDB)):
			for j in range(len(objectDB[i])):
				connectedObjects = []
				edgeStatus = "no_eval"
				if (objectDB[i][j][20]+objectDB[i][j][23]>=pixelLimit or objectDB[i][j][21]+objectDB[i][j][24]>=pixelLimit or objectDB[i][j][20]==0 or objectDB[i][j][21]==0):
					edgeStatus = "edge"
					containingTiles = [int(x) for x in objectDB[i][j][37].split("-")]
					#print containingTiles
					for k in containingTiles:
						if (k != i+1):
							for m in range(len(objectDB[k-1])):
								overlap = compute_volume_overlap_bboxes(objectDB[i][j][27:33],objectDB[k-1][m][27:33])
								# print "bbox1: " + str(objectDB[i][j][37]) + " bbox2: " + str(objectDB[k-1][m][37]) + " overlap: " + str(overlap)
								if overlap > 0:
									connectedObjects.append(objectDB[k-1][m][38])
				else:
					edgeStatus = "contained"
				connectedObjects = [str(x) for x in connectedObjects]
				objectDB[i][j] = objectDB[i][j] + [edgeStatus] + ['-'.join(connectedObjects)]
		
		## Deletes objects that are on the edge of a tile but have no neighbor (objects cut in two)
		objectCounter = 0
		counter = 0
		counter2 = 0
		for i in range(len(objectDB)):
			delList = []
			for j in range(len(objectDB[i])):
				if (objectDB[i][j][40] == "edge" and objectDB[i][j][41] == ""):
					edgeOnlyObjectDB[i].append(list(objectDB[i][j]))
					delList.append(j)
				objectCounter = objectCounter + 1
			for l in range(len(objectDB[i])-1,-1,-1):
				if l in delList:
					objectDB[i].pop(l)
					counter = counter + 1
		IJ.log(str(objectCounter) + " remaining objects on stack")
		IJ.log("Pass 4: Removed " + str(counter) + " objects that are on edge of tile but have no neighbor")
		
		## Deletes objects that are on the edge of one tile but fully contained within the neighboring tile
		objectCounter = 0
		counter = 0
		counter2 = 0
		for i in range(len(objectDB)):
			delList = []
			for j in range(len(objectDB[i])):
				doCull = False
				if (objectDB[i][j][40] == "edge"):
					containingTiles = [int(x) for x in objectDB[i][j][37].split("-")]
					connectorIDs = [int(x) for x in objectDB[i][j][41].split("-")]
					for k in containingTiles:
						if (k != i+1):
							for m in range(len(objectDB[k-1])):
								if (int(objectDB[k-1][m][38]) in connectorIDs):
									if (objectDB[k-1][m][40] == "contained"):
										doCull = True
										edgeContainedObjectDB[i].append(list(objectDB[k-1][m]))
				if (doCull):
					delList.append(j)
				objectCounter = objectCounter + 1
			for l in range(len(objectDB[i])-1,-1,-1):
				if l in delList:
					objectDB[i].pop(l)
					counter = counter + 1
		IJ.log(str(objectCounter) + " remaining objects on stack")
		IJ.log("Pass 5: Removed " + str(counter) + " objects that are on the edge of tile but fully contained within a neighbor")

		## Writes remaining objects that are fully described by a tile to the permanent database
		## The unwritten remaining objects all need to be restitched from the images
		objectCounter = 0
		counter = 0
		counter2 = 0
		for i in range(len(objectDB)):
			delList = []
			for j in range(len(objectDB[i])):
				if (objectDB[i][j][40] == "contained"):
					containedMultipleObjectDB[i].append(list(objectDB[i][j]))
					delList.append(j)
				objectCounter = objectCounter + 1
			for l in range(len(objectDB[i])-1,-1,-1):
				if l in delList:
					objectDB[i].pop(l)		 
					counter = counter + 1
		IJ.log(str(objectCounter) + " remaining objects on stack")
		IJ.log("Pass 6: Kept " + str(counter) + " objects whose coordinates are in multiple tiles but are fully described by one tile")

		## Serializes the object databases to disk
		
		write_object_db(objectDB,parentLSMFilePath+"_tiles/objects/C" + str(channel) + ".objects.trash.prestitch.csv")
		write_object_db(edgeOnlyObjectDB,parentLSMFilePath+"_tiles/objects/C" + str(channel) + ".objects.trash.edgeonly.csv")
		write_object_db(containedMultipleObjectDB,parentLSMFilePath+"_tiles/objects/C" + str(channel) + ".objects.keep.contained.csv")
		write_object_db(filteredObjectDB,parentLSMFilePath+"_tiles/objects/C" + str(channel) + ".objects.keep.unique.csv")
		write_object_db(uniqueDuplicatedObjectDB,parentLSMFilePath+"_tiles/objects/C" + str(channel) + ".objects.keep.duplicated.csv")
		write_object_db(duplicatedObjectDB,parentLSMFilePath+"_tiles/objects/C" + str(channel) + ".objects.trash.duplicated.csv")
		write_object_db(edgeContainedObjectDB,parentLSMFilePath+"_tiles/objects/C" + str(channel) + ".objects.trash.edgecontained.csv")
		
		## Restitches objects that not contained by any one tile
		for i in range(len(objectDB)):
			for j in range(len(objectDB[i])):
				if len(objectDB[i]) > 0:
					containingTiles = [int(x) for x in objectDB[i][j][37].split("-")]
					copy_fullsize_tiles(["C"+str(channel)+"-tile_"+str(x) for x in containingTiles],parentLSMFilePath+"_tiles/maps/",parentLSMFilePath+"_tiles/subtiles/",".tif")
					subupcoords_vals = normalize_coords_in_list(get_list_from_dict(["tile_"+str(x) for x in containingTiles],upscaled_coords))
					offsets = get_coordinate_offsets(get_list_from_dict(["tile_"+str(x) for x in containingTiles],upscaled_coords))
					print offsets
					write_tileconfig_file(parentLSMFilePath+"_tiles/subtiles/TileConfiguration.subtiles.txt",subupcoords_vals,".tif")
					stitch_from_tileconfig(parentLSMFilePath+"_tiles/subtiles/")
					fusedImage = WindowManager.getImage("Fused")
					connectorIDs = [int(x) for x in objectDB[i][j][41].split("-")]
					cc = 0
					subNormedCoordsMaster = []
					subBoundingCoordsMaster = []
					for k in containingTiles:
						delList = []
						if (i == k-1):
							subNormedCoords = [subupcoords_vals[cc][0]+objectDB[i][j][20],subupcoords_vals[cc][1]+objectDB[i][j][21],subupcoords_vals[cc][2]+objectDB[i][j][22]]
							subBoundingCoords = [subNormedCoords[0]+objectDB[i][j][23],subNormedCoords[1]+objectDB[i][j][24],subNormedCoords[2]+objectDB[i][j][25]]
							subNormedCoordsMaster.append(list(subNormedCoords))
							subBoundingCoordsMaster.append(list(subBoundingCoords))
						else:
							for m in range(len(objectDB[k-1])):
								if (int(objectDB[k-1][m][38]) in connectorIDs):
									subNormedCoords = [subupcoords_vals[cc][0]+objectDB[k-1][m][20],subupcoords_vals[cc][1]+objectDB[k-1][m][21],subupcoords_vals[cc][2]+objectDB[k-1][m][22]]
									subNormedCoordsMaster.append(list(subNormedCoords))
									subBoundingCoords = [subNormedCoords[0]+objectDB[k-1][m][23],subNormedCoords[1]+objectDB[k-1][m][24],subNormedCoords[2]+objectDB[k-1][m][25]]
									subBoundingCoordsMaster.append(list(subBoundingCoords))
									delList.append(m)
							for l in range(len(objectDB[k-1])-1,-1,-1):
								if l in delList:
									objectDB[k-1].pop(l)
						cc = cc + 1
					cropMargins = get_bounding_box(subNormedCoordsMaster,subBoundingCoordsMaster)
					if (cropMargins[0]>=0 and cropMargins[1]>=0 and cropMargins[2]>=0 and cropMargins[3]<fusedImage.getWidth() and cropMargins[4]<fusedImage.getHeight() or cropMargins[5]<fusedImage.getNSlices()):
						fusedImage.setRoi(cropMargins[0],cropMargins[1],cropMargins[3]-cropMargins[0]+1,cropMargins[4]-cropMargins[1]+1)
						dupstackImage = fusedImage.duplicate()
						dataImage = get_substack(dupstackImage,cropMargins[2],cropMargins[5])
						dataImage.show()
						dupstackImage.close()
						params = ("volume surface nb_of_obj._voxels " + 
							"nb_of_surf._voxels integrated_density mean_gray_value " +
							"std_dev_gray_value median_gray_value minimum_gray_value " +
							"maximum_gray_value centroid mean_distance_to_surface " + 
							"std_dev_distance_to_surface median_distance_to_surface centre_of_mass " +
							"bounding_box dots_size=5 font_size=10 " + 
							"redirect_to=none")
						IJ.run("3D OC Options", params)
						params = "threshold=1 slice=1 min.=1 max.=24903680 statistics"
						IJ.redirectErrorMessages(True)
						IJ.run(dataImage, "3D Objects Counter", params)
						dataImage.changes = False
						dataImage.close()
						rt = ResultsTable.getResultsTable()
						theObjects = []
						if (rt.getCounter()>0):
							#print rt.getCounter()
							for k in range(rt.getCounter()):
								tempFields = (rt.getRowAsString(k)).split("\t")
								tempFields = cast_field_variable(tempFields)
								theObjects.append(tempFields)
							fields = select_best_object(theObjects) + [i+1,offsets[0]+cropMargins[0]+fields[20],offsets[1]+cropMargins[1]+fields[21],offsets[2]+cropMargins[2]+fields[22],offsets[0]+cropMargins[0]+fields[20]+fields[23],offsets[1]+cropMargins[1]+fields[21]+fields[24],offsets[2]+cropMargins[2]+fields[22]+fields[25]]
							fields = fields + objectDB[i][j][33:42]
							restitchedObjectDB[i].append(fields)
					oldContainingTiles = list(containingTiles)
					fusedImage.close()
				
				
				
				#if len(objectDB[i]) > 1:
				#	for j in range(1,len(objectDB[i])):
				#		containingTiles = [int(x) for x in objectDB[i][j][37].split("-")]
				#		if (set(containingTiles) == set(oldContainingTiles)):
				#			print "Old images"
				#		else:
				#			#fusedImage.close()
				#			print "New images"
				#		oldContainingTiles = list(containingTiles)

		write_object_db(restitchedObjectDB,parentLSMFilePath+"_tiles/objects/C" + str(channel) + ".objects.keep.restitched.csv")
		

		