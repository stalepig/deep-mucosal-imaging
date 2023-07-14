from loci.formats import ImageReader
from loci.formats import MetadataTools
from ij import IJ
from ij import ImageStack
from ij import ImagePlus
from ij.measure import Calibration
from ij.process import ShortProcessor
from ij.io import OpenDialog
from java.nio import ByteBuffer
from java.nio import ByteOrder
from java.awt.image import ColorModel
from array import array
import math
import os

od = OpenDialog("Open *.sld file...")
baseDir = od.getDirectory()
if (baseDir is not None):
	baseName = od.getFileName()
	filePath = baseDir + baseName
	saveDir = filePath + "_tiles/"
	
	if not os.path.exists(saveDir):
		os.makedirs(saveDir)	
	
	theReader = ImageReader()
	omeMeta = MetadataTools.createOMEXMLMetadata()
	theReader.setMetadataStore(omeMeta)
	theReader.setId(filePath)
	IJ.log("Processing " + filePath)
	IJ.log("Series count: " + str(theReader.getSeriesCount()))
	print("Series count: " + str(theReader.getSeriesCount()))
	for series in range(0,theReader.getSeriesCount()):
		theReader.setSeries(series)
		title = omeMeta.getImageName(series)
		xcal = omeMeta.getPixelsPhysicalSizeX(series)
		ycal = omeMeta.getPixelsPhysicalSizeY(series)
		zcal = omeMeta.getPixelsPhysicalSizeZ(series)
		IJ.log(str(theReader.getImageCount()) + " planes in series " + str(series+1))
		iStack = [ImageStack(theReader.getSizeX(),theReader.getSizeY()) for ch in range(0,theReader.getSizeC())]
		for z in range(0,theReader.getImageCount()):
	 		theBytes = theReader.openBytes(z)
	 		bb = ByteBuffer.wrap(theBytes)
	 		bb.order(ByteOrder.LITTLE_ENDIAN)
	 		sb = bb.asShortBuffer()
	 		pixels = []
	 		for i in range(0,sb.capacity()):
	 			pixels.append(sb.get(i))
	 		print(z)
	 		sProcess = ShortProcessor(theReader.getSizeX(),theReader.getSizeY())
	 		[sProcess.set(idx,pixels[idx]) for idx in range(0,len(pixels))]
	 		iStack[z % theReader.getSizeC()].addSlice(sProcess)
	 		IJ.showProgress(z,theReader.getImageCount())
		theImage = [ImagePlus("ch_" + str(ch),iStack[ch]) for ch in range(0,theReader.getSizeC())]
		for ch in range(0,theReader.getSizeC()):
			theImage[ch].show()
		if (theReader.getSizeC() == 3):
			params = "c1=ch_1 c2=ch_2 c3=ch_0 create ignore"
		elif (theReader.getSizeC() == 2):
			params = "c1=ch_1 c4=ch_0 create ignore"
		else:
			params = "c4=ch_0 create ignore"
		IJ.run("Merge Channels...", params)
		compositeImage = IJ.getImage()
		compositeImage.setTitle(title)
		cal = Calibration()
		if (xcal is not None):
			cal.pixelWidth = xcal.value()
			cal.pixelHeight = ycal.value()
		if (zcal is not None):
			cal.pixelDepth = zcal.value()
		else:
			cal.pixelDepth = 1
		cal.setXUnit("um")
		cal.setYUnit("um")
		cal.setZUnit("um")
		compositeImage.setCalibration(cal)
		compositeImage.updateAndRepaintWindow()
		
		IJ.saveAsTiff(compositeImage,saveDir + title + ".tif")
		compositeImage.close()
	theReader.close()