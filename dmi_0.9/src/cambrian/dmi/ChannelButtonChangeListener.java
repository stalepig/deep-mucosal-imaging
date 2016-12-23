package cambrian.dmi;

import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;

public class ChannelButtonChangeListener implements ChangeListener {

	private int channel;
	private DmiImageWindow window;
	
	public ChannelButtonChangeListener(int channel, DmiImageWindow win) {
		this.channel = channel;
		this.window = win;
	}
	
	@Override
	public void stateChanged(ChangeEvent e) {
		// TODO Auto-generated method stub
		window.onChannelChanged(channel);
	}

}
