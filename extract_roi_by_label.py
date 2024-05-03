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
#
# seg_volume: array resulting from a segmentation, typically filled with regions identified by numerical labels
# labels: list of integers corresponding to regions in seg_volume
# returns a volume of the same shape as seg_volume containing only the regions corresponding to the integers in labels

import numpy as np

def extract_roi_by_label(seg_volume, labels):
    label_seg_volume = None

    for label in labels:
        tmp_label_seg_volume = np.where(
            seg_volume == int(label), int(label), 0
        )
        # print(np.unique(tmp_label_seg_volume))
        if label_seg_volume is None:
            label_seg_volume = tmp_label_seg_volume > 0
        label_seg_volume = np.where(
            tmp_label_seg_volume > 0, tmp_label_seg_volume, label_seg_volume
        )
        # print(np.unique(label_seg_volume))
    return label_seg_volume
