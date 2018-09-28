import glob
import argparse
import os
import importlib
import shutil

import sys
# Make it possible to print strings coming from SQL database without encoding errors...
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

def extend_parser_with_plugins( prefix ):
    plugins = dict()
    # get available inputs
    for file in glob.glob(prefix + "*.py"):
        modulename = os.path.splitext(os.path.basename( file ))[0]
        pluginname = modulename[len(prefix):]
    
        mod = importlib.import_module(modulename)
        mod.addArguments( parser )

        plugins[pluginname] = mod
    return plugins

parser = argparse.ArgumentParser(description="Bug tracker import/export tool.")

possible_imports = extend_parser_with_plugins( "loadplugin_" )
possible_exports = extend_parser_with_plugins( "saveplugin_" )    

parser.add_argument("--load_plugin", type=str, required=True, choices=possible_imports, help="Plugin to be used to load list of bugs")
# Make saver optional so that we can easily test a loader without bothering about the saver
parser.add_argument("--save_plugin", type=str, required=False, choices=possible_exports, help="Plugin to be used to save list of bugs")
parser.add_argument("-v", "--verbose", dest='verbose', action='store_true', help="Verbose mode")
parser.set_defaults(verbose=False)
parser.add_argument("--dry", dest='dry', action='store_true', help="Do everything but creating artifacts (for testing without impacting target system)")
parser.set_defaults(dry=False)

args = parser.parse_args()

importModule = possible_imports[args.load_plugin]
exportModule = possible_exports[args.save_plugin] if args.save_plugin != None else None

if not importModule.checkArguments( args ):
    exit(1)

if exportModule != None and not exportModule.checkArguments( args ):
    exit(1)

all_bugs = importModule.loadBugs( args )

if len(all_bugs) == 0:
    print( "No bug to convert" )
    exit(1)

if exportModule != None:
    choiceStr = "\nReady to import: " + str(len(all_bugs)) + " bug(s)?\n"
    choiceStr += "y: Yes " + ("(dry)" if args.dry else "") + "\n"
    choiceStr += "v: View bugs\n"
    choiceStr += "Any thing else: cancel operation\n"
        
    while ( True ):
        choice = input(choiceStr)
        if choice == "v":
            for bug in all_bugs:
                print(str(bug))
            continue

        if choice == "y":
            if exportModule.saveBugs( args, all_bugs ):
                print( "All " + str(len(all_bugs)) + " bug(s) were successfully imported")
            else:
                print( "Bugs were not imported")
    
        break
else:
    for bug in all_bugs:
        print(str(bug))
