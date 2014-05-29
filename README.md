deep-mucosal-imaging
====================

Convenience plugins for FIJI/ImageJ to reconstruct, explore, and analyze extended imaging volumes of colon

# Status
The routines that form the deep-mucosal-imaging project are still in pre-alpha phase, meaning they have not been tested on a wide range of systems or input files, nor have they been debugged for various configurations of user input outside what the initial programmer may idiosyncratically use. That being said, the routines in themselves are unlikely to cause severe data loss because they are based on a stable release of FIJI.

# Development
The deep-mucosal-imaging project currently has 1 programmer (Cambrian Liu) who authored the initial versions of the plugins. Most current work is still focused on adding features through additional plugins, rather than debugging and refining existing plugins. A full documentation of existing plugins is forthcoming. You are welcome to suggest changes or extensions, report bugs, and/or contribute directly to the programming on the project. Please contact Cambrian Liu at camliu@chla.usc.edu for all correspondence relating to this software. 

# Organization
The /core directory contains the main plugins to be used in analyzing large microscopy images. The /hcs directory contains a few unrelated plugins for medium-throughput analysis of scratch wound healing and EdU proliferation assays in cell culture, that are being released anyways.

# Requirements
Because many of the scripts are written in Jython, the Jython interpreter included in standard installations of FIJI (FIJI Is Just ImageJ) is required. The bare-bones installation of ImageJ is not sufficient.

# Installation
The deep-mucosal-imaging project does not run as a separate executable. Rather, installation is as simple as copying the Java and Python (Jython) files into the plugins directoy of FIJI. For a typical installation on a Mac, these are the steps to install:

1. Close and quit the FIJI program if it is running.
2. Open the /Applications folder.
3. Right click on FIJI and select "Show package contents."
4. Select and open the /plugins folder.
5. Create a new folder called /deep_mucosal_imaging (the underscores are essential).
6. Copy the files from the GitHub /core and /hcs (if desired) into your newly created folder.
7. Re-launch FIJI. The plugins should be available from the Plugins menu, under an expandable menu item called "deep mucosal imaging."

# Citations
If you find the deep-mucosal-imaging package to be useful in your work, you may cite a (hopefully) upcoming paper.
