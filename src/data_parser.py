import csv
import hashlib
from os.path import isfile
from datetime import datetime, timedelta, date
from yaml import safe_load, YAMLError

from src.sql_helpers import Helpers

class Data_Parser:

    #######################################################################
    ## Helper functions

    def File_Exists(File):
         
        if (isfile(File) == False):
            print("File couldn't be found")
            return False
        
        return True
    
    def Hash_File(Content):
        hash = hashlib.sha256()
        hash.update(Content)
        sha_hash = hash.hexdigest()
        
        return sha_hash

    #######################################################################

    #################################################################################
    ## Get

    @Helpers.Int_Id_Clense
    def Get_Affected_Ips(Remediation_Id):

        Helpers.sql_cursor.execute(f'''
                SELECT ip_list.ip_list_id, ip_list.ip_list_address, ips.date_reported, ips.remediated, ips.last_seen, ips.remediated_previously
                FROM remedicado.remediation rem
                JOIN remedicado.affected_ips ips
                ON ips.remediation_id = rem.remediation_id
                JOIN remedicado.ip_list ip_list
                ON ip_list.ip_list_id = ips.ip_list_id
                WHERE rem.remediation_id = {Remediation_Id};
                ''')
            
        ip_dict = Helpers.Multi_Sql_To_Dict(Helpers.sql_cursor.description, Helpers.sql_cursor.fetchall())

        return ip_dict

    @Helpers.Int_Id_Clense
    def Get_Unremediated_Ips(Remediation_Id):
        all_ips = Data_Parser.Get_Affected_Ips(Remediation_Id)

        unremediated_ips = []

        for ip in all_ips:
            if (all_ips[ip]['remediated'] == 0):
                unremediated_ips.append(all_ips[ip]['ip_list_id'])
        
        return unremediated_ips, all_ips
    
    @Helpers.Int_Id_Clense
    def Get_Remediated_Ips(Remediation_Id):
        all_ips = Data_Parser.Get_Affected_Ips(Remediation_Id)

        remediated_ips = []

        for ip in all_ips:
            if (all_ips[ip]['remediated'] == 1):
                remediated_ips.append(all_ips[ip]['ip_list_id'])
        
        return remediated_ips, all_ips


    def Get_Remediation_List():
        Helpers.sql_cursor.execute(f'''
                SELECT *
                FROM remedicado.remediation
                ''')

        remediation_dict = Helpers.Multi_Sql_To_Dict(Helpers.sql_cursor.description, Helpers.sql_cursor.fetchall())

            
        return remediation_dict
    
    @Helpers.Int_Id_Clense
    def Get_Remediation_Details(Remediation_Id):
        Helpers.sql_cursor.execute(f'''
                SELECT *
                FROM remedicado.remediation
                WHERE remediation_id = {Remediation_Id};
                ''')
        
        remediation_details = Helpers.Sql_To_Dict(Helpers.sql_cursor.description, Helpers.sql_cursor.fetchone())

        return remediation_details
    
    @Helpers.Int_Id_Clense
    def Policy_Status_Check(Remediation_Id):
        ip_list = Data_Parser.Get_Affected_Ips(Remediation_Id)
        remediation_details = Data_Parser.Get_Remediation_Details(Remediation_Id)

        sum = 0
        count = 0
        for ip in ip_list:
            if (ip_list[ip]['remediated'] == 0):
                
                if ( date.today() >= ip_list[ip]['last_seen'] ):
                    diff = date.today() - ip_list[ip]['date_reported']
                else:
                    diff = ip_list[ip]['last_seen'] - ip_list[ip]['date_reported']
                
                sum += (diff / timedelta(days=1))
                count += 1

        average = sum / count
        if (average <= 0):
            return 0

        if not Data_Parser.File_Exists('data/remediation_rules.yaml'):
            return None


        with open('data/remediation_rules.yaml') as file:
            try:
                policy_rules = safe_load(file)
            except YAMLError as error:
                return None
        

        ## Find the remediation timeframe for severity policy
        previous_severity = 0
        timeframe = 0
        for policy in policy_rules['remediation policies']:

            if (remediation_details['remediation_sev'] >= policy_rules['remediation policies'][policy]['severity'] ):
                if (policy_rules['remediation policies'][policy]['severity'] >= previous_severity):
                    previous_severity = policy_rules['remediation policies'][policy]['severity']
                    timeframe = policy_rules['remediation policies'][policy]['timeframe']

        if (average <= timeframe):

            policy_percent = average / timeframe * 100
            if (policy_percent >= 100):
                policy_percent = 100

            return policy_percent, average
    
        else:
            over_policy = timeframe - average
            return 100, over_policy

    def List_Sources():
        Helpers.sql_cursor.execute(f'''
                    SELECT *
                    FROM remedicado.sources ''')
        
        sources_dict = Helpers.Multi_Sql_To_Dict(Helpers.sql_cursor.description, Helpers.sql_cursor.fetchall())

        return sources_dict
    

    @Helpers.Int_Id_Clense
    def Get_Source_Breakdown(Source_Id):
        source_list = Data_Parser.List_Sources()

        valid = False
        for source in source_list:
            if (int(Source_Id) == int(source_list[source]['source_id'])):
                source_name = f"{source_list[source]['source_name']}_Remediations_Breakdown.csv"
                valid = True

        if (valid == False):
            return
        
        Helpers.sql_cursor.execute(f'''
                SELECT remediation_id, remediation_source_id, remediation_last_updated
                FROM remedicado.remediation
                WHERE remediation_source = {Source_Id};
                ''')
        

        remediation_dict = Helpers.Multi_Sql_To_Dict(Helpers.sql_cursor.description, Helpers.sql_cursor.fetchall())

        for source in remediation_dict:
            
            unremediated, total = Data_Parser.Get_Unremediated_Ips(remediation_dict[source]['remediation_id'])

            remediation_dict[source].update({'reported_ips': len(total), 'affected_ips':len(unremediated)})


        with open(f'data/files/{source_name}', 'w', newline='') as csvfile:  
            csv_writer = csv.DictWriter(csvfile, remediation_dict[0].keys())
            csv_writer.writeheader()
            for source in remediation_dict:
                csv_writer.writerow(remediation_dict[source])
            

        return source_name, remediation_dict 


    @Helpers.Int_Id_Clense
    def List_Uploaded_Files(Remediation_Id):
        Helpers.sql_cursor.execute(f'''
                SELECT uploaded_reports_id, uploaded_reports_filename, uploaded_reports_upload_date, uploaded_reports_hash
                FROM remedicado.uploaded_reports
                WHERE remediation_id = {Remediation_Id};
                ''')
        
        file_dict = Helpers.Multi_Sql_To_Dict(Helpers.sql_cursor.description, Helpers.sql_cursor.fetchall())
        return file_dict
    
    def Remediate_Ip(Ip_Id, Remediation_Id):
        
        Helpers.sql_cursor.execute(f'''
                UPDATE remedicado.affected_ips 
                SET remediated=true,
                    remediated_previously=true
                WHERE remediation_id=\'{Remediation_Id}\'
                AND ip_list_id=\'{Ip_Id}\';
                ''')
        Helpers.db.commit()



    #################################################################################
    ## Delete

    @Helpers.Int_Id_Clense
    def Delete_Report(Report_ID):

        try:
            Helpers.sql_cursor.execute(f'''
            DELETE FROM remedicado.uploaded_reports 
            WHERE uploaded_reports_id = {Report_ID};
            ''')
            Helpers.db.commit()

        except Exception as error: 
            print(error)
            return
        
    @Helpers.Int_Id_Clense
    def Delete_Remediation(Remediation_Id):
        
        try:
            Helpers.sql_cursor.execute(f'''
            DELETE FROM remedicado.affected_ips 
            WHERE remediation_id = {Remediation_Id};
            ''')
            Helpers.db.commit()


            Helpers.sql_cursor.execute(f'''
            DELETE FROM remedicado.remediation 
            WHERE remediation_id = {Remediation_Id};
            ''')
            Helpers.db.commit()

        except Exception as error: 
            print(error)
            return



    