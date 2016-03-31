from ij.io import DirectoryChooser
from ij.gui import GenericDialog
from ij import IJ
from ij import WindowManager
import os
import glob

dirChooser = DirectoryChooser("Choose directory of images to normalize...")
dirPath = dirChooser.getDirectory()
scaleXs = []
if dirPath is not None:
	if not os.path.exists(dirPath + "resized"):
		os.mkdir(dirPath + "resized")

	gd = GenericDialog("Settings...")
	gd.addNumericField("Final scale factor:",0.5,2)
	gd.addCheckbox("Convert multichannel to RGB:",True)
	gd.showDialog()
	if (gd.wasOKed()):
		common_scale = gd.getNextNumber()
		convert_to_rgb = gd.getNextBoolean()
		filecollection = glob.glob(os.path.join(dirPath, '*.tif'))
		if (len(filecollection) > 0):
			for path in filecollection:
				theImage = IJ.openImage(path)
				calibration = theImage.getCalibration()
				scaleXs.append(calibration.pixelWidth)
				theImage.close()
			lc_scale = max(scaleXs)
			print lc_scale
			for path in filecollection:
				theImage = IJ.openImage(path)
				bname1 = os.path.basename(path)
				bname2 = os.path.splitext(bname1)[0]
				this_cal = theImage.getCalibration()
				scale_factor = (this_cal.pixelWidth / lc_scale) * common_scale
				params = "x=" + str(scale_factor) + " y=" + str(scale_factor) + " z=1.0 interpolation=Bilinear average process create title=doggie"
				IJ.run(theImage,"Scale...",params)
				saveImage = WindowManager.getImage("doggie")
				pixelWidth = saveImage.getCalibration().pixelWidth
				pixelHeight = saveImage.getCalibration().pixelHeight
				pixelDepth = saveImage.getCalibration().pixelDepth
				if convert_to_rgb:
					old_saveImage = saveImage
					old_saveImage.changes = False
					saveImage = old_saveImage.flatten()
					old_saveImage.close()
				saveImage.getCalibration().pixelWidth = pixelWidth
				saveImage.getCalibration().pixelHeight = pixelHeight
				saveImage.getCalibration().pixelDepth = pixelDepth
				IJ.saveAsTiff(saveImage,dirPath+"resized/"+bname2+".tif")
				theImage.close()
				saveImage.close()
