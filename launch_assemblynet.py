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
# Runs the AssemblyNet (https://github.com/volBrain/AssemblyNet) docker on the NiFTI file indicated by nifti_path

import os
import subprocess

def launch_assemblynet(nifti_path):
    print('in launch_assemblynet')
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
    cmd_string = ' '.join(cmd)
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
