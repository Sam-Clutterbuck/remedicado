import mysql.connector

import test_data.SECRETS as SECRETS

db = mysql.connector.connect(
    host=SECRETS.host,
    user=SECRETS.user,
    passwd=SECRETS.passwd,
    database=SECRETS.database
)

mycursor = db.cursor()

class Data_Parser:

    def Get_Affected_Ips(Remediation_Id):

        mycursor.execute(f'''
                SELECT rem.remediation_name, ip_list.ip_list_address, ips.date_reported, ips.remediated, ips.last_seen, ips.remediated_previously
                FROM remedicado.remediation rem
                JOIN remedicado.affected_ips ips
                ON ips.remediation_id = rem.remediation_id
                JOIN remedicado.ip_list ip_list
                ON ip_list.ip_list_id = ips.ip_list_id
                WHERE rem.remediation_id = {Remediation_Id};
                ''')
            
        return mycursor.fetchall()

    def Get_Unremediated_Ips(Remediation_Id):
        all_ips = Data_Parser.Get_Affected_Ips(Remediation_Id)

        unremediated_ips = []

        for ip in all_ips:
            if (ip[3] == 0):
                unremediated_ips.append(ip)
        
        return unremediated_ips
    
    def Get_Remediated_Ips(Remediation_Id):
        all_ips = Data_Parser.Get_Affected_Ips(Remediation_Id)

        remediated_ips = []

        for ip in all_ips:
            if (ip[3] == 1):
                remediated_ips.append(ip)
        
        return remediated_ips
