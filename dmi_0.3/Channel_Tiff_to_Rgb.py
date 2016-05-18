import os
from ij.io import DirectoryChooser
from ij import IJ
from ij.plugin import ChannelSplitter
from ij.process import LUT
from ij.process import StackConverter
from java.awt import Color
from ij.gui import GenericDialog

dc = DirectoryChooser("Select folder to operate on...")
dirPath = dc.getDirectory()
if dirPath is not None:
	dc2 = DirectoryChooser("Select output directory...")
	outPath = dc2.getDirectory()
	if outPath is not None:
		gd = GenericDialog("Options...")
		gd.addCheckbox("Recolor_images",True)
		gd.showDialog()
		if (gd.wasOKed()):
			doRecolor = gd.getNextBoolean()
		
			for f in os.listdir(dirPath):
				if f.endswith(".tif") or f.endswith(".tiff"):
					theImage = IJ.openImage(dirPath+f)
					IJ.log("Loaded " + f)
					palette = [Color.GREEN,Color.RED,Color.BLUE]
					if (theImage.getNChannels() < 4):
						if doRecolor:
							for i in range(theImage.getNChannels()):
								theImage.setChannelLut(LUT.createLutFromColor(palette[i]),i+1)
						try:
							sc = StackConverter(theImage)
							sc.convertToRGB()
							IJ.saveAsTiff(theImage,outPath+os.path.splitext(f)[0]+"_rgb.tif")
							IJ.log("Completed " + f)
						except:
							IJ.log("Exception thrown during RGB conversion, image skipped")
						finally:
							theImage.close()
					else:
						IJ.log("Image has too many color channels")
				