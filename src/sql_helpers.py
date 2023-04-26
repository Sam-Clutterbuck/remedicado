import mysql.connector
from datetime import datetime

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="OfAllProblems!",
    database="remedicado"
)
mycursor = db.cursor()

class Helpers:

    def Ip_To_Id(Ip_Address):

        ## Check if ip is already in list and return its ID 
        ## If not in list add it and get new ID
        exists = False
        try:
            mycursor.execute(f'''
                SELECT ip_list_id
                FROM remedicado.ip_list
                WHERE ip_list_address=\'{Ip_Address}\';
                ''')
            
            for found_ip in mycursor:
                exists = True
                #print(f"{Ip_Address} exists with id {found_ip[0]}")
                return found_ip[0]

        except Exception as error: 
            print(error)

        if not exists:
            mycursor.execute(f'''
                INSERT INTO remedicado.ip_list (ip_list_address)
                VALUES (\'{Ip_Address}\');
                ''')
            db.commit()
            
            mycursor.execute(f'''
                SELECT ip_list_id
                FROM remedicado.ip_list
                WHERE ip_list_address=\'{Ip_Address}\';
                ''')
            
            for ip_id in mycursor:
                #print(f"Added '{Ip_Address}' to ip list with id {ip_id[0]}")
                return ip_id[0]


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