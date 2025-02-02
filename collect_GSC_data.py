#!/usr/bin/env python3

"""
Run in a folder with subfolders for different weeks. These subfolders
contain weekly snapshots from the sharepoint analysis tracker and status summaries for each week.
Outputs a csv with the number of projects in each bucket for each week.
"""

import glob
import os

def ClearCommas(line):
    """Replaces non-separating commas in a csv file with spaces"""
    out_string = []
    quote_count = 0
    
    for char in line:
        
        if char == '"':
            quote_count = 0 if quote_count == 1 else 1
            
        elif char == ',' and quote_count == 1:
            out_string.append(" ")
        else:
            out_string.append(char)
            
    return "".join(out_string)


if __name__ == "__main__":
    # Step through through each week and open the services anaysis tracker file.
    # Opens the files and retrieves the number of projects at each status. 
    with open("gsc_summary.csv", 'w') as summary_outfile:
        gsc_summary = {"Week":[], "Analyzing":[], "Cancelled":[], "Not started":[],
                       "On hold":[], "Sequencing incomplete":[], "Delivered":[]
                       }
        for week in os.scandir("."):
            tracker_path = os.path.join(week.path, "Services Analysis Tracker.csv")
            status_summary_path = os.path.join(week.path, "status_summary.csv")

            if not week.is_dir() or not os.path.exists(tracker_path):
                continue
                
            with open(tracker_path, 'r') as apr_data:
                next(apr_data)
                status_data = {}
                
                for line in map(ClearCommas,apr_data):
                    line = line.replace('"','').strip().split(",")

                    # Data in the sharepoint output can be messy.
                    # We drop lines with ten or less fields.
                    if line[0].isnumeric() and len(line) > 10:
                        status = line[6]
                        status_data[status] = status_data.get(status,0) + 1

                            
            gsc_summary["Week"].append(week.name)

            # Transfers the data from the weekly summary to the final summary
            for status in ["Analyzing", "Cancelled", "Not started",
                           "On hold", "Sequencing incomplete"]:
                    gsc_summary[status].append(status_data.get(status, 0))

            # If no projects were delivered the status will not exist in status_summary.csv
            # The "delivered" status in ther services analysis tracker will have all projects
            # that have ever been delivered.
            delivered = 0
            if os.path.exists(status_summary_path):
                with open(status_summary_path, 'r') as apr_summary_data:
                    next(apr_summary_data)
                    for line in apr_summary_data:
                        line = line.replace('"','').strip().split(",")
                        if line[0] == "Delivered":
                            delivered = line[1]
                            
            gsc_summary["Delivered"].append(delivered)


    # Adds all the summaries to a final outfile.
    for key in gsc_summary.keys():
        summary_outfile.write("{}".format(key))
        for i in gsc_summary[key]:
            summary_outfile.write(",{}".format(i))
        summary_outfile.write("\n")

