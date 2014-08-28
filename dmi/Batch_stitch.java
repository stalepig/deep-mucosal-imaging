import ij.*;
import ij.process.*;
import ij.gui.*;
import java.awt.*;
import ij.plugin.*;
import ij.plugin.frame.*;
import ij.io.*;
import java.io.*;

public class Batch_stitch implements PlugIn {

	public void run(String arg) {
		int i;
		String currFile = "";
		String currPath = "";
		String outDir = "";
		String [] fileTokens;
		boolean success = false;
		String params = "";

		DirectoryChooser dc = new DirectoryChooser("Select directory of LSM files...");
		String theDir = dc.getDirectory();
		if (theDir==null) { return; }
		File folder = new File(theDir);
		File [] fileList = folder.listFiles(new FilenameFilter() {
			public boolean accept(File folder, String name) {
				return name.endsWith(".lsm");
			}
		});
		for (i=0;i<fileList.length;i++) {
			currFile = fileList[i].getName();
			fileTokens = currFile.split("\\.(?=[^\\.]+$)");
			outDir = theDir + fileTokens[0] + "_seq/";
			success = (new File(outDir)).mkdirs();
			currPath = theDir + currFile;

			params = "type=[Positions from file] order=[Defined by image metadata] browse=[" + currPath + "] multi_series_file=[" + currPath + "] fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 compute_overlap increase_overlap=10 subpixel_accuracy computation_parameters=[Save memory (but be slower)] image_output=[Write to disk] output_directory=[" + outDir + "]";
		
			// WaitForUserDialog wd = new WaitForUserDialog(params);
			// wd.show();
			IJ.run("Grid/Collection stitching", params);
		}

	}
}
