from src import Importer, Data_Parser
from web import web_server as WEB

WEB.Start_Web_App()
quit()

upload = Importer('test_data/DEMO_UPLOAD.csv')
upload.Source_Appender()

quit()
print(Data_Parser.Get_Affected_Ips(2))
print(Data_Parser.Get_Unremediated_Ips(2))
print(Data_Parser.Get_Remediated_Ips(2))