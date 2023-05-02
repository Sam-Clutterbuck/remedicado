from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from werkzeug.utils import secure_filename
from re import search

from src import Data_Parser, Importer, Helpers

app = Flask(__name__, template_folder='templates', static_folder='static')

#####################
#Globals

app.config['UPLOAD_FOLDER'] = "data/uploads/"
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 #10MB max limit

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

########################################################################
# Remediation pages


@app.route("/remediations")
def Remediations_List():

    remediation_list = Data_Parser.Get_Remediation_List()

    headers = ['Vulnerabilty','Severity','Date Reported','Progress','Policy Status','Rating']
    data = []


    for remediation in remediation_list:

        remediated_ips, total_ips = Data_Parser.Get_Remediated_Ips(remediation_list[remediation]['remediation_id'])
        policy_percentage, policy_days = Data_Parser.Policy_Status_Check(remediation_list[remediation]['remediation_id'])

        remediated_ammount = f"{len(remediated_ips)}/{len(total_ips)}"
        remediated_percent = len(remediated_ips) / len(total_ips) * 100

        source_list = Data_Parser.List_Sources()


        icon = Icon_Selector(remediation_list[remediation]['remediation_sev'],remediated_percent,policy_percentage)

        data.append((remediation_list[remediation]['remediation_id'],
                     remediation_list[remediation]['remediation_name'],
                     remediation_list[remediation]['remediation_sev'],
                     remediation_list[remediation]['remediation_date_reported'],
                     remediated_ammount,
                     remediated_percent,
                     policy_percentage,
                     f"{int(policy_days)}days",
                     icon))    
    

    return render_template("./remediations.html", Header_Length=len(headers), Headings=headers, data=data, Sources=source_list)

@app.route("/remediations/details/<ID>")
def Remediation_Details(ID):

    remediation_details = Data_Parser.Get_Remediation_Details(ID)

    source_name = Helpers.Source_Id_To_Name(remediation_details['remediation_source'])

    remediated_ips, total_ips = Data_Parser.Get_Remediated_Ips(ID)

    policy_percentage, policy_days = Data_Parser.Policy_Status_Check(ID)

    uploaded_files = Data_Parser.List_Uploaded_Files(ID)

    remediated_ammount = f"{len(remediated_ips)}/{len(total_ips)}"
    remediated_percent = len(remediated_ips) / len(total_ips) * 100

    ip_dict = Data_Parser.Get_Affected_Ips(ID)
    ip_headers = ['Ip Address','Date Reported','Remediated','Last Seen','Remediated Previously']
    

    icon = Icon_Selector(remediation_details['remediation_sev'],remediated_percent,policy_percentage)
    


    return render_template("./remediation_details.html", 
                           ID=ID,
                           Remediation_Name=remediation_details['remediation_name'], 
                           Remediation_Desc=remediation_details['remediation_desc'].split('\n'),
                           Remediation_Sev=remediation_details['remediation_sev'],
                           Remediation_Source=source_name['source_name'],
                           Remediation_Source_Id=remediation_details['remediation_source_id'],
                           Date_Added=remediation_details['remediation_date_reported'],
                           Last_Updated=remediation_details['remediation_last_updated'],
                           Status_Icon=icon,
                           Remediation_Ip_Count=remediated_ammount,
                           Remediation_Percent=remediated_percent,
                           Policy_Percent=policy_percentage,
                           Policy_Days= f"{int(policy_days)}days",
                           Ip_Data=ip_dict,
                           Ip_Header_Length=len(ip_headers),
                           Ip_Headers=ip_headers,
                           Uploaded_Files = uploaded_files)


def Icon_Selector(Severity, Remediated_Percent, Policy_Percent):

    if Severity is None or Remediated_Percent is None or Policy_Percent is None:
        return

    icon_name=""

    if (float(Severity) >= 9):
        icon_name += 'crit-'
    elif (float(Severity) >= 7):
        icon_name += 'high-'
    else :
        icon_name += 'low-'

    if (float(Remediated_Percent) >= float(100)):
        icon_name = 'safe.svg'
        return icon_name
    if (float(Remediated_Percent) >= float(75)):
        icon_name += '1-'
    elif (float(Remediated_Percent) >= float(40)):
        icon_name += '2-'
    else:
        icon_name += '3-'

    if (int(Policy_Percent) >= int(100)):
        icon_name += '2.svg'
    elif (int(Policy_Percent) >= int(75)):
        icon_name += '1.svg'
    else:
        icon_name += '0.svg'

    return icon_name

@app.route("/remediations/source_breakdown", methods=['POST'])
def Source_Breakdown():
    source_id=request.form['source_id']

    if source_id is None:
        return redirect(url_for('Remediations_List'))
    
    if (type(source_id) != int):
        try:
            source_id = int(source_id)
        except ValueError:
            return redirect(url_for('Remediations_List'))
    

    file_name, remediation_dict = Data_Parser.Get_Source_Breakdown(source_id)
    return send_file(f"../data/{file_name}", as_attachment=True) 
        


@app.route("/remediations/details/<ID>/upload_report", methods=['POST'])
def Upload_Report(ID):

    allowed_extensions = ['pdf']

    if (request.method == 'POST'):
        file = request.files['vuln_report']

        if file is None:
            flash(f"No file provided")
            return redirect(f"{url_for('Remediation_Details', ID=ID)}#vuln_reports")

        if secure_filename(file.filename).split('.')[-1] not in allowed_extensions:
            flash(f"This file extension is not allowed")
            return redirect(f"{url_for('Remediation_Details', ID=ID)}#vuln_reports")

        content = file.stream.read()
        sha_hash = Data_Parser.Hash_File(content)
        filename = secure_filename(file.filename)


        uploaded_files = Data_Parser.List_Uploaded_Files(ID)
        for file in uploaded_files:
            if (str(sha_hash).lower() == str(uploaded_files[file]['uploaded_reports_hash']).lower()):
                flash(f"This file already exists ({uploaded_files[file]['uploaded_reports_filename']})")
                return redirect(f"{url_for('Remediation_Details', ID=ID)}#vuln_reports")


        with open(app.config['UPLOAD_FOLDER']+filename, 'wb') as file:
            file.write(content)
        
        Importer.Upload_File(filename, ID, sha_hash)

        return redirect(f"{url_for('Remediation_Details', ID=ID)}#vuln_reports")

    print()

@app.route("/remediations/details/<ID>/download_report/<Report_Id>")
def Report_Download(ID, Report_Id):

    file_info = Helpers.Report_Id_To_Name(Report_Id)

    if not Data_Parser.File_Exists(f"data/uploads/{file_info['uploaded_reports_filename']}"):
        flash(f"File isn't avaliable to be downloaded")
        return redirect(f"{url_for('Remediation_Details', ID=ID)}#vuln_reports")
    

    return send_file(f"../data/uploads/{file_info['uploaded_reports_filename']}", as_attachment=True) 

@app.route("/remediations/details/<ID>/remediate_ips", methods=['POST'])
def Remediate_Ips(ID):

    selected_ips = request.form['selected_ips']

    ip_list = selected_ips.replace(" ", "").split(",")

    clean_list = []
    for ip in ip_list:
        clean_ip = search(r".*\d", ip)
        if clean_ip is not None:
            clean_list.append(clean_ip.group())
    
    secure_ips = []
    for ip in clean_list:
        valid = search(r"(\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}", ip)
        if valid is not None:
            secure_ips.append(ip)

    print(secure_ips)


    valid_ip_ids = []
    for ip in secure_ips:
        validate = Helpers.Ip_To_Id(ip)
        if validate is not None:
            valid_ip_ids.append(validate)

    for ip in valid_ip_ids:
        Data_Parser.Remediate_Ip(ip, ID)

    

    return redirect(f"{url_for('Remediation_Details', ID=ID)}#ip_list")


@app.route("/remediations/details/<ID>/download_report/<Report_Id>", methods=['POST'])
def Delete_Report(ID, Report_Id):

    Data_Parser.Delete_Report(Report_Id)

    return redirect(f"{url_for('Remediation_Details', ID=ID)}#vuln_reports")

@app.route("/remediations/details/<ID>/download_remediation", methods=['POST'])
def Delete_Remediation(ID):
    
    Data_Parser.Delete_Remediation(ID)

    return redirect(url_for('Remediations_List'))

@app.route("/remediations/details/<ID>/edit")
def Edit_Remediation_Details(ID):

    remediation_details = Data_Parser.Get_Remediation_Details(ID)

    return render_template("./edit_remediation.html", 
                           ID=ID,
                           Remediation_Name=remediation_details['remediation_name'], 
                           Remediation_Desc=remediation_details['remediation_desc'],
                           Remediation_Sev=remediation_details['remediation_sev'])

@app.route("/remediations/details/<ID>/edit/commit", methods=['POST'])
def Commit_Remediation_Edit(ID):
    
    remediation_name = request.form['remediation_name']
    remediation_severity = request.form['remediation_severity']
    remediation_desc = request.form['remediation_desc']

    Data_Parser.Edit_Remediation(ID,remediation_name,remediation_severity,remediation_desc)

    return redirect(f"{url_for('Remediation_Details', ID=ID)}")