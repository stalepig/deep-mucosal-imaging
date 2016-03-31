from ij.io import OpenDialog
from ij.gui import WaitForUserDialog
from ij.gui import PolygonRoi
from ij.gui import Roi
from ij import IJ
from ij import WindowManager
from ij.gui import NonBlockingGenericDialog
from ij.gui import WaitForUserDialog
from ij.plugin import ChannelSplitter
from ij.process import ImageProcessor
from ij.process import LUT
from ij.process import Blitter
from ij.measure import Calibration
import re
import sys
import os
import shutil
from java.awt.event import AdjustmentListener
from java.awt.event import ItemListener
from java.awt.event import ItemEvent
from java.awt import Color

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

	return([scale,resized_dim[0],acquisition_dim[0],cal.pixelWidth,cal.pixelHeight,cal.pixelDepth,cal.getUnit()])

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
	
def upscale_coords(coords,scale):
	for key in coords.keys():
		coords[key] = [coords[key][0]*scale,coords[key][1]*scale,coords[key][2]]
	return(coords)
	
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

def rearrange_tile_list(containment_tups_superlist):
	tile_dict = {}
	for roi in containment_tups_superlist:
		for tup in roi:
			tile_dict[str(tup[0])] = []
	for roi in containment_tups_superlist:
		for tup in roi:
			tile_dict[str(tup[0])].append(tup)

	return tile_dict

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
	cal = active_image.getCalibration()
	# cal.pixelDepth = 1.0
	# cal.pixelHeight = 1.0
	# cal.pixelWidth = 1.0
	# cal.setUnit("pixel")
	proi = PolygonRoi(masterXs,masterYs,Roi.FREEROI)
	active_image.setRoi(proi)
	return active_image

def make_image_binary(theImage):
	for z in range(1,theImage.getNSlices()+1):
		theImage.setSlice(z)
		theProcessor = theImage.getProcessor()
		for x in range(theImage.getWidth()):
			for y in range(theImage.getHeight()):
				if theProcessor.getPixel(x,y) > 0:
					theProcessor.putPixel(x,y,255)
	return theImage

def get_image_for_calibration(path):
	IJ.run("Bio-Formats Importer", "open=" + path + " color_mode=Default view=Hyperstack stack_order=XYCZT")
	theImage = WindowManager.getImage(os.path.split(path)[1])
	return theImage

## Listener classes for event handling
class ThresholdListener(AdjustmentListener):
	def __init__(self,theImage):
		self.theImage = theImage
	def adjustmentValueChanged(self,e):
		self.theImage.resetDisplayRange()
		self.theImage.updateAndDraw()
		ip = self.theImage.getProcessor()
		ip.setThreshold(e.getValue(),255,ImageProcessor.RED_LUT)

class MinCheckboxListener(ItemListener):
	def __init__(self,theImage,virginImage,medCheckbox):
		self.theImage = theImage
		self.virginImage = virginImage
		self.medCheckbox = medCheckbox
	def itemStateChanged(self,e):
		if (e.getStateChange() == ItemEvent.SELECTED):
			self.medCheckbox.setState(False)
			IJ.run(self.theImage,"Minimum...", "radius=2 stack")
		else:
			currSlice = self.theImage.getSlice()
			for i in range(1,self.theImage.getNSlices()):
				self.theImage.setSliceWithoutUpdate(i)
				ip = self.theImage.getProcessor()
				self.virginImage.setSliceWithoutUpdate(i)
				ip.copyBits(self.virginImage.getProcessor(),0,0,Blitter.COPY)
			self.theImage.updateAndDraw()	
			self.theImage.setSlice(currSlice)

class MedCheckboxListener(ItemListener):
	def __init__(self,theImage,virginImage,minCheckbox):
		self.theImage = theImage
		self.virginImage = virginImage
		self.minCheckbox = minCheckbox
	def itemStateChanged(self,e):
		if (e.getStateChange() == ItemEvent.SELECTED):
			self.minCheckbox.setState(False)
			IJ.run(self.theImage,"Median...", "radius=2 stack")
		else:
			currSlice = self.theImage.getSlice()
			for i in range(1,self.theImage.getNSlices()):
				self.theImage.setSliceWithoutUpdate(i)
				ip = self.theImage.getProcessor()
				self.virginImage.setSliceWithoutUpdate(i)
				ip.copyBits(self.virginImage.getProcessor(),0,0,Blitter.COPY)
			self.theImage.updateAndDraw()	
			self.theImage.setSlice(currSlice)

class WorkROICheckboxListener(ItemListener):
	def __init__(self,theImage,thresholdSlider,sizeText,workROICheckbox):
		self.theImage = theImage
		self.thresholdSlider = thresholdSlider
		self.sizeText = sizeText
		self.workRoiCheckbox = workROICheckbox
	def itemStateChanged(self,e):
		theRoi = self.theImage.getRoi()
		if (theRoi is not None):
			if (e.getStateChange() == ItemEvent.SELECTED):
				self.theImage.deleteRoi()
				backupImage = self.theImage.duplicate()
				self.theImage.setRoi(theRoi)
				outputImage = self.theImage.duplicate()
				for i in range(1,self.theImage.getNSlices()):
					self.theImage.setSliceWithoutUpdate(i)
					ip = self.theImage.getProcessor()
					ip.setValue(0)
					ip.fillOutside(theRoi)
				self.theImage.updateAndDraw()
				params = ("volume surface nb_of_obj._voxels " + 
						"nb_of_surf._voxels integrated_density mean_gray_value " +
						"std_dev_gray_value median_gray_value minimum_gray_value " +
						"maximum_gray_value centroid mean_distance_to_surface " + 
						"std_dev_distance_to_surface median_distance_to_surface centre_of_mass " +
						"bounding_box dots_size=5 font_size=10 show_numbers white_numbers " + 
						"redirect_to=none")
				IJ.run("3D OC Options", params)
				params = ("threshold=" + str(self.thresholdSlider.getValue()) + 
						" slice=1 min.=" + self.sizeText.getText() + " max.=24903680 surfaces statistics")
				print params
				self.theImage.resetDisplayRange()
				self.theImage.updateAndDraw()
				IJ.run(self.theImage, "3D Objects Counter", params)
				self.theImage.setImage(backupImage)
				self.theImage.updateAndRepaintWindow()
				surfacesImage = WindowManager.getImage("Surface map of " + self.theImage.getTitle())
				surfacesImage.setRoi(theRoi)
				surfacesImageCut = surfacesImage.duplicate()
				IJ.run(surfacesImageCut,"8-bit","")
				surfacesImageCut = make_image_binary(surfacesImageCut)
				surfacesImageCut.show()
				outputImage.show()
				surfacesImage.close()
				self.theImage.setSlice(self.theImage.getNSlices()/2)
				IJ.run("Merge Channels...", "c2=[" + outputImage.getTitle() + "] c6=[" + surfacesImageCut.getTitle() + "] create ignore")
				self.workRoiCheckbox.setState(False)
			else:
				IJ.showStatus("Select freeform ROI to operate on, or delete to operate on whole image")
				
		else:
			IJ.showStatus("Need to pick an ROI first before running this option")
			self.workRoiCheckbox.setState(False)

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
	wfud = WaitForUserDialog("Select a freehand ROI, then click here")
	wfud.show()
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
			calibImage = get_image_for_calibration(parentLSMFilePath+"_tiles/tile_" + containing_tiles_dict.keys()[0] + ".ome.tif")
			hadStitched = True
		else:
			IJ.run("Bio-Formats Importer", "open=" + parentLSMFilePath + "_tiles/tile_" + (containing_tiles_dict.keys())[0] + ".ome.tif color_mode=Default view=Hyperstack stack_order=XYCZT")
			IJ.log("Opened tile " + str((containing_tiles_dict.keys())[0]))
		subupcoords_dict = normalize_coords_in_dict(dict(("tile_"+k,upscaled_coords["tile_"+k]) for k in containing_tiles_dict.keys()))
		activeImage = draw_roi_on_full_res_tile(containing_tiles_dict,subupcoords_dict)	
		if (hadStitched):
			activeImage.copyScale(calibImage)
			calib = calibImage.getCalibration()
			calibImage.close()
			activeImage.updateAndRepaintWindow()
		else:
			calib = activeImage.getCalibration()
		
		## Runs interface that allows to correct for bleedthrough and refraction
		if activeImage is not None:
			gd = NonBlockingGenericDialog("Select channel to operate on...")
			gd.addChoice("Select_channel:",["Channel "+str(i) for i in range(1,activeImage.getNChannels()+1)],"Channel 1")
			gd.addChoice("Bleeding_channel:",["None"] + ["Channel "+str(i) for i in range(1,activeImage.getNChannels()+1)],"None")
			gd.addChoice("Refraction_reference_channel:",["None"] + ["Channel "+str(i) for i in range(1,activeImage.getNChannels()+1)],"None")
			gd.showDialog()
			if (gd.wasOKed()):
				channelImages = ChannelSplitter.split(activeImage)
				channel = gd.getNextChoiceIndex()+1
				bleedingC = gd.getNextChoiceIndex()
				refractRefC = gd.getNextChoiceIndex()
				if (bleedingC > 0):
					params = ("bleeding_channel=" + str(bleedingC) + " bloodied_channel=" + str(channel) + " " +
							"allowable_saturation_percent=1.0 rsquare_threshold=0.50")
					IJ.run("Remove Bleedthrough (automatic)", params)
					dataImage = WindowManager.getImage("Corrected_ch" + str(channel))
					if (refractRefC > 0):
						refractCImage = channelImages[refractRefC-1].duplicate()
						refractCImage.show()
						IJ.run("Merge Channels...", "c1=" + dataImage.getTitle() + " c2=" + refractCImage.getTitle() + " create ignore")
						mergedImage = WindowManager.getImage("Composite")
						params = ("reference_channel=2 application_channel=1 automatic_operation generate_log " +
								"max_slice=43 surface_slice=87")
						IJ.run(mergedImage,"Refractive Signal Loss Correction",params)
						dataImage = WindowManager.getImage("App Corrected")
						mergedImage.close()
						refCorrectedImage = WindowManager.getImage("Ref Corrected")
						refCorrectedImage.close()
				else:
					dataImage = channelImages[channel-1]
					if (refractRefC > 0):
						params = ("reference_channel=" + str(refractRefC) + 
								" application_channel=" + str(channel) + " automatic_operation" +
								" generate_log max_slice=43 surface_slice=87")
						IJ.run(activeImage,"Refractive Signal Loss Correction",params)
						dataImage = WindowManager.getImage("App Corrected")
						refCorrectedImage = WindowManager.getImage("Ref Corrected")
						refCorrectedImage.close()
				dataImage.setLut(LUT.createLutFromColor(Color.WHITE))
				dataImage.setCalibration(calib)
				dataImage.show()
				
				## Interface dialog for setting object finding parameters
				virginImage = dataImage.duplicate()
				gd10 = NonBlockingGenericDialog("Select size and threshold parameters...")
				gd10.addNumericField("Minimum_size:",100,0)
				gd10.addSlider("Threshold_intensity:",0,255,128)
				gd10.addCheckbox("Min_filter",False)
				gd10.addCheckbox("Med_filter",False)
				gd10.addCheckbox("Work_on_ROI",False)
				sliders = gd10.getSliders()
				boxes = gd10.getCheckboxes()
				texts = gd10.getNumericFields()
				sizeText = texts.elementAt(0)
				thresholdSlider = sliders.elementAt(0)
				thresholdSlider.addAdjustmentListener(ThresholdListener(dataImage))
				minFilterBox = boxes.elementAt(0)
				medFilterBox = boxes.elementAt(1)
				workROIBox = boxes.elementAt(2)
				minFilterBox.addItemListener(MinCheckboxListener(dataImage,virginImage,medFilterBox))
				medFilterBox.addItemListener(MedCheckboxListener(dataImage,virginImage,minFilterBox))
				workROIBox.addItemListener(WorkROICheckboxListener(dataImage,thresholdSlider,sizeText,workROIBox))
				gd10.showDialog()
				
				if (gd10.wasOKed()):
					sizeMin = gd10.getNextNumber()
					thresholdInt = gd10.getNextNumber()
					applyMinFilter = gd10.getNextBoolean()
					applyMedFilter = gd10.getNextBoolean()
					workOnRoi = gd10.getNextBoolean()
					params = ("volume surface nb_of_obj._voxels " + 
							"nb_of_surf._voxels integrated_density mean_gray_value " +
							"std_dev_gray_value median_gray_value minimum_gray_value " +
							"maximum_gray_value centroid mean_distance_to_surface " + 
							"std_dev_distance_to_surface median_distance_to_surface centre_of_mass " +
							"bounding_box dots_size=5 font_size=10 show_numbers white_numbers " + 
							"redirect_to=none")
					IJ.run("3D OC Options", params)
					
					params = ("threshold=" + str(thresholdInt) + 
							" slice=1 min.=" + str(sizeMin) + " max.=24903680 surfaces statistics")
					dataImage.resetDisplayRange()
					dataImage.updateAndDraw()
					IJ.run(dataImage, "3D Objects Counter", params)
					surfacesImage = WindowManager.getImage("Surface map of " + dataImage.getTitle())
					IJ.run(surfacesImage,"8-bit","")
					surfacesImage = make_image_binary(surfacesImage)
					IJ.run("Merge Channels...", "c2=[" + dataImage.getTitle() + "] c6=[" + surfacesImage.getTitle() + "] create ignore")