# ----- LICENSE -----
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License (GPL) as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version. For more detail see the
#    GNU General Public License at <http://www.gnu.org/licenses/>.
# -----------------
#
# Developed by A. Delphin, E. Gourieux, J. Pietras, L. Lamalle
# May 2024


import os
import nibabel as nib
import numpy as np
import glob
import xmlrec as xml # ask your Philips clinical scientist to obtain this library
from launch_assemblynet import launch_assemblynet
from extract_roi_by_label import extract_roi_by_label

# Modify lines below ----------------------------------------------------

# path definition
input_dir_path = '/path/to/directory/containing/SagCorTra/directories' # e.g. /data/Exam0/, in which you placed Sag/, Cor/, Tra/
output_path = 'path/to/write/segmented/XMLREC' # e.g. /data/Exam0/segmented

# labels to extract
labels = [181, 185, 201, 207]  # See README.pdf produced by AssemblyNet to select appropriate labels


# Code begins here ------------------------------------------------------
input_image_path = glob.glob(os.path.join(input_dir_path, 'Sag'))[0]

# creation of PAR file
par_files = glob.glob(os.path.join(input_image_path, "*.PAR"))
if not par_files:
    print('Converting XML to PAR')
    import xml2par # make par from xml (opens dialog box)
else:
    print('PAR file already existing')

print('Loading XML REC')
# Load XML REC to get right general_info and series_info structures
path_to_xml = glob.glob(os.path.join(input_image_path, "*.XML"))
images, general_info, series_info = xml.read_xmlrec(path_to_xml[0])
in_array = np.squeeze(xml.to_nd_array(images, general_info, series_info))

# open parrec with nibabel needed to have right orientation
path_to_rec = glob.glob(os.path.join(input_image_path, "*.REC"))
img = nib.load(path_to_rec[0])

# convert rec to nii
print('Converting to nii')
nifti_path = path_to_rec[0][:-4] + ".nii"
nifti = nib.Nifti1Image(img.dataobj, img.affine, header=img.header)
nifti.set_data_dtype('<f4')
nifti.to_filename(nifti_path)
print('Nii  written')

# -------------------------------
# Segmentation happens here
# Will write all AssemblyNet output files in input_dir_path/Sag (input_image_path)
launch_assemblynet(nifti_path)
# -------------------------------

# load data from segmented nifti
print('Loading modified Nii')
path_to_rois = glob.glob(os.path.join(input_image_path, 'native_structures_*.nii.gz'))
mod_img = nib.load(path_to_rois[0])
mod_img_array = np.array(mod_img.get_fdata())
mod_img_array = np.transpose(mod_img_array, (1, 0, 2))  # image matrix in nifti not in the same orientation as REC


# extract roi
extracted_roi = extract_roi_by_label(mod_img_array, labels)

# mask image
# Needs scaling to have mask brighter than the image
max_value = np.max(in_array)
window_width = series_info[0]["Window Width"]["Value"]
window_center = series_info[0]["Window Center"]["Value"]
offset = 0.5 * window_width / (len(labels) + 1)
scaled_max = max_value - window_center
out_array = in_array * scaled_max / max_value

# extract masks
for i in np.arange(len(labels)):
    out_array = np.where(
        extracted_roi == labels[i], window_center + offset * (i + 2), out_array
    )

# Saving XMLREC containing masked array
if not os.path.exists(output_path):
    os.makedirs(output_path)
    print("Directory created successfully")
else:
    print("Directory already exists")

print('Saving new sagittal REC')
general_info["Protocol Name"]['Value'] = general_info["Protocol Name"]['Value'] + '_Seg'
xml.write_xmlrec(os.path.join(output_path, 'Sagittal_masked.xml'),
                 general_info, series_info, np.ascontiguousarray(out_array))

# outArray is oriented as the original scan (Sag ?)
# need to produce the other 2 orientations
# -- first coro
out_array_coro = np.fliplr(np.transpose(out_array, (0, 2, 1)))

coro_path = glob.glob(os.path.join(input_dir_path, 'Cor'))[0]
path_to_xml = glob.glob(os.path.join(coro_path, "*.XML"))
images, general_info, series_info = xml.read_xmlrec(path_to_xml[0])

general_info["Protocol Name"]['Value'] = general_info["Protocol Name"]['Value'] + '_Seg'
xml.write_xmlrec(os.path.join(output_path, 'Coronal_masked.xml'),
                 general_info, series_info, np.ascontiguousarray(out_array_coro))

# -- then transversal
out_array_tra = np.flip(np.flip(np.transpose(out_array, (1, 2, 0)), 1), 2)

tra_path = glob.glob(os.path.join(input_dir_path, 'Tra'))[0]
path_to_xml = glob.glob(os.path.join(tra_path, "*.XML"))
images, general_info, series_info = xml.read_xmlrec(path_to_xml[0])

general_info["Protocol Name"]['Value'] = general_info["Protocol Name"]['Value'] + '_Seg'
xml.write_xmlrec(os.path.join(output_path, 'Transversal_masked.xml'),
                 general_info, series_info, np.ascontiguousarray(out_array_tra))
