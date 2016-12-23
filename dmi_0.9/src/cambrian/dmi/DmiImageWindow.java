package cambrian.dmi;

import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.Image;
import java.awt.Toolkit;
import java.awt.event.ComponentEvent;
import java.awt.event.ComponentListener;

import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JToggleButton;
import javax.swing.SwingConstants;
import javax.swing.border.BevelBorder;

public class DmiImageWindow extends JFrame implements ComponentListener {
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	private DmiImageCanvas canvas;
	private DmiVirtualImageDisplayManager manager;
	private JPanel statusPanel;
	private JLabel statusLabel;
	private JPanel channelPanel;
	private JToggleButton [] channelButtons;
	private DmiVirtualImage dmiImage;
	
	public DmiImageWindow(DmiVirtualImageDisplayManager manager, DmiVirtualImage dmiImage) {
		super(dmiImage.getTitle());
		this.manager = manager;
		this.dmiImage = dmiImage;
		Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
		double aspectRatio = dmiImage.getYSize() / (double) dmiImage.getXSize();
		int windowSizeX;
		int windowSizeY;
		double mag = 0.1;
		int trialSize;
		int i;
		
		// determines the best window size to show based on image dimensions
		if (aspectRatio < 1) {
			do {
				trialSize = (int) (dmiImage.getXSize() / mag);
				mag = mag + 0.1;
			} while (trialSize > (int) (screenSize.getWidth()*0.5));
			
			windowSizeX = trialSize;
			windowSizeY = (int) (windowSizeX * aspectRatio);
		} else {
			do {
				trialSize = (int) (dmiImage.getYSize() / mag);
				mag = mag + 0.1;
			} while (trialSize > (int) (screenSize.getHeight()*0.75));
			
			windowSizeY = trialSize;
			windowSizeX = (int) (windowSizeY / aspectRatio);
		}
		setSize(new Dimension(windowSizeX+32,windowSizeY+32));
		
		// sets other window properties
		setLayout(new BorderLayout());
		setResizable(true);
		
		// sets window event listeners
		addComponentListener(this);
		
		// adds the canvas and status bar components to the window
		canvas = new DmiImageCanvas(this,dmiImage,windowSizeX,windowSizeY);
		add(canvas);
		canvas.setPreferredSize(new Dimension(windowSizeX,windowSizeY));
		channelPanel = new JPanel();
		add(channelPanel,BorderLayout.WEST);
		channelPanel.setPreferredSize(new Dimension(32,this.getHeight()));
		channelButtons = new JToggleButton[dmiImage.getNChannels()];
		for (i=1;i<=dmiImage.getNChannels();i++) {
			channelButtons[i-1] = new JToggleButton("ch"+Integer.toString(i),true);
			channelButtons[i-1].addChangeListener(new ChannelButtonChangeListener(i,this));
			channelPanel.add(channelButtons[i-1]);
		}
		statusPanel = new JPanel();
		add(statusPanel,BorderLayout.SOUTH);
		statusPanel.setPreferredSize(new Dimension(this.getWidth(),32));
		statusPanel.setBorder(new BevelBorder(BevelBorder.LOWERED));
		statusLabel = new JLabel();
		statusLabel.setHorizontalAlignment(SwingConstants.LEFT);
		statusLabel.setText("Z:" + manager.getCurrentZSlice() + "/" + dmiImage.getNZSlices());
		statusPanel.add(statusLabel);
		
		setVisible(true);
	}
	
	public void passImage(Image img) {
		canvas.setPixelData(img);
		canvas.repaint();
	}
	
	public Image requestImage(int zSliceOffset) {
		return manager.getSliceAsImage(zSliceOffset);
	}
	
	public void onZSliceChanged() {
		updateStatusBar();
	}
	
	public void onChannelChanged(int channel) {
		manager.toggleChannel(channel);
		canvas.setPixelData(manager.getSliceAsImage(0));
		canvas.repaint();
	}
	
	public void onZoomChanged(double zoomOffset) {
		manager.setZoom(zoomOffset);
		updateStatusBar();
	}
	
	public void onMouseMoved(int x, int y) {
		updateStatusBar(x,y);
	}
	
	private void updateStatusBar() {
		statusLabel.setText("Z:" + manager.getCurrentZSlice() + "/" + dmiImage.getNZSlices() + " -- Zoom: " + manager.getCurrentZoom());
	}
	
	private void updateStatusBar(int x, int y) {
		statusLabel.setText("(X,Y):(" + Integer.toString(x) + "," + Integer.toString(y) + ") -- Z:" + manager.getCurrentZSlice() + "/" + dmiImage.getNZSlices() + " -- Zoom: " + manager.getCurrentZoom());
	}
	
	public DmiImageCanvas getCanvas() { return canvas; }

	@Override
	public void componentResized(ComponentEvent e) {
		// TODO Auto-generated method stub
		canvas.setNewSize(getWidth(), getHeight());
	}

	@Override
	public void componentMoved(ComponentEvent e) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void componentShown(ComponentEvent e) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void componentHidden(ComponentEvent e) {
		// TODO Auto-generated method stub
		
	}
}
