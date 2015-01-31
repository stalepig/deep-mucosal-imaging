import ij.*;
import ij.process.*;
import ij.gui.*;
import java.awt.*;
import ij.plugin.*;
import ij.plugin.frame.*;
import ij.io.*;
import java.io.*;

public class Make_condition_histogram implements PlugIn {

	public void run(String arg) {
		int i,j;
		ImagePlus imp;
		ImagePlus theImage = IJ.getImage();
		int [] wList = WindowManager.getIDList();
		String [] titles = new String[wList.length];
		int threshold=1;

		if (wList.length < 2) { return; }

		for (i=0;i<wList.length;i++) {
			imp = WindowManager.getImage(wList[i]);
			titles[i] = imp.getTitle();
		}

		GenericDialog gd = new GenericDialog("Select z-slice");
		int numSlices = theImage.getNSlices();
		gd.addNumericField("z slice:",1,0);
		gd.addChoice("Conditioning image:",titles,titles[0]);
		gd.addChoice("Data image:",titles,titles[1]);
		gd.addNumericField("Starting threshold:",15,0);
		gd.addNumericField("Threshold increment:",10,0);
		gd.addCheckbox("Normalize conditioning image contrast",true);
		gd.addCheckbox("Normalize data image contrast",true);
		gd.showDialog();

		if (gd.wasCanceled()) { return; }

		int activeSlice = (int) gd.getNextNumber();
		int conditionImageIndex = gd.getNextChoiceIndex();
		int dataImageIndex = gd.getNextChoiceIndex();
		int thresholdStart = (int) gd.getNextNumber();
	    int thresholdInc = (int) gd.getNextNumber();	
		boolean autoContrast = gd.getNextBoolean();
		boolean autoDataContrast = gd.getNextBoolean();
		ImagePlus conditionImage = WindowManager.getImage(wList[conditionImageIndex]);
		ImagePlus dataImage = WindowManager.getImage(wList[dataImageIndex]);

		if (activeSlice > numSlices) { return; }

		conditionImage.setSlice(activeSlice);
		dataImage.setSlice(activeSlice);
		if (autoContrast) {
			IJ.run(conditionImage,"Enhance Contrast","saturated=0.01 normalize");
		}
		if (autoDataContrast) {
			IJ.run(dataImage,"Enhance Contrast","saturated=0.01 normalize");
		}
		ImageProcessor conditionIP = conditionImage.getProcessor();
		ImageProcessor dataIP = dataImage.getProcessor();

		try {
			SaveDialog sdialog = new SaveDialog("Save histogram file",titles[0]+"-hist",".csv");
			String saveDir = sdialog.getDirectory();
			String saveName = sdialog.getFileName();
			String outPath = saveDir + saveName;

			FileWriter fileWriter = new FileWriter(outPath);
			BufferedWriter bufferedWriter = new BufferedWriter(fileWriter);
			int iContainer;

			for (threshold=thresholdStart;threshold <= 255; threshold+=thresholdInc) {
				bufferedWriter.write(String.valueOf(threshold)+",");
				for (i=0;i<conditionImage.getWidth();i++) {
					for (j=0;j<conditionImage.getHeight();j++) {
						if (conditionIP.getPixel(i,j) >= threshold) {
							iContainer = dataIP.getPixel(i,j);
							bufferedWriter.write(String.valueOf(iContainer)+",");
						}
					}
				}
				bufferedWriter.write("\n");
			}

			bufferedWriter.close();

		} catch (IOException ex) {
			ex.printStackTrace();
		}

	}
}
