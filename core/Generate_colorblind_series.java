import ij.*;
import ij.process.*;
import ij.gui.*;
import java.awt.*;
import ij.plugin.*;
import ij.plugin.frame.*;
import ij.io.*;

public class Generate_colorblind_series implements PlugIn {

	public void run(String arg) {
		int [] wList = WindowManager.getIDList();
		if (wList.length != 3) { return; }

		int i;
		String [] titles = new String[3];
		ImagePlus imp;
		for (i=0;i<3;i++) {
			imp = WindowManager.getImage(wList[i]);
			titles[i] = imp.getTitle();
		}

		GenericDialog gd = new GenericDialog("Pick images");
		gd.addChoice("Always green:",titles,titles[2]);
		gd.addChoice("Always magenta:",titles,titles[0]);
		gd.addStringField("Image title:","mouse_num",16);
		gd.addStringField("Always green channel label:","Lgr5");
		gd.addStringField("Always magenta channel label:","Rosa26");
		gd.addStringField("Variable color channel label:","Hoechst"); 
		gd.showDialog();

		if (gd.wasCanceled()) { return; }

		DirectoryChooser dc = new DirectoryChooser("Select directory to save files...");
		String theDir = dc.getDirectory();
		if (theDir==null) { return; }


		int alwaysGreenIndex = gd.getNextChoiceIndex();
		int alwaysMagentaIndex = gd.getNextChoiceIndex();
		String imageTitle = gd.getNextString();
		String img1key = gd.getNextString();
		String img3key = gd.getNextString();
		String img2key = gd.getNextString();
		int alwaysVariableIndex = 0;

		if (alwaysGreenIndex==alwaysMagentaIndex) { return; }
		if (alwaysGreenIndex+alwaysMagentaIndex==1) { alwaysVariableIndex = 2; }
		if (alwaysGreenIndex+alwaysMagentaIndex==2) { alwaysVariableIndex = 1; }
		if (alwaysGreenIndex+alwaysMagentaIndex==3) { alwaysVariableIndex = 0; }

		ImagePlus img1 = WindowManager.getImage(wList[alwaysGreenIndex]);
		ImageStack img1_is = img1.getStack();
		ImagePlus img2 = WindowManager.getImage(wList[alwaysVariableIndex]);
		ImageStack img2_is = img2.getStack();
		ImagePlus img3 = WindowManager.getImage(wList[alwaysMagentaIndex]);
		ImageStack img3_is = img3.getStack();

		ImageStack res1_is = RGBStackMerge.mergeStacks(img2_is,img1_is,img2_is,true);
		String res1title = imageTitle + "-" + img1key + "-" + img2key;
		ImagePlus res1 = new ImagePlus(res1title,res1_is);
		ImageStack res2_is = RGBStackMerge.mergeStacks(img3_is,img1_is,img3_is,true);
		String res2title = imageTitle + "-" + img1key + "-" + img3key;
		ImagePlus res2 = new ImagePlus(res2title,res2_is);
		ImageStack res3_is = RGBStackMerge.mergeStacks(img3_is,img2_is,img3_is,true);
		String res3title = imageTitle + "-" + img2key + "-" + img3key;
		ImagePlus res3 = new ImagePlus(res3title,res3_is);
		ImageStack res4_is = RGBStackMerge.mergeStacks(img3_is,img1_is,img2_is,true);
		String res4title = imageTitle + "-" + img1key + "-" + img3key + "-" + img2key;
		ImagePlus res4 = new ImagePlus(res4title,res4_is);
		res1.show();
		res2.show();
		res3.show();
		res4.show();

		IJ.save(res1,theDir+"/"+res1title+".png");
		IJ.save(res2,theDir+"/"+res2title+".png");
		IJ.save(res3,theDir+"/"+res3title+".png");
		IJ.save(res4,theDir+"/"+"zzz-"+res4title+".png");

		img1.close();
		img2.close();
		img3.close();

	}

}
