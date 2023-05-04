##############################
# take a plugin report from tenable and convert it to a format that remedicado can intake
##############################
from os.path import isfile, isdir
from datetime import datetime
import csv

class Tenable_Formatter:

    def __init__(SELF, Upload_File, Save_Location):
        SELF.IMPORTED = False
        SELF.UPLOAD_FILE = Upload_File
        SELF.SAVE_LOC = Save_Location
        SELF.UPLOAD_DICT = {}
        if SELF.Read_File():
            SELF.IMPORTED = True
        SELF.Format()

        
    def Import_Validation(Func):
        ## Block upload if file failed import
        def Check_Imported(SELF, *args, **kwargs):
            if SELF.IMPORTED: 
                return Func(SELF, *args, **kwargs)
        return Check_Imported

    def Read_File(SELF):

        if (isfile(SELF.UPLOAD_FILE) == False):
            print("File couldn't be found")
            return False
        
        if (isdir(SELF.SAVE_LOC) == False):
            print("Save loc couldn't be found")
            return False
        
        if(SELF.SAVE_LOC[-1] != '\\') and (SELF.SAVE_LOC[-1] != '/'):
            print("Save loc should end in a '\\' or '/'")
            return False
           
        

        with open(SELF.UPLOAD_FILE, "r") as demo:

            csv_file = csv.DictReader(demo)

            count = 0
            for line in csv_file:
                SELF.UPLOAD_DICT.update({count : line})
                count += 1

        formated_headers = ['IP Address', 'Plugin', 'Plugin Name', 'CVSS V3 Base Score', 'Description'] 
        recieved_headers = list(SELF.UPLOAD_DICT[0].keys())
        
        if (len(recieved_headers) != len(formated_headers)):
            return False


        
        for recieved_header in recieved_headers:
            header_found = False
            for header in formated_headers:
                if (recieved_header == header):
                    header_found = True
                    break
            
            if not header_found:
                print("failed to match all headers\nShould include ['IP Address', 'Plugin', 'Plugin Name', 'CVSS V3 Base Score', 'Description']")
                return False

        return True

    @Import_Validation
    def Format(SELF):

        formated_headers = ['source', 'source_id', 'name', 'desc', 'severity', 'ips']
        formated_rows=[]
        
        for row in SELF.UPLOAD_DICT:
            
            exists = False
            for existing_row in formated_rows:
                if (existing_row[1] == SELF.UPLOAD_DICT[row]['Plugin']):
                    ip_addresses = []

                    if (type(existing_row[5]) != list):
                        ip_addresses.append(existing_row[5])
                    else:
                        ip_addresses=list(existing_row[5])

                    ip_addresses.append(SELF.UPLOAD_DICT[row]['IP Address'])
                    existing_row[5] = str(ip_addresses).replace('[','').replace(']','').replace("'","")
                    exists = True
            
            if not exists:
                formated_rows.append(['Tenable', 
                        SELF.UPLOAD_DICT[row]['Plugin'],
                        SELF.UPLOAD_DICT[row]['Plugin Name'],
                        SELF.UPLOAD_DICT[row]['Description'],
                        SELF.UPLOAD_DICT[row]['CVSS V3 Base Score'],
                        SELF.UPLOAD_DICT[row]['IP Address']])

        SELF.Export_CSV(formated_headers, formated_rows)
    
        return
        

    @Import_Validation
    def Export_CSV(SELF, Header, Data):

        with open(f'{SELF.SAVE_LOC}Tenable_Import_Data_{datetime.now().strftime("%Y_%m_%d")}.csv', 'w', newline='') as csvfile:  
            csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
            csv_writer.writerow(Header)
            for row in Data:
                csv_writer.writerow(row)

        return
       
    

Tenable_Formatter("C:\\Users\\Sam\\Documents\\Coding\\remedicado\\test_data\\DEMO NESSUS REPORT.csv", "C:\\Users\\Sam\\Documents\\Coding\\remedicado\\test_data\\")