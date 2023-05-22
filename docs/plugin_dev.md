# Plugin Development
If you want to create a plugin to be used by Remedicado there are a few formats and rules that need to be followed.  ***(examples used from csv_comparison plugin)***

# Modular format:
The plugin structure is set up in a modular format as such each plugin is contained in its own directory placed within the src/plugins directory of Remedicado in order for them to be read and used.

Each plugin must contain 3 specific files named exactly as shown to run properly and be recognised as a plugin, those are:
* `__init__.py` - This is the standard init file for a python module and must include the at least one reference to the **Trigger class** `from src.plugins.<plugin name>.trigger import Trigger`
* `trigger.py`- This is the trigger file that is called by the use to interface with the plugin. You could have all your plugin code here or import other helper files from the plugin directory
* `plugin_hashes.yaml` - This file contains a dictionary of all the hashes of helper files in order to confirm integrity of the plugin

## Trigger file format:
### Opener
In order to make it obvious what your plugin does and how up to date it is there should be a small blurb at the top of the script with the following details :
```
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
```
This example shows the key information that should be included however any extra info or points can be mentioned if you require it.
### Class structure
In order for plugins to be ingested properly it has to follow a specific class structure : 
```
from flask import Blueprint, render_template

class Trigger:
    
    def Call():
		# This is the code run on interfacing with user
        print("Move control to this script")
        return

class Web_GUI:

    <plugin name> = Blueprint("<plugin name>", __name__, template_folder='./')

    @plugin.route("/<plugin name>")
    def <plugin name>_Start():

        return render_template("./template_gui.html")
	
```
The class **must be named exactly `Trigger`** and **must contain one function named exactly `Call()`**, It must also have a second class **named exactly `Web_GUI`** and **must contain one function named `<plugin name>_Start()` with a route to `("/<plugin name>")`**

This allows the Trigger class to be accessed by the user as the user is able to call the `Trigger.Call()` function. As such any code in this function will be run when called. If your plugin only has one task you can trigger it here; Otherwise if it is made up of mutliple inputs or tasks you can create a looping interface simular to the cli file to allow user to control what the plugin does

If required you can also import any of the helper files to this file to allow them to interact.

The Web_GUI class naturally should only be listed if your plugin allows access through web GUI and uses the \<plugin name>_Start function to move control over to the plugin to navigate plugin pages.

## plugin_hashes.yaml
The `plugin_hashes.yaml` file is core for confirming the integrity of a plugin.

This file should contain key : value pairs for every file within the plugin with the **key** being the `filename.ext` and the **value** being the coresponding `SHA256 Hash` of the file. For example:

```
__init__.py : 0E49FDBE7B8EEB4EAD0619A4D2B1EDFA87FFD0850647711F34F5D96C9078F4DB
trigger.py : A7F84A221C823F87D3CA20B3D8F11400D3297EF738B6642674A8621CBF3DB41E
template_gui.html : 1FC9CC7D7475AD2035EFD29AC6F7F5F0CFFAD2FA9AA386FEDCF687303656A533
```

This allows the Remedicado plugin system to parse through all of the listed files and ensure they match the hashes listed in the `plugin_hashes.yaml` file.

***Note: if your plugin has nested folders enter the name as <foldername/filename.ext>***

# valid_plugins.yaml
Simularly to the `plugin_hashes.yaml` file within the plugin, Remedicado itself holds a list of valid plugins that are allowed to be downloaded into the system.

A plugin will not be loaded unless it is found in this `valid_plugins.yaml` file so needs to be updated to authenticate the plugin. This is done by adding the name of the plugin (this is the name of the dir that the plugin is housed in) alongside the `sha256 hash` of the plugins `plugin_hashes.yaml` file. This allows the system to confirm the integrity and validity of the `plugin_hashes.yaml` file first before trusting any of the hashes it provides. Again it is important to ensure the file name is exactly correct and that the hash matches otherwise it will not run.
```
template : DC46E93E22F8E0FE3A0826E8E396D89FDA527AE71976D7BCA76866F0819BCF3A
```
