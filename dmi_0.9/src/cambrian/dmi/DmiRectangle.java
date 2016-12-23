package cambrian.dmi;

import java.awt.Rectangle;

public class DmiRectangle {
	public int x1;
	public int y1;
	public int x2;
	public int y2;
	
	public DmiRectangle(int x1, int y1, int x2, int y2) {
		int tmpx;
		int tmpy;
		if (x2 < x1) { 
			tmpx = x1;
			x1 = x2;
			x2 = tmpx;
		}
		if (y2 < y1) {
			tmpy = y1;
			y1 = y2;
			y2 = tmpy;
		}
		
		this.x1 = x1;
		this.y1 = y1;
		this.x2 = x2;
		this.y2 = y2;
	}
	
	public int getWidth() {
		return (x2-x1+1);
	}
	
	public int getHeight() {
		return (y2-y1+1);
	}
	
	public Rectangle getRectangle() {
		return (new Rectangle(x1,y2,getWidth(),getHeight()));
	}
	
	public void magnify(double magnification) {
		int orgWidth = x2-x1+1;
		int orgHeight = y2-y1+1;
		int newWidth = (int) (orgWidth / magnification);
		int newHeight = (int) (orgHeight / magnification);
		x2 = x1 + newWidth - 1;
		y2 = y1 + newHeight - 1;
	}
	
	public static DmiRectangle duplicateAndMagnify(DmiRectangle rect, double magnification) {
		DmiRectangle retRect = rect.duplicate();
		retRect.magnify(magnification);
		return retRect;
	}
	
	public int getX1() { return x1; }
	public int getX2() { return x2; }
	public int getY1() { return y1; }
	public int getY2() { return y2; }
	public void setX1(int x) { x1 = x; }
	public void setX2(int x) { x2 = x; }
	public void setY1(int y) { y1 = y; }
	public void setY2(int y) { y2 = y; }
	
	public void clip(DmiRectangle rect) {
		if (rect.getX2() < x2) {
			x2 = rect.getX2();
		}
		if (rect.getX1() > x1) {
			x1 = rect.getX1();
		}
		if (rect.getY2() < y2) {
			y2 = rect.getY2();
		}
		if (rect.getY1() > y1) {
			y1 = rect.getY1();
		}
	}
	
	public void fitInside(DmiRectangle rect) {
		int w = x2-x1+1;
		int h = y2-y1+1;

		if (rect.getX2() < x2) {
			x2 = rect.getX2();
			x1 = x2 - w + 1;
		}
		if (rect.getY2() < y2) {
			y2 = rect.getY2();
			y1 = y2 - h + 1;
		}
		if (rect.getX1() > x1) {
			x1 = rect.getX1();
			x2 = x1 + w - 1;
		}
		if (rect.getY1() > y1) {
			y1 = rect.getY1();
			y2 = y1 + h - 1;
		}
	}
	
	public void conform(DmiRectangle rect) {
		x1 = rect.getX1();
		x2 = rect.getX2();
		y1 = rect.getY1();
		y2 = rect.getY2();
	}
	
	public void moveToLeft(DmiRectangle rect) {
		int w = x2-x1+1;
		x1 = rect.getX1();
		x2 = x1 + w - 1;
	}
	
	public void moveToRight(DmiRectangle rect) {
		int w = x2-x1+1;
		x2 = rect.getX2();
		x1 = x2 - w + 1;
	}
	
	public void moveToTop(DmiRectangle rect) {
		int h = y2-y1+1;
		y1 = rect.getY1();
		y2 = y1 + h - 1;
	}
	
	public void moveToBottom(DmiRectangle rect) {
		int h = y2-y1+1;
		y2 = rect.getY2();
		y1 = y2 - h + 1;
	}
	
	public void translate(int offsetX, int offsetY) {
		x1 = x1 + offsetX;
		x2 = x2 + offsetX;
		y1 = y1 + offsetY;
		y2 = y2 + offsetY;
	}
	
	public boolean isFullyContainedWithin(DmiRectangle rect) {
		if (x1>=rect.getX1() && x2<=rect.getX2() && y1>=rect.getY1() && y2<=rect.getY2()) {
			return true;
		} else {
			return false;
		}
	}
	
	public boolean doesFullyContain(DmiRectangle rect) {
		if (x1<=rect.getX1() && x2>=rect.getX2() && y1<=rect.getY1() && y2>=rect.getY2()) {
			return true;
		} else {
			return false;
		}
	}
	
	public DmiRectangle duplicate() {
		return new DmiRectangle(x1,y1,x2,y2);
	}
}
