"""
Find projects in the services analysis tracker than had not been logged
in the antibody validation pass fail rate sheet
"""

projects = []
ABQ_LIST = []

with open("/Users/lmanlove/Downloads/Antibody validation pass fail rate 2024.csv",'r') as infile:
    header = infile.readline()

    for line in infile:
        project = line.strip().split(",")[0].split(" ")[0].strip("/")[-4:]
        project = project.replace('"','')
        
        if len(project) == 4 and project.isalnum():
            if (project[1] == "0" or project[1] == "1" or project[1] == "2"):
                ABQ_LIST.append(project)

with open("/Users/lmanlove/Downloads/Services Analysis Tracker.csv",'r') as infile:

    header = infile.readline().strip().split(",")
    assay_field = header.index('"Assay"')

    for line in infile:
        fields = line.strip().split(",")
       
        if len(fields) >= 6 and fields[assay_field] == '"ChIP AbQ"':
            project_number = fields[2].strip('"')
            if not project_number.isalnum():
                project_number = project_number.split(" ")[0][-4:]

            if project_number not in ABQ_LIST:
                quote = fields[1].replace('"','')
                institute = fields[3].replace('"','')
                
                customer = ""
                if len(fields) >= 21:
                    customer = fields[20].replace('"','')
                date = ""
                if len(fields) >= 10:
                    date = fields[10].replace('"','')
                    
                projects.append('"P-{} {} ({}) Quote {},{}"'.format(project_number,institute,customer,quote,date))


# Output the missing projects to a separate .csv
with open("outABQ.csv","w") as outfile:
    outfile.write("Project")
    for i in projects:
        outfile.write("\n{}".format(i))
