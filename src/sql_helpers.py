import mysql.connector
from datetime import datetime

import test_data.SECRETS as SECRETS

class Helpers:

    db = mysql.connector.connect(
    host=SECRETS.host,
    user=SECRETS.user,
    passwd=SECRETS.passwd,
    database=SECRETS.database
    )

    sql_cursor = db.cursor()

    def Int_Id_Clense(Func):
        def Int_Check(ID):
            if ID is None:
                return

            if (type(ID) != int):

                try:
                    int_id = int(ID)
                    Func(int_id)
                except ValueError:
                    return
            
            return Func(ID)
            
        return Int_Check

    def Ip_To_Id(Ip_Address):

        ## Check if ip is already in list and return its ID 
        ## If not in list add it and get new ID
        exists = False
        try:
            Helpers.sql_cursor.execute(f'''
                SELECT ip_list_id
                FROM remedicado.ip_list
                WHERE ip_list_address=\'{Ip_Address}\';
                ''')
            
            for found_ip in Helpers.sql_cursor:
                exists = True
                #print(f"{Ip_Address} exists with id {found_ip[0]}")
                return found_ip[0]

        except Exception as error: 
            print(error)

        if not exists:
            Helpers.sql_cursor.execute(f'''
                INSERT INTO remedicado.ip_list (ip_list_address)
                VALUES (\'{Ip_Address}\');
                ''')
            Helpers.db.commit()
            
            Helpers.sql_cursor.execute(f'''
                SELECT ip_list_id
                FROM remedicado.ip_list
                WHERE ip_list_address=\'{Ip_Address}\';
                ''')
            
            for ip_id in Helpers.sql_cursor:
                #print(f"Added '{Ip_Address}' to ip list with id {ip_id[0]}")
                return ip_id[0]

    @Int_Id_Clense
    def Report_Id_To_Name(Report_Id):
        
        Helpers.sql_cursor.execute(f'''
                SELECT uploaded_reports_filename, uploaded_reports_hash
                FROM remedicado.uploaded_reports
                WHERE uploaded_reports_id = {Report_Id};
                ''')
        
        report_dict = Helpers.Sql_To_Dict(Helpers.sql_cursor.description, Helpers.sql_cursor.fetchone())
        return report_dict
    

    @Int_Id_Clense
    def Remediation_Id_To_Name(Remediation_Id):
        
        Helpers.sql_cursor.execute(f'''
                SELECT remediation_name
                FROM remedicado.remediation
                WHERE remediation_id = {Remediation_Id};
                ''')
        
        remediation_dict = Helpers.Sql_To_Dict(Helpers.sql_cursor.description, Helpers.sql_cursor.fetchone())
        return remediation_dict

    def Multi_Sql_To_Dict(Header_list, Sql_Data):
        
        sql_dict = {}
        counter = 0
        for row in Sql_Data:
            sql_item = Helpers.Sql_To_Dict(Header_list, row)
            sql_dict.update({counter:sql_item})
            counter +=1
        
        return sql_dict


    def Sql_To_Dict(Header_list, Sql_Data):

        if Header_list is None or Sql_Data is None:
                return

        headers = []
        for header in Header_list:
            headers.append(header[0])

        sql_dict = {}
        for count in range(0,len(Sql_Data)):
            sql_dict.update({headers[count]:Sql_Data[count]})

        return sql_dict