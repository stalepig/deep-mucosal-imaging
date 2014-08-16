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

## Typical Use
You have just acquired your gigantic image and want to begin the process of stitching and analyzing it. 


