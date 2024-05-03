# segment-from-pride
Allows to externally process scans exported with the Philips PRIDE tool and import the result back in the Philips console

**Available under GNU GENERAL PUBLIC LICENSE Version 3**

# Disclaimer 
The present tool is intended to be used in conjunction with the PRIDE tool from Philips. To do so, it reads and writes XML/REC files through the `xmlrec.py` library developed by Philips.
The present code will not run without this library. Please get in touch with your Philips clinical scientist to access PRIDE and the required library.

# Requirements
- Developed with Python 3.8, but should run with more recent versions.
- `xmlrec.py`, as indicated above.
- AssemblyNet, ran through a docker as indicated in their [documentation](https://github.com/volBrain/AssemblyNet). The user running the code must have the appropriate priviledges to launch a docker.
- Simple packages: `os`, `glob`, `numpy`, `nibabel` and `subprocess`

# How to - Python
This tool was developed to be used following the steps below:
- Acquire a sagittal T1w scan, 256x256 in-plane resolution.
- In volume view, produce three 256x256x256 images, one for each orientation, isotropic resolution. Use the "original" resolution mode when asked (not "high"). The aim is to obtain three XML/REC with proper geometry information.
- Using PRIDE, export these three images in separate directories called "Sag", "Cor" and "Tra".
- Adapt `input_dir_path` and `output_path` in the main.py, as well as the labels to use.
- A dialog box opens, navigate to the sagittal .XML file.
- The code runs on its own from there and produces 3 XML/REC in `output_path` which can be imported back in the console with a single PRIDE call (copy the 6 files in the `dirXmlRecOut`, see below).

# How to - PRIDE
- Create a `InlineExportXML` directory in `G:\Patch\PRIDE` (or equivalent on your system) and place the `inlineExportXML.pl` file there.
- Edit the `dirXmlRecIn`, `adirXmlRecPost` and `dirXmlRecOut` variables ot suit your system.
- Place the InlmineExportXML.xml in the `G:\Patch\PRIDE\packageconfiguration` directory.
- When calling PRIDE to export data, a NotePad window will open. Data will only be imported back in the console from `dirXmlRecOut` when this NotePad window is closed.
- Once imported by PRIDE, the images can be used in scan planning by pulling them from the "Thumbnail view".
  
# Possible improvement
- It should be possible to skip the XML to PAR conversion with a few rotations of the volume read by `xmlrec`
- Producing three 256x256x256 volumes allows to obtain XML files with correct geometry information, which avoids computing all the offcenters from the sagittal scan. There may be a cleaner wat with fewer PRIDE exports to implement. 
