import ij.*;
import ij.process.*;
import ij.gui.*;
import java.awt.*;
import ij.plugin.*;
import ij.plugin.frame.*;
import ij.io.*;
import java.io.*;

public class Make_condition_image implements PlugIn {

	public void run(String arg) {
		int i,j,k;
		ImagePlus imp;
		ImagePlus theImage = IJ.getImage();
		int [] wList = WindowManager.getIDList();
		String [] titles = new String[wList.length];
		int threshold=1;
		int iContainer;

		if (wList.length < 2) { return; }

		for (i=0;i<wList.length;i++) {
			imp = WindowManager.getImage(wList[i]);
			titles[i] = imp.getTitle();
		}

		GenericDialog gd = new GenericDialog("Set images");
		int numSlices = theImage.getNSlices();
		gd.addChoice("Conditioning image:",titles,titles[0]);
		gd.addChoice("Data image:",titles,titles[1]);
		gd.addNumericField("Conditioning threshold:",45,0);
		gd.addCheckbox("Normalize conditioning image contrast",false);
		gd.addCheckbox("Normalize data image contrast",true);
		gd.showDialog();

		if (gd.wasCanceled()) { return; }

		int conditionImageIndex = gd.getNextChoiceIndex();
		int dataImageIndex = gd.getNextChoiceIndex();
		threshold = (int) gd.getNextNumber();
		boolean autoContrast = gd.getNextBoolean();
		boolean autoDataContrast = gd.getNextBoolean();
		ImagePlus conditionImage = WindowManager.getImage(wList[conditionImageIndex]);
		ImagePlus dataImage = WindowManager.getImage(wList[dataImageIndex]);
		ImagePlus newDataImage = dataImage.duplicate();

		for (k=0;k<numSlices;k++) {
			conditionImage.setSliceWithoutUpdate(k+1);
			dataImage.setSliceWithoutUpdate(k+1);
			newDataImage.setSliceWithoutUpdate(k+1);
			if (autoContrast) {
				IJ.run(conditionImage,"Enhance Contrast","saturated=0.01 normalize");
			}

			ImageProcessor conditionIP = conditionImage.getProcessor();
			ImageProcessor dataIP = dataImage.getProcessor();
			ImageProcessor newDataIP = newDataImage.getProcessor();

			for (i=0;i<conditionImage.getWidth();i++) {
				for (j=0;j<conditionImage.getHeight();j++) {
					if (conditionIP.getPixel(i,j) >= threshold) {
						iContainer = dataIP.getPixel(i,j);
					} else {
						iContainer = 0;
					}
					newDataIP.set(i,j,iContainer);
				}
			}
		} 
		
		if (autoDataContrast) {
			IJ.run(newDataImage,"Enhance Contrast","saturated=0.01 normalize");
		}
		newDataImage.show();
	}

}
