deep-mucosal-imaging
====================

Convenience plugins for FIJI/ImageJ to reconstruct, explore, and analyze extended imaging volumes of colon

# Status
The routines that form the deep-mucosal-imaging project have been used on a Mac installation of FIJI analyzing LSM images captured using a Zeiss LSM700 confocal microscope (running the Zen software). The routines have not been tested on other types of systems, but the code should be platform-independent. Please communicate your experience with using these plugins, especially any bugs that you encounter so that the software can be improved and be better utilized. Feel free to write in for advice or guidance when using this software.

# Development
The deep-mucosal-imaging project currently has 1 programmer (Cambrian Liu) who authored the initial versions of the plugins. Most current work is still focused on adding features through additional plugins, rather than debugging and refining existing plugins. A preliminary documentation of existing plugins is available and is continually updated. You are welcome to suggest changes or extensions, report bugs, and/or contribute directly to the programming on the project. Please contact Cambrian Liu at camliu@chla.usc.edu for all correspondence relating to this software. 

# Organization
The /dmi directory contains the main plugins to be used in analyzing large microscopy images. 

# Requirements
Because many of the scripts are written in Jython, the Jython interpreter included in standard installations of FIJI (FIJI Is Just ImageJ) is required. The bare-bones installation of ImageJ is not sufficient.

# Installation
The deep-mucosal-imaging project does not run as a separate executable. Rather, installation is as simple as copying the Java and Python (Jython) files into the plugins directoy of FIJI. For a typical installation on a Mac, these are the steps to install:

1. Close and quit the FIJI program if it is running.
2. Open the /Applications folder.
3. Right click on FIJI and select "Show package contents."
4. Select and open the /plugins folder.
5. Create a new folder called /deep_mucosal_imaging (the underscores are essential).
6. Copy the files from the GitHub /dmi into your newly created folder.
7. Re-launch FIJI. The plugins should be available from the Plugins menu, under an expandable menu item called "deep mucosal imaging."

# Citations
If you find the deep-mucosal-imaging package to be useful in your work, you may cite a (hopefully) upcoming paper.
