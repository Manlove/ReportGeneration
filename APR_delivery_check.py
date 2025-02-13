"""
Takes the projects, assays, and revenue from the APR snapshot and associates
the data with the services tracker snapshot to output a table associating the 
invoiced numbers to bioinformaticians by date.
"""

import sys
from typing import List, Dict, Generator, Tuple

# Field numbers in input APR sheet
APR_ASSAY_FIELD = 12
APR_INVOICE_DATA_FIELD = 6
APR_INVOICE_AMOUNT_FIELD = 7
APR_QUOTE_FIELD = 0

# Field numbers in input tracker sheet
TRACKER_QUOTE_FIELD = 1
TRACKER_ASSAY_FIELD = 5
TRACKER_INFORMATICIAN_FIELD = 7

class QuoteStats:
    def __init__(self) -> None:
        self.APR_dict: Dict[str, List[str, str, List[str]]] = {}

    def add_quote(self,
                  quote_number: str,
                  assay: str,
                  invoice_amount: str,
                  invoice_date: str
                  ) -> None:
        """
        Adds new quotes, new assays to found quotes or adds additional
        invoiced lines to the invoice amount.
        """
        if self.check_quote(quote_number):
            if assay in self.APR_dict[quote_number]:
                self.APR_dict[quote_number][assay][1] += invoice_amount
            else:
                self.APR_dict[quote_number][assay] = [invoice_date, invoice_amount, []]
        else:
            self.APR_dict[quote_number] = {assay:[invoice_date, invoice_amount, []]}

    def check_quote(self, quote_number: str) -> bool:
        return quote_number in self.APR_dict

    def check_assay(self, quote_number: str, assay: str) -> bool:
        if self.check_quote(quote_number):
            return assay in self.APR_dict[quote_number]
        return False

    def AddInformatician(self, quote_number: str, assay: str, name: str) -> None:
        self.APR_dict[quote_number][assay][2].append(name)

    def GetData(self) -> Generator[Tuple[str, str, str, str, List[str]], None, None]:
        for quote in self.APR_dict.keys():
            for assay in self.APR_dict[quote].keys():
                yield quote, assay, self.APR_dict[quote][assay][0], self.APR_dict[quote][assay][1], self.APR_dict[quote][assay][2]

def line_split(line: str) -> str:
    """Replaces non-separating commas in a csv file with spaces and returns a list"""
    out_string: List = []
    quote_count: int =0

    for char in line:
        
        if char == '"':
            quote_count += 1
        elif char == ',' and quote_count%2 != 0:
            out_string.append(" ")
        else:
            out_string.append(char)

    return "".join(out_string).split(",")

def check_assay(assay: str) -> str:
    """Encapsulates the assay list"""
    
    assay_dict: Dict[str,str] = {
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

def parse_informatician(info_in: List[str]) -> List[str]:
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

def GetRevenueData(APR_dict: QuoteStats, apr_file: str) -> QuoteStats:
    """Get the dollar amount for each project split by assay"""
    with open(apr_file,'r') as apr:
        next(apr)
        for line in apr:
            fields=line_split(line.strip())
            if len(fields) > 12:
                
                assay_type = fields[APR_ASSAY_FIELD]
                invoice_date = fields[APR_INVOICE_DATA_FIELD]
                invoice_amount = fields[APR_INVOICE_AMOUNT_FIELD].strip("$")
                quote_number = fields[APR_QUOTE_FIELD]
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

                            APR_dict.add_quote(
                                quote_number,
                                check_assay(assay_type),
                                float(invoice_amount),
                                invoice_date
                                )
                except:
                    print(fields)
                    continue
    return APR_dict

def AddTrackerData(APR_dict: QuoteStats, tracker_file: str) -> None:
    """Associates informaticians with the projects from the revenue sheet"""
    with open(tracker_file,'r') as tracker:
        next(tracker)
        for line in tracker:
            parts = line_split(line.strip())
            if len(parts) >= 6:

                quote_number = parts[TRACKER_QUOTE_FIELD]
                assay_type = parts[TRACKER_ASSAY_FIELD]
                informatician = parts[TRACKER_INFORMATICIAN_FIELD]

                #Quote numbers are numeric and 5 digits long
                if len(quote_number)==5 and quote_number.isnumeric() and informatician != "":
                    if APR_dict.check_quote(quote_number):
                        if APR_dict.check_assay(quote_number, assay_type):
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

def WriteRevenue(APR_dict: QuoteStats, outfile: str) -> None:
    """Write the information from APR_dict to outfile"""
    with open(outfile,'w') as outfile:
        outfile.write("Quote,Assay,Date,Amount,Informatician")
        for quote, assay, date, amount, informaticians in APR_dict.GetData():
            if informaticians != []:
                info_in = parse_informatician(informaticians)
                outfile.write("\n{},{},{},{},{}".format(quote,assay,date,amount,''.join(info_in)))

if __name__ == "__main__":
    # Takes the services analysis tracker sheet (1), the services apr 
    # sheet (2), An outfile title (3), and a sheet to output projects 
    # with two informaticians (4) as inputs.
    tracker_file: str = sys.argv[1]
    apr_file: str = sys.argv[2]
    out_file: str = sys.argv[3]

    APR_dict = QuoteStats()
    APR_dict = GetRevenueData(APR_dict, apr_file)
    AddTrackerData(APR_dict, tracker_file)
    WriteRevenue(APR_dict, out_file)
    