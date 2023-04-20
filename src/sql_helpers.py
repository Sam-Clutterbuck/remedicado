import mysql.connector
from datetime import datetime

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="OfAllProblems!",
    database="remediator"
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
                FROM remediator.ip_list
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
                INSERT INTO remediator.ip_list (ip_list_address)
                VALUES (\'{Ip_Address}\');
                ''')
            db.commit()
            
            mycursor.execute(f'''
                SELECT ip_list_id
                FROM remediator.ip_list
                WHERE ip_list_address=\'{Ip_Address}\';
                ''')
            
            for ip_id in mycursor:
                #print(f"Added '{Ip_Address}' to ip list with id {ip_id[0]}")
                return ip_id[0]
