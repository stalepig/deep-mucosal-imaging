import ij.*;
import ij.process.*;
import ij.gui.*;
import java.awt.*;
import ij.plugin.*;
import ij.plugin.frame.*;
import ij.io.*;

public class Normalize_contrast_on_z implements PlugIn {

	public void run(String arg) {
		ImagePlus imp = IJ.getImage();
		ImagePlus resultImage = imp.duplicate();
		int numSlices = imp.getNSlices();
		int currSlice;
		ContrastEnhancer conhance = new ContrastEnhancer();
		String [] algorithms = new String[2];
		
		algorithms[0] = "Global";
		algorithms[1] = "Local";

		GenericDialog gd = new GenericDialog("Parameters");
		gd.addNumericField("Percent of pixels to saturate:",0.35,2);
		gd.addChoice("Select algorithm:",algorithms,"Global");
		gd.showDialog();
		double percent = gd.getNextNumber();
		int selectAlgorithm = gd.getNextChoiceIndex();

		if (gd.wasCanceled()) { return; }

		if (percent<0 || percent>100) { return; }

		String paramArg = "saturated=" + percent + " normalize";

		for (currSlice=1;currSlice<=numSlices;currSlice++) {
			resultImage.setSliceWithoutUpdate(currSlice);	
			if (selectAlgorithm==0) {
				IJ.run(resultImage,"Enhance Contrast",paramArg);
			} else {
				IJ.run(resultImage,"Enhance Local Contrast (CLAHE)", "blocksize=127 histogram=256 maximum=3 mask=*None* fast_(less_accurate)");
			}
			IJ.showProgress(currSlice,numSlices);
		}
		resultImage.setSliceWithoutUpdate(1);

		resultImage.show();

	}

}
