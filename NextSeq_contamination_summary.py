'''Summarizes the contamination screens from a single NextSeq directory'''

import sys
import glob
from os.path import isfile

home_dir = sys.argv[1]

# reads the lines in a samplesheet and creates a dictionary of the samples with sample information [run type, genome, dictionary for contam]
with open(glob.glob(home_dir + "/SampleSheet*.csv")[0], 'r') as SampleSheetSummary:
    next(SampleSheetSummary)
    sample_list = {}
    line = SampleSheetSummary.readline()
    while "[Data]" not in line:
        line = SampleSheetSummary.readline()

    for line in SampleSheetSummary:
        line = line.strip().split(",")
        if len(line) > 5 and line[0] != "Sample_ID":
            genome = line[1].split("_")[-2]
            sample_list[line[1]] = [line[9], "Human" if "hs" in genome else "Mouse" if "mm" in genome else "", {}]

# reads the statistics.tsv file and retrieves the number of reads, adds the number of reads to the dictionary for the sample
with open(glob.glob(home_dir + "/*.tsv")[0], 'r') as RunStatistics:
    RunStatistics.readline()
    for line in RunStatistics.readlines():
        line = line.strip().split("\t")
        if line[0] in sample_list:
            sample_list[line[0]].append(line[2])
        else:
            print(line[0])

with open("output_NextSeq.csv", 'w') as output:
    for name in sample_list.keys():
        # Sample names for ATAC and Chip are of the form #_libID_project#
        if sample_list[name][0] in ["ATAC", "ChIP", "CHIP", "ChIPSeq", "ChIPPE"]:
            project = name.split("_")[2][0:4]

        # Sample names for RNA-Seq Hi-C and RRBS are #_project#
        else:
            project = name.split("_")[1][0:4]

        if isfile(home_dir + "/FASTQ/QC/" + name + "_r1_screen.txt"):
            screen_path = home_dir + "/FASTQ/QC/" + name + "_r1_screen.txt"
        else:
            screen_path = home_dir + "/FASTQ/QC/" + name + "_screen.txt"

        with open(screen_path, 'r') as screen_file:
            next(screen_file)
            next(screen_file)
            for line in screen_file:
                line = line.strip().split("\t")
                if len(line) > 10:
                    if line[0] == "Human":
                        sample_list[name][2]["Human"] = [line[5], line[3]]
                    elif line[0] == "Mouse":
                        sample_list[name][2]["Mouse"] = [line[5], line[3]]
                    elif float(line[3]) <= 90 and float(line[5]) >= 1:
                        sample_list[name][2][line[0]] = [line[5], line[3]]
        outdata = sample_list[name]
        other_species = []
        for i in sample_list[name][2].keys():
            if i not in ["Mouse", "Human"]:
                other_species.append(i)
        output.write("{},,,NextSeq,NA,{},{},{},{},{},{},{},{},,,,".format(name, 
                                                                          project, 
                                                                          outdata[0], 
                                                                          outdata[1], 
                                                                          outdata[3], 
                                                                          outdata[2]["Human"][0], 
                                                                          100 - float(outdata[2]["Human"][1]), 
                                                                          outdata[2]["Mouse"][0], 
                                                                          100 - float(outdata[2]["Mouse"][1])
                                                                          ))

        for i in other_species:
            output.write(",{},{},{}".format(i, 
                                            outdata[2][i][0], 
                                            100 - float(outdata[2][i][1])
                                            ))
        output.write("\n")
