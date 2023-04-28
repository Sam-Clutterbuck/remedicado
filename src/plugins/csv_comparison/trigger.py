#########################################################
# Plugin : csv_comparison
# Created by: @Sam-Clutterbuck
# Version: 0.0.1
# Last Updated: 27/04/2023
#
#
# Usage:
# This plugin takes a source breakdown csv and compares it with a top xxxx csv from a source.
#########################################################
from os.path import isfile

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

        return

