"""
    Main functions:
        - extract_roi_by_label
        - launch_assemblynet
        - segment

    ----- LICENSE -----
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License (GPL) as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version. For more detail see the
    GNU General Public License at <http://www.gnu.org/licenses/>.
    -----------------

    Developed by A. Delphin, E. Gourieux, J. Pietras, L. Lamalle
    May 2024
"""

import glob
import os
import subprocess
import nibabel as nib
import numpy as np

from xml2par import main_xml2par
import xmlrec as xml  # ask your Philips clinical scientist to obtain thoses functions


def extract_roi_by_label(seg_volume, labels):
    """
    Extract ROI by label

        Parameters: 
            seg_volume (a numpy array): array resulting from a segmentation, 
                                        typically filled with regions identified
                                        by numerical labels
            labels (a list): list of the labels to extract (ex [181, 185])
        Returns:
            label_seg_volume (a numpy array): a volume of the same shape as seg_volume 
                                containing only the regions corresponding
                                to the integers in labels
    """
    label_seg_volume = None

    for label in labels:
        tmp_label_seg_volume = np.where(
            seg_volume == int(label), int(label), 0
        )
        if label_seg_volume is None:
            label_seg_volume = tmp_label_seg_volume > 0
        label_seg_volume = np.where(
            tmp_label_seg_volume > 0, tmp_label_seg_volume, label_seg_volume
        )
    return label_seg_volume


def launch_assemblynet(nifti_path):
    """
    Runs the AssemblyNet docker
    (https://github.com/volBrain/AssemblyNet)
    on the NIfTI file 

        Parameters:
            nifti_path (a string): NIfTI path
    """
    print("Launch assemblynet")
    in_directory = os.path.dirname(os.path.realpath(nifti_path))
    file_name = os.path.basename(nifti_path)

    id_u = (
        subprocess.check_output(["id", "-u"])
        .decode("utf-8")
        .replace("\n", "")
    )
    id_g = (
        subprocess.check_output(["id", "-g"])
        .decode("utf-8")
        .replace("\n", "")
    )
    cmd = [
        "docker",
        "run",
        "--rm",
        "--user",
        id_u + ":" + id_g,
        "-v",
        in_directory + ":/data",
        "volbrain/assemblynet:1.0.0",
        "/data/" + file_name
    ]
    print(cmd)
    cmd_string = " ".join(cmd)
    os.system(cmd_string)
    # p = subprocess.Popen(
    #     cmd,
    #     shell=False,
    #     bufsize=-1,
    #     stdin=subprocess.PIPE,
    #     stdout=subprocess.PIPE,
    #     stderr=subprocess.PIPE,
    #     close_fds=True,
    # )


def main_processing(input_dir_path, output_path, labels):
    """
    Launch main processing (convert to NIfTI,
    segment image using AssemblyNet, prepare result for PRIDE)

        Parameters:
            input_dir_path (a string): input directory path with XML/REC 
                                       images from PRIDE (in three 
                                       sub-directory Sag, Cor, Tra)
            output_path (a string): output path
            lables (a list): list of the labels to extract (ex [181, 185]) 
    """

    input_image_path = os.path.join(input_dir_path, "Sag")
    path_to_xml = glob.glob(os.path.join(input_image_path, "*.XML"))[0]
    # Creation of PAR file 
    par_files = glob.glob(os.path.join(input_image_path, "*.PAR"))
    if not par_files:
        print("Converting XML to PAR")
        # import xml2par # make par from xml (opens dialog box
        main_xml2par(path_to_xml)
    else:
        print("PAR file already existing")

    # Load XML REC to get right general_info and series_info structures
    print("Loading XML REC")
    images, general_info, series_info = xml.read_xmlrec(path_to_xml)
    in_array = np.squeeze(xml.to_nd_array(images, general_info, series_info))

    # Open parrec with nibabel needed to have right orientation (use .PAR file)
    path_to_rec = glob.glob(os.path.join(input_image_path, "*.REC"))[0]
    img = nib.load(path_to_rec)

    assemblynet_out_path = os.path.join(output_path, "AssemblyNet")
    if not os.path.exists(assemblynet_out_path):
        os.makedirs(assemblynet_out_path)
    # Convert rec to nii
    print("Converting to nii")
    nifti_path = os.path.join(
        assemblynet_out_path,
        path_to_rec.split("/")[-1].replace(".REC", ".nii")
    )
    nifti = nib.Nifti1Image(img.dataobj, img.affine, header=img.header)
    nifti.set_data_dtype("<f4")
    nifti.to_filename(nifti_path)
    print("Nii written")

    # Segmentation happens here
    # Will write all AssemblyNet output files in output_path
    launch_assemblynet(nifti_path)

    # Load data from segmented nifti
    print("Loading modified Nii")
    path_to_rois = glob.glob(os.path.join(
        assemblynet_out_path, "native_structures_*.nii.gz"))
    mod_img = nib.load(path_to_rois[0])
    mod_img_array = np.array(mod_img.get_fdata())
    # image matrix in nifti not in the same orientation as REC
    mod_img_array = np.transpose(mod_img_array, (1, 0, 2))

    # Extract roi
    extracted_roi = extract_roi_by_label(mod_img_array, labels)

    # Mask image
    # Needs scaling to have mask brighter than the image
    max_value = np.max(in_array)
    window_width = series_info[0]["Window Width"]["Value"]
    window_center = series_info[0]["Window Center"]["Value"]
    offset = 0.5 * window_width / (len(labels) + 1)
    scaled_max = max_value - window_center
    out_array = in_array * scaled_max / max_value

    # Extract masks
    for i in np.arange(len(labels)):
        out_array = np.where(
            extracted_roi == labels[i], window_center +
            offset * (i + 2), out_array
        )

    # Saving XMLREC containing masked array
    final_out_path = os.path.join(output_path, "results_to_export")
    if not os.path.exists(final_out_path):
        os.makedirs(final_out_path)

    print("Saving new sagittal REC")
    general_info["Protocol Name"]["Value"] = general_info["Protocol Name"]["Value"] + "_Seg"
    xml.write_xmlrec(os.path.join(final_out_path, "Sagittal_masked.xml"),
                     general_info, series_info, np.ascontiguousarray(out_array))

    # outArray is oriented as the original scan (Sag ?)
    # Need to produce the other 2 orientations
    # -- first coro
    out_array_coro = np.fliplr(np.transpose(out_array, (0, 2, 1)))
    coro_path = os.path.join(input_dir_path, "Cor")
    path_to_xml = glob.glob(os.path.join(coro_path, "*.XML"))[0]
    images, general_info, series_info = xml.read_xmlrec(path_to_xml)

    general_info["Protocol Name"]["Value"] = general_info["Protocol Name"]["Value"] + "_Seg"
    xml.write_xmlrec(os.path.join(final_out_path, "Coronal_masked.xml"),
                     general_info, series_info, np.ascontiguousarray(out_array_coro))

    # -- then transversal
    out_array_tra = np.flip(np.flip(np.transpose(out_array, (1, 2, 0)), 1), 2)
    tra_path = os.path.join(input_dir_path, "Tra")
    path_to_xml = glob.glob(os.path.join(tra_path, "*.XML"))[0]
    images, general_info, series_info = xml.read_xmlrec(path_to_xml)

    general_info["Protocol Name"]["Value"] = general_info["Protocol Name"]["Value"] + "_Seg"
    xml.write_xmlrec(os.path.join(final_out_path, "Transversal_masked.xml"),
                     general_info, series_info, np.ascontiguousarray(out_array_tra))

    print(
        f"End of processing. The results to used in PRIDE are in {final_out_path}"
    )
