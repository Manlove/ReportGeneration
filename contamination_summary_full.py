'''
Summarizes the contamination screens from all NovaSeq run directories
in a folder.

Adapted from contamination_summary.
'''

import sys
import glob
from os import listdir
import os.path


def summarize_contamination(home_dir: str, run_dir: str, run_num: str, run_date: str, write_file: str) -> None:

    if (
        os.path.exists(os.path.join(home_dir, run_dir, 'Demux_Params','SampleSheetSummary.csv')) and 
        os.path.exists(os.path.join(home_dir, run_dir, 'Demux_Results','QC','RunStatistics.csv')) and 
        os.path.isdir(os.path.join(home_dir, run_dir, 'Demux_Results','QC','fastq_screen'))
        ):
        with open(home_dir + run_dir + '/Demux_Params/SampleSheetSummary.csv', 'r') as SampleSheetSummary:
            next(SampleSheetSummary)
            sample_list = {}
            for line in SampleSheetSummary:
                line = line.strip().split(",")
                sample_list[line[0]] = [line[1], line[2], line[3], line[7], {}]

        with open(home_dir + run_dir + '/Demux_Results/QC/RunStatistics.csv', 'r') as RunStatistics:
            next(RunStatistics)
            for line in RunStatistics:
                line = line.strip().split(",")
                if line[0] in sample_list:
                    sample_list[line[0]].append(line[2])
                else:
                    print(line[0])
        try:
            for name in sample_list:
                if sample_list[name][1] == "ChIP":
                    trail = "_screen.txt"
                else:
                    trail = "_r1_screen.txt"
                with open(home_dir + run_dir + "/Demux_Results/QC/fastq_screen/" + sample_list[name][0] + "/" + name + trail, 'r') as screen_file:
                    next(screen_file)
                    next(screen_file)
                    for line in screen_file:
                        line = line.strip().split("\t")
                        if line[0] == "Human":
                            sample_list[name][4]["Human"] = [line[5], line[3]]
                        elif line[0] == "Mouse":
                            sample_list[name][4]["Mouse"] = [line[5], line[3]]
                        elif "%Hit_no_genomes:" in line[0] and float(line[0].split(" ")[1]) > 10:
                            sample_list[name][4]["No_Genome"] = [line[0].split(" ")[1], 100]
                        elif len(line) > 10 and float(line[3]) <= 90 and float(line[5]) >= 1:
                            sample_list[name][4][line[0]] = [line[5], line[3]]

                outdata = sample_list[name]
                other_species = []
                for i in sample_list[name][4].keys():
                    if i not in ["Mouse", "Human"]:
                        other_species.append(i)

                write_file.write("{},{},{},NovaSeq6000,{},{},{},{},{},{},{},{},{}".format(name, run_num, run_date, outdata[3], outdata[0], outdata[1], "Human" if outdata[2] == "hg38" or outdata[2] == "hg19" else "Mouse" if outdata[2] == "mm10" else "", outdata[5], outdata[4]["Human"][0], 100 - float(outdata[4]["Human"][1]), outdata[4]["Mouse"][0], 100 - float(outdata[4]["Mouse"][1])))
                for i in other_species:
                    write_file.write(",{},{},{}".format(i, outdata[4][i][0], 100 - float(outdata[4][i][1])))
                write_file.write("\n")

        except:
            print("Sample failed", run_num, name)
    else:
        print("Run failed", run_dir)

home_dir: str = sys.argv[1]

if os.path.isdir(home_dir):
    with open("output2.csv", 'w') as output:
        output.write("SampleName,Run,Sequencing date,Sequencer,Lane,Project,Assay,Species,AllLanes_TotalReads,Human(OneHit OneGenome),Human(Unmapped),Mouse(OneHit OneGenome),Mouse(Unmapped)\n")
        for run_dir in listdir(home_dir):
            if len(run_dir.split("_")) == 4:
                run_date = run_dir.split("_")[0]
                run_num = run_dir.split("_")[2]
                summarize_contamination(home_dir, run_dir, run_num, run_date, output)
