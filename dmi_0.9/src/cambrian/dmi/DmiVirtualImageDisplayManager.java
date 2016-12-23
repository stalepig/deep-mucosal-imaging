package cambrian.dmi;

import ij.gui.NonBlockingGenericDialog;
import ij.gui.ImageWindow;
import ij.gui.StackWindow;
import ij.process.LUT;
import ij.gui.ImageCanvas;
import ij.CompositeImage;
import ij.ImagePlus;

import java.util.Arrays;
import java.util.Vector;
import java.awt.Color;
import java.awt.Image;
import java.awt.Scrollbar;
import java.awt.event.AdjustmentEvent;
import java.awt.event.AdjustmentListener;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;

public class DmiVirtualImageDisplayManager implements AdjustmentListener, MouseListener {
	private DmiVirtualImage vImage;
	public int currentZSlice;
	private CompositeImage shownImage;
	private Scrollbar zScrollbar;
	private DmiImageWindow window;
	private boolean [] isChannelDisplayed;
	private LUT nullLUT;
	private LUT [] LUTarray;
	private LUT [] defaultLUTarray;
	private double zoom;
	
	public DmiVirtualImageDisplayManager(DmiVirtualImage vImage) {
		this.vImage = vImage;
		this.window = new DmiImageWindow(this,vImage);
		this.zoom = 1.0;
		currentZSlice = vImage.getNZSlices() / 2;
		shownImage = vImage.getZImage(currentZSlice, 1);
		window.onZSliceChanged();
		window.passImage(shownImage.getImage());
		int i;
		
		isChannelDisplayed = new boolean[vImage.getNChannels()];
		for (i=0;i<vImage.getNChannels();i++) {
			isChannelDisplayed[i] = true;
		}

		byte [] zeros = new byte[256];
		for (i=0;i<256;i++) {
			zeros[i] = 0;
		}
		nullLUT = new LUT(zeros,zeros,zeros);
		
		LUTarray = new LUT[vImage.getNChannels()];
		defaultLUTarray = new LUT[vImage.getNChannels()];
		if (vImage.getNChannels() == 1) { 
			LUTarray = new LUT[] {LUT.createLutFromColor(Color.WHITE)};
			defaultLUTarray = new LUT[] {LUT.createLutFromColor(Color.WHITE)};
		} else if (vImage.getNChannels() == 2) {
			LUTarray = new LUT[] {LUT.createLutFromColor(Color.RED),LUT.createLutFromColor(Color.WHITE)};
			defaultLUTarray = new LUT[] {LUT.createLutFromColor(Color.RED),LUT.createLutFromColor(Color.WHITE)};
		} else if (vImage.getNChannels() == 3) {
			LUTarray = new LUT[] {LUT.createLutFromColor(Color.GREEN),LUT.createLutFromColor(Color.RED),LUT.createLutFromColor(Color.WHITE)};
			defaultLUTarray = new LUT[] {LUT.createLutFromColor(Color.GREEN),LUT.createLutFromColor(Color.RED),LUT.createLutFromColor(Color.WHITE)};
		} else if (vImage.getNChannels() == 4) {
			LUTarray = new LUT[] {LUT.createLutFromColor(Color.BLUE),LUT.createLutFromColor(Color.RED),LUT.createLutFromColor(Color.GREEN),LUT.createLutFromColor(Color.WHITE)};
			defaultLUTarray = new LUT[] {LUT.createLutFromColor(Color.BLUE),LUT.createLutFromColor(Color.RED),LUT.createLutFromColor(Color.GREEN),LUT.createLutFromColor(Color.WHITE)};
		} else if (vImage.getNChannels() == 5) {
			LUTarray = new LUT[] {LUT.createLutFromColor(Color.BLACK),LUT.createLutFromColor(Color.RED),LUT.createLutFromColor(Color.GREEN),LUT.createLutFromColor(Color.YELLOW),LUT.createLutFromColor(Color.WHITE)};
			defaultLUTarray = new LUT[] {LUT.createLutFromColor(Color.BLACK),LUT.createLutFromColor(Color.RED),LUT.createLutFromColor(Color.GREEN),LUT.createLutFromColor(Color.YELLOW),LUT.createLutFromColor(Color.WHITE)};
		} else {
			LUTarray = null;
			defaultLUTarray = null;
		}
		// initDialog();
	}
	
	public void showSlice(int zSlice) {
		shownImage = vImage.getZImage(zSlice, 1);
		applyDisplayMappings(shownImage);
		window.onZSliceChanged();
		window.passImage(shownImage.getImage());
	}
	
	public Image getSliceAsImage(int zSliceOffset) {
		int newZSlice = currentZSlice + zSliceOffset;
		if (newZSlice <= 0 || newZSlice > vImage.getNZSlices()) {
			return shownImage.getImage();
		} else {
			shownImage = vImage.getZImage(newZSlice, 1);
			applyDisplayMappings(shownImage);
			currentZSlice = newZSlice;
			return shownImage.getImage();
		}
	}
	
	public int getCurrentZSlice() {
		return currentZSlice;
	}
	
	public double getCurrentZoom() {
		return zoom;
	}
	
	public void toggleChannel(int channel) {
		if (isChannelDisplayed[channel-1]) {
			isChannelDisplayed[channel-1] = false;
		} else {
			isChannelDisplayed[channel-1] = true;
		}
	}
	
	public void setZoom(double zoomOffset) {
		zoom = zoom + zoomOffset;
	}
	
	private void applyDisplayMappings(CompositeImage imgp) {
		int i;
		
		for (i=0;i<imgp.getNChannels();i++) {
			if (isChannelDisplayed[i] == false) {
				imgp.setChannelLut(nullLUT, i+1);
			} else {
				imgp.setChannelLut(LUTarray[i],i+1);
			}
		}
	}
	
	private void initDialog() {
		Vector vSliders;
		NonBlockingGenericDialog gd = new NonBlockingGenericDialog(vImage.getTitle());
		gd.addSlider("Z_slice", 1, vImage.getNZSlices(), currentZSlice);
		gd.setCancelLabel("Close image");
		vSliders = gd.getSliders();
		zScrollbar = (Scrollbar) vSliders.elementAt(0);
		zScrollbar.addAdjustmentListener(this);
		zScrollbar.addMouseListener(this);
		gd.showDialog();
		if (gd.wasOKed()) {
			
		} else {
			window.dispose();
			shownImage.close();
		}
	}

	@Override
	public void adjustmentValueChanged(AdjustmentEvent e) {
		/* int zSlice = e.getValue();
		showSlice(zSlice); */
	}

	@Override
	public void mouseClicked(MouseEvent e) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void mousePressed(MouseEvent e) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void mouseReleased(MouseEvent e) {
		// TODO Auto-generated method stub
		int zSlice = zScrollbar.getValue();
		showSlice(zSlice);
	}

	@Override
	public void mouseEntered(MouseEvent e) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void mouseExited(MouseEvent e) {
		// TODO Auto-generated method stub
		
	}
}
