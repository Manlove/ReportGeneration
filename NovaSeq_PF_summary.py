from os import listdir
import os.path
import time
import datetime
import glob

def clean_str(in_str):
    keep = False
    out_str = ""
    for i in range(0,len(in_str)):
        if in_str[i] == "<":
            keep = False
        if keep and in_str[i] != ",":
            out_str = out_str + in_str[i]
        if in_str[i] == ">":
            keep = True
    return out_str

# Step through each run directory
  # grab the run number
  # grab the run date
  # grab each QC folder
    # step through each fastq_screen file
      # step through each sample
        # save each sample to a list or dictionary to reduce duplicate samples

# Path to run info
multi_demux_dir = "/Volumes/NovaSeq_Data/"

with open('NovaSeq_PF_Summary.csv', "w") as outfile:
    outfile.write("Run_Number,Run_Date,Assays,PF")

    # Step through each run directory
    for seq_run in listdir(multi_demux_dir):
        if os.path.isdir(os.path.join(multi_demux_dir, seq_run)):
            if len(seq_run.split("_")) > 2:

                #Save the run number, date, and machine
                run_number = seq_run.split("_")[2]
                run_date = seq_run.split("_")[0]
                run_machine = seq_run.split("_")[1]

                lane_path = glob.glob(os.path.join(multi_demux_dir, seq_run, "Demux_Results","*Reports","html","*","all","all","all","lane.html"))
                if len(lane_path) > 0:
                    assaytypes = []
                    with open(os.path.join(multi_demux_dir, seq_run,"Demux_Params","SampleSheetSummary.csv"),'r') as sumfile:
                        sumfile.readline()
                        for line in sumfile.readlines():
                            line = line.strip().split(",")
                            if line[2] not in assaytypes:
                                assaytypes.append(line[2])

                    with open(lane_path[0],'r') as infile:
                        td = False
                        tdcount = 0
                        for line in infile.readlines():

                            if "Yield (MBases)" in line:
                                td = True

                            if td and line[0:4] == "<td>":
                                if tdcount == 0:
                                    raw = line.split()
                                if tdcount == 1:
                                    pf = line.split()
                                    td = False
                                tdcount += 1
                                
                        raw = float(clean_str(raw[0]))
                        pf = float(clean_str(pf[0]))
                        outfile.write("\n{},{},{},{}".format(run_number, run_date, ";".join(assaytypes), pf/raw))
