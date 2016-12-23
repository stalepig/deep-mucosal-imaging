package cambrian.dmi;

import ij.ImagePlus;
import ij.process.LUT;
import ij.process.ImageProcessor;
import java.io.FilenameFilter;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.awt.Color;
import java.io.File;
import ij.ImageStack;
import ij.IJ;
import ij.CompositeImage;

public class DmiVirtualImage {
	
	protected String [] slicePaths;
	protected int zSlices, cSlices, tSlices;
	protected int xSize, ySize;
	protected String imageTitle;
	protected LUT [] LUTarray;
	
	public DmiVirtualImage(String imageTitle, String imageDirectory, final String ext, int zSlices, int cSlices, int tSlices) {
		int i;
		this.imageTitle = imageTitle;
		
		FilenameFilter theFilter = new FilenameFilter() {
			public boolean accept(File dir, String name) {
				String lowercaseName = name.toLowerCase();
				if (lowercaseName.endsWith("." + ext)) {
					return true;
				} else {
					return false;
				}
			}
		};
		
		File folder = new File(imageDirectory);
		File [] fileList = folder.listFiles(theFilter);
		ImagePlus diagnosticImage;
		Pattern p = Pattern.compile("img_z_(\\d+)_c_(\\d+).tif");
		Matcher m;
		int zInd = 0;
		int cInd = 0;
		String text;
		boolean doesMatch;
		
		if (fileList.length > 0) {
			slicePaths = new String[fileList.length];
			for (i=0;i<fileList.length;i++) {
				text = fileList[i].getName();
				m = p.matcher(text);
				doesMatch = m.matches();
				if (doesMatch) {
					zInd = Integer.parseInt(m.group(1)) - 1;
					cInd = Integer.parseInt(m.group(2)) - 1;
					slicePaths[zInd*cSlices+cInd] = fileList[i].getAbsolutePath();
				}
			}
			diagnosticImage = IJ.openImage(slicePaths[0]);
			this.xSize = diagnosticImage.getWidth();
			this.ySize = diagnosticImage.getHeight();
			diagnosticImage.close();
		}
		
		this.zSlices = zSlices;
		this.cSlices = cSlices;
		this.tSlices = tSlices;
		
		if (cSlices == 1) { 
			LUTarray = new LUT[] {LUT.createLutFromColor(Color.WHITE)};
		} else if (cSlices == 2) {
			LUTarray = new LUT[] {LUT.createLutFromColor(Color.RED),LUT.createLutFromColor(Color.WHITE)};
		} else if (cSlices == 3) {
			LUTarray = new LUT[] {LUT.createLutFromColor(Color.GREEN),LUT.createLutFromColor(Color.RED),LUT.createLutFromColor(Color.WHITE)};
		} else if (cSlices == 4) {
			LUTarray = new LUT[] {LUT.createLutFromColor(Color.BLUE),LUT.createLutFromColor(Color.RED),LUT.createLutFromColor(Color.GREEN),LUT.createLutFromColor(Color.WHITE)};
		} else if (cSlices == 5) {
			LUTarray = new LUT[] {LUT.createLutFromColor(Color.BLACK),LUT.createLutFromColor(Color.RED),LUT.createLutFromColor(Color.GREEN),LUT.createLutFromColor(Color.YELLOW),LUT.createLutFromColor(Color.WHITE)};
		} else {
			LUTarray = null;
		}
		
	}
	
	public ImagePlus getIndividualSlice(int slice) {
		return(IJ.openImage(slicePaths[slice-1]));
	}
	
	public CompositeImage getZImage(int zSlice, int tSlice) {
		int startSliceIndex = cSlices*(zSlice-1)*tSlice;
		int i;
		int color;
		int ch;
		ImageStack iStack = new ImageStack(xSize,ySize);
		ImagePlus containerImage;
		ImagePlus resultImage;
		CompositeImage returnImage;
		
		for (i=startSliceIndex;i<startSliceIndex+cSlices;i++) {
			containerImage = IJ.openImage(slicePaths[i]);
			color = i-startSliceIndex+1;
			iStack.addSlice("c:"+Integer.toString(color), containerImage.getProcessor());
		}
		
		resultImage = new ImagePlus("z_"+Integer.toString(zSlice)+"_t_"+Integer.toString(tSlice),iStack);
		resultImage.setDimensions(cSlices, 1, 1);
		returnImage = new CompositeImage(resultImage,CompositeImage.COMPOSITE);
		returnImage.setOpenAsHyperStack(true);	
		for (ch=0;ch<cSlices;ch++) {
			returnImage.setChannelLut(LUTarray[ch], ch+1);
		}
		return returnImage;
	}
	
	public CompositeImage getZImage(int zStart, int zEnd, int tSlice) {
		int i;
		int color;
		int zpos;
		int startSliceIndex = cSlices*(zStart-1)*tSlice;
		int endSliceIndex = cSlices*(zEnd-1)*tSlice+cSlices-1;
		ImagePlus containerImage;
		ImagePlus resultImage;
		CompositeImage returnImage;
		int ch;
		
		resultImage = IJ.createHyperStack("z_"+Integer.toString(zStart)+"-"+Integer.toString(zEnd)+"_t_"+Integer.toString(tSlice), xSize, ySize, cSlices, zEnd-zStart+1, 1, 8);		
		for (i=startSliceIndex;i<=endSliceIndex;i++) {
			containerImage = IJ.openImage(slicePaths[i]);
			color = (i-startSliceIndex)%cSlices+1;
			zpos = (i-startSliceIndex)/cSlices+1;
			resultImage.setSliceWithoutUpdate(i-startSliceIndex+1);
			resultImage.setProcessor(containerImage.getProcessor());
		}
		resultImage.setSliceWithoutUpdate(1); // have to change slice so that the last ImageProcessor is written - a bug in ImageJ
		returnImage = new CompositeImage(resultImage,CompositeImage.COMPOSITE);
		returnImage.setOpenAsHyperStack(true);
		for (ch=0;ch<cSlices;ch++) {
			returnImage.setChannelLut(LUTarray[ch], ch+1);
		}
		return returnImage;
	}
	
	
	public int getNChannels() { return cSlices; }
	public int getNZSlices() { return zSlices; }
	public int getNFrames() { return tSlices; }
	public int getXSize() { return xSize; }
	public int getYSize() { return ySize; }
	public String getTitle() { return imageTitle; }
	
}
