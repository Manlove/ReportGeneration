'''
Summarizes the contamination screens from a single NovaSeq directory.

Build around on newer demultiplex output
'''

import sys

HOME_DIR: str = sys.argv[1]

with open(HOME_DIR + '/Demux_Params/SampleSheetSummary.csv', 'r') as SampleSheetSummary:
    next(SampleSheetSummary)
    sample_list = {}
    for line in SampleSheetSummary:
        line = line.strip().split(",")
        sample_list[line[0]] = [line[1], line[2], line[3], line[7], {}]

with open(HOME_DIR + '/Demux_Results/QC/RunStatistics.csv', 'r') as RunStatistics:
    next(RunStatistics)
    for line in RunStatistics:
        line = line.strip().split(",")
        if line[0] in sample_list:
            sample_list[line[0]].append(line[2])
        else:
            # There shouldnt be any samples that are in the SampleSheetSummary but not in the RunStatistics
            print(line[0])

with open("output.csv", 'w') as output:
    output.write("SampleName,Run,Sequencing date,Sequencer,Lane,Project,Assay,Species,AllLanes_TotalReads,Human(OneHit OneGenome),Human(Unmapped),Mouse(OneHit OneGenome),Mouse(Unmapped)\n")
    for name in sample_list:

        # Everything other than ChIP is sequenced as paired end. This needs to be more flexible
        if sample_list[name][1] == "ChIP":
            trail = "_screen.txt"
        else:
            trail = "_r1_screen.txt"

        with open(HOME_DIR + "/Demux_Results/QC/fastq_screen/" + sample_list[name][0] + "/" + name + trail, 'r') as screen_file:
            next(screen_file)
            next(screen_file)
            for line in screen_file:
                line = line.strip().split("\t")
                if line[0] == "Human":
                    sample_list[name][4]["Human"] = [line[5], line[3]]
                elif line[0] == "Mouse":
                    sample_list[name][4]["Mouse"] = [line[5], line[3]]
                elif "%Hit_no_genomes:" in line[0] and float(line[0].split(" ")[1]) > 10:
                    print("this happened")
                    sample_list[name][4]["No_Genome"] = [line[0].split(" ")[1], 100]
                elif len(line) > 10 and float(line[3]) <= 90 and float(line[5]) >= 1:
                    sample_list[name][4][line[0]] = [line[5], line[3]]

        outdata = sample_list[name]
        other_species = []
        for i in sample_list[name][4]:
            if i not in ["Mouse", "Human"]:
                other_species.append(i)
        output.write("{},,,,{},{},{},{},{},{},{},{},{}".format(name, outdata[3], outdata[0], outdata[1], "Human" if outdata[2] == "hg38" or outdata[2] == "hg19" else "Mouse" if outdata[2] == "mm10" else "", outdata[5], outdata[4]["Human"][0], 100 - float(outdata[4]["Human"][1]), outdata[4]["Mouse"][0], 100 - float(outdata[4]["Mouse"][1])))
        for i in other_species:
            output.write(",{},{},{}".format(i, outdata[4][i][0], 100 - float(outdata[4][i][1])))
        output.write("\n")

