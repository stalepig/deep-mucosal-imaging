import ij.*;
import ij.process.*;
import ij.gui.*;
import ij.plugin.*;
import ij.plugin.filter.*;
import ij.io.*;
import ij.measure.*;
import java.awt.*;
import java.awt.event.*;
import java.util.*;

public class Annotate_ROI implements PlugInFilter, MouseListener {
	ImagePlus imp;
	ImageCanvas canvas;
	ArrayList<ArrayList<String>> annotations;
	int numCustomFields;

	public int setup(String arg, ImagePlus imp) {
		this.imp = imp;

		annotations = new ArrayList<ArrayList<String>>();
		numCustomFields = 1;
		return DOES_ALL;
	}

	public void mousePressed(MouseEvent e) {
		GenericDialog gd;
		String [] input = new String[numCustomFields];
		int i;
		ArrayList<String> arr;

		int selectedTool = Toolbar.getToolId();
		if (selectedTool == Toolbar.POINT) {
			gd = new GenericDialog("Set ROI parameters");
			for (i=0; i<numCustomFields; i++) {
				input[i] = "";
				gd.addStringField("Value "+Integer.toString(i)+":","");
			}
			gd.showDialog();
	
			if (gd.wasOKed()) {
				for (i=0; i<numCustomFields; i++) {
					input[i] = gd.getNextString();
				}
			} else {
				for (i=0;i<numCustomFields;i++) {
					input[i] = "NA";
				}
			}
	
			for (i=0;i<numCustomFields;i++) {
				arr = annotations.get(i);
				arr.add(input[i]);
			}
		}
	}

	public void mouseClicked(MouseEvent e) { }
	public void mouseReleased(MouseEvent e) { }
	public void mouseEntered(MouseEvent e) { }
	public void mouseExited(MouseEvent e) { }

	public void serialize() {
		PointRoi roi = (PointRoi) imp.getRoi();
		ResultsTable rt = ResultsTable.getResultsTable();
		FloatPolygon fp = roi.getFloatPolygon();
		int i,j;
		int counter = fp.npoints;
		ArrayList<String> arr;

		rt.reset();
		for (i=0;i<numCustomFields;i++) {
			arr = annotations.get(i);
			arr.trimToSize();
		}
		
		for (i=0; i<counter;i++) {
			rt.incrementCounter();
			rt.addValue("X",fp.xpoints[i]);
			rt.addValue("Y",fp.ypoints[i]);
			for (j=0;j<numCustomFields;j++) {
				arr = annotations.get(j);
				rt.addValue("Custom "+Integer.toString(j),arr.get(i));
			}
			
		}
		rt.show("Results");
	}

	public void run(ImageProcessor ip) {
		int i;
		GenericDialog intro_gd = new GenericDialog("Annotate ROI...");
		intro_gd.addNumericField("Number of custom fields:",1,0);
		intro_gd.showDialog();

		if (intro_gd.wasOKed()) {
			numCustomFields = (int) intro_gd.getNextNumber();
			for (i=0;i<numCustomFields;i++) {
				annotations.add(new ArrayList<String>());
			}
			annotations.trimToSize();
			
			imp.deleteRoi();
			WaitForUserDialog waitDialog;
			
			ImageWindow win = imp.getWindow();
			canvas = win.getCanvas();
			canvas.addMouseListener(this);
			waitDialog = new WaitForUserDialog("Control panel","Click to exit ROI annotation");
			waitDialog.show();
			this.serialize();
			canvas.removeMouseListener(this);	
		}
		
	}
} 