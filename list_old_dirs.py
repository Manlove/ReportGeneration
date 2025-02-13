#!/usr/bin/env python

'''
Returns a list of all directories that have a last 
modified date older than a set date. Used to find 
project folders that can me removed.
 '''

import glob
from os import listdir
from os import stat
import os.path
import time
import datetime

delete_date = datetime.date(2021,1,1)

PATH_BASE: str = "/home/mnt/services_data/Data_Storage/"

with open("old_dirs.csv", "w") as outfile:
    for institute in listdir(PATH_BASE):
        if os.path.isdir(PATH_BASE + institute) and institute not in ["AM", "CTAGBATCH", "QCATAC", "QCCTAG"]:
            print(institute)

            # get a list of the project directories in the institute directory
            for project in listdir(os.path.join(PATH_BASE,institute)):
                if os.path.isdir(os.path.join(PATH_BASE,institute, project)):
                    print("\t{0}".format(project))

                    # Assumes everything is old
                    is_old = True
                    # Sets the newest date as None
                    save_time = None

                    # Steps through each file and folder
                    for item in listdir(os.path.join(PATH_BASE, institute, project)):
                        if os.path.isdir(os.path.join(PATH_BASE, institute, project, item)) or os.path.isfile(os.path.join(PATH_BASE, institute, project, item)):

                            # Gets the last modified date of the item
                            a = stat(os.path.join(PATH_BASE, institute, project, item)).st_mtime
                            file_time = datetime.datetime.fromtimestamp(a).date()

                            # Checks if there is a time saved in save_time
                            if save_time == None:
                                save_time = file_time

                            # If the new time is newer than the previous time saves the new time
                            if file_time > save_time:
                                save_time = file_time

                            # If the time is newer than the delete date set delete to False
                            if file_time > delete_date:
                                    # print(True)
                                    is_old = False

                    # If the project should still be deleted writes a file of paths and a file with paths and last modified date
                    if is_old and save_time != None:
                        #print(os.path.join(PATH_BASE, institute, project))
                        outfile.write("{0}\n".format(os.path.join(PATH_BASE, institute, project)))
