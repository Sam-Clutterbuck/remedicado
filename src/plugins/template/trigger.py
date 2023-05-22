#########################################################
# Plugin : template
# Created by: @Sam-Clutterbuck
# Version: 0.0.1
# Last Updated: 27/04/2023
#
#
# Usage:
# This shows the default plugin layout
#########################################################
from flask import Blueprint, render_template

class Trigger:
    
    def Call():
        print("Move control to this script")
        return

    def Trigger_GUI():

        return Web_GUI

class Web_GUI:

    template = Blueprint("template", __name__, template_folder='./')

    @template.route("/template")
    def GUI_Start():
        print("HERE I AM")

        return render_template("./template_gui.html")
