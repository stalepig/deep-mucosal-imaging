import ij.*;
import ij.process.*;
import ij.gui.*;
import java.awt.*;
import ij.plugin.*;
import ij.plugin.frame.*;
import ij.plugin.filter.*;
import ij.measure.*;

public class Explore_zseries implements PlugIn {
	
	public void run(String arg) {
		ImagePlus theImage = IJ.getImage();
		boolean isQuit = false;
		int numSlices = theImage.getNSlices();
		int i,j;
		Analyzer analyte = new Analyzer(theImage);
		ResultsTable rt = ResultsTable.getResultsTable();
		double [] xresults, yresults;
		Plot pl;
		PlotWindow pw;

		xresults = new double[numSlices];
		for (i=0;i<numSlices;i++) {
			xresults[i] = i + 1.0;
		}
		
		do {
			NonBlockingGenericDialog gd = new NonBlockingGenericDialog("Click to plot ROI over time");
			gd.addMessage("Pick a single ROI to examine");
			gd.showDialog();

			if (gd.wasCanceled()) {
				isQuit = true;
			} else {
				isQuit = false;

				rt.reset();
				for (i=0;i<numSlices;i++) {
					theImage.setSliceWithoutUpdate(i+1);
					analyte.measure();
					analyte.displayResults();
				}
				theImage.setSlice(1);
				yresults = rt.getColumnAsDoubles(1);


				pl = new Plot("Plot","Z-Slice","Intensity",xresults,yresults);
				pw = pl.show(); 
			}
		} while (isQuit == false);
	}
}
