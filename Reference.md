Plugin reference for deep-mucosal-imaging
=========================================

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
* The input image is broken into its tiles. Each tile is written as a separate OME-TIFF file to disk. The tiles are numbered sequentially as tile_{i}_.ome.tif where *i* is the tile number. Each tile contains all the color channels and z planes.

## Typical Use
You have just acquired your gigantic image and want to begin the process of stitching and analyzing it. 


