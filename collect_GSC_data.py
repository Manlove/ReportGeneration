#!/usr/bin/env python3

# Run in a folder with subfolders for different weeks. These subfolders
# contain weekly snapshots from the sharepoint analysis tracker and status summaries for each week.
# Outputs a csv with the number of projects in each bucket for each week.

import glob
from os import listdir
import os.path

def ClearCommas(line):
    """Replaces non-separating commas in a csv file with spaces"""
    i=0
    quote_count = 0
    while i < len(line):
        
        if line[i] == '"':
            quote_count = 0 if quote_count == 1 else 1
            
        elif line[i] == ',' and quote_count == 1:
            line = line[:i] + " " + line[i+1:]
            
        i += 1
    return line

# Step through through each wekk and open the services anaysis tracker file.
# Opens the files and retrieves the number of projects at each status. 
with open("gsc_summary.csv", 'w') as summary_outfile:
    gsc_summary = {"Week":[], "Analyzing":[], "Cancelled":[], "Not started":[],
                   "On hold":[], "Sequencing incomplete":[], "Delivered":[]}
    for week in listdir("."):
        if os.path.isdir(os.path.join('.', week)):
            if os.path.exists(os.path.join('.', week, "Services Analysis Tracker.csv")):
                
                with open(os.path.join('.', week, "Services Analysis Tracker.csv"), 'r') as apr_data:
                    apr_data.readline()
                    status_data = {}
                    
                    for line in apr_data.readlines():
                        line = ClearCommas(line)
                        line = line.replace('"','')
                        line = line.strip().split(",")

                        # Data in the sharepoint output can be messy.
                        # We drop lines with ten or less fields.
                        if line[0].isnumeric() and len(line) > 10:
                            status = line[6]
                            if status in status_data:
                                status_data[status] += 1
                            else:
                                status_data[status] = 1
                                
                gsc_summary["Week"].append(week)

                # Transfers the data from the weekly summary to the final summary
                for status in ["Analyzing", "Cancelled", "Not started",
                               "On hold", "Sequencing incomplete"]:
                        gsc_summary[status].append(status_data[status] if status in status_data else 0)

            # If no projects were delivered the status will not exist in status_summary.csv
            # The "delivered" status in ther services analysis tracker will have all projects
            # that have ever been delivered.
            delivered = 0
            if os.path.exists(os.path.join('.', week, "status_summary.csv")):
                with open(os.path.join('.', week, "status_summary.csv"), 'r') as apr_summary_data:
                    apr_summary_data.readline()
                    for line in apr_summary_data.readlines():
                        line = line.replace('"','')
                        line = line.strip().split(",")
                        if line[0] == "Delivered":
                            delivered = line[1]
            gsc_summary["Delivered"].append(delivered)


    # Adds all the summaries to a final outfile.
    for key in gsc_summary.keys():
        summary_outfile.write("{}".format(key))
        for i in gsc_summary[key]:
            summary_outfile.write(",{}".format(i))
        summary_outfile.write("\n")

