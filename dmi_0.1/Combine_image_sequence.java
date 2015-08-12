import ij.*;
import ij.process.*;
import ij.gui.*;
import java.awt.*;
import ij.plugin.*;
import ij.plugin.frame.*;
import ij.io.*;
import java.io.*;

public class Combine_image_sequence implements PlugIn {

	public void run(String arg) {
		DirectoryChooser dc = new DirectoryChooser("Select image sequence directory...");
		String theDir = dc.getDirectory();
		if (theDir==null) { return; }

		String params = "open=[" + theDir + "] starting=1 increment=1 scale=100 file=[] sort";
		IJ.run("Image Sequence...", params);

		int [] wList = WindowManager.getIDList();
		if (wList.length < 1) { return; }
		String [] titles = new String[wList.length];
		int i;
		ImagePlus imp;
		for (i=0;i<wList.length;i++) {
			imp = WindowManager.getImage(wList[i]);
			titles[i] = imp.getTitle();
		}

		GenericDialog gd = new GenericDialog("Settings");
		gd.addChoice("Active stack:",titles,titles[0]);
		gd.addNumericField("Number of channels:",5,0);
		gd.addStringField("File label:","IMGid");
		gd.addCheckbox("Close images on exit?",false);
		gd.showDialog();

		if (gd.wasCanceled()) { return; }

		int activeStack = gd.getNextChoiceIndex();
		int numChannels = (int) gd.getNextNumber();
		ImagePlus img = WindowManager.getImage(wList[activeStack]);
		String baseTitle = gd.getNextString();
		if (baseTitle == null || baseTitle=="") baseTitle = "IMG";
		boolean doCloseImgs = gd.getNextBoolean();
		int numSlices = img.getNSlices();

		for (i=1;i<=numChannels;i++) {
			params = "slices=" + String.valueOf(i) + "-" + String.valueOf(numSlices) + "-" + String.valueOf(numChannels);
			IJ.run(img,"Make Substack...",params);
		}

		img.close();

		
		dc = new DirectoryChooser("Select saving directory...");
		String saveDir = dc.getDirectory();
		if (saveDir==null) { return; }
		wList = WindowManager.getIDList();
		if (wList.length < 1) { return; }
		for (i=0;i<wList.length;i++) {
			imp = WindowManager.getImage(wList[i]);
			IJ.save(imp,saveDir+"/"+baseTitle+"_ch"+String.valueOf(i+1)+".tif");
		}

		if (doCloseImgs) {
			for (i=0;i<wList.length;i++) {
				imp = WindowManager.getImage(wList[i]);
				imp.close();
			}
		}
	}
}
