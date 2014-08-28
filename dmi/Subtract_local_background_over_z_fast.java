import ij.*;
import ij.process.*;
import ij.gui.*;
import java.awt.*;
import ij.plugin.*;
import ij.plugin.frame.*;
import ij.plugin.filter.*;
import ij.measure.*;
import java.util.Arrays;

public class Subtract_local_background_over_z_fast implements PlugIn {

	public double[] range(double start, double end, double interval)
	{
		int i = 0;
		double sum = start;
		
		while (sum < end) {
			i++;
			sum = sum + interval;
		}

		int size = i;

		double[] result = new double[size];
		
		for (int j=0;j<size;j++) {
			result[j] = start+j*interval;
		}

		return result;
	}

	public int[] range(int start, int end)
	{
		int size = end-start;
		int [] result = new int[size];

		for (int i=0;i<size;i++) {
			result[i] = start+i;
		}

		return result;
	}
	
	public void run(String arg) {

		GenericDialog gd = new GenericDialog("Parameters to subtract local background...");
		gd.addNumericField("Window Size (pixels):",512,0);
		gd.addNumericField("Window overlap factor (>1):",5,0);
		gd.addNumericField("Standard deviation limit:",1.0,1);
		gd.addNumericField("Pixel ignore threshold (higher is faster):",10,0);
		gd.showDialog();

		double windowSize, windowMultiple, sdMultiple, ignoreIntensity;
		ImagePlus originalImage, theImage, writeImage;
		int startSlice;
		Analyzer analyzer;
		ResultsTable rt;
		double [] lefts, tops;
		ImageProcessor ip;
		Roi roi;
		double left, top;
		double miniWidth,miniHeight;
		double meanvalue, sdvalue, threshold;
		double [] xs, ys;

		if (gd.wasOKed()) {
			windowSize = gd.getNextNumber();
			windowMultiple = gd.getNextNumber();
			sdMultiple = gd.getNextNumber();
			ignoreIntensity = gd.getNextNumber();

			IJ.run("Set Measurements...", "  mean standard redirect=None decimal=3");
			originalImage = IJ.getImage();
			startSlice = originalImage.getSlice();
			theImage = originalImage.duplicate();
			writeImage = originalImage.duplicate();
			analyzer = new Analyzer(theImage);
			rt = ResultsTable.getResultsTable();
			rt.reset();

			lefts = range(0,theImage.getWidth(),windowSize/windowMultiple);
			tops = range(0,theImage.getHeight(),windowSize/windowMultiple);
			System.out.println(Arrays.toString(lefts));
			System.out.println(Arrays.toString(tops));

			for (int i=1;i<theImage.getNSlices()+1;i++) {
				theImage.setSliceWithoutUpdate(i);
				writeImage.setSliceWithoutUpdate(i);
				ip = writeImage.getProcessor();

				for (int j=0;j<lefts.length;j++) {
					left = lefts[j];
					for (int k=0;k<tops.length;k++) {
						top = tops[k];
						if (left+windowSize>theImage.getWidth()) {
							miniWidth = theImage.getWidth() - left;
						} else {
							miniWidth = windowSize;
						}
						if (top+windowSize>theImage.getHeight()) {
							miniHeight = theImage.getHeight() - top;
						} else {
							miniHeight = windowSize;
						}

						roi = new Roi(left,top,miniWidth,miniHeight);
						theImage.setRoi(roi,false);
						analyzer.measure();
						meanvalue = rt.getValueAsDouble(ResultsTable.MEAN,rt.getCounter()-1);
						sdvalue = rt.getValueAsDouble(ResultsTable.STD_DEV,rt.getCounter()-1);
						threshold = meanvalue + sdMultiple*sdvalue;

						if (threshold > ignoreIntensity) {
							xs = range(left,left+miniWidth,1);
							ys = range(top,top+miniHeight,1);
							for (int l=0;l<xs.length;l++) {
								for (int m=0;m<ys.length;m++) {
									if (ip.get((int)xs[l],(int)ys[m]) < threshold) {
										ip.set((int)xs[l],(int)ys[m],0);
									}
								}
							}
						}
					}
				}

				IJ.showProgress(i,theImage.getNSlices()+1);
			}
		
			writeImage.show();
			writeImage.setSlice(startSlice);
		}
	}

}