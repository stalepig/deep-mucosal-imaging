Plugin reference for deep-mucosal-imaging
=========================================

# Annotate ROI
Allows placement of ROIs on image with manual annotations.

## Requirements
* An open image on FIJI.
* Specification of the number of annotations to add per ROI.

## Returns
* Use the multi-point ROI chooser to mark ROIs. After placing each mark, a dialog box will pop up where annotations (text or number) can be entered.
* After exiting the main control sequence of the plugin, the list of ROIs and their annotations will be sent to the Results window, from which it can be saved.

## Typical Use
For example, you can use this plugin to mark crypts and annotate their position relative to other crypts or their clonal status. Because the dialog box where you enter annotations is modal, it is best to know what you will enter before you select an individual point ROI (because the image window is locked while the dialog box is up).

---
# Batch resizer
Resizes individual image tiles.

## Requirements
* A directory containing OME-TIFF image file tiles that have been created by Explode into tiles plugin.
* Specification of the resizing ratio. This is done by specifying the ratio of the desired sum total disk size occupied by the resized tiles divided by the sum total disk space currently occupied by the tiles. For example, if you have tiles that sum up to 10 GB, and you want your resized tiles to occupy 2.5 GB, the ratio you input would be 0.25. For a computer with 8 GB RAM, a safe guideline is that the resized total tile size should not exceed 1.75 GB and that each color channel should not exceed 750 MB (whichever is smaller). So, the tiles of a 1-channel image get resized to 750 MB, a 2-channel image to 1.5 GB, and a 3-channel image to 1.75 GB. Obviously this will vary across images and systems as well as the available RAM to the computer and FIJI.

## Returns
* Creates a subdirectory within the directory containing the OME-TIFF image file tiles.
* Stores the resized tiles as TIFF files in the created subdirectory. The resized files are named tile_{i}_.tif where *{i}* is the tile number.

## Typical Use
This step is performed after breaking the source image into tiles but right before the stitching process, to prevent FIJI from running out of memory during the sstitching procedure.

---
# Batch stitch


---
# Clone counter
An ROI picker that allows dividing of consecutively picked ROIs into distinct classes or categories.

## Requirements
* An open image in FIJI.

## Returns
* ROIs are selected with a user interface using the multi-point tool.
* After selecting a certain number of ROIs, you can mark whether the last n ROIs belong to the same class, where n equals the number of ROIs selected from the end of the last ROI class.
* ROIs are saved as a CSV file with their position and class number.

## Typical Use
Clone counter is good for counting the number of colonic crypts that are thought to have originated from a single crypt (clonal succession). Each crypt is marked by the multi-point picker, and once you have finished marking the entire clone, you click the "Finalize clone" button to advance to marking the crypts of the next clone.

---
# Combine image sequence
Simplifies combining the output of stitching into a multichannel image for easy viewing.

## Requirements
* A directory of images where each image represents the stitched z-plane of a single color channel. This image sequence is the typical output of the "Stitch_wrapper" plugin, which wraps Stephan Preibisch wounderful Fourier stitching plugin for simplicity.

## Returns
* All the images in the image sequence directory are imported and sorted based on the number of channels.
* The user provides a file prefix title and a directory where the merged TIFF files can be saved.

## Typical Use
After stitching the downsampled DMI image tiles, the image sequence has to be combined into a merged TIFF file to simplify exploration of the image over the various z-planes and color channels.

---
# Copy scale info
Copies the scaling information from an image on disk to the open image.

## Requirements
* An open image on FIJI
* An image file on disk from which you want to clone the scaling information.

## Returns
* The scaling information of the open image is overwritten by the scaling information of the chosen image on disk.

## Typical Use
You have stitched together an image from individual tiles, but you want to add the scaling information from those tiles so that you can put an accurate scale bar on the stitched image.

---
# Downsample huge LSM
An alternative way to break down and resize multi-tile images.

## Requirements
* An LSM or other Bio-format-readable image file that contains multiple tiles on disk.
* Specification of which tiles to resize as well as the resizing scale. See "Batch_resizer" plugin for how to specify the resize scale.
* Indication of how many tiles to hold in memory for resizing at one time. If the number is too high, FIJI may run out of memory.

## Returns
* Creates a new output directory in the image input directory.
* Resizes each tile in the input image to the specified scale. See "Batch_resizer" plugin for how to specify the resize scale.
* Writes each resized tile as a separate TIFF file to the output directory. 

## Typical Use
This plugin is an alternative to quickly generate resized tiles, instead of using "Explode_into_tiles" followed by "Batch_resizer". However, use of this plugin is not compatible with "Explore_full_resolution" and is for the most part deprecated.

---
# Draw grid
Draws a grid on an open image.

## Requirements
* An open image on FIJI
* Input of the number of rows and columns of the grid to draw

## Returns
* Irreversibly draws a grid of the specified size on the open image.

## Typical Use
You want to break apart a large image into manageable sections for manual analysis.

---
# Explode into tiles
The first step in breaking apart a tiled image that is too big to fit in RAM.

## Requirements
* A tiled image on disk - only LSM files have been tested - representing a single timepoint but can have multiple color channels and z planes.

## Returns
* A new directory is created in the directory of the input file.
* The input image is broken into its tiles. Each tile is written as a separate OME-TIFF file to disk. The tiles are numbered sequentially as tile_{i}_.ome.tif where *{i}* is the tile number. Each tile contains all the color channels and z planes.
* A metadata file indicating the number of channels and the tile configuration is written to the output directory.

## Typical Use
You have just acquired your gigantic image and want to begin the process of stitching and analyzing it. 

---
# Explore full resolution
Allows the user to pick an area on a downsampled image produced through DMI and retrieve the local tiles stitched at high (original or acquisition) resolution.

## Requirements
* A downsampled (scaled) image, opened in FIJI, produced via "Explode_into_tiles", "Batch_resizer", and "Stitch_wrapper" plugins of the DMI package.
* A directory of full-szied OME TIFF files that each correspond to a tile of the original image, produced by "Explode_into_tiles".
* A metadata file of the tile scan produced by "Explode_into_tiles" called tile_info.txt that is placed in the same directory as the individual full-resolution tile files.

## Returns
* This plugin draws a grid on the downsampled active image that indicates where the tile boundaries are located.
* Using the rectangular ROI tool of FIJI/ImageJ, the user can select a region for closer inspection at higher resolution.
* This plugin will stitch the original region together, provided there is enough RAM (that is, the selected region is sufficiently small). The stitched high-resolution image will be rendered on the screen.
* The user can repetitively choose different regions for inspection.
* The selected tiles used for stitching, as well as the stitched output, is stored in a temp directory in the master directory containing the tiles.

## Typical Use
You have a stitched, downsampled overview image of your sample produced by DMI. You want to analyze a small region at higher resolution; this will be the plugin that allows you to do this to spare you from having to manually calculate which tile corresponds to your region-of-interest.

---
# Explore z series

---
# Injury counter

---
# Injury counter 2


---
# Isolate stack ROI
Isolate a feature within a stack without doing further processing.

## Requirements
* An open image stack in FIJI, can be multi-channel.

## Returns
* User interface asks for a slice range.
* If image is multi-channel, plugin asks for a source image, which is the reference image used to pick an ROI through the stack.
* For each slice within range, user can select a rectangular, ellipse, or freehand ROI.
* Plugin produces an image with the features within the ROI shown and the non-ROI areas in black.

## Typical Use
You just want to isolate a particular crypt within an image, but you cannot use the ImageJ ROI feature by itself because the crypt is not straight vertical through the stack. This plugin alows you to move the ROI with the crypt (or other feature) throughout the stack, so when you do the 3D reconstruction, other crypts do not get in the way.
 
---
# Normalize contrast on z
Postprocessing way of adjusting contrast throughout the z levels in an image stack.

## Requirements
* An open image stack in FIJI.
* Selection of mode: global or local. Global mode means that for each z slice, the intensities are independently normalized to a range such that a specified percentage of the pixels are saturated. Local means that for each z slice, intensities are adjusted using an adaptive histogram equalization (CLAHE) algorithm. In the local case, the saturation parameter in the numeric box does not matter, and the defaults in the FIJI version of CLAHE are used. 

## Returns
* A duplicated version of the image stack that has the adjusted intensities.

## Typical Use
Because pixel intensity degrades as one goes deeper into the z-stack, running this plugin will allow partial correction for this phenomenon. Note that this plugin can only fix intensity dropoff and cannot fix the gradual loss of resolution.

---
# Normalize image sizes

---
# Remove bleedthrough
Performs compensation on fluorescence images.

## Requirements
* Two open single-channel images in FIJI of the same XYZ dimensions.
* Specification of which image serves as image to subtract bleedthrough from ("Main channel") and which image has the data that are bleeding through ("Subtracted channel").
* Selection of a rectangular ROIs on the main channel that represent just the bleedthrough intensity and background (autofluorescence) intensity.
* The best intensity ratio for image subtraction is automatically calculated, but manual adjustment is also an option.

## Returns
* Copies the main channel and presents a version with the bleedthrough subtracted throughout the full z-stack.

## Typical Use
A multichannel image is split into component channels using Image->Color->Split Channels, and this plugin is used to remove bleedthrough prior to recombining the channels.

---
# Set cast
Enables manual tracing of a feature throughout a z-stack, slice by slice.

## Requirements
* A single-channel z-stack image open in FIJI.

## Returns
* User interface asks to select a range of slices over which to define a region of interest.
* The plugin iterates over each slice within this range, asking user to outline the region using the ellipse, rectangular, or freehand ROI tool of ImageJ.
* At the end of the slice range, a new image with the ROIs isolated by gray values is produced.

## Typical Use
Suppose the user wants to highlight an individual crypt within a field of crypts; this plugin allows tracing of the crypt and subsequent 3D reconstruction.
 
---
# Set cast by threshold
Automatic highlighting of a feature identified by pixel value throughout a z-stack.

## Requirements
* A single-channel z-stack image open in FIJI.

## Returns
* User interface asks for a slice range.
* For each slice within range, user selects an ROI using the rectangular, ellipse, or freehand ROI tool.
* User selects a threshold value (1-254); any pixels above this value within the ROI will be saved. User can adjust threshold over each slice.
* A z-stack of saved pixels is created at the end of the slice sequence.

## Typical Use
Suppose the user wants to highlight a crypt within a field of crypts, and the crypt needs to be outlined using some kind of label (for example, highlighting a crypt by its labeled nuclei).

---
# Shine light
Automatically adjusts contrast over z-stack in the selected region-of-interest (ROI).

## Requirements
* An open single-channel z-stack in FIJI.

## Returns
* User interface allows for repetitive selection of an ROI in the open image.
* A duplicate image stack is made from the ROI only, and then Normalize_contrast_on_z is run with the global option on the duplicate image.

## Typical Use
There is a dark portion in the image that has a feature that needs closer examination. This plugin enables the brightening of that feature.

---
# Stitch wrapper


---
# Stretch stack on z
Takes an image stack consisting of n slices and converts it to an image stack of sn slices, where s is a natural number.

## Requirements
* An open single-channel z-stack in FIJI.
* Specification of s, the multiplier for the stack expansion.

## Returns
* Duplicates each slice in the input stack by s times and returns the stretched stack as a duplicate image.

## Typical Use
This is useful prior to 3D visualization so that the rendering does not produce a smushed version of the crypt. It does not improve z-resolution; however, it can provide a more-proportional representation of the shape of the object.

----
# Subtract local background over z fast
