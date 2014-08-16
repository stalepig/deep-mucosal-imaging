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

## Requirements
* An open image on FIJI
* Input of the number of rows and columns of the grid to draw

## Returns
* Irreversibly draws a grid of the specified size on the open image.

## Typical Use
You want to break apart a large image into manageable sections for manual analysis.
