from ij import IJ
from ij.gui import NonBlockingGenericDialog
from ij.io import SaveDialog

class CounterPoint:
	def __init__(self,x,y,clonenum):
		self.x = x
		self.y = y
		self.clonenum = clonenum
		

theImage = IJ.getImage()
stayinloop = True
cloneNum = 1
pointList = []

while (stayinloop):
	gd = NonBlockingGenericDialog("Clone counter...")
	gd.addNumericField("Clone:",cloneNum,0)
	gd.setOKLabel("Finalize clone")
	gd.setCancelLabel("Quit")
	gd.showDialog()

	if (gd.wasOKed()):
		roi = theImage.getRoi()
		if (not roi is None):
			cloneNum = int(gd.getNextNumber())
			polygon = roi.getFloatPolygon()
			for i in range(polygon.npoints):
				pointList.append(CounterPoint(polygon.xpoints[i],polygon.ypoints[i],cloneNum))
			IJ.run("Draw","stack")
			theImage.deleteRoi()
			cloneNum = cloneNum + 1
	else:
		stayinloop = False

sd = SaveDialog("Save counter file...","",".csv")
fileDir = sd.getDirectory()
fileName = sd.getFileName()
if fileName is not None:
	filePath = fileDir + fileName
	fileobj = open(filePath,"w")
	for item in pointList:
		fileobj.write(str(item.x)+","+str(item.y)+","+str(item.clonenum)+"\n")
	fileobj.close()

	
