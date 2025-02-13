"""
Checks the projects in the services analysis tracker
against the projects that have been demultiplexed to ensure
that all of the projects have been logged
"""

from typing import Dict

TRACKER_LIST: str = "Services Analysis Tracker.csv"
DEMUXED_LIST: str = "demuxed_projects.csv"

logged_projects: Dict[str, str] = {}

with open(TRACKER_LIST,'r') as tracker:
    next(tracker)
    for line in tracker:
        split_line = line.strip().split(",")
        if len(split_line) >= 10 and split_line[10] != "":
            if split_line[1] in logged_projects:
                if split_line[10] > logged_projects[split_line[1]] or logged_projects[split_line[1]] == "NA":
                    logged_projects[split_line[1]] = split_line[10]
            else:
                logged_projects[split_line[1]] = split_line[10]
        else:
            if split_line[1] in logged_projects:
                logged_projects[split_line[1]] = "NA"

with open("/Users/lmanlove/Desktop/matched_list.csv", 'w') as output:
    with open(DEMUXED_LIST, 'r') as demuxed:
        for line in demuxed:
            if line.strip() in logged_projects:
                output.write("{},{}\n".format(line.strip(), logged_projects[line.strip()]))
            else:
                output.write("{},not in tracker\n".format(line.strip()))
