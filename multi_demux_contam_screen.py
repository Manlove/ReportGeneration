'''
Summarize the contamination from all samples run on a sequencing machine.

Expanded from NextSeq_contamination_summary.
'''

from os import listdir
import os.path
import time
import datetime
import glob

# Step through each run directory
  # grab the run number
  # grab the run date
  # grab each QC folder
    # step through each fastq_screen file
      # step through each sample
        # save each sample to a list or dictionary to reduce duplicate samples

# Path to saved run info
MULTI_DEMUX_DIR: str = "/multi_demux/"

with open('NextSeq_Demux_Contam_Log.csv', "w") as logfile:
    with open('NextSeq_Demux_Contam_Summary.csv', "w") as outfile:
        outfile.write("Sample_Name,Run_Number,Run_Date,Machine,Lane,Project_ID,Assay_Type,Species,AllLanes_TotalReads,Human (one hit - one genome),Human Mapped,Mouse (one hit - one genome),Mouse Mapped,,,,\n")

        # Step through each saved nextseq run directory
        for nextseq_run in listdir(MULTI_DEMUX_DIR):
            if os.path.isdir(os.path.join(MULTI_DEMUX_DIR, nextseq_run)):

                # Save the run number, date, and machine
                run_number = nextseq_run.split("_")[2]
                run_date = nextseq_run.split("_")[0]
                run_machine = nextseq_run.split("_")[1]

                # Create a dictionary to hold the samples and the sample QC info from the run
                run_sample_list = {}

                # Steps through multiple demux in the run directory
                for demux in listdir(os.path.join(MULTI_DEMUX_DIR, nextseq_run)):
                    if os.path.isdir(os.path.join(MULTI_DEMUX_DIR, nextseq_run, demux)):

                        # Creates a dictionary to hold the sample and the QC info from the individual demux
                        demux_sample_list = {}

                        # Opens the samplesheet for the demux and grabs all the sample names
                        with open(glob.glob(os.path.join(MULTI_DEMUX_DIR, nextseq_run, demux,'SampleSheet*.csv')), 'r') as SampleSheetSummary:
                            line = SampleSheetSummary.readline()
                            while "[Data]" not in line:
                                line = SampleSheetSummary.readline()

                            for line in SampleSheetSummary:
                                line = line.strip().split(",")
                                try:
                                    if len(line) > 5 and line[0] != "Sample_ID":

                                        # Gets the species of the sample
                                        species = line[1].split("_")[-2]

                                        run_type = line[9]
                                        sample_name = line[1]

                                        # Saves the sample and the QC info to the demux dict sample_name = [Run type, species, dict for contam]
                                        demux_sample_list[sample_name] = [run_type, "Human" if "hs" in species else "Mouse" if "mm" in species else "", {}]

                                        if run_type in ["ATAC", "ATACSeq", "ChIP", "CHIP", "ChIPSeq", "ChIPPE"]:
                                            project = sample_name.split("_")[2][0:4]
                                        else:
                                            project = sample_name.split("_")[1][0:4]

                                        demux_sample_list[sample_name].append(project)

                                except:
                                    pass

                        # Opens the run stats tsv file and retrieves the read numbers for each sample
                        try:
                            with open(glob.glob(os.path.join(MULTI_DEMUX_DIR, nextseq_run, demux,"*.tsv"))[0], 'r') as RunStatistics:
                                next(RunStatistics)
                                for line in RunStatistics:
                                    line = line.strip().split("\t")
                                    if line[0] in demux_sample_list:
                                        demux_sample_list[line[0]].append(line[2])
                                    elif line[0] != "Undetermined":
                                        logfile.write('sample {0} in tsv but not found in samplesheet\n'.format(line[0]))
                        except:
                            tsv_file = glob.glob(os.path.join(MULTI_DEMUX_DIR, nextseq_run, demux,"*.tsv"))
                            if len(tsv_file) > 0:
                                logfile.write("Unknown error opening tsv with run number: {0}\n".format(run_number))
                            else:
                                logfile.write("tsv file for run number {0} does not exist\n".format(run_number))
                            for sample in demux_sample_list.keys():
                                demux_sample_list[sample].append("")

                        # Steps through the saved sample names in the demux_sample_list and opens the corresponding fastq_screen file
                        for name in demux_sample_list.keys():

                            # Checks if the sample from the demux list is in the run_sample_list or not, if it is checks if there are more reads in the new demux
                            try:
                                if name not in run_sample_list.keys() or int(demux_sample_list[name][3]) > int(run_sample_list[name[3]]):

                                    # Finds the correct fastq_screen naming convention
                                    if os.path.isfile(os.path.join(MULTI_DEMUX_DIR, nextseq_run, demux, name + "_r1_screen.txt")):
                                        screen_path = os.path.join(MULTI_DEMUX_DIR, nextseq_run, demux, name + "_r1_screen.txt")
                                    else:
                                        screen_path = os.path.join(MULTI_DEMUX_DIR, nextseq_run, demux, name + "_screen.txt")

                                    # Opens the fastq_screen file
                                    with open(screen_path, 'r') as screen_file:

                                        # Discards the header line and the specs line
                                        next(screen_file)
                                        next(screen_file)

                                        # Steps through the rest of the lines in the file, only acting on lines with more than 10 fields
                                        for line in screen_file:
                                            line = line.strip().split("\t")
                                            if len(line) > 10:

                                                # Explicitly looks for the Human and Mouse lines to make sure those species are at the front
                                                if line[0] == "Human":
                                                    demux_sample_list[name][2]["Human"] = [line[5], line[3]]
                                                elif line[0] == "Mouse":
                                                    demux_sample_list[name][2]["Mouse"] = [line[5], line[3]]

                                                # For the rest of the tested species saves the name and the contamination
                                                elif float(line[3]) <= 90 and float(line[5]) >= 1:
                                                    demux_sample_list[name][2][line[0]] = [line[5], line[3]]

                                    # Transfers the demux data to the run data
                                    run_sample_list[name] = demux_sample_list[name]

                                else:
                                    logfile.write("Duplicate Sample Ignored: {0}\n".format(name))
                            except:
                                logfile.write("error with sample: {}\n".format(name))

                for name in run_sample_list.keys():
                    outdata = run_sample_list[name]
                    other_species = []
                    for i in run_sample_list[name][2].keys():
                        if i not in ["Mouse", "Human"]:
                            other_species.append(i)
                    outfile.write("{},{},{},{},NA,{},{},{},{},{},{},{},{},,,,".format(name, run_number, run_date, run_machine, outdata[3], outdata[0], outdata[1], outdata[4], outdata[2]["Human"][0], 100 - float(outdata[2]["Human"][1]), outdata[2]["Mouse"][0], 100 - float(outdata[2]["Mouse"][1])))
                    for i in other_species:
                        outfile.write(",{},{},{}".format(i, outdata[2][i][0], 100 - float(outdata[2][i][1])))
                    outfile.write("\n")
