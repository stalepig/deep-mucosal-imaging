import ij.*;
import ij.process.*;
import ij.gui.*;
import java.awt.*;
import ij.plugin.*;
import ij.plugin.frame.*;

public class Z_projection_and_color_split implements PlugIn {

	public void run(String arg) {
		ImagePlus theImage = IJ.getImage();
		GenericDialog gd = new GenericDialog("Select z-stacks");
		int numSlices = theImage.getNSlices();
		gd.addNumericField("Start z slice:",1,0);
		gd.addNumericField("End z slice:",numSlices,0);
		gd.showDialog();

		if (gd.wasCanceled()) { return; }

		int startSlice = (int) gd.getNextNumber();
		int endSlice = (int) gd.getNextNumber();

		ImagePlus [] splitImages = ChannelSplitter.split(theImage);

		int i;
		ZProjector zproj = new ZProjector();
		ImagePlus projectedImage;
		for (i=0;i<splitImages.length;i++) {
			zproj.setImage(splitImages[i]);
			zproj.setStartSlice(startSlice);
			zproj.setStopSlice(endSlice);
			zproj.setMethod(ZProjector.MAX_METHOD);
			zproj.doProjection();
			projectedImage = zproj.getProjection();
			projectedImage.show();	
		}

		theImage.close();


	}

}
