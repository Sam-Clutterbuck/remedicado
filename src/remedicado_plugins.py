import hashlib
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

discovered_plugins = [
    name
    for finder, name, ispkg
    in iter_namespace(src.plugins)
]


for name in discovered_plugins:
    for plugin in validated_plugins:

        filename = f"{name.split('.')[-1]}.py"
        if (filename == plugin):
            ## check the hash of file
            with open(f'src/plugins/{filename}', 'rb') as file:
                content = file.read()

            hash = hashlib.sha256()
            hash.update(content)
            sha_hash = hash.hexdigest()

            if (sha_hash == validated_plugins[plugin]):
                ##
                #LOAD PLUGIN
                print(f"Loading Plugin {plugin}")
                reference = importlib.import_module(name)
                plugin_class = getattr(reference, reference.class_name)
                installed_plugins.update({name: plugin_class})

                continue

            print(f"Hashes don't match for {file}")

        