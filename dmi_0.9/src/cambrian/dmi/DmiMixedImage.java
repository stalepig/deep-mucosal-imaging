package cambrian.dmi;

import java.io.File;

import ij.IJ;
import ij.CompositeImage;
import ij.ImagePlus;
import ij.ImageStack;

public class DmiMixedImage extends DmiVirtualImage {
	protected double imageDiskSize;
	protected double sliceDiskSize;
	protected int fastStackZSize;
	protected int fastStackZCenter;
	protected int fastStackZStart;
	protected int fastStackZEnd;
	protected CompositeImage fastStackImage;
	
	public DmiMixedImage(String imageTitle, String imageDirectory, final String ext, int zSlices, int cSlices, int tSlices) {
		super(imageTitle,imageDirectory,ext,zSlices,cSlices,tSlices);
		
		int i;
		File fi;
		double size;
		int halfWidth;
		for (i=0;i<this.slicePaths.length;i++) {
			fi = new File(this.slicePaths[i]);
			if (fi.exists()) {
				size = fi.length();
				imageDiskSize = imageDiskSize + size;
				sliceDiskSize = size;
			}
		}
		
		fastStackZSize = computeZSlicesInRAM(0.5);
		fastStackZCenter = (int) (zSlices / 2);
		if (fastStackZSize % 2 == 0) {
			halfWidth = (int) (fastStackZSize / 2);
			fastStackZStart = fastStackZCenter-halfWidth+1;
			fastStackZEnd = fastStackZCenter+halfWidth;
		} else {
			halfWidth = (int) ((fastStackZSize-1) / 2);
			fastStackZStart = fastStackZCenter-halfWidth;
			fastStackZEnd = fastStackZCenter+halfWidth;
		}
		fastStackImage = getZImage(fastStackZStart,fastStackZEnd,1);
	}
	
	public CompositeImage getZImage(int zSlice,int tSlice) {
		int ch;
		ImageStack iStack = new ImageStack(xSize,ySize);
		ImagePlus resultImage;
		CompositeImage returnImage;
		
		if (zSlice < fastStackZStart || zSlice > fastStackZEnd) {
			return super.getZImage(zSlice, tSlice);
		} else {
			for (ch=1;ch<=cSlices;ch++) {
				fastStackImage.setPositionWithoutUpdate(ch, zSlice-fastStackZStart+1, tSlice);
				iStack.addSlice("c:"+Integer.toString(ch), fastStackImage.getProcessor());
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
	}
	
	public void recenterFastStackZ(int zCenter, int tSlice, boolean processLikeQueue) {
		int distance = zCenter - fastStackZCenter;
		int i;
		
		if (distance != 0) {
			if (processLikeQueue) {
				if (distance > 0) {
					for (i=0;i<distance;i++) {
						moveFastStackZUp(tSlice);
					}
				} else {
					for (i=0;i<distance;i--) {
						moveFastStackZDown(tSlice);
					}
				}
			} else {
				// recompute total RAM-resident stack
				initializeFastStack(zCenter,tSlice);
			}
		}
	}
	
	private int computeZSlicesInRAM(double fractionOfFreeMemToUse) {
		double memUsed = (double) IJ.currentMemory();
		double memMax = (double) IJ.maxMemory();
		double memFree = memMax - memUsed;
		double memToUse = fractionOfFreeMemToUse * memFree;
		int slicesInMem = (int) (memToUse / sliceDiskSize);
		int zSlicesInMem = (int) (slicesInMem / cSlices);
		
		if (zSlicesInMem > zSlices) {
			zSlicesInMem = zSlices;
		}
		if (zSlicesInMem < 1) {
			zSlicesInMem = 0;
		}
		
		return zSlicesInMem;
	}
	
	private void moveFastStackZUp(int tSlice) {
		ImageStack iStack = fastStackImage.getStack();
		int ch;
		int startSliceIndex = cSlices*fastStackZEnd*tSlice;
		int i;
		ImagePlus containerImage;
		int color;
		
		if (fastStackZEnd < zSlices) {
			// remove old slice from beginning of stack, if there is no more room for stack to grow
			if (getActualFastStackSize() == fastStackZSize) {
				for (ch=1;ch<=cSlices;ch++) {
					iStack.deleteSlice(1);
				}
				fastStackZStart++;
			}
			
			// add new slice to end of stack
			for (i=startSliceIndex;i<startSliceIndex+cSlices;i++) {
				containerImage = IJ.openImage(slicePaths[i]);
				color = i-startSliceIndex+1;
				iStack.addSlice("c:"+Integer.toString(color), containerImage.getProcessor());
			}
			
			// updates the metadata for the RAM-resident stack
			fastStackZCenter++;
			fastStackZEnd++;
		}
	}
	
	private void moveFastStackZDown(int tSlice) {
		int ch;
		ImageStack iStack = fastStackImage.getStack();
		int startSliceIndex = cSlices*(fastStackZStart-2)*tSlice;
		int i;
		ImagePlus containerImage;
		int color;

		
		if (fastStackZStart > 0) {
			// remove old slice from the end of the stack, if there is no more room for stack to grow
			if (getActualFastStackSize() == fastStackZSize) {
				for (ch=1;ch<=cSlices;ch++) {
					iStack.deleteSlice(iStack.getSize());
				}
				fastStackZEnd--;
			}
			
			// add new slice to the beginning of the stack
			for (i=startSliceIndex;i<startSliceIndex+cSlices;i++) {
				containerImage = IJ.openImage(slicePaths[i]);
				color = i-startSliceIndex+1;
				iStack.addSlice("c:"+Integer.toString(color), containerImage.getProcessor(),0);
			}

			// updates the metadata for the RAM-resident stack
			fastStackZCenter--;
			fastStackZStart--;
		}
	}
	
	private void initializeFastStack(int zCenter,int tSlice) {
		
	}
	
	public double getImageDiskSize() { return imageDiskSize; }
	public int getActualFastStackSize() { 
		return (fastStackZEnd-fastStackZStart+1); 
	}
	public int getActualFastStackZCenter() {
		int center;
		
		if (getActualFastStackSize() % 2 == 0) {
			center = (int) ((fastStackZEnd + fastStackZStart) / 2) + 1;
		} else {
			center = (int) ((fastStackZEnd + fastStackZStart) / 2);
		}
		
		return center;
	}
}
