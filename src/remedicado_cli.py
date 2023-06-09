from yaml import safe_load, YAMLError
from prettytable import PrettyTable
from os.path import isfile
from werkzeug.utils import secure_filename
from getpass import getpass

from src.data_parser import Data_Parser, Helpers
from src.importer import Importer
import src.remedicado_plugins as PLUGINS
from src.account_controller import Acccount_Controller
import src.__version__ as Version

class Cli:

    #########################################################################################
    ## Globals

    if (isfile('data/cli_commands.yaml') == False):
        print(f"Unable to find commands yaml file (should be found at remedicado/data/cli_commands.yaml )")
        quit()


    with open('data/cli_commands.yaml') as commands:
        try:
            COMMANDS = safe_load(commands)
        except YAMLError as error:
            print(f"Unable to find commands : {error}")
            quit()

    Authenticated = False


    #########################################################################################
    ## Helpers

    def Format_Table(Headers, Data):

        formatted_table = PrettyTable(Headers)

        for row in Data:
            cropped = []
            for item in Data[row]:
                value = str(Data[row][item])
                if (len(str(Data[row][item])) > 25 ):
                    value = f"{str(Data[row][item])[:22]}..."
                cropped.append(value)

            formatted_table.add_row(cropped)

        return formatted_table
    
    def Get_Int_Input(Prompt):
        while True:
            selection = input(f"{Prompt}\n").lower()

            try:
                int_selection = int(selection)
                return int_selection
            except ValueError:
                if (selection == "q") or (selection == "quit"):
                    Cli.Enter_Command()

                print(f"Enter a numerical value")


    def Yes_No_Option(Prompt):

        while True:
            selection = input(f"{Prompt}\n[y]es or [n]o?\n").lower()

            if (selection == "q") or (selection == "quit"):
                Cli.Enter_Command()
            elif (selection == "y") or (selection == "yes"):
                return True
            elif (selection == "n") or (selection == "no"):
                return False

            print(f"please select [y]es or [n]o?")

    
    def Authenicate(Func):
        def Check_Authentication(*Args, **Kwargs):
            if Cli.Authenticated:
                return Func(*Args, **Kwargs)
            else:
                print("You must be signed in to access this")
                return
        return Check_Authentication


    
    #########################################################################################

    def Print_Banner():

        banner = f'''
                                                                              
                                                                      
                                                   .....              
                                               ---====---=            
                                          .---+:----::--:++=.         
                                       .-=+-----::::::--=++*#+.       
                                     .------::::::::::=-=-++##=.      
                                  .+=-=---:::::::::::::-=-++###=.     
                                .=+-=-:::::::::::::::::-=+++####=     
                              .=+-=-:::::::::::::::::-=-=++*####=     
                            :=+-:-:::::::::::::::::---==+++%%###=     
                         ::==-:::::::::::::::::::::---=+++#%####=     
                      ::+=:-==+######==-::::::::::::-=+++*%%###+:     
                   :-==::-*#%%%%%%#%%%%%+-::::::::---=++*%%###+:      
                -=---:::-*%%%%%%@%#@%%%%%*-:::::::--=++*#%##*-        
              -==::-:::+%%%%%@@@@@@@@@@@@@*:::::--=+++*#%#*:          
            :+==::::::%#%@@@@@@@@@@@@@@@@@*::::-=-=++**#*-            
           :--=::::::+@%%@@@@@@@@@@@@@@@@@*:::-=-+++*#*-              
          :+=-=:::::-%@%@@@@@@@@@@@@@@@@@*::-=-++++*#*-               
         .=-=-=::::::#@@@@@@@@@@@@@@@@@@*:::-=-++++##=                
        .+=-=-::::::::=#@@@@@@@@@@@@@@%+-:-=-=++++##+.                
        .+=-=-::::::::::===#%%@@@%%%==::::-=-=+++*##=                 
        .+=-=-:::::::::::::::-++=::::::::=-=-++++###=                 
         --=-=-=-:::::::::::::::::::-=----==++++####=                 
          +=-=------:-:-::::::::-:-=-=---=++++*####-                  
           --===--=-=-=-=------=-=-=-=-=+++**#%####-                  
            .=++++=-++=-=-=----=-=-=+++++**#%####*-                   
              .=+*++++++=+=++++=+=++****##%%####-                     
                :+##*+++++++++++++##%%%%#%%###-                       
                   .+#%#%%##%%%%#%#%########-                         
                        =++*##########+==-                            
                            ..........                                
                                                                      
                                                    ▄▄   ▄▄                        ▄▄           
▀███▀▀▀██▄                                        ▀███   ██                      ▀███           
  ██   ▀██▄                                         ██                             ██           
  ██   ▄██   ▄▄█▀██▀████████▄█████▄   ▄▄█▀██   ▄█▀▀███ ▀███  ▄██▀██ ▄█▀██▄    ▄█▀▀███   ▄██▀██▄ 
  ███████   ▄█▀   ██ ██    ██    ██  ▄█▀   ██▄██    ██   ██ ██▀  ████   ██  ▄██    ██  ██▀   ▀██
  ██  ██▄   ██▀▀▀▀▀▀ ██    ██    ██  ██▀▀▀▀▀▀███    ██   ██ ██      ▄█████  ███    ██  ██     ██
  ██   ▀██▄ ██▄    ▄ ██    ██    ██  ██▄    ▄▀██    ██   ██ ██▄    ▄█   ██  ▀██    ██  ██▄   ▄██
▄████▄ ▄███▄ ▀█████▀████  ████  ████▄ ▀█████▀ ▀████▀███▄████▄█████▀▀████▀██▄ ▀████▀███▄ ▀█████▀ 
                                                                                                
cli version: {Version.__version__}
created by: @Sam-Clutterbuck
                                                                               
        '''


        return banner

    def Print_Help():
        print(f"Listing possible commands:\nTo use a command you can type its full name or use its [alt] shorthand \n")

        for command in Cli.COMMANDS:
            print(f"{command} : {Cli.COMMANDS[command]['alt']}")

        return

    def Cli_Start():
        print(Cli.Print_Banner())
        Cli.Enter_Command()
        

    def Enter_Command():
        while True:

            selection = input("\nEnter a command to run: ").lower()

            if not Cli.Command_Validate(selection):
                print(f"'{selection}' Is an invalid command \n[use 'help' or 'h' to list options]")


    def Command_Validate(Input_Command):
      
    #make sure command is valid
        for command in Cli.COMMANDS:
            if (Input_Command == command):
                Cli.COMMANDS[command]['func']()
                return True
            
            #check for alternate shorthands
            for alternate in Cli.COMMANDS[command]['alt']:
                if (Input_Command == alternate):
                    Cli.COMMANDS[command]['func']()
                    return True
            
        return False
    
    def List_Plugins():
        print(f"Installed Plugins")

        count = 0
        for plugin in PLUGINS.installed_plugins:
            print(f"{plugin.split('.')[-1]} | [{count}]")
            count += 1

        return
    
    @Authenicate
    def Run_Plugin():
        if (Cli.Yes_No_Option("Would you like to view installed plugins?")):
            Cli.List_Plugins()

        option = Cli.Get_Int_Input("Select a plugin number to run:")

        class_ref = None
        count = 0
        for plugin in PLUGINS.installed_plugins:
            if (int(option) == int(count)):
                print(f"List plugins for {plugin.split('.')[-1]}: \n")
                class_ref = PLUGINS.installed_plugins[plugin]

            count += 1


        if class_ref is None:
            print("No plugin found")
            return
        
        class_ref.Call()

        return


    def Sign_In():

        username = input(f"Enter Username\n")
        if (username == "q") or (username == "quit"):
            return 
        
        password = getpass(f"Enter Password\n")
        if (password == "q") or (password == "quit"):
            return 
        
        success = Acccount_Controller.Login(username, password)
        if success:
            Cli.Authenticated = True

        return
    
    @Authenicate
    def List_Remediations():
        print(f"Listing Remediations: \n")
        
        remediations = Data_Parser.Get_Remediation_List()
        if remediations is None or (remediations == {}):
            return
        print(Cli.Format_Table(remediations[0].keys(), remediations))
        return
    
    @Authenicate
    def List_Sources():
        print(f"Listing Sources: \n")

        sources = Data_Parser.List_Sources()
        if sources is None or (sources == {}):
            return
        print(Cli.Format_Table(sources[0].keys(), sources))
        return
    
    @Authenicate
    def Download_Source_Breakdown():
        print(f"Breakdown Source: \n")

        if (Cli.Yes_No_Option("Would you like to view possible sources?")):
            Cli.List_Sources()

        source_id = Cli.Get_Int_Input("Select a source ID to download:")

        file_name, remediation_dict = Data_Parser.Get_Source_Breakdown(source_id)
        
        if file_name is None or remediation_dict is None or (file_name == {}) or (remediation_dict == {}):
            return

        if (Cli.Yes_No_Option("Would you like to view in console?")):
            print(Cli.Format_Table(remediation_dict[0].keys(), remediation_dict))

        print(f"Created file: data/{file_name}")
        ### DOWNLOAD SOMEHOW????
        return

    @Authenicate
    def Remediation_Details():
        print(f"Selecting remediation: \n")

        if (Cli.Yes_No_Option("Would you like to view possible remediations?")):
            Cli.List_Remediations()

        remediation_id = Cli.Get_Int_Input("Select a remediation ID to view:")
        remediation_details = Data_Parser.Get_Remediation_Details(remediation_id)
        if remediation_details is None or (remediation_details == {}):
            return
        remediated_ips, total_ips = Data_Parser.Get_Remediated_Ips(remediation_id)
        if remediated_ips is None or (remediated_ips == {}) or total_ips is None or (total_ips == {}):
            return

        policy_percentage, policy_days = Data_Parser.Policy_Status_Check(remediation_id)
        if policy_percentage is None or (policy_percentage == {}) or policy_days is None or (policy_days == {}):
            return
        if (policy_percentage >= 100): 
            policy_status = "Out of Policy"
        else:
            policy_status = "In Policy"


        remediated_ammount = f"{len(remediated_ips)}/{len(total_ips)}"
        remediated_percent = len(remediated_ips) / len(total_ips) * 100


        print(f'''
Vulnerability: {remediation_details["remediation_name"]}
Source ID : {remediation_details["remediation_source_id"]}

    Severity: {remediation_details["remediation_sev"]}
    Remediation progress: {remediated_percent}% [{remediated_ammount} remediated ips]
    Policy Status: {policy_status} [{int(policy_days)} days]

    Date Reported:{remediation_details["remediation_date_reported"]}
    Last Updated: {remediation_details["remediation_last_updated"]}

Description: 
{remediation_details["remediation_desc"]}
        ''')

        ip_dict = Data_Parser.Get_Affected_Ips(remediation_id)
        if ip_dict is not None and (len(ip_dict) > 0):
            print(f"Assosiated Ips:")
            print(Cli.Format_Table(ip_dict[0].keys(), ip_dict))

        uploaded_files = Data_Parser.List_Uploaded_Files(remediation_id)
        if uploaded_files is not None and (len(uploaded_files) > 0):
            print(f"Uploaded Reports:")
            print(Cli.Format_Table(uploaded_files[0].keys(), uploaded_files))
        
        return
        
    @Authenicate
    def Import_Remediations():

        while True:

            file = input("\nEnter file path to import: ").lower()

            if (file == "q") or (file == "quit"):
                    Cli.Enter_Command()

            if (isfile(file) == True):

                if (file.split('.')[-1] == "csv"):
                    break
                
                print("Only formatted csv's are able to be imported")

            print("Please enter a valid file path")

        upload = Importer(file)
        if upload.IMPORTED:
            print(f"Uploading {file}")
            upload.Source_Appender()
        else:
            print(f"Unable to upload file {file}")
        
        return
    
    @Authenicate
    def Upload_Reports():
        
        if (Cli.Yes_No_Option("Would you like to view possible remediations?")):
            Cli.List_Remediations()

        remediation_id = Cli.Get_Int_Input("Select a remediation ID to upload to:")

        while True:

            file = input("\nEnter file path to import: ").lower()

            if (file == "q") or (file == "quit"):
                    Cli.Enter_Command()

            if (isfile(file) == True):

                if (file.split('.')[-1] == "pdf"):
                    break
                
                print("Only pdf reports are able to be imported")

            print("Please enter a valid file path")

        with open(file, "rb") as open_content:
            content = open_content.read()
        sha_hash = Data_Parser.Hash_File(content)
        
        if (len(file.split('\\')) > 1):
            filename = secure_filename(file.split('\\')[-1])
        if (len(file.split('/')) > 1):
            filename = secure_filename(file.split('/')[-1])


        uploaded_files = Data_Parser.List_Uploaded_Files(remediation_id)
        if uploaded_files is None or (uploaded_files == {}):
            return
        for file in uploaded_files:
            if (str(sha_hash).lower() == str(uploaded_files[file]['uploaded_reports_hash']).lower()):
                print(f"This file already exists ({uploaded_files[file]['uploaded_reports_filename']})")
                return 

        print(f"Uploading {filename}")
        with open('data/uploads/'+filename, 'wb') as file:
            file.write(content)
        
        Importer.Upload_File(filename, remediation_id, sha_hash)

        return

    @Authenicate
    def Delete_Report():

        if (Cli.Yes_No_Option("Would you like to view possible remediations?")):
            Cli.List_Remediations()

        remediation_id = Cli.Get_Int_Input("Select a remediation ID to delete report from:")

    
        uploaded_files = Data_Parser.List_Uploaded_Files(remediation_id)
        if uploaded_files is not None and (len(uploaded_files) > 0):
            if (Cli.Yes_No_Option("Would you like to view remediation reports?")):
                print(f"Uploaded Reports:")
                print(Cli.Format_Table(uploaded_files[0].keys(), uploaded_files))
        else:
            print(f"No reports Found")
            return

        report_id = Cli.Get_Int_Input(f"Select a report ID to delete from remediation:")

        report_details = Helpers.Report_Id_To_Name(report_id)
        if not(Cli.Yes_No_Option(f"Are you sure you want to delete : {report_details['uploaded_reports_filename']}?")):
            print(f"Cancelling deletion request")
            return

        Data_Parser.Delete_Report(report_id)
        print(f"'{report_details['uploaded_reports_filename']}' Report Deleted")

        return
    
    @Authenicate
    def Delete_Remediation():

        if (Cli.Yes_No_Option("Would you like to view possible remediations?")):
            Cli.List_Remediations()

        remediation_id = Cli.Get_Int_Input("Select a remediation ID to delete:")

        remediation_details = Helpers.Remediation_Id_To_Name(remediation_id)
        if not(Cli.Yes_No_Option(f"Are you sure you want to delete : {remediation_details['remediation_name']}?")):
            print(f"Cancelling deletion request")
            return

        Data_Parser.Delete_Remediation(remediation_id)
        print(f"'{remediation_details['remediation_name']}' Remediation Deleted")

        return

    @Authenicate
    def Remediate_Ip():
        if (Cli.Yes_No_Option("Would you like to view possible remediations?")):
            Cli.List_Remediations()

        remediation_id = Cli.Get_Int_Input("Select a remediation ID to remediate ips for:")

        ip_dict = Data_Parser.Get_Affected_Ips(remediation_id)
        if ip_dict is not None and (len(ip_dict) > 0):
            if (Cli.Yes_No_Option("Would you like to view possible ips?")):
                print(f"Assosiated Ips:")
                print(Cli.Format_Table(ip_dict[0].keys(), ip_dict))
        else:
            print("No ips found")
            return

        if (Cli.Yes_No_Option("Would you like to remediate multiple ips?")):
            while True:
                ip_id = Cli.Get_Int_Input("Select an ip ID to remediate:\n[press 'q' to quit once done]")
                Data_Parser.Remediate_Ip(ip_id, remediation_id)

        ip_id = Cli.Get_Int_Input("Select an ip ID to remediate:")
        Data_Parser.Remediate_Ip(ip_id, remediation_id)
        return

    @Authenicate
    def Add_Source():

        if (Cli.Yes_No_Option("Would you like to view existing sources?")):
            Cli.List_Sources()


        selection = input(f"What source would you like to add:\n")

        if (selection.lower() == "q") or (selection.lower() == "quit"):
            print(f"quiting...")
            return
        
        Data_Parser.Add_Source(selection)

        return
    
    @Authenicate
    def Delete_Source():

        if (Cli.Yes_No_Option("Would you like to view possible sources?")):
            Cli.List_Sources()

        source_id = Cli.Get_Int_Input("Select a source ID to delete:")

        Data_Parser.Delete_Source(source_id)

        return

    @Authenicate
    def Add_User():
        
        username = input(f"Enter Username\n")
        if (username == "q") or (username == "quit"):
            return 
        
        password = getpass(f"Enter Password\n")
        if (password == "q") or (password == "quit"):
            return 
        
        Acccount_Controller.Create_Account(username, password)
        return

    @Authenicate
    def Pasword_Reset():
        username = input(f"Enter Username\n")
        if (username == "q") or (username == "quit"):
            return 
        
        password = getpass(f"Enter New Password for {username}\n")
        if (password == "q") or (password == "quit"):
            return 
        
        Acccount_Controller.Password_Reset(username, password)
        return
    
    @Authenicate
    def Delete_User():
        username = input(f"Enter Username\n")
        if (username == "q") or (username == "quit"):
            return 
        
        Acccount_Controller.Delete_user(username)
        return

    COMMANDS['login'].update({'func':Sign_In})
    COMMANDS['quit'].update({'func':quit})
    COMMANDS['help'].update({'func':Print_Help})
    COMMANDS['list plugins'].update({'func':List_Plugins})
    COMMANDS['remediations list'].update({'func':List_Remediations})
    COMMANDS['source list'].update({'func':List_Sources})
    COMMANDS['download source breakdown'].update({'func':Download_Source_Breakdown})
    COMMANDS['remediation details'].update({'func':Remediation_Details})
    COMMANDS['import remediations'].update({'func':Import_Remediations})
    COMMANDS['upload report'].update({'func':Upload_Reports})
    COMMANDS['delete report'].update({'func':Delete_Report})
    COMMANDS['delete remediation'].update({'func':Delete_Remediation})
    COMMANDS['remediate ip'].update({'func':Remediate_Ip})
    COMMANDS['run plugin'].update({'func':Run_Plugin})
    COMMANDS['add source'].update({'func':Add_Source})
    COMMANDS['delete source'].update({'func':Delete_Source})
    COMMANDS['add user'].update({'func':Add_User})
    COMMANDS['delete user'].update({'func':Delete_User})
    COMMANDS['password reset'].update({'func':Pasword_Reset})


    