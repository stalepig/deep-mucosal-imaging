Plugin reference for deep-mucosal-imaging
=========================================

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
# Stretch stack on z
Takes an image stack consisting of n slices and converts it to an image stack of sn slices, where s is a natural number.

## Requirements
* An open single-channel z-stack in FIJI.
* Specification of s, the multiplier for the stack expansion.

## Returns
* Duplicates each slice in the input stack by s times and returns the stretched stack as a duplicate image.

## Typical Use
This is useful prior to 3D visualization so that the rendering does not produce a smushed version of the crypt. It does not improve z-resolution; however, it can provide a more-proportional representation of the shape of the object.
