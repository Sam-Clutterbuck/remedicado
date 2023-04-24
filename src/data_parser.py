import mysql.connector

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
        
        return unremediated_ips
    
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