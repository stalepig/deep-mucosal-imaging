import ij.*;
import ij.process.*;
import ij.gui.*;
import java.awt.*;
import ij.plugin.*;
import ij.plugin.frame.*;
import ij.io.*;
import loci.plugins.BF;
import loci.formats.*;
import loci.formats.meta.*;
import java.io.*;
import ome.xml.model.primitives.*;
import ome.xml.model.enums.*;

public class Explode_into_tiles implements PlugIn {
	
	private String filepath;
	private String saveDir;
	private String savePath;
	private IMetadata omeMeta;
	private loci.formats.ImageReader theReader;
	private int numXTiles;
	
	public void deleteAllFiles(String path) {
		File folder = new File(path);
		File[] files = folder.listFiles();
		if (files != null) {
			for (File f: files) {
				if (!f.isDirectory()) {
					f.delete();
				}
			}
		}
	}

	public void writeLogFile(String path) {
		try {
			File logFile = new File(path);
			BufferedWriter writer = new BufferedWriter(new FileWriter(logFile));
			writer.write(filepath+"\n");
			writer.write("Num tiles: " + String.valueOf(theReader.getSeriesCount()) + "\n");
			writer.write("Num planes per tile: " + String.valueOf(omeMeta.getPlaneCount(0)) + "\n");
			writer.write("Num channels: " + String.valueOf(theReader.getSizeC()) + "\n");
			writer.write("Num X Tiles: " + String.valueOf(numXTiles) + "\n");
			writer.write("Num Y Tiles: " + String.valueOf(theReader.getSeriesCount()/numXTiles) + "\n");
			writer.close();
		}
		catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	public void run(String arg) {
		OpenDialog od = new OpenDialog("Open image file...");
		String dir = od.getDirectory();
		String name = od.getFileName();
		this.filepath = dir + name;
		this.saveDir = dir + name + "_tiles/";
		String savePath;

		this.omeMeta = MetadataTools.createOMEXMLMetadata();
		IMetadata outMeta;

		boolean success = (new File(saveDir)).mkdirs();
		deleteAllFiles(saveDir);
		
		int i, j;
		theReader = new loci.formats.ImageReader();
		loci.formats.ImageWriter theWriter;
		int imgX,imgY,imgZ,imgC,imgT;

		double startPlanePosY, currPlanePosY;
		boolean planePosUpdated = false;
		this.numXTiles = 1;

		try {
			theReader.setMetadataStore(omeMeta);
			theReader.setId(filepath);

			startPlanePosY = omeMeta.getPlanePositionY(0,0);
			
			for (i=0;i<theReader.getSeriesCount();i++) {
				theWriter = new loci.formats.ImageWriter();
				outMeta = MetadataTools.createOMEXMLMetadata();
				
				theReader.setSeries(i);
	
				imgX = theReader.getSizeX();
				imgY = theReader.getSizeY();
				imgZ = theReader.getSizeZ();
				imgT = theReader.getSizeT();
				imgC = theReader.getSizeC();
	
				outMeta.setImageID("Tile:"+String.valueOf(i),0);
				outMeta.setPixelsID("Pixels:"+String.valueOf(i),0);
				outMeta.setPixelsBinDataBigEndian(Boolean.FALSE,0,0);
				outMeta.setPixelsDimensionOrder(DimensionOrder.XYCZT,0);
				outMeta.setPixelsType(PixelType.UINT8,0);
				outMeta.setPixelsSizeX(new PositiveInteger(imgX),0);
				outMeta.setPixelsSizeY(new PositiveInteger(imgY),0);
				outMeta.setPixelsSizeZ(new PositiveInteger(imgZ),0);
				outMeta.setPixelsSizeT(new PositiveInteger(imgT),0);
				outMeta.setPixelsSizeC(new PositiveInteger(imgC),0);
				outMeta.setPixelsPhysicalSizeX(omeMeta.getPixelsPhysicalSizeX(i),0);
				outMeta.setPixelsPhysicalSizeY(omeMeta.getPixelsPhysicalSizeY(i),0);
				outMeta.setPixelsPhysicalSizeZ(omeMeta.getPixelsPhysicalSizeZ(i),0);
				for (j=0;j<imgC;j++) { 
					outMeta.setChannelID("Channel:0:" + String.valueOf(j),0,j);
					outMeta.setChannelSamplesPerPixel(new PositiveInteger(1),0,j);
					outMeta.setChannelColor(omeMeta.getChannelColor(i,j),0,j);
				}
				
	
				savePath = saveDir + "tile_" + String.valueOf(i+1) + ".ome.tif";
				theWriter.setMetadataRetrieve(outMeta);
				theWriter.setId(savePath);
				currPlanePosY = omeMeta.getPlanePositionY(i,0);
				for (j=0;j<theReader.getImageCount();j++) {		
					outMeta.setTiffDataFirstC(new NonNegativeInteger(j%imgC),0,j);
					theWriter.saveBytes(j,theReader.openBytes(j));
					IJ.showStatus("Slice: " + String.valueOf(j+1) + "/" + String.valueOf(theReader.getImageCount()) + "; Tile: " + String.valueOf(i+1) + "/" + String.valueOf(theReader.getSeriesCount()));		
				}

				if (Math.abs(currPlanePosY - startPlanePosY) > 1.0 && !planePosUpdated) {
					this.numXTiles = i;
					planePosUpdated = true;
				}

				theWriter.close();
			}

			writeLogFile(saveDir+"tile_info.txt");

			theReader.close();
			
		}
		catch (FormatException exc) {
			IJ.error("Error: " + exc.getMessage());
		}
		catch (IOException exc) {
			IJ.error("Error: " + exc.getMessage());
		}


	}
}
