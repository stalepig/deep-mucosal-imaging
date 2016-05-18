from ij import IJ
from ij.gui import GenericDialog
from ij.plugin import ChannelSplitter
from ij.plugin import RGBStackMerge
from ij.plugin import ImageCalculator
from ij import WindowManager

theImage = IJ.getImage()
gd = GenericDialog("Options...")
channelText = [("Channel " + str(ch+1)) for ch in range(theImage.getNChannels())]
gd.addChoice("Amplified_channel",channelText,channelText[0])
gd.addChoice("Reference_channel",channelText,channelText[-1])
gd.addNumericField("Amplifying_ratio",1,0)
gd.addCheckbox("Remove_bleedthrough",True)
gd.addCheckbox("Correct_for_refraction",True)
gd.showDialog()
if gd.wasOKed():
	amplifyChannel = gd.getNextChoiceIndex() + 1
	refChannel = gd.getNextChoiceIndex() + 1
	ampFactor = gd.getNextNumber()
	doRemoveBleedthrough = gd.getNextBoolean()
	doCorrectRefraction = gd.getNextBoolean()
	chImages = ChannelSplitter.split(theImage)
	
	## After this step, the image to operate on is "nextStepImage"
	if doRemoveBleedthrough:
		params = ("bleeding_channel=" + str(refChannel) + " bloodied_channel=" + str(amplifyChannel) + " " +
				"allowable_saturation_percent=1.0 rsquare_threshold=0.50")
		IJ.run("Remove Bleedthrough (automatic)", params)
		unbledImage = WindowManager.getImage("Corrected_ch" + str(amplifyChannel))
		mergingImages = [unbledImage,chImages[refChannel-1].duplicate()]
		nextStepImage = RGBStackMerge.mergeChannels(mergingImages,True)
		#nextStepImage.show()
		unbledImage.close()
		for img in mergingImages:
			img.close()
	else:
		mergingImages = [chImages[amplifyChannel-1].duplicate(),chImages[refChannel-1].duplicate()]
		nextStepImage = RGBStackMerge.mergeChannels(mergingImages,True)
		#nextStepImage.show()
		for img in mergingImages:
			img.close()
	for img in chImages:
		img.close()
	# theImage.close()

	## After this step, the image to operate on is "next2StepImage"
	if doCorrectRefraction:
		params = ("reference_channel=2 application_channel=1 automatic_operation generate_log " +
				"max_slice=43 surface_slice=87")
		IJ.run(nextStepImage,"Refractive Signal Loss Correction",params)
		mergingImages = [WindowManager.getImage("App Corrected"),WindowManager.getImage("Ref Corrected")]
		next2StepImage = RGBStackMerge.mergeChannels(mergingImages,True)
		for img in mergingImages:
			img.close()
		#next2StepImage.show()
		nextStepImage.close()
	else:
		next2StepImage = nextStepImage
	nextStepImage.close()

	## Makes the amplified composite image
	ic = ImageCalculator()
	indChannels = ChannelSplitter.split(next2StepImage)
	sourceDataImage = indChannels[0].duplicate()
	for sl in range(1,sourceDataImage.getNSlices()+1):
		sourceDataImage.setSliceWithoutUpdate(sl)
		ip = sourceDataImage.getProcessor()
		ip.multiply(ampFactor)
	ratedRefImage = ic.run("Subtract create stack",indChannels[1],sourceDataImage)
	mergingImages = [indChannels[0],ratedRefImage]
	outputImage = RGBStackMerge.mergeChannels(mergingImages,True)
	for img in mergingImages:
		img.close()
	for img in indChannels:
		img.close()
	next2StepImage.close()
	sourceDataImage.close()
	outputImage.show()
	
		