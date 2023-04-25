import mysql.connector
import yaml
from os.path import isfile
from datetime import datetime, timedelta, date

import test_data.SECRETS as SECRETS
from src.sql_helpers import Helpers

db = mysql.connector.connect(
    host=SECRETS.host,
    user=SECRETS.user,
    passwd=SECRETS.passwd,
    database=SECRETS.database
)

mycursor = db.cursor()

class Data_Parser:

    #######################################################################
    ## Helper functions

    def Remediation_Id_Clense(Func):
        def Int_Check(Remediation_Id):
            if Remediation_Id is None:
                return

            if (type(Remediation_Id) != int):

                try:
                    int_remediation_id = int(Remediation_Id)
                    Func(int_remediation_id)
                except ValueError:
                    return
            
            return Func(Remediation_Id)
            
        return Int_Check


    #######################################################################

    @Remediation_Id_Clense
    def Get_Affected_Ips(Remediation_Id):

        mycursor.execute(f'''
                SELECT ip_list.ip_list_address, ips.date_reported, ips.remediated, ips.last_seen, ips.remediated_previously
                FROM remedicado.remediation rem
                JOIN remedicado.affected_ips ips
                ON ips.remediation_id = rem.remediation_id
                JOIN remedicado.ip_list ip_list
                ON ip_list.ip_list_id = ips.ip_list_id
                WHERE rem.remediation_id = {Remediation_Id};
                ''')
            
        ip_dict = {}
        counter = 0
        for row in mycursor.fetchall():
            row_dict = Helpers.Sql_To_Dict(mycursor.description, row)
            ip_dict.update({counter:row_dict})
            counter +=1

        return ip_dict

    @Remediation_Id_Clense
    def Get_Unremediated_Ips(Remediation_Id):
        all_ips = Data_Parser.Get_Affected_Ips(Remediation_Id)

        unremediated_ips = []

        for ip in all_ips:
            if (all_ips[ip]['remediated'] == 0):
                unremediated_ips.append(ip)
        
        return unremediated_ips, all_ips
    
    @Remediation_Id_Clense
    def Get_Remediated_Ips(Remediation_Id):
        all_ips = Data_Parser.Get_Affected_Ips(Remediation_Id)

        remediated_ips = []

        for ip in all_ips:
            if (all_ips[ip]['remediated'] == 1):
                remediated_ips.append(ip)
        
        return remediated_ips, all_ips


    def Get_Remediation_List():
        mycursor.execute(f'''
                SELECT *
                FROM remedicado.remediation
                ''')

        remediation_dict = {}
        counter = 0
        for row in mycursor.fetchall():
            remediation_item = Helpers.Sql_To_Dict(mycursor.description, row)
            remediation_dict.update({counter:remediation_item})
            counter +=1

            
        return remediation_dict
    
    @Remediation_Id_Clense
    def Get_Remediation_Details(Remediation_Id):
        mycursor.execute(f'''
                SELECT *
                FROM remedicado.remediation
                WHERE remediation_id = {Remediation_Id};
                ''')
        
        remediation_details = Helpers.Sql_To_Dict(mycursor.description, mycursor.fetchone())

        return remediation_details
    
    @Remediation_Id_Clense
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

        if (isfile('data/remediation_rules.yaml') == False):
            print("File couldn't be found")
            return None

        with open('data/remediation_rules.yaml') as file:
            try:
                policy_rules = yaml.safe_load(file)
            except yaml.YAMLError as error:
                return None
        

        ## Find the remediation timeframe for severity policy
        previous_severity = 0
        timeframe = 0
        for policy in policy_rules['remediation policies']:

            if (remediation_details['remediation_sev'] >= policy_rules['remediation policies'][policy]['severity'] ):
                if (policy_rules['remediation policies'][policy]['severity'] >= previous_severity):
                    previous_severity = policy_rules['remediation policies'][policy]['severity']
                    timeframe = policy_rules['remediation policies'][policy]['timeframe']

        policy_percent = average / timeframe * 100
        if (policy_percent >= 100):
            policy_percent = 100

        return policy_percent, average
