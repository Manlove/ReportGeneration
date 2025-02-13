#!/usr/bin/env python3

"""
Finds work directories with antibody qualifications based on the peak calling tool.
ABQs use MACS, while full-scale projects use MACS2.
"""

import os
import datetime

BASE_DIR: str = "/home/mnt/services_data/Data_Storage/"
OUTPUT_FILE: str = "/home/lmanlove/scripts/abq_list_file.txt"

with open(OUTPUT_FILE, 'w') as abq_list_outfile:
    abq_list_outfile.write("Project\tInstitute\tNumber of samples\tDate")

    for institute in os.scandir(BASE_DIR):
        institute_path = os.path.join(BASE_DIR, institute)

        if not os.path.isdir(institute_path):
            continue

        for project in os.scandir(institute_path):
            project_path = os.path.join(institute_path, project)
            params_file = os.path.join(project_path, "params.txt")

            if not (os.path.isdir(project_path) and os.path.exists(params_file)):
                continue

            try:
                project_date = datetime.datetime.fromtimestamp(os.stat(params_file).st_mtime)
                
                with open(params_file, 'r') as param_file:
                    for line in param_file:
                        line = line.strip().split(" = ")
                        if line[0] == "PeakCallTool" and line[1] == "MACS":
                            bw_path = os.path.join(project_path, "BW")
                            bigwigs = len(os.listdir(bw_path)) if os.path.isdir(bw_path) else "NO BigWigs"

                            abq_list_outfile.write(f"\n{project}\t{institute}\t{bigwigs}\t{project_date}")
                            
            except Exception as e:
                print("Error processing {}: {}".format(project_path,e))


                    
