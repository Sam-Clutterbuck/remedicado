import csv
import mysql.connector
from datetime import datetime
from os.path import isfile

import test_data.SECRETS as SECRETS
from src.sql_helpers import Helpers

db = mysql.connector.connect(
    host=SECRETS.host,
    user=SECRETS.user,
    passwd=SECRETS.passwd,
    database=SECRETS.database
)

mycursor = db.cursor()


class Importer:

    def __init__(SELF, Upload_File):
        SELF.IMPORTED = False
        SELF.UPLOAD_FILE = Upload_File
        SELF.UPLOAD_DICT = {}
        if SELF.Read_File():
            SELF.IMPORTED = True

        
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
        

        with open(SELF.UPLOAD_FILE, "r") as demo:

            csv_file = csv.DictReader(demo)

            count = 0
            for line in csv_file:
                SELF.UPLOAD_DICT.update({count : line})
                count += 1

        return True

    

    @Import_Validation
    def Ip_Loop(SELF, Source):

        ## See if there are already any affected ips listed
        try:
            mycursor.execute(f'''
                SELECT ip_list_id
                FROM remedicado.affected_ips
                WHERE remediation_id=\'{SELF.UPLOAD_DICT[Source]['SQL_REPORTED_ID']}\';
                ''')
            
            ip_list = mycursor.fetchall()

        except Exception as error: 
            print(error)


        ## Cycle through all ips for source and check if they are in the database

        ip_array = SELF.UPLOAD_DICT[Source]['ips'].replace(",", "").split()
        for ip in ip_array:
            

            ip_id = Helpers.Ip_To_Id(ip)

            already_listed = False
            for ip in ip_list:
                if (int(ip[0]) == int(ip_id)):
                    already_listed = True

            if already_listed:
                mycursor.execute(f'''
                    UPDATE remedicado.affected_ips 
                    SET remediated=false,
                        last_seen=\'{datetime.now().strftime('%Y-%m-%d')}\'
                    WHERE remediation_id=\'{SELF.UPLOAD_DICT[Source]['SQL_REPORTED_ID']}\'
                    AND ip_list_id=\'{ip_id}\';
                    ''')
                db.commit()
            else:
                print(f"INSERTING {ip}")
                mycursor.execute(f'''
                    INSERT INTO remedicado.affected_ips (
                        remediation_id, 
                        ip_list_id, 
                        date_reported,
                        remediated,
                        last_seen,
                        remediated_previously
                        )
                    VALUES (
                        \'{SELF.UPLOAD_DICT[Source]['SQL_REPORTED_ID']}\',
                        \'{ip_id}\', 
                        \'{datetime.now().strftime('%Y-%m-%d')}\', 
                        false,
                        \'{datetime.now().strftime('%Y-%m-%d')}\', 
                        false
                        );
                    ''')
                db.commit()
            
        ## Check if any ips have been remediated
        for recorded_ip in ip_list:

            in_array = False
            for passed_ip in ip_array:
                ip_id = Helpers.Ip_To_Id(passed_ip)

                if (int(recorded_ip[0]) == int(ip_id)):
                    in_array = True
                    break

            if not in_array:
                ## if its in the affected ips but not the array it means its been remediated
                mycursor.execute(f'''
                    UPDATE remedicado.affected_ips 
                    SET remediated=true,
                        remediated_previously=true
                    WHERE remediation_id=\'{SELF.UPLOAD_DICT[Source]['SQL_REPORTED_ID']}\'
                    AND ip_list_id=\'{recorded_ip[0]}\';
                    ''')
                db.commit()


    @Import_Validation
    def Source_Appender(SELF):

        ## Scan through the sources provided to see if they are reported

        for source in SELF.UPLOAD_DICT:
            source_name = SELF.UPLOAD_DICT[source]['source']
            

            ## Source Check
            try:

                ## Check if source exists and its related ID
                mycursor.execute(f'''
                    SELECT source_id
                    FROM remedicado.sources 
                    WHERE source_name=\'{source_name}\';
                    ''')
                
                source_id = mycursor.fetchone()
                if source_id is None:  
                    ## If source isn't in list skip source
                    print(f"Skipping '{SELF.UPLOAD_DICT[source]['name']}' as its source '{source_name}' is not in sources list")
                    continue

                ## Add a pointer to the SQL source ID var to dict for later use
                SELF.UPLOAD_DICT[source].update({'SQL_SOURCE_ID' : source_id[0]})
                
            except Exception as error: 
                print(error)
                continue


            
            ## Check if alredy reported
            reported = False
            try:
                mycursor.execute(f'''
                    SELECT remediation_id, remediation_name, remediation_source_id 
                    FROM remedicado.remediation 
                    WHERE remediation_source=\'{SELF.UPLOAD_DICT[source]['SQL_SOURCE_ID']}\';
                    ''')
                
                ## Check if the current source is already in database via the source id

                remediation_info = mycursor.fetchall()
                if (len(remediation_info) != 0):
                    for remediation in remediation_info:
                        if (int(remediation[2]) == int(SELF.UPLOAD_DICT[source]['source_id'])):
                            reported = True
                            SELF.UPLOAD_DICT[source].update({'SQL_REPORTED_ID' : remediation[0]})
                            print(f"'{remediation[1]}' has already been reported ")
                            break
            
            except Exception as error: 
                print(error)
                continue

                    
            

            if not reported:
                ## If not in db already, add to db
                print(f"{SELF.UPLOAD_DICT[source]['name']} hasn't been reported before")

                print(SELF.UPLOAD_DICT[source])

                try:
                    mycursor.execute(f'''
                        INSERT INTO remedicado.remediation (
                            remediation_name, 
                            remediation_desc, 
                            remediation_sev, 
                            remediation_date_reported, 
                            remediation_last_updated, 
                            remediation_source, 
                            remediation_source_id
                            )
                        VALUES (
                            \'{SELF.UPLOAD_DICT[source]["name"]}\',
                            \'{SELF.UPLOAD_DICT[source]["desc"]}\',
                            \'{SELF.UPLOAD_DICT[source]["severity"]}\',
                            \'{datetime.now().strftime('%Y-%m-%d')}\',
                            \'{datetime.now().strftime('%Y-%m-%d')}\',
                            \'{SELF.UPLOAD_DICT[source]["SQL_SOURCE_ID"]}\',
                            \'{SELF.UPLOAD_DICT[source]["source_id"]}\'
                        );
                        ''')
                    db.commit()

                except Exception as error: 
                    print(error)
                    continue
                
                #locate
                mycursor.execute(f'''
                    SELECT remediation_id
                    FROM remedicado.remediation 
                    WHERE remediation_source=\'{SELF.UPLOAD_DICT[source]['SQL_SOURCE_ID']}\'
                    AND remediation_source_id=\'{SELF.UPLOAD_DICT[source]['source_id']}\';
                    ''')
                

                remediation_id = mycursor.fetchone()
                if remediation_id is None:
                    print("AN error occured finding id")
                    continue

                SELF.UPLOAD_DICT[source].update({'SQL_REPORTED_ID' : remediation_id[0]})
                            
                SELF.Ip_Loop(source)
            
            else:
                ## If already in db then add any potential new ips to list
                mycursor.execute(f'''
                        UPDATE remedicado.remediation 
                        SET remediation_last_updated=\'{datetime.now().strftime('%Y-%m-%d')}\'
                        WHERE remediation_id=\'{SELF.UPLOAD_DICT[source]["SQL_REPORTED_ID"]}\';
                        ''')
                db.commit()


                SELF.Ip_Loop(source)




        


