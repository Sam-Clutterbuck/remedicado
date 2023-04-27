# Plugin Development
If you want to create a plugin to be used by Remedicado there are a few formats and rules that need to be followed.  ***(examples used from csv_comparison plugin)***
## Python file format:
### Opener
In order to make it obvious what your plugin does and how up to date it is there should be a small blurb at the top of the script with the following details :
```
#########################################################
# Plugin : CSV_Comparison
# Created by: @Sam-Clutterbuck
# Version: 0.0.1
# Last Updated: 27/04/2023
#
#
# Usage:
# This plugin takes a source breakdown csv and compares it with a top xxxx csv from a source.
#########################################################
```
This example shows the key information that should be included however any extra info or points can be mentioned if you require it.
### Class structure
In order for plugins to be ingested properly it has to follow a specific class structure : 
```
class_name = "CSV_Comparison"

class  CSV_Comparison:

	def  List_Options():
		# Option Func Name : arguments
		options = {'init':
		{'breakdown file location' : str,
		'Top Vuln file location' : str},
		}

		return  options
		
```
The class can have any suitable name however code needs to be contained within that class in order to be called by the user.

 - The `class_name` declaration needs to be made outside of the class and be named exactly as shown. This should be a string with the exact name of the class. This string is polled by the plugin system to determine what class needs to be run
 - The `List_Options()` function needs to be created and named exactly as shown in order to be found and passed to the user so they know what they can trigger.  The list options function should return a dictionary containing pairs of:
	 - `Command Names` - The exact name of the function that needs to be called
	 - `arguments` - This is a sub dictionary of the required arguments containing a prompt on what needs to be passed and the type that it needs to be
 - **Note: __init__ functions should be declared as just 'init' exactly in order to call the class**

### Plugin location
The plugins need to be installed in the src/plugins section of Remedicado in order for them to be read and used.

## valid_plugins.yaml
The final element is that the valid_plugins.yaml file needs to be updated to authenticate the plugin. This is done by adding the name of the file alongside its sha256 hash to the yaml file. Again it is important to ensure the file name is exactly correct and that the hash matches otherwise it will not run.
```
csv_comparison.py : dbbc6be60c8db57d38077a063d4d04c5cb5710e0ce701eec6caf12c9625b11c5
```
