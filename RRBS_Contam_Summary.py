'''
Creates a summary of the contamination reports of all samples from
all RRBS projects in the Data_Storage directory.
'''

import glob
from os import listdir
import os.path
import time
import datetime

path_base = "/Data_Storage/"

with open("RRBS_Contam_Summary.csv", "w") as outfile:
    outfile.write("Sample_Number, Sample_Name, Institute, Project, Day, Month, Year, Type, Human, Mouse, Rat, Cow, Drosophila, E.coli, S.maltophilia, H.polygyrus, Mycoplasma, PhiX, Vectors, No_Genome")
    sample_num = 1
    for institute in listdir(path_base):
        # Skips 
        if os.path.isdir(path_base + institute) and institute not in ["AM", "CTAGBATCH", "QCATAC", "QCCTAG"]:
            for project in listdir(os.path.join(path_base,institute)):
                if os.path.isdir(os.path.join(path_base,institute, project)):

                    service_report_path = glob.glob(os.path.join(path_base, institute, project, "RRBS_Services_Report*.pdf"))
                    if len(service_report_path) > 0 and os.path.exists(service_report_path[0]):

                        project_date = datetime.datetime.strptime(time.ctime(os.path.getmtime(service_report_path[0])), "%a %b %d %H:%M:%S %Y")
                        if project_date.year >= 2021:
                            project_type = "RRBS"
                            screen_path = os.path.join(path_base, institute, project, "QC", "fastq_screen")
                            if os.path.isdir(screen_path):
                                for screen_file in glob.glob(os.path.join(path_base, institute, project, "QC", "fastq_screen", "*r1_screen.txt")):

                                    sample_name = "_".join(screen_file.split("/")[-1].split("_")[0:7])
                                    outfile.write("\n{0},{1},{2},{3},{4},{5},{6},{7}".format(
                                        sample_num,
                                        sample_name,
                                        institute, 
                                        project,
                                        project_date.day,
                                        project_date.month,
                                        project_date.year,
                                        project_type
                                        ))
                                    sample_num += 1
                                    with open(screen_file, 'r') as file:
                                        for f in file:
                                            f = f.strip().split("\t")
                                            if f[0] in ["Human", "Mouse", "Rat", "Cow", "Drosophila", "E.coli", "S.maltophilia", "H.polygyrus", "Mycoplasma","PhiX", "Vectors"]: #"Drosophila",
                                                outfile.write(",{0}".format(f[5]))
                                            elif "%Hit_no_genomes" in f[0]:
                                                outfile.write(",{0}".format(f[0].split(" ")[1]))
                                    outfile.write("\n")
