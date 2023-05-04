import mysql.connector
from yaml import safe_load, YAMLError
from datetime import datetime
from os.path import isfile


import test_data.SECRETS as SECRETS

class Helpers:

    if (isfile('data/remedicado_config.yaml') == False):
        print(f"Unable to find commands yaml file (should be found at remedicado/data/remedicado_config.yaml )")
        quit()

    with open('data/remedicado_config.yaml') as commands:
        try:
            CONFIG = safe_load(commands)
        except YAMLError as error:
            print(f"Unable to find config file : {error}")
            quit()


    db = mysql.connector.connect(
    host=CONFIG['host'],
    user=SECRETS.user,
    passwd=SECRETS.passwd,
    database=CONFIG['database']
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
        try:
            Helpers.sql_cursor.execute(f'''
                SELECT ip_list_id
                FROM ip_list
                WHERE ip_list_address=\'{Ip_Address}\';
                ''')
            
            for found_ip in Helpers.sql_cursor:
                #print(f"{Ip_Address} exists with id {found_ip[0]}")
                return found_ip[0]

        except Exception as error: 
            print(error)
            return None
        
        return None


    def Ip_To_Id_And_Add(Ip_Address):

        ## Check if ip is already in list and return its ID 
        ## If not in list add it and get new ID
        exists = False

        returned_id = Helpers.Ip_To_Id(Ip_Address)
        if returned_id is not None:
            return returned_id
            exists = True


        if not exists:

            try:
                Helpers.sql_cursor.execute(f'''
                    INSERT INTO ip_list (ip_list_address)
                    VALUES (\'{Ip_Address}\');
                    ''')
                Helpers.db.commit()
                
                Helpers.sql_cursor.execute(f'''
                    SELECT ip_list_id
                    FROM ip_list
                    WHERE ip_list_address=\'{Ip_Address}\';
                    ''')
                
                for ip_id in Helpers.sql_cursor:
                    #print(f"Added '{Ip_Address}' to ip list with id {ip_id[0]}")
                    return ip_id[0]
                
            except Exception as error: 
                print(error)
                return None

    @Int_Id_Clense
    def Report_Id_To_Name(Report_Id):
        
        try:
            Helpers.sql_cursor.execute(f'''
                    SELECT uploaded_reports_filename, uploaded_reports_hash
                    FROM uploaded_reports
                    WHERE uploaded_reports_id = {Report_Id};
                    ''')
            
            report_dict = Helpers.Sql_To_Dict(Helpers.sql_cursor.description, Helpers.sql_cursor.fetchone())
            return report_dict

        except Exception as error: 
            print(error)
            return None
    

    @Int_Id_Clense
    def Remediation_Id_To_Name(Remediation_Id):
        
        try:
            Helpers.sql_cursor.execute(f'''
                    SELECT remediation_name
                    FROM remediation
                    WHERE remediation_id = {Remediation_Id};
                    ''')
            
            remediation_dict = Helpers.Sql_To_Dict(Helpers.sql_cursor.description, Helpers.sql_cursor.fetchone())
            return remediation_dict
        
        except Exception as error: 
            print(error)
            return None
        

    @Int_Id_Clense
    def Source_Id_To_Name(Source_Id):
        
        try:
            Helpers.sql_cursor.execute(f'''
                    SELECT source_name
                    FROM sources
                    WHERE source_id = {Source_Id};
                    ''')
            
            source_dict = Helpers.Sql_To_Dict(Helpers.sql_cursor.description, Helpers.sql_cursor.fetchone())
            return source_dict

        except Exception as error: 
            print(error)
            return None
    

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