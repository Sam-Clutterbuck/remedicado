import hashlib
from os import walk
from os.path import isdir
from yaml import safe_load, YAMLError

import importlib
import pkgutil


import src.plugins


with open('data/valid_plugins.yaml') as file:
    try:
        validated_plugins = safe_load(file)
    except YAMLError as error:
        quit()
        
installed_plugins = {}

if not isdir('src/plugins/'):
    print("Missing Plugin Folder 'src/plugins/'")
    quit()

def iter_namespace(ns_pkg):
    # Specifying the second argument (prefix) to iter_modules makes the
    # returned name an absolute name instead of a relative one. This allows
    # import_module to work without having to do additional modification to
    # the name.
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")

def Hash_File_Confirmation(Plugin_Filename, File_Hashes):

    ## Get list of all files in plugin
    plugin_files = []
    for (dirpath, dirnames, filenames) in walk(f'src/plugins/{Plugin_Filename}/'):
        ## Ignore any __pycache__
        if (str(dirpath).split('/')[-1] == "__pycache__"):
            continue

        ## add nested dirs onto the name
        if (str(dirpath) == f'src/plugins/{Plugin_Filename}/'):
            plugin_files.extend(filenames)
        else:
            temp = []
            for name in filenames:
                temp.append(f"{str(dirpath).split('/')[-1]}/{name}")
            plugin_files.extend(temp)

    ## Check that all files found are referenced in the plugin_hashes.yaml file
    for found_file in plugin_files:
        valid = False
        for file in File_Hashes:
            if (str(found_file) == 'plugin_hashes.yaml'):
                valid = True
            if (str(file) == str(found_file)):
                valid = True
        if not valid:
            return False
        
    return True

def Detailed_Hash_Checks(Plugin_Filename):

    ## Get plugin hashes list
    with open(f'src/plugins/{Plugin_Filename}/plugin_hashes.yaml') as file:
        try:
            file_hashes = safe_load(file)
        except YAMLError as error:
            quit()

    if file_hashes is None or (file_hashes == {}):
        return False
    
    if not Hash_File_Confirmation(Plugin_Filename, file_hashes):
        return False

    ## Check the hashes in hash list are correct
    for file in file_hashes:
        with open(f'src/plugins/{Plugin_Filename}/{file}', 'rb') as file_to_hash:
            content = file_to_hash.read()

        if (type(content) != bytes):
            content = content.encode()
        
        sha_hash = hashlib.sha256(content).hexdigest()
        
        if (sha_hash.lower() != file_hashes[file].lower()):
            return False

    return True

def Import_Check(Discovered_Plugins):
    for name in Discovered_Plugins:
        for plugin in validated_plugins:

            try:

                filename = f"{name.split('.')[-1]}"
                if (filename == plugin):
                    ## check the hash of file
                    with open(f'src/plugins/{filename}/plugin_hashes.yaml', 'rb') as file:
                        content = file.read()

                    if (type(content) != bytes):
                        content = content.encode()
                
                    sha_hash = hashlib.sha256(content).hexdigest()


                    if (sha_hash.lower() == validated_plugins[plugin].lower()):
                    
                        ## Check hashes
                        if Detailed_Hash_Checks(filename):
                            ## LOAD PLUGIN
                            print(f"Loading Plugin {plugin}")

                            reference = importlib.import_module(name)
                            plugin_trigger = getattr(reference, 'Trigger')
                            installed_plugins.update({name: plugin_trigger})


                            
                        continue

            
            except:
                continue

        
        

discovered_plugins = [
    name
    for finder, name, ispkg
    in iter_namespace(src.plugins)
]

Import_Check(discovered_plugins)

