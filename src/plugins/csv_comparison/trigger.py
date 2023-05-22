#########################################################
# Plugin : csv_comparison
# Created by: @Sam-Clutterbuck
# Version: 0.0.2
# Last Updated: 27/04/2023
#
#
# Usage:
# This plugin takes a source breakdown csv and compares it with a top xxxx csv from a source.
#########################################################
from os.path import isfile
from flask import Blueprint, render_template, request, redirect, url_for, send_file, flash
from werkzeug.utils import secure_filename


from src.plugins.csv_comparison.csv_comparison import CSV_Comparison


class Trigger:
    
    def Path_Request(Prompt):
        while True:

            file = input(f"\n{Prompt}\n").lower()

            if (file == "q") or (file == "quit"):
                    return None

            if (isfile(file) == True):

                if (file.split('.')[-1] == "csv"):
                    break
                
                print("Only csv reports are able to be imported")

            print("Please enter a valid file path")
        
        return file

    def Call():
        print("Move control to this script")

        breakdown_path = Trigger.Path_Request("Enter breakdown csv file location:")
        if breakdown_path is None:
            return

        vuln_path = Trigger.Path_Request("Enter top vulnerability csv file location:")
        if vuln_path is None:
            return
        
        compare = CSV_Comparison(breakdown_path, vuln_path)
        compare.Print_Table()


        answer = False
        response = False
        while not answer:
            selection = input(f"Would you like to \n[y]es or [n]o?\n").lower()

            if (selection == "q") or (selection == "quit"):
                response = False
                answer = True
            elif (selection == "y") or (selection == "yes"):
                response = True
                answer = True
            elif (selection == "n") or (selection == "no"):
                response = False
                answer = True

            print(f"please select [y]es or [n]o?")

        if response:
            analysis = CSV_Comparison.Analyse_Results(compare.COMPARISON)
            print("The following sources have changes in ip counts and should be updated")
            for row in analysis:
                print(f"{row} : {analysis[row]}")

        return

class Web_GUI:

    csv_comparison = Blueprint("csv_comparison", __name__, template_folder='./')
    UPLOAD_FOLDER = "data/uploads/"
    COMPARISON = {}
    COMPARISON_FILE = None
    RESULTS_ANALYSIS = {}

    @csv_comparison.route("/csv_comparison", methods=['GET', 'POST'])
    def Csv_Comparison_Start():

        if (request.method == 'POST'):

            if Web_GUI.COMPARISON_FILE is None:
                return redirect(url_for('csv_comparison.Csv_Comparison_Start'))

            return send_file(f"../{Web_GUI.COMPARISON_FILE}", as_attachment=True)
        else:

            if Web_GUI.COMPARISON_FILE is None:
                return render_template("./csv_comparison_gui.html", Comparison_Table=False, Table_Results=None, Analysis=None)
            
            else:
            
                ## Convert severities to int to allow math
                for row in range(len(Web_GUI.COMPARISON)):
                    Web_GUI.COMPARISON[row][2] = int(Web_GUI.COMPARISON[row][2])

                return render_template("./csv_comparison_gui.html", Comparison_Table=True, Table_Results=Web_GUI.COMPARISON, Analysis=Web_GUI.RESULTS_ANALYSIS)

        
    
    
    @csv_comparison.route("/csv_comparison/compare", methods=['POST'])
    def Csv_Compare():
        
        allowed_extensions = ['csv']

        if (request.method == 'POST'):
            top_file = request.files['top_report']
            breakdown_file = request.files['breakdown_report']

            if top_file is None or breakdown_file is None:
                flash(f"No file provided")
                return redirect(url_for('csv_comparison.Csv_Comparison_Start'))

            if secure_filename(top_file.filename).split('.')[-1] not in allowed_extensions or secure_filename(breakdown_file.filename).split('.')[-1] not in allowed_extensions:
                flash(f"This file extension is not allowed")
                return redirect(url_for('csv_comparison.Csv_Comparison_Start'))

            top_content = top_file.stream.read()
            breakdown_content = breakdown_file.stream.read()
            top_filename = secure_filename(top_file.filename)
            breakdown_filename = secure_filename(breakdown_file.filename)

            with open(Web_GUI.UPLOAD_FOLDER+top_filename, 'wb') as file:
                file.write(top_content)

            with open(Web_GUI.UPLOAD_FOLDER+breakdown_filename, 'wb') as file:
                file.write(breakdown_content)

            compare = CSV_Comparison(Web_GUI.UPLOAD_FOLDER+breakdown_filename, Web_GUI.UPLOAD_FOLDER+top_filename)
            
            Web_GUI.COMPARISON = compare.COMPARISON
            Web_GUI.COMPARISON_FILE = compare.COMPARE_FILE
            Web_GUI.RESULTS_ANALYSIS = CSV_Comparison.Analyse_Results(compare.COMPARISON)

            while True:
                if (compare.RUNNING == False):
                    return redirect(url_for('csv_comparison.Csv_Comparison_Start'))

        return redirect(url_for('csv_comparison.Csv_Comparison_Start'))
