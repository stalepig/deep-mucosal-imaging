deep-mucosal-imaging
====================

Convenience plugins for FIJI/ImageJ to reconstruct, explore, and analyze extended imaging volumes of colon

# Status
The routines that form the deep-mucosal-imaging project have been used on a Mac installation of FIJI analyzing LSM images captured using a Zeiss LSM700 confocal microscope (running the Zen software). The routines have not been tested on other types of systems, but the code should be platform-independent. We are looking for people who would be willing to test out the routines on various platforms. Please communicate your experience with using these plugins, especially any bugs that you encounter so that the software can be improved and be better utilized. Feel free to write in for advice or guidance when using this software.

NOTE: The plugins in the /dmi_0.1 folder are known to work with the July, 2013 version of FIJI, running on a Mac with Java 6. They will not work with the current version of FIJI running on a Mac with Java 8. This is because the recent updates to FIJI have changed some of the plugin programming rules dramatically. We are currently working on an update that works with the new FIJI version and Java 8 by the end of August, 2015.

# Development
The deep-mucosal-imaging project currently has 1 programmer (Cambrian Liu) who authored the initial versions of the plugins. Most current work is focused on adding features through additional plugins as well as debugging and refining existing plugins. A preliminary documentation of existing plugins is available and is continually updated. You are welcome to suggest changes or extensions, report bugs (especially if some routines just flat-out don't work), and/or contribute directly to the programming on the project. Please contact Cambrian Liu at camliu@chla.usc.edu for all correspondence relating to this software. 

# Organization
The /dmi_0.1 directory contains the main plugins to be used in analyzing large microscopy images. 

# Requirements
Because many of the scripts are written in Jython, the Jython interpreter included in standard installations of FIJI (FIJI Is Just ImageJ) is required. The bare-bones installation of ImageJ is not sufficient. You can download FIJI at http://fiji.sc/Fiji

# Installation
The deep-mucosal-imaging project does not run as a separate executable. Rather, installation is as simple as downloading the zip file, unzipping, and copying the Java and Python (Jython) files into the plugins directoy of FIJI. For a typical installation on a Mac, these are the steps to install:

1. Close and quit the FIJI program if it is running.
2. Open the /Applications folder.
3. Right click on FIJI and select "Show package contents."
4. Select and open the /plugins folder.
5. Create a new folder called /deep_mucosal_imaging (the underscores are essential).
6. Copy the unzipped files downloaded from Github into your newly created folder.
7. Re-launch FIJI. The plugins should be available from the Plugins menu, under an expandable menu item called "deep mucosal imaging."

# Citations
If you find the deep-mucosal-imaging package to be useful in your work, you may cite Liu et al. (2015), "Optical reconstruction of murine colorectal mucosa at cellular resolution," Am J Physiol Gastrointest Liver Physiol, G721-35.
