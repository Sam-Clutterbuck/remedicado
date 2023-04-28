
import csv

from os.path import isfile
from prettytable import PrettyTable
from datetime import datetime


class CSV_Comparison:

    def __init__(SELF, Source_Breakdown, Top_Vulns):

        SELF.IMPORTED = False
        SELF.BREAKDOWN = Source_Breakdown
        SELF.VULNS_CSV = Top_Vulns
        SELF.VULN_DICT = {}
        SELF.BREAKDOWN_DICT = {}
        if SELF.Read_File():
            SELF.IMPORTED = True

        if SELF.IMPORTED:
            SELF.Merge_Comparison()

        return
    
    def Import_Validation(Func):
        ## Block upload if file failed import
        def Check_Imported(SELF, *args, **kwargs):
            if SELF.IMPORTED: 
                return Func(SELF, *args, **kwargs)
        return Check_Imported

    def Read_File(SELF):

        if (isfile(SELF.BREAKDOWN) == False):
            print("Source breakdown file couldn't be found")
            return False
        
        if (isfile(SELF.VULNS_CSV) == False):
            print("Top vulnerability file couldn't be found")
            return False
        

        with open(SELF.BREAKDOWN, "r") as demo:

            csv_file = csv.DictReader(demo)

            count = 0
            for line in csv_file:
                SELF.BREAKDOWN_DICT.update({count : line})
                count += 1        

        breakdown_headers = ['remediation_id','remediation_source_id','remediation_last_updated','reported_ips', 'affected_ips']
        if not SELF.Header_Check(list(SELF.BREAKDOWN_DICT[0].keys()), breakdown_headers):
            return False

        with open(SELF.VULNS_CSV, "r") as demo:

            csv_file = csv.DictReader(demo)

            count = 0
            for line in csv_file:
                SELF.VULN_DICT.update({count : line})
                count += 1        

        vuln_headers = ['remediation_name','source_id','severity','affected_ip_count']
        
        if not SELF.Header_Check(list(SELF.VULN_DICT[0].keys()), vuln_headers):
            return False
        
        return True
    
    def Header_Check(SELF, Recieved_Headers, Expected_Headers):

        if (len(Recieved_Headers) != len(Expected_Headers)):
            print("Incorrect number of headers recieved")
            return False

        for header_count in range(len(Expected_Headers)):
            if (Recieved_Headers[header_count] != Expected_Headers[header_count]):
                print(f"'{Recieved_Headers[header_count]}' recieved when expecting '{Expected_Headers[header_count]}'")
                return False
            
        return True
    
    @Import_Validation
    def Merge_Comparison(SELF):

        comparison = [['remediation_name','source_id','severity','affected_ip_count', 'reported', 'remediation_id', 'remediation_last_updated','reported_ips', 'affected_ips']]

        for vuln in SELF.VULN_DICT:
            match = False
            matched_details = {}
            for reported in SELF.BREAKDOWN_DICT:
                if (int(SELF.VULN_DICT[vuln]['source_id']) == int(SELF.BREAKDOWN_DICT[reported]['remediation_source_id'])):
                    match = True
                    matched_details.update(SELF.BREAKDOWN_DICT[reported])
                    break
            
            if match:
                comparison.append([SELF.VULN_DICT[vuln]['remediation_name'],
                                   SELF.VULN_DICT[vuln]['source_id'],
                                   SELF.VULN_DICT[vuln]['severity'],
                                   SELF.VULN_DICT[vuln]['affected_ip_count'],
                                   True,
                                   matched_details['remediation_id'],
                                   matched_details['remediation_last_updated'],
                                   matched_details['reported_ips'],
                                   matched_details['affected_ips']])
            else:
                comparison.append([SELF.VULN_DICT[vuln]['remediation_name'],
                                   SELF.VULN_DICT[vuln]['source_id'],
                                   SELF.VULN_DICT[vuln]['severity'],
                                   SELF.VULN_DICT[vuln]['affected_ip_count'],
                                   False,
                                   'Not Reported',
                                   'Not Reported',
                                   'Not Reported',
                                   'Not Reported'])


        headers = comparison.pop(0)
        formatted_table = PrettyTable(headers)

        for row in comparison:
            
            cropped = []
            for item in row:
                value = str(item)
                if (len(str(item)) > 25 ):
                    value = f"{str(item)[:22]}..."
                cropped.append(value)

            formatted_table.add_row(cropped)

        print(formatted_table)

        with open(f'data/files/Vulnerability_List_{datetime.now().strftime("%Y_%m_%d")}.csv', 'w', newline='') as csvfile:  
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(headers)
            for row in comparison:
                csv_writer.writerow(row)

        print(f"Created file : data/files/Vulnerability_List_{datetime.now().strftime('%Y_%m_%d')}.csv")
    