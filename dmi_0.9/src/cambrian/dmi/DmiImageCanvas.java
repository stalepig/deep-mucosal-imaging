package cambrian.dmi;

import java.awt.Canvas;
import java.awt.Cursor;
import java.awt.Graphics;
import java.awt.Image;
import java.awt.Rectangle;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.awt.event.MouseMotionListener;
import java.awt.event.MouseWheelEvent;
import java.awt.event.MouseWheelListener;

import javax.swing.JPanel;

import ij.IJ;

public class DmiImageCanvas extends JPanel implements MouseWheelListener, MouseMotionListener, MouseListener {
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	private Rectangle srcRect;
	private double magnification;
	private Image img;
	private DmiImageWindow window;
	private DmiRectangle canvasRect;
	private DmiRectangle imageOrigMagRect;
	private DmiRectangle imageRect;
	private DmiRectangle paintRect;
	private DmiRectangle dataRect;
	private int mousePressedX;
	private int mousePressedY;
	private boolean showWholeImage;
	private boolean drawRectangularRoi;
	private DmiRectangle rectangularRoi;
	
	public DmiImageCanvas(DmiImageWindow window, DmiVirtualImage dmiImage, int sizeX, int sizeY) {
		this.window = window;
		canvasRect = new DmiRectangle(0,0,sizeX,sizeY);
		paintRect = new DmiRectangle(0,0,sizeX,sizeY);
		imageRect = new DmiRectangle(0,0,dmiImage.getXSize()-1,dmiImage.getYSize()-1);
		dataRect = new DmiRectangle(0,0,dmiImage.getXSize()-1,dmiImage.getYSize()-1);
		if (imageRect.doesFullyContain(canvasRect)) {
			imageRect.clip(canvasRect);
			showWholeImage = false;
		} else {
			imageRect.conform(dataRect);
			paintRect.conform(dataRect);
			showWholeImage = true;
		}
		imageOrigMagRect = imageRect.duplicate();

		// setSize(sizeX, sizeY);
		this.magnification = 1.0;
		
		this.addMouseWheelListener(this);
		this.addMouseMotionListener(this);
		this.addMouseListener(this);
		
		setCursor(new Cursor(Cursor.HAND_CURSOR));
		drawRectangularRoi = false;
		rectangularRoi = new DmiRectangle(0,0,0,0);
	}
	
	public void setPixelData(Image img) {
		this.img = img;
	}
	
	
	public void paintComponent(Graphics g) {
		try {
			if (img != null) {
				// g.drawImage(img, 0, 0, (int)(srcRect.width*magnification+0.5), (int)(srcRect.height*magnification+0.5),
				//		srcRect.x, srcRect.y, srcRect.x+srcRect.width, srcRect.y+srcRect.height, null);
				super.paintComponent(g);
				g.drawImage(img, paintRect.getX1(), paintRect.getY1(), paintRect.getX2(), paintRect.getY2(), 
						imageRect.getX1(), imageRect.getY1(), imageRect.getX2(), imageRect.getY2(), null);
			}
		} catch (OutOfMemoryError e) { IJ.log(e.getMessage()); }
	}
	
	public void setNewSize(int sizeX, int sizeY) {
		// buggy: needs fixing
		
		canvasRect.x2 = sizeX;
		canvasRect.y2 = sizeY;
		paintRect.conform(canvasRect);
		imageRect.x2 = imageRect.x1 + (int) (sizeX / magnification);
		imageRect.y2 = imageRect.y1 + (int) (sizeY / magnification);
		repaint();
	}

	@Override
	public void mouseWheelMoved(MouseWheelEvent e) {
		// TODO Auto-generated method stub
		int zSliceOffset = 0;
		int onMask = MouseWheelEvent.SHIFT_DOWN_MASK;
		if ((e.getModifiersEx() & onMask) == onMask) {
			
			if (imageRect.doesFullyContain(dataRect)) {		
				showWholeImage = true;
			} else {
				showWholeImage = false;
			}
			
			if (!showWholeImage || e.getWheelRotation() < 0) {
				magnification = magnification + (e.getWheelRotation() * -0.25);
				window.onZoomChanged(e.getWheelRotation() * -0.25);
				imageRect.x2 = imageRect.x1 + (int) (imageOrigMagRect.getWidth() / magnification);
				imageRect.y2 = imageRect.y1 + (int) (imageOrigMagRect.getHeight() / magnification);
				imageRect.fitInside(dataRect);
			}
			
			repaint();
		} else {
			zSliceOffset = e.getWheelRotation() * -1;
			this.img = window.requestImage(zSliceOffset);
			window.onZSliceChanged();
			repaint();
		}
	}

	@Override
	public void mouseDragged(MouseEvent e) {
		// TODO Auto-generated method stub
		int offsetX;
		int offsetY;
		
		if (e.isShiftDown()) {
			rectangularRoi.x2 = e.getX();
			rectangularRoi.y2 = e.getY();
			repaint();
		} else {
			offsetX = (e.getX() - mousePressedX) * -1;
			offsetY = (e.getY() - mousePressedY) * -1;
			
			imageRect.translate(offsetX, offsetY);
			imageRect.fitInside(dataRect);
			/* if (!imageRect.isFullyContainedWithin(dataRect)) {
				imageRect.conform(dataRect);
			} */
			repaint();
			
			mousePressedX = e.getX();
			mousePressedY = e.getY();
		}
	}

	@Override
	public void mouseMoved(MouseEvent e) {
		// TODO Auto-generated method stub
		window.onMouseMoved(imageRect.x1 + (int) (e.getX()/magnification), imageRect.y1 + (int) (e.getY()/magnification));
	}

	@Override
	public void mouseClicked(MouseEvent e) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void mousePressed(MouseEvent e) {
		// TODO Auto-generated method stub
		if (e.getButton() == MouseEvent.BUTTON1) {
			if (e.isShiftDown()) {
				rectangularRoi.x1 = e.getX();
				rectangularRoi.y1 = e.getY();
				drawRectangularRoi = true;
			} else {
				mousePressedX = e.getX();
				mousePressedY = e.getY();
			}
		}
	}

	@Override
	public void mouseReleased(MouseEvent e) {
		// TODO Auto-generated method stub
		drawRectangularRoi = false;
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
