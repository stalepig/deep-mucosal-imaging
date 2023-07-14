## Imports
import os
import re
import glob
import math
import datetime
from ij.io import DirectoryChooser
from ij.gui import GenericDialog
from ij import IJ
from ij import Macro
from ij import WindowManager
from ij import ImagePlus
from ij import ImageStack
from ij.plugin import ZProjector
from ij.plugin import Memory
from ij.measure import Calibration
from java.lang import Thread
from java.io import File
from java.io import FileInputStream
from java.nio.channels import FileChannel
from java.nio import ByteBuffer
from java.awt import Graphics2D
from com.sun.media.jai.codec import ImageDecoder
from com.sun.media.jai.codec import ByteArraySeekableStream
from com.sun.media.jai.codec import ImageCodec
from com.sun.media.jai.codec import ImageDecoder
from javax.media.jai import PlanarImage
from javax.imageio import ImageIO
from java.awt.image import BufferedImage


## Caliber-specific channel dictionaries
channelDict = {
	"405": "c3",
	"488": "c2",
	"561": "c1",
	"640": "c4"
}

## Function definitions
def check_if_filetype(inputString,extension):
	pattern = u"\." + extension + u"$"
	if re.search(extension,inputString) is not None:
		return True
	else:
		return False

def get_directory_size(sourceDir):
	sumSize = 0
	files = glob.glob(os.path.join(sourceDir,'*.tif'))
	for theFile in files:
		theSize = os.path.getsize(theFile)
		sumSize = sumSize + theSize
	return sumSize

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

def decode_image(data):
    stream = ByteArraySeekableStream(data);
    names = ImageCodec.getDecoderNames(stream);
    dec = ImageCodec.createImageDecoder(names[0], stream, None);
    im = dec.decodeAsRenderedImage();
    image = PlanarImage.wrapRenderedImage(im).getAsBufferedImage();
    return image

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
		

## Main body of script starts here
dc = DirectoryChooser("Choose image directory")
parentPath = dc.getDirectory()
if parentPath is not None:
	imageDirs = next(os.walk(parentPath))[1]
	print(imageDirs)
	gd = GenericDialog("Select directories to process...")
	gd.addCheckboxGroup(len(imageDirs),1,imageDirs,[True]*len(imageDirs))
	gd.showDialog()
	if (gd.wasOKed()):
		imageDirsToProcess = [imageDirs[count] for count,cbox in enumerate(gd.getCheckboxes()) if cbox.state == True]
		print(imageDirsToProcess)
		
		for currentDir in imageDirsToProcess:
			rootPath = parentPath + currentDir + "/composites/"
			IJ.log(rootPath)

			subDirs = next(os.walk(rootPath))[1]
			subDirstoProcess = [di for di in subDirs if di in channelDict.keys()]
			if (len(subDirstoProcess) == 0):
				subDirstoProcess.append("")
			subPathstoProcess = [rootPath + di for di in subDirstoProcess]
			
			## calculates the re-size ratio
			subDirSizes = [get_directory_size(path) for path in subPathstoProcess]
			totFileSize = sum(subDirSizes)
			totFijiMem = Memory().maxMemory()
			allowedMem = totFijiMem/3.0
			ratio = allowedMem / totFileSize
			xyratio = math.sqrt(ratio)
			if xyratio > 1:
				ratio = 1
				xyratio = 1
			print(subDirSizes)
			print(totFileSize,allowedMem,ratio,xyratio)
		
			## gets calibration
			calImage = IJ.openImage(glob.glob(os.path.join(subPathstoProcess[0],'*.tif'))[0])
			cal = calImage.getCalibration()
			write_log_file(parentPath+currentDir+"/scales.log.txt","Original: 1 px = " + str(cal.pixelWidth*10000) + " microns")
			write_log_file(parentPath+currentDir+"/scales.log.txt","Downsampled: 1 px = " + str(cal.pixelWidth/xyratio*10000) + " microns")
			
			## Resizes each slice using Java
			count = 1
			scaledWidth = 0
			scaledHeight = 0
			for path in subPathstoProcess:
				files = glob.glob(os.path.join(path,'*.tif'))
				outPath = path + "/resized/"
				make_destination_directories(outPath,True)
				print(outPath)
				for theFile in files:
					inputFileHandle = File(theFile)
					if inputFileHandle.exists():
						inputStream = FileInputStream(inputFileHandle)
						inputChannel = inputStream.getChannel()
						inputBuffer = ByteBuffer.allocate(inputChannel.size())
						inputChannel.read(inputBuffer)
						inputImage = decode_image(inputBuffer.array())
						inputStream.close()
			
						scaledWidth = int(round(inputImage.getWidth() * xyratio))
						scaledHeight = int(round(inputImage.getHeight() * xyratio))
						outputImage = BufferedImage(scaledWidth,scaledHeight,inputImage.getType())
						g2d = outputImage.createGraphics()
						g2d.drawImage(inputImage,0,0,scaledWidth,scaledHeight,None)
						g2d.dispose()
			
						outputImagePlus = ImagePlus(os.path.basename(theFile),outputImage)
						IJ.saveAsTiff(outputImagePlus,outPath + outputImagePlus.getTitle())
						IJ.showStatus("Tile: " + str(count) + "/" + str(len(files)*len(subPathstoProcess)))
						count = count + 1
		
			## Builds ImageJ-compatible downsampled images from resized z slices
			resImage = []
			for i,ch in enumerate(subDirstoProcess):
				IJ.showStatus("Processing channel wavelength " + ch)
				iStack = ImageStack(scaledWidth,scaledHeight)
				dirPath = rootPath + ch + "/resized/"
				files = glob.glob(os.path.join(dirPath,'*.tif'))
				maxZ = len(files)
				for fi in files:
					ip = (IJ.openImage(fi)).getProcessor()
					iStack.addSlice(ip)
				if (ch == ""):
					resImage.append(ImagePlus("ch_base",iStack))
				else:
					resImage.append(ImagePlus("ch_"+ch,iStack))
				resImage[i].show()
			write_log_file(parentPath+currentDir+"/analysis.log.txt","Built smaller images from Caliber source with disk ratio " + str(ratio) + " and xy ratio " + str(xyratio))
		
		
			## Makes composite image
			if (len(subDirstoProcess) == 1):
				compositeImage = IJ.getImage()
			else:
				paramList = [channelDict[ch]+"="+resImage[i].getTitle() for i,ch in enumerate(subDirstoProcess)]
				print(paramList)
				params = ' '.join(paramList) + " create ignore"
				print(params)
				IJ.run("Merge Channels...", params)
				compositeImage = IJ.getImage()
			targetCalibration = compositeImage.getCalibration()
			targetCalibration.pixelWidth = targetCalibration.pixelWidth / xyratio
			compositeImage.setCalibration(targetCalibration)
			# IJ.saveAsTiff(compositeImage,rootPath+os.path.basename(os.path.normpath(rootPath))+"_composite.tif")
			IJ.saveAsTiff(compositeImage,parentPath+currentDir+"/"+currentDir+"_composite.tif")
		
			## Makes MIP
			zproj = ZProjector(compositeImage)
			zproj.setMethod(ZProjector.MAX_METHOD)
			zproj.setStartSlice(1)
			zproj.setStopSlice(maxZ)
			zproj.doHyperStackProjection(True)
			projImage = zproj.getProjection()
			IJ.saveAsTiff(projImage,parentPath+currentDir+"/"+currentDir+"_composite_mip.tif")
		
			## Cleans up
			projImage.close()
			compositeImage.close()