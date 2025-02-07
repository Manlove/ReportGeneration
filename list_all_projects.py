'''Creates a list of demultiplexed projects from several run directories'''

from os import listdir
import os.path
import time
import datetime
import glob

# Path to baase dir
base_dir = "/Volumes/"

with open("list_demuxed_projects.csv", "w") as projects_outfile:
    projects_outfile.write("Sequencer,Run,Date,Project,Samples")
    for sequencer in ["NovaSeq_Data", "NextSeq_Data"]:
        for run in listdir(os.path.join(base_dir, sequencer)):
            run_num = run.split("_")
            if len(run_num) > 3:
                if os.path.isdir(os.path.join(base_dir, sequencer, run, "Demux_Results","FASTQ")):
                    for project in listdir(os.path.join(base_dir, sequencer, run, "Demux_Results/FASTQ/")):
                        if os.path.isdir(os.path.join(base_dir, sequencer, run, "Demux_Results","FASTQ", project)):
                            projects_outfile.write("\n{},{},{},{},{}".format("NovaSeq" if sequencer == "NovaSeq_Data" else "NextSeq", run_num[2], run_num[0], project, len(listdir(os.path.join(base_dir, sequencer, run, "Demux_Results/FASTQ/", project)))))
