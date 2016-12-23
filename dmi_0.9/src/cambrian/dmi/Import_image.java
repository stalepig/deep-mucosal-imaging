package cambrian.dmi;

import java.io.File;
import java.io.FilenameFilter;
import java.io.IOException;

import ij.IJ;
import ij.ImageJ;
import ij.io.OpenDialog;
import ij.plugin.PlugIn;
import loci.formats.FormatException;
import loci.formats.ImageReader;

public class Import_image implements PlugIn {
	FilenameFilter tiffFilter = new FilenameFilter() {
		public boolean accept(File dir, String name) {
			String lowercaseName = name.toLowerCase();
			if (lowercaseName.endsWith(".tif")) {
				return true;
			} else {
				return false;
			}
		}
	};
	
	public void run(String arg) {
		OpenDialog od = new OpenDialog("Select parent LSM file to open");
		String parentLSMFilePath = od.getPath(); 
		String subdirectoryPath;
		DmiVirtualImage dmiImage;
		ImageReader theReader;
		DmiVirtualImageDisplayManager dm;
		
		if (parentLSMFilePath != null) {
			theReader = new ImageReader();
			try {
				theReader.setId(parentLSMFilePath);					
				subdirectoryPath = parentLSMFilePath + "_tiles/v_img/";
				dmiImage = new DmiVirtualImage(subdirectoryPath,subdirectoryPath,"tif",theReader.getSizeZ(),theReader.getSizeC(),theReader.getSizeT());
				theReader.close();
				
				dm = new DmiVirtualImageDisplayManager(dmiImage);
				
			} catch(IOException e) {
				IJ.log("Could not open LSM file for reading of metadata!");
				IJ.log(e.getMessage());
			} catch(FormatException e) {
				IJ.log("Input file is not of supported type!");
				IJ.log(e.getMessage());
			}
		}
	}
	
	

	/**
	 * Main method for debugging.
	 *
	 * For debugging, it is convenient to have a method that starts ImageJ, loads an
	 * image and calls the plugin, e.g. after setting breakpoints.
	 *
	 * @param args unused
	 */
	public static void main(String[] args) {
		// set the plugins.dir property to make the plugin appear in the Plugins menu
		Class<?> clazz = Import_image.class;
		String url = clazz.getResource("/" + clazz.getName().replace('.', '/') + ".class").toString();
		String pluginsDir = url.substring(5, url.length() - clazz.getName().length() - 6);
		System.setProperty("plugins.dir", pluginsDir);

		// start ImageJ
		new ImageJ();

		// open a sample image

		// run the plugin
		IJ.runPlugIn(clazz.getName(), "");
	}

}
