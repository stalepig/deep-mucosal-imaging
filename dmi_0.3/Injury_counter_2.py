from ij import IJ
from ij.io import SaveDialog
from ij.gui import WaitForUserDialog

theImage = IJ.getImage()
ip = theImage.getProcessor()

sd = SaveDialog("Select file to save results","injury",".csv")
saveFileName = sd.getFileName()
saveFileDir = sd.getDirectory()
if (saveFileName is not None):
	saveFilePath = saveFileDir + saveFileName
	savefilehandler = open(saveFilePath,"w")
	
	waitDialog = WaitForUserDialog("Use freeform tool to outline the piece of tissue")
	waitDialog.show()
	
	roi = theImage.getRoi()
	if (roi is not None):
		print type(roi)
		thePolygon = roi.getPolygon()
		boundRect = thePolygon.getBounds()
	
		for i in range(boundRect.x,boundRect.x+boundRect.width):
			pos_pixels = 0
			tot_pixels = 0
			IJ.showProgress(i-boundRect.x,boundRect.width)
			for j in range(boundRect.y,boundRect.y+boundRect.height):
				if thePolygon.contains(i,j):
					value = ip.getPixelValue(i,j)
					tot_pixels = tot_pixels + 1
					if (value > 128):
						pos_pixels = pos_pixels + 1
			if tot_pixels > 0:
				pos_fraction = pos_pixels / float(tot_pixels)
			else:
				pos_fraction = 0
			str_out = str(i) + "," + str(pos_pixels) + "," + str(tot_pixels) + "," + str(pos_fraction) + "\n"
			savefilehandler.write(str_out)
	
	savefilehandler.close()
