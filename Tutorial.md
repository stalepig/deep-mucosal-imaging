Getting Started with deep-mucosal-imaging
=========================================

Plugins for the deep-mucosal-imaging project run within the FIJI environment. For installation instructions, please see the readme file. 

---
# Setting up the memory parameters on FIJI
* Go to Edit -> Options -> Memory & Threads...
* Change the memory to 75% of your system memory (for an 8 GB RAM machine, this will be 6 GB).
* Close and re-start FIJI. 

---
# Creating a downsampled overview of your giant LSM multi-tile z-stack image ("ERSC" sequence for Explode, Resize, Stitch, Combine)
* Assume your image is named tiled_z_tif.lsm and has a raw size of 15 GB, which you are trying to analyze on an 8 GB RAM system. Assume it has 3 channels for GFP, Alexa Fluor 555, and DAPI.
* Run "Explode into tiles" plugin.
* Select tiled_z_tif.lsm as your input file.
* This will take awhile (several hours typically) as the plugin unpackages the LSM file into individual OME TIFF tiles.
* A new directory called /tiled_z_tif.lsm_tiles containing the unpacked tiles will be made in the same directory of the input image.
* After the unpacking is complete, run the "Batch resizer" plugin. 
* The plugin will recommend a resampling ratio based on the amount of memory on your system. It may seem like the ratio is too low for the amount of RAM, but there needs to be a lot of extra space because stitching and other operations often duplicate the image without you noticing it; this takes up RAM and does not run using the virtual stacks as currently implemented. You have to know how many channels are in the image to pick the optimal resize ratio, but if you do not know you can pick something relatively safe like 10% of the original size (provided 10% is less than 25-30% of your system RAM resources).
* "Batch resizer" resizes each of the tiles and places the resized tiles as regular TIFFs within /tiled_z_tif.lsm_tiles/resized This process is quite fast compared to the "Explode into tiles" part. 
* Now you are ready to stitch your resized tiles. Run the "Stitch wrapper" plugin.
* Select the /tiled_z_tif.lsm_tiles/resized directory as your input directory of TIFF files.
* You have to provide a DMI metadata file that was automatically generated during the running of the "Explode into tiles" plugin that provides tiling layout information to the "Stitch wrapper" plugin. This file is called tile_info.txt and is located in the parent /tiled_z_tif.lsm_tiles directory.
* "Stitch wrapper" will also ask you to name the image. This name is used for the output directory of stitched images, each image representing a single z-plane of a single channel. If we name the image test_DMI, the output directory path will be /tiled_z_tif.lsm_tiles/resized/test_DMI_seq
* "Stitch wrapper" will stitch your image tiles using the excellent Fourier stitching plugin by Stephan Preibisch, which is included in FIJI. "Stitch wrapper" simplifies the stitching process and uses default starting parameters of 10% overlap between tiles and smooth fusion, but if you have custom needs for stitching, you can run the Fourier stitching plugin directly without using "Stitch wrapper."
* Computing tile overlaps tends to be fast, but the fusion part is slow, but not as slow as the "Explode into tiles" plugin that forms the bottleneck of the image reconstruction procedure.
* After stitching is complete, you have to process the output files using the "Combine image sequence" plugin. Run the plugin and navigate to the stitching output directory /tiled_z_tif.lsm_tiles/resized/test_DMI_seq
* You will have to specify the number of channels (3 in this example) as well as the prefix to be used on the name of the final stitched images. If we re-use test_DMI as the prefix, the output files will be test_DMI_ch1.tif, test_DMI_ch2.tif, and test_DMI_ch3.tif
* Specify an output directory where to put the stitched channels. Usually it is better to keep the images open so that you can explore them while the files are being written, which is not instantaneous if there are a lot of slices or channels.
* You can now open the stitched images in the future directly in FIJI, channel-by-channel. All functions of FIJI are available on these images. These downsampled images allow you to explore the z-stack while the image data are stored in RAM, which is much faster. The best way to use these images is to find a feature of interest and use the "Explore full resolution" plugin to have a closer look, if needed. Often the downsampled images have enough resolution to do some basic quantification and visual rendering of many features in the mouse colon. 

---
# Creating 2D images of your 3D stack for publication
* It is usually impractical to present DMI image stacks at full resolution for print publication. Often you will want to highlight only certain features, or give the reader or audience an general sense of the types of things your images can reveal. There are several ways DMI can assist in preparing 2D representations of your 3D images.
* You can make maximum intensity z-projections from the stitched, downsampled images generated by the "Explode" -> "Resize" -> "Stitch" -> "Combine" ("ERSC") sequence. This is especially good for presenting on the mucosal surface of the colon. While not technically a bona fide surface representation, because fluoresecence signal naturally degrades as a function of imaging depth, features that are closer to the surface or unobstructed will be preferentially displayed. Go to Image -> Stacks -> Z-Project... in FIJI to generate maximum intensity projections. 
* If the feature you want to show is a little bit deeper, you can try 3D projections (Image -> Stacks -> 3D-Project...). Alternatively, you can remove obstructing slices by creating a substack (Image -> Stacks -> Tools -> Make Substack...), and then making a z-projection. Yet another option is to make a montage of your z-slices (Image -> Stacks -> Make Montage...).
* A similar problem is if your region of interest is deeply embedded within the stack, with other structures covering it up from all sides (for example, a particular crypt within a sea of colonic crypts). Here, you can use DMI functions to isolate the feature prior to making 3D reconstructions of it. One function is the "Set cast" plugin. This allows you to manually outline your feature of interest slice-by-slice using one of the polygonal selection tools on the FIJI toolbar (rectangle, circle/ellipse, or freehand selection). Everything you outline is turned gray; everything else is turned black. Another plugin is "Set cast by threshold," which uses a user-defined threshold within an ROI that you can adjust throughout the stack to define the feature (this is good if your hands are too wobbly to use "Set cast"). Yet another option is to rely on the endogenous imaging signal (if your staining is very good or if your fluorescent protein preservation is exceptional). The "Isolate stack ROI" allows you to manually go through the stack and outline your feature; the resulting image blacks out the areas outside of the feature and displays only the signal within your outline. After deriving these images from these methods, you can use the 3D projection function of FIJI (described earlier) or the 3D viewer (Plugins -> 3D Viewer) to get all sorts of views/angles on your feature of interest. 
* The "Copy scale info" plugin allows you to port scaling information from your acquisition tiles to your processed images. For example, after obtaining your stitched, downsampled images from the ERSC sequence, you can run this plugin and provide one of the resized tiles in the /tiled_z_tif.lsm_tiles/resized/ directory to get the scaling information (provided you have not additionally resized the output image of the ERSC sequence, the scales should be the same between the 2 sets of images). The scaling information will be really useful for putting scale bars on your image projections. 
* You may run into a situation where you have several DMI images that have to be presented together (for example, images representing a time-course) in a single figure. It would be wise for quick comparison that the scales in the images are the same size. The "Normalize image sizes" plugin resizes all the TIFF images within a given directory so that the images are on the same scale. Of course, this only works provided that the "Copy scale info" plugin has been run, or that the image scales have been input manually and are correct. 

---
# Helping to explore your 3D datasets
* A common and obvious task is to load a specific region of your stitched, downsampled image generated from the ERSC sequence for high-resolution view. The "Explore full resolution" plugin enables this. When you run it, you provide the DMI metadata tile file that you used for stitching (for example, in  /tiled_z_tif.lsm_tiles/tile_info.txt). The plugin draws a grid on the downsampled image that roughly represents the location of the acquisition tiles. You can then use a selection tool (usually rectangular, ellipsoid, or freehand) to highlight a region of interest. The plugin will load those full-resolution corresponding tiles, stitch them, and display the stitched result. Because the stitching is recomputed each time, it is advisable to select the minimal area that captures the feature that you need to see up-close. In future versions of the software, we hope to have a "Google map" approach to exploring DMI images. 
* Illumination correction can be performed with the "Normalize contrast on z" plugin. You can choose local or global algorithms. This plugin brings up the brightness of features that are deeper within the tissue. It should not be used if the goal is to quantitate intensities for scientific comparison, because it will alter the intensities to optimize for visualization. Likewise, z-projections on the output images from using this plugin will not be representative of features at the surface. Fortunately the plugin copies the original data and produces a duplicate image where the intensities have been changed. 
* The "Shine light" plugin performs illumination correction on a specific sub-region. This is desirable when there is an xy bias in the fluorescent signal that dominates and skews the correction performed by "Normalize contrast on z."
* Removing bleedthrough: The "Remove bleedthrough" provides a semi-automated way to compensate for fluorescence overlap between channels throughout the z-stack. 
* The "Explore zseries" plugin plots the intensity of a region of interest throughout the stack.
* The "Subtract local background over z fast" plugin iterates over each slice in the stack and locally subtracts out the background (sets it to 0), where the background is calculated as a percentage of the total range of intensity values. This is useful for correcting for the fact that the mucosal surface might have a higher background autofluorescence (due to luminal contents) than the inside of the tissue. However, if used too aggressively, this plugin could also end up hiding features of interest, so use it carefully. 

---
# A few analytical tricks
* Plugins for DMI offer a few ways to help in the analysis of colonic crypts. Some of these are very simple enhancements to the intrinsic capabilities of ROI selection in FIJI. The plugins were written with specific goals for colonic mucosal analysis in mind, but they may have some more general utility provided you can get past how the plugins are named.
* The "Clone counter" plugin was used in the original publication to track how many crypts and/or cells belonged to a clonal lineage. It basically allows marking crypts with the multi-point selection button in FIJI and enables you to demarcate how many ROIs belong to a single clone. For example, if you had clone sizes of 3, 5, and 2 crypts, you would click 3 times on the 3-sized clone, then use the dialog box to mark that as a completed clone, and then you would click 5 times on the 5-sized clone, hit complete, and then click twice for the 2-sized clone, mark that as complete, etc.
* With large images, a common problem is forgetting what you have already counted or analyzed, which necessitates a way of moving through the image systematically. The "Draw grid" function is very simple and draws a grid of your chosen dimensions on the image, to facilitate marking off areas that you have already analyzed.
* The "Injury counter" plugin was originally made to quantify areas of ulceration on a piece of colon. With this plugin, you repetitively mark what fraction of the vertical distance is ulcerated (or any other feature), and you progressively do this along the horizontal distance, resulting in a profile of the ulceration along the horizontal axis.
* The "Injury counter 2" plugin was made as a second-generation injury counter that is more automated. It relies on the fact that your tissue is stained with a marker of the feature you are trying to report (for example, a lack of E-cadherin staining reports ulceration in colon). You then use the stain to generate a thresholded image (Image -> Adjust -> Threshold...). Running "Injury counter 2" on the thresholded image will then trigger pixel-by-pixel counting of the number of injured pixels along the vertical axis, for each pixel on the horizontal axis, within your ROI. This results in a finer-resoution version of the ulceration profile. Note that for both injury counting plugins that your image has to be rotated in the desired orientation for the information obtained to be useful.

---
# Miscellaneous
* Not every tiled image z-stack to be analyzed requires the ERSC sequence. If the raw LSM image is small enough to fit into RAM, you can directly stitch it using the Fourier stitching plugin (Plugins -> Stitching -> Grid/Collection Stitching...). In this case, the stitched output images can be directly viewed at their full resolution. In some cases (e.g., a lot of distinct tiled images capturing sub-regions at high resolution), you may want to stitch all the images in an entire directory automatically. The "Batch stitch" plugin performs this, relying on the tile configurations stored in the image metadata, and puts the stitched images in their own distinct output directories.
* If the input image is larger than RAM, but you do not want to use the ERSC sequence, you combine the "Explode" and "Resize" steps into one using the "Downsample huge LSM" plugin. This may be a little faster, but probably not by much, if at all. However, you will not be able to run "Explore full resolution" on the output images because the metadata file is not created.