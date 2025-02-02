#!/usr/bin/env python3

"""
Creates a summary of the contamination reports of all samples 
from all ChIP, ATAC, and RNA project directories within the given directory.
"""

import os
import glob
import datetime
import time

path_base = "/Volumes/services_data/Data_Storage/"
excluded_institutes = {"AM", "CTAGBATCH", "QCATAC", "QCCTAG"}
output_file = "Data_Storage_Contam_Summary.csv"

HEADER = (
    "Sample_Number,Sample_Name,Institute,Project,Day,Month,Year,Type,"
    "Human,Mouse,Rat,Hamster,Pig,Cow,Drosophila,C.elegans,E.coli,"
    "S.maltophilia,H.polygyrus,Mycoplasma,PhiX,Vectors,No_Genome\n"
)

def determine_project_type(service_report_path):
    """Determines project type from the service report filename."""
    if "ChIP-Seq" in service_report_path:
        return "ChIP"
    if "ATAC-Seq" in service_report_path:
        return "ATAC"
    if "RNA-Seq" in service_report_path:
        return "RNA"
    return None

def extract_contamination_data(screen_file):
    """Extracts contamination data from a given fastq_screen report."""
    contamination_values = []
    with open(screen_file, "r") as file:
        for line in file:
            fields = line.strip().split("\t")
            if fields[0] in {
                "Human", "Mouse", "Rat", "Hamster", "Pig", "Cow",
                "Drosophila", "C.elegans", "E.coli", "S.maltophilia",
                "H.polygyrus", "Mycoplasma", "PhiX", "Vectors"
            }:
                contamination_values.append(fields[5])
            elif "%Hit_no_genomes" in fields[0]:
                contamination_values.append(fields[0].split(" ")[1])
    return contamination_values

def main():
    sample_num = 1
    with open(output_file, "w") as outfile:
        outfile.write(HEADER)

        for institute in os.scandir(path_base):
            if not institute.is_dir() or institute.name in excluded_institutes:
                continue

            for project in os.scandir(institute.path):
                if not project.is_dir():
                    continue

                service_reports = glob.glob(os.path.join(project.path, "*Services_Report*.pdf"))
                if not service_reports:
                    continue

                service_report_path = service_reports[0]  # Take the first matching report
                if not os.path.exists(service_report_path):
                    continue

                try:
                    project_date = datetime.datetime.strptime(
                        time.ctime(os.path.getmtime(service_report_path)), "%a %b %d %H:%M:%S %Y"
                    )

                    if project_date.year < 2019:
                        continue

                    project_type = determine_project_type(service_report_path)
                    if project_type is None:
                        continue

                    screen_path = os.path.join(project.path, "QC", "fastq_screen")
                    if not os.path.isdir(screen_path):
                        continue

                    for screen_file in glob.glob(os.path.join(screen_path, "*.txt")):
                        sample_name = "_".join(os.path.basename(screen_file).split("_")[:7])
                        contamination_data = extract_contamination_data(screen_file)

                        outfile.write("{0},{1},{2},{3},{4},{5},{6},{7},{8}".format(
                            sample_num, sample_name, institute.name, project.name, project_date.day,
                            project_date.month, project_date.year, project_type, ','.join(contamination_data)
                            ))
                        sample_num += 1

                except Exception as e:
                    print("Error processing {}: {}".format(project.path,e))

if __name__ == "__main__":
    main()