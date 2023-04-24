from flask import Flask, render_template, request, redirect, url_for, jsonify

from src import Data_Parser

app = Flask(__name__, template_folder='templates', static_folder='static')

#####################
#Globals

app.secret_key = "TEST"
#####################

def Start_Web_App():
    app.run(host="0.0.0.0", port=80, debug = True)

########################################################################
# Error Handles

@app.errorhandler(404)
def Page_Not_Found(error):
    return render_template("./404.html")

########################################################################
# Home page

@app.route("/home")
@app.route("/")
def Home():

    return render_template("./home.html")

@app.route("/remediations")
def Remediations_List():

    remediation_list = Data_Parser.Get_Remediation_List()

    headers = ['Vulnerabilty','Severity','Date Reported','Progress','Policy Status']
    data = []


    for remediation in remediation_list:

        remediated_ips, total_ips = Data_Parser.Get_Remediated_Ips(remediation_list[remediation]['remediation_id'])

        remediated_ammount = f"{len(remediated_ips)}/{len(total_ips)}"
        remediated_percent = len(remediated_ips) / len(total_ips) * 100


        data.append((remediation_list[remediation]['remediation_id'],
                     remediation_list[remediation]['remediation_name'],
                     remediation_list[remediation]['remediation_sev'],
                     remediation_list[remediation]['remediation_date_reported'],
                     remediated_ammount,
                     remediated_percent))    
    
    print(data)

    return render_template("./remediations.html", headings=headers, data=data)

@app.route("/remediations/Details/<ID>")
def Remediation_Details(ID):

    remediation_details = Data_Parser.Get_Remediation_Details(ID)

    remediated_ips, total_ips = Data_Parser.Get_Remediated_Ips(ID)

    remediated_ammount = f"{len(remediated_ips)}/{len(total_ips)}"
    remediated_percent = len(remediated_ips) / len(total_ips) * 100

    ip_dict = Data_Parser.Get_Affected_Ips(ID)
    print(ip_dict)
    ip_headers = ['Ip Address','Date Reported','Remediated','Last Seen','Remediated Previously']


    return render_template("./remediation_details.html", 
                           ID=ID,
                           Remediation_Name=remediation_details['remediation_name'], 
                           Remediation_Desc=remediation_details['remediation_desc'].split('\n'),
                           Remediation_Sev=remediation_details['remediation_sev'],
                           Date_Added=remediation_details['remediation_date_reported'],
                           Last_Updated=remediation_details['remediation_last_updated'],
                           Remediation_Ip_Count=remediated_ammount,
                           Remediation_Percent=remediated_percent,
                           Ip_Data=ip_dict,
                           Ip_Headers=ip_headers)