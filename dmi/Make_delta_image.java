import ij.*;
import ij.process.*;
import ij.gui.*;
import java.awt.*;
import ij.plugin.*;
import ij.plugin.frame.*;
import ij.plugin.filter.*;
import ij.measure.*;

public class Make_delta_image implements PlugIn {

	public void run(String arg) {
		ImagePlus sourceImage = IJ.getImage();
		ImagePlus theImage = sourceImage.duplicate();;
		ImageProcessor theIP, deltaIP;
		ImagePlus deltaImage = theImage.duplicate();
		ImageCalculator ic = new ImageCalculator();
		ImagePlus img1, img2, resImg;

		GenericDialog gd = new GenericDialog("Parameters");
		gd.addNumericField("Slice distance:",2,0);
		gd.addNumericField("Start of time window (slice num):",10,0);
		gd.addNumericField("End of time window (slice num):",20,0);
		gd.addCheckbox("Run median filter on source image",true);
		gd.showDialog();

		int numSlices = theImage.getNFrames();
		int sliceDistance = (int) gd.getNextNumber();
		int sliceStart = (int) gd.getNextNumber();
		int sliceEnd = (int) gd.getNextNumber();
		boolean runMedianFilter = gd.getNextBoolean();
		if (sliceDistance > numSlices || sliceStart > numSlices || sliceEnd > numSlices) return;
		if (sliceStart <= sliceDistance) return;

		int i,j,k;

		if (runMedianFilter) IJ.run(theImage,"Median...","radius=2 stack");

		img1 = extractSlice(theImage,1);
		for (k=sliceDistance;k<numSlices;k++) {
			img2 = extractSlice(theImage,k+1);
			resImg = ic.run("Subtract create",img2,img1);
			deltaImage.setSliceWithoutUpdate(k+1);
			deltaImage.setProcessor(resImg.getProcessor());
			img1 = img2.duplicate();
		}

		deltaImage.show();
		String params = "start=" + String.valueOf(sliceStart-sliceDistance+1) + " stop=" + String.valueOf(sliceEnd-sliceDistance+1) + " projection=[Max Intensity]";
		IJ.run(deltaImage,"Z Project...",params);

		for (i=0;i<sliceDistance;i++) {
			deltaImage.setSliceWithoutUpdate(1);
			IJ.run(deltaImage,"Delete Slice","");
		}

	}

	private ImagePlus extractSlice(ImagePlus img, int slice) {
		ImageProcessor ip;
		ImagePlus retImg = new ImagePlus();

		img.setSliceWithoutUpdate(slice);
		ip = img.getProcessor().duplicate();
		retImg.setProcessor(ip);

		return retImg;
	}

}
