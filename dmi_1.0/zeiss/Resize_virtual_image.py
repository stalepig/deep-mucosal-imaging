## Adds jar dependencies
import sys
sys.path.append("./jai-codec.jar")
sys.path.append("./jai-core.jar")

## Imports
import glob
import os
import math
import re
import shutil
import datetime
from ij.io import OpenDialog
from ij.plugin import Memory
from ij import IJ
from ij import WindowManager
from ij import ImagePlus
from ij import ImageStack
from ij.plugin import ZProjector
from javax.imageio import ImageIO
from java.awt.image import BufferedImage
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

def get_directory_size(sourceDir):
	sumSize = 0
	files = glob.glob(os.path.join(sourceDir,'*.tif'))
	for theFile in files:
		theSize = os.path.getsize(theFile)
		sumSize = sumSize + theSize
	return sumSize

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

def decode_image(data):
    stream = ByteArraySeekableStream(data);
    names = ImageCodec.getDecoderNames(stream);
    dec = ImageCodec.createImageDecoder(names[0], stream, None);
    im = dec.decodeAsRenderedImage();
    image = PlanarImage.wrapRenderedImage(im).getAsBufferedImage();
    return image

## Main body of script starts here
od = OpenDialog("Select parent LSM file...")
parentLSMFilePath = od.getPath()
parentLSMImageName = os.path.basename(parentLSMFilePath)
if parentLSMFilePath is not None:
	## Makes temporary directory
	make_destination_directories(parentLSMFilePath+"_tiles/tmp/",False)

	## Reads v_img/ directory
	if os.path.isdir(parentLSMFilePath+"_tiles/v_img/"):
		## Computes total file size and resizing ratio
		totFileSize = get_directory_size(parentLSMFilePath+"_tiles/v_img/") / 1048576.0
		totFijiMem = Memory().maxMemory() / 1048576.0
		allowedMem = totFijiMem/3.0
		ratio = allowedMem / totFileSize
		xyratio = math.sqrt(ratio)
		files = glob.glob(os.path.join(parentLSMFilePath+"_tiles/v_img/",'*.tif'))
		if xyratio > 1:
			ratio = 1
			xyratio = 1

		## Parses the filenames for image metadata
		maxZ = 0
		maxC = 0
		for theFile in files:
			p = re.compile(r'img_z_(\d+)_c_(\d+).tif')
			m = p.search(theFile)
			if m is None:
				IJ.log("Could not generate metadata for " + theFile)
			else:
				zSlice = int(m.group(1))
				cSlice = int(m.group(2))
				if (zSlice > maxZ):
					maxZ = zSlice
				if (cSlice > maxC):
					maxC = cSlice

		## Resizes each slice using Java
		count = 1
		scaledWidth = 0
		scaledHeight = 0
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
				IJ.saveAsTiff(outputImagePlus,parentLSMFilePath+"_tiles/tmp/" + outputImagePlus.getTitle())
				IJ.showStatus("Tile: " + str(count) + "/" + str(len(files)))
				count = count + 1

		## Builds ImageJ-compatible downsampled images from resized z slices
		make_destination_directories(parentLSMFilePath+"_tiles/stitched/",False)
		resImage = []
		for ch in range(maxC):
			IJ.showStatus("Processing channel " + str(ch+1))
			iStack = ImageStack(scaledWidth,scaledHeight)
			for z in range(maxZ):
				path = parentLSMFilePath + "_tiles/tmp/img_z_" + str(z+1) + "_c_" + str(ch+1) + ".tif"
				ip = (IJ.openImage(path)).getProcessor()
				iStack.addSlice(ip)
			resImage.append(ImagePlus("ch_"+str(ch+1),iStack))
			resImage[ch].show()
			IJ.saveAsTiff(resImage[ch],parentLSMFilePath+"_tiles/stitched/" + os.path.splitext(parentLSMImageName)[0] + "_ch" + str(ch+1) + ".tif")
		write_log_file(parentLSMFilePath+"_tiles/analysis.log.txt","Built smaller images from v_img/ source with disk ratio " + str(ratio) + " and xy ratio " + str(xyratio))

		## Makes composite image
		if maxC > 1:
			if maxC == 2:
				params = ("c1=" + resImage[0].getTitle() + 
						" c4=" + resImage[1].getTitle() + " create ignore")
			elif maxC == 3:
				params = ("c1=" + resImage[1].getTitle() +
						" c2=" + resImage[0].getTitle() +
						" c4=" + resImage[2].getTitle() + " create ignore")
			elif maxC == 4:
				params = ("c1=" + resImage[1].getTitle() +
						" c2=" + resImage[2].getTitle() +
						" c3=" + resImage[0].getTitle() +
						" c4=" + resImage[3].getTitle() + " create ignore")
			elif maxC == 5:
				params = ("c1=" + resImage[1].getTitle() +
						" c2=" + resImage[2].getTitle() +
						" c3=" + resImage[0].getTitle() +
						" c4=" + resImage[4].getTitle() + 
						" c7=" + resImage[3].getTitle() +
						" create ignore")
			else:
				IJ.log("No composite image created due to excess channels (>4)")
			IJ.run("Merge Channels...", params)
			compositeImage = IJ.getImage()
			IJ.saveAsTiff(compositeImage,parentLSMFilePath+"_tiles/stitched/" + os.path.splitext(parentLSMImageName)[0]+"_composite.tif")
		else:
			compositeImage = resImage[0]
		write_log_file(parentLSMFilePath+"_tiles/analysis.log.txt","Built composite image into stitched/")

		## Makes MIP
		zproj = ZProjector(compositeImage)
		zproj.setMethod(ZProjector.MAX_METHOD)
		zproj.setStartSlice(1)
		zproj.setStopSlice(maxZ)
		zproj.doHyperStackProjection(True)
		projImage = zproj.getProjection()
		IJ.saveAsTiff(projImage,parentLSMFilePath+"_tiles/stitched/" + os.path.splitext(parentLSMImageName)[0]+"_composite_mip.tif")
		write_log_file(parentLSMFilePath+"_tiles/analysis.log.txt","Built maximum intensity projection into stitched/")

		## Cleans up
		projImage.close()
		compositeImage.close()

		## Clears tmp/ directory
		shutil.rmtree(parentLSMFilePath+"_tiles/tmp")