"""
Takes a list of genes from a customer with the gene name in the "name_filed"
variable. Also takes any number of RRBS_gene_methylation.csv files
(currently does not support xlsx)

Outputs a csv file with the genes from the customers list that matched
gene names in the RRBS_gene_methylation lists and the average coverage
from across the files provided.
"""


import sys
from typing import List, Dict

NAME_FIELD = 3

def parse_header(line: str) -> List[List[str]]:
    """ 
    {USAGE} Takes the header line of a RRBS_gene_methylation.csv file and
            identifies the "Coverage" columns associated with each sample.
            Returns a list of list containing the columns for each region
            of the sample. Should look something like [[1,4],[2,5],[3,6]]
    
    {NOTE}  Should just be two numbers from promoter and gene body; if more
            regions are in the column names this code will need to be adapted.

    {UPDATE} Identify a way to allow this code to be more adaptable.
             Could look for sample names using only the "Promoter" or "Gene Body"
             columns and then look for additonal names with that name.

    """

    out_samples = []
    header = line.strip().split(",")
    sample_dict = {}

    for i in range(6,len(header)):
        if "Coverage" in header[i]:
            sample = header[i].split(" Coverage")[0].split(" Promoter")[0].split(" Gene Body")[0]
            if sample in sample_dict:
                sample_dict[sample].append(i)
            else:
                sample_dict[sample] = [i]
    for i in sample_dict.keys():
        out_samples.append(sample_dict[i])
    return out_samples
        
def parse_coverage(line: str) -> str:
    """ 
    {USAGE} Takes the list of coverage numbers and returns them in string
            format to allow use of a .join function. This function is not
            used when a single average number is returned for each gene

    {NOTE}

    {UPDATE} Check if there is a more streamlined way to do this 

    """
    for i in range(0,len(line)):
        line[i] = str(line[i])
    return line

def average_dict_genes(
        temp_gene_to_coverage: Dict[str, List[int]]
        ) -> Dict[str, int]:
    """ 
    {USAGE} Given a dictionary with gene names as the keys and a list of coverage
            from different samples or projects; averages the values for each gene
            name and saves the averaged value to that gene name instead.

    {NOTE}  

    {UPDATE} 

    """
    for i in temp_gene_to_coverage:
        nsamp=0
        total=0
        for j in temp_gene_to_coverage[i]:
            total+=j
            nsamp+=1
        average=total//nsamp
        temp_gene_to_coverage[i]=average
    return temp_gene_to_coverage

def combine_gene_to_coverages(
        gene_to_coverage: Dict[str, List[int]], 
        temp_gene_to_coverage: Dict[str, int]
        ) -> Dict[str, List[int]]:
    """ 
    {USAGE} Given two dictionaries with gene names as the keys for both, gene_to_coverage
            having lists of averaged values from multiple projects, and temp_gene_to_coverage
            having the average coverage from multiple samples; adds the value from
            temp_gene_to_coverage to the list from gene_to_coverage for each gene

    {NOTE}  

    {UPDATE} There may be a better way to combined dictionaries like this.

    """
    for i in temp_gene_to_coverage.keys():
        if i in gene_to_coverage:
            gene_to_coverage[i].append(temp_gene_to_coverage[i])
        else:
            gene_to_coverage[i] = [temp_gene_to_coverage[i]]
    return gene_to_coverage

# Input files: [1] is the customer gene list with gene names in the NAME_FIELD column (.csv format)
customer_file: str = sys.argv[1]
gene_to_coverage: Dict[str, List[int]] = {}

# {NOTE} The RRBS pipeline returns xlsx files so it would be good to update this to take those.
for i in range(2,len(sys.argv)):

    temp_gene_to_coverage: Dict[str, List[int]] = {}

    with open(sys.argv[i],'r') as in_file:

        # Calls the parse_header function to retrieve the column numbers for the "Coverage" columns
        sample_fields = parse_header(in_file.readline())

        for line in in_file:
            fields = line.strip().split(",")
            gene_name = fields[2]
            num_samples = 0
            sample_sum = 0
            for sample in sample_fields:
                for region in sample:

                    # If no coverage is found it is #N/A in the sheet instead of 0. 
                    # This adds that 0 for the coverage and otherwise adds the value from the sheet
                    if fields[region] == "#N/A":
                        sample_sum += 0
                    else:
                        sample_sum += int(fields[region])
                num_samples += 1

            # Adds the gene to the temp_gene_to_coverage along with the average of the coverage rounded down. 
            # {NOTE} Some genes show up on multiple lines in the sheet and they will all end up under the same gene.
            if gene_name in temp_gene_to_coverage:
                temp_gene_to_coverage[gene_name].append(sample_sum//num_samples)
            else:
                temp_gene_to_coverage[gene_name] = [sample_sum//num_samples]

    # Averages the coverage values from the samples in a single project
    temp_gene_to_coverage = average_dict_genes(temp_gene_to_coverage)
    gene_to_coverage = combine_gene_to_coverages(gene_to_coverage,temp_gene_to_coverage)

# Averages value from all projects.
# {NOTE} This can be commented out to output each value from each project 
gene_to_coverage = average_dict_genes(gene_to_coverage)

# Opens the customer file and an output file
# {NOTE} This probably should be something that is also passed from the command line.
with open(customer_file,'r') as in_file:
    with open("RRBS_outfile.csv", 'w') as out_file:

        # Adds headers to the files
        # {NOTE} This header only works if you only output one value. If you output values from each project it wonnt
        out_file.write("Gene Name,Coverage")

        next(in_file)
        for line in in_file:
            fields = line.strip().split(",")
            if fields[NAME_FIELD] != "" and fields[NAME_FIELD] in gene_to_coverage.keys():
                out_file.write("\n{},{}".format(fields[NAME_FIELD],gene_to_coverage[fields[NAME_FIELD]]))
               
                
