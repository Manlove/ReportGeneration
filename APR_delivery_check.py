"""
Takes the projects, assays, and revenue from the APR snapshot and associates
the data with the services tracker snapshot to output a table associating the 
invoiced numbers to bioinformaticians by date.
"""

import sys

# Field numbers in input APR sheet
APR_assay_field = 12
APR_invoice_date_field = 6
APR_invoice_amount_field = 7
APR_quote_field = 0

# Field numbers in input tracker sheet
tracker_quote_field = 1
tracker_assay_field = 5
tracker_informatician_field = 7

def line_split(line):
    """Replaces non-separating commas in a csv file with spaces and returns a list"""
    out_string = []
    quote_count=0

    for char in line:
        
        if char == '"':
            quote_count += 1
        elif char == ',' and quote_count%2 != 0:
            out_string.append(" ")
        else:
            out_string.append(char)

    return "".join(out_string).split(",")

def check_assay(assay):
    """Encapsulates the assay list"""
    
    assay_dict={
                '[ATAC-Seq (No data analysis)]':'ATAC',
                '[ATAC-Seq (Sample Validation)]':'ATAC validation',
                '[ATAC-Seq (TissueNo data analysis)]':'ATAC',
                '[ATAC-Seq (Tissue)]':'ATAC',
                '[ATAC-Seq]':'ATAC',
                '[ChIC/CUT&RUN (No data analysis)]':'CUT&Run',
                '[ChIC/CUT&RUN Tissue (No data analysis)]':'CUT&Run',
                '[ChIC/CUT&RUN Tissue]':'CUT&Run',
                '[ChIC/CUT&RUN]':'CUT&Run',
                '[ChIP-qPCR FactorPath]':'ChIP',
                '[ChIP-qPCR HistonePath]':'ChIP',
                '[ChIP-Seq (Antibody Qualification)]':'ChIP AbQ',
                '[ChIP-Seq FactorPath (No data analysis)]':'ChIP',
                '[ChIP-Seq FactorPath]':'ChIP',
                '[ChIP-Seq FFPE (No data analysis)]':'ChIP',
                '[ChIP-Seq FFPE (Sample Validation)]':'ChIP',
                '[ChIP-Seq FFPE]':'ChIP',
                '[ChIP-Seq HistonePath (No data analysis)]':'ChIP',
                '[ChIP-Seq HistonePath]':'ChIP',
                '[ChIP-Seq Low Cell Number]':'ChIP',
                '[ChIP-Seq TranscriptionPath]':'ChIP',
                '[Custom Assay]':'Custom Assay',
                '[CUT&Tag (Antibody Qualification)]':'CUT&Tag validation',
                '[CUT&Tag (No data analysis)]':'CUT&Tag',
                '[CUT&Tag Tissue (No data analysis)]':'CUT&Tag',
                '[CUT&Tag Tissue]':'CUT&Tag',
                '[CUT&Tag]':'CUT&Tag',
                '[Data Analysishourly]':'Custom Analysis',
                '[Hi-C Service1 billion sequencing depth]':'Hi-C',
                '[Hi-C Service600 million sequencing depth]':'Hi-C',
                '[Hi-C]':'Hi-C',
                '[Input-Seq]':'ChIP',
                '[Mod Spec]':'ModSpec',
                '[RIME (Antibody Qualification)]':'RIME ABQ',
                '[RIME]':'RIME',
                '[RNA-Seq (Total RNANo data analysis)]':'RNA',
                '[RNA-Seq (Total RNA)]':'RNA',
                '[RNA-Seq]':'RNA',
                '[RRBS (gDNA)]':'RRBS',
                '[RRBS]':'RRBS',
                '[scATAC-Seq Service (Tissue)]':'scATAC',
                '[scATAC-Seq Service]':'scATAC',
                '[scMultiome (No data analysis)]':'scMultiome',
                '[scMultiome (TissueNo data analysis)]':'scMultiome',
                '[scMultiome (Tissue)]':'scMultiome',
                '[scMultiome]':'scMultiome',
                '[scRNA-Seq (No data analysis)]':'scRNA',
                '[scRNA-Seq]':'scRNA',
                '[snRNA-Seq]':'scRNA',
                '[Spike-in Normalization Add-on]':'ChIP'
                }
    
    return assay_dict.get(assay,"")

def parse_informatician(info_in):
    """
    Checks if the same person is listed multiple times for a project.
    Returns the original list if more than one person is found.
    Intended to collapse lists with multiple entries of a single name
    into one name but maintain relative contributions if more than one
    person is listed.

    """
    check_informaticians = list(set(info_in))
    if len(check_informaticians) == 1:
        return check_informaticians
    else:
        return info_in

def GetRevenueData(APR_dict,apr_file):
    """Get the dollar amount for each project split by assay"""
    with open(apr_file,'r') as apr:
        next(apr)
        for line in apr:
            fields=line_split(line.strip())
            if len(fields) > 12:
                
                assay_type = fields[APR_assay_field]
                invoice_date = fields[APR_invoice_date_field]
                invoice_amount = fields[APR_invoice_amount_field].strip("$")
                quote_number = fields[APR_quote_field]
                try:
                    if len(quote_number)==5 and quote_number.isnumeric():
                        
                        # Only includes quotes that have been invoiced, have a positive value,
                        # and have a included assay
                        if (
                            invoice_amount != "" and 
                            float(invoice_amount) > 0 and 
                            invoice_date != "" and 
                            check_assay(assay_type) != ""
                            ):

                            APR_dict.AddQuote(
                                quote_number,
                                check_assay(assay_type),
                                float(invoice_amount),
                                invoice_date
                                )
                except:
                    print(fields)
                    continue
    return APR_dict

def AddTrackerData(APR_dict, tracker_file):
    """Associates informaticians with the projects from the revenue sheet"""
    with open(tracker_file,'r') as tracker:
        next(tracker)
        for line in tracker:
            parts = line_split(line.strip())
            if len(parts) >= 6:

                quote_number = parts[quote_field]
                assay_type = parts[assay_field]
                informatician = parts[informatician_field]

                #Quote numbers are numeric and 5 digits long
                if len(quote_number)==5 and quote_number.isnumeric() and informatician != "":
                    if APR_dict.CheckQuote(quote_number):
                        if APR_dict.CheckAssay(quote_number, assay_type):
                            APR_dict.AddInformatician(quote_number,assay_type,informatician)

                        # No analysis projects are not associated with a specific assay
                        elif assay_type == "No Analysis":
                            if len(APR_dict[quote_number]) == 1: 
                                assay = list(APR_dict[quote_number].keys())[0]
                                if assay != "":
                                    try:
                                        APR_dict.AddInformatician(quote_number,assay_type,informatician)
                                    except:
                                        print(APR_dict[quote_number])
                            else:
                                print(quote_number, assay_type, informatician, len(APR_dict[quote_number]),APR_dict[quote_number])

def WriteRevenue(APR_dict, outfile):
    """Write the information from APR_dict to outfile"""
    with open(out_file,'w') as outfile:
        outfile.write("Quote,Assay,Date,Amount,Informatician")
        for quote, assay, date, amount, informaticians in APR_dict.GetData():
            if informaticians != []:
                info_in = parse_informatician(informaticians)
                outfile.write("\n{},{},{},{},{}".format(quote,assay,date,amount,''.join(info_in)))

class QuoteStats():
    def __init__():
        APR_dict = {}

    def AddQuote(self,quote_number, assay, invoice_amount, invoice_date):
        """
        Adds new quotes, new assays to found quotes or adds additional
        invoiced lines to the invoice amount.
        """
        if self.CheckQuote(quote_number):
            if assay in APR_dict[quote_number]:
                APR_dict[quote_number][assay][1] += invoice_amount
            else:
                APR_dict[quote_number][assay] = [invoice_date, invoice_amount, []]
        else:
            APR_dict[quote_number] = {assay:[invoice_date, invoice_amount, []]}

    def CheckQuote(self, quote_number):
        return quote_number in APR_dict

    def CheckAssay(self, quote_number, assay):
        if self.CheckQuote(quote_number):
            return assay in APR_dict[quote_number]
        return False

    def AddInformatician(self, quote_number, assay, name):
        APR_dict[quote_number][assay][2].append(name)

    def GetData(self):
        for quote in APR_dict.keys():
            for assay in APR_dict[quote].keys():
                yield quote, assay, APR_dict[quote][assay][0], APR_dict[quote][assay][1], APR_dict[quote][assay][2]

if __name__ == "__main__":
    # Takes the services analysis tracker sheet (1), the services apr 
    # sheet (2), An outfile title (3), and a sheet to output projects 
    # with two informaticians (4) as inputs.
    tracker_file = sys.argv[1]
    apr_file = sys.argv[2]
    out_file = sys.argv[3]

    APR_dict=QuoteStats()
    APR_dict = GetRevenueData(APR_dict, apr_file)
    APR_dict = AddTrackerData(APR_dict, tracker_file)
    WriteRevenue(APR_dict, out_file)
    