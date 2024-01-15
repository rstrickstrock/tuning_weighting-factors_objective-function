#   main FFLOW control script
#
#   start_doc
#   Script:         main.py
#
#   Author:         Robin Strickstrock
#                   Marco Huelsmann
#
#   Date:           26-10-2023
#
#   Description:    main FFLOW control script
#
#   Usage:          python main.py <configuration_script>
#
#   Arguments:
#
#   Options:
#
#   Output:
#
#   Imported:		os
#                   sys
#                   log
#                   fflow
#
#   Called:
#
#   Modifications:
#   end_doc

###############################################################################
#   required python modules
###############################################################################
import os
import sys
from fflow import Fflow
from utilities.log import Log
from utilities.io import IO
IO = IO()




###############################################################################
#   reading the command line
###############################################################################
#   read arguments of system call
args = sys.argv

#   extract configuration file
config_file = "not_defined"
try:
    config_file = args[1]
except:
    print("ERROR in main: You must indicate a configuration file.")
    print("Optimization aborted.")
    sys.exit(1)

try:
    os.stat(config_file)
except:
    print("ERROR in main: Your indicated configuration file '{}' does not exist.".format(config_file))
    print("Optimization aborted.")
    sys.exit(1)
else:
    config_file = os.path.abspath(config_file)

#   create config file object
try:
    config = IO.read_config_file(config_file)
except:
    print("ERROR in main: could not read config file.")
    print("Optimization aborted.")
    sys.exit(1)

try:
    Log = Log(config)
except:
    print("ERROR in main: Failed to initialize logging (0).")
    print("Optimization aborted.")
    sys.exit(1)

#   start FFLOW in normal/verbose/debug mode
#   initialize logging object based on mode
try:
    verbose = args[2]
except:
    print("################################")
    print("Starting Optimization Workflow #")
    print("################################")
    try:
        Gr = Fflow(config_file, Log)
    except:
        print("ERROR in main: Failed to initialize logging (1).")
        print("Optimization aborted.")
        sys.exit(1)
else:
    if verbose == "-v" or verbose == "--verbose":
        print("################################")
        print("Starting Optimization Workflow #")
        print("################################")
        try:
            Gr = Fflow(config_file, Log, verbose=True)
        except:
            print("ERROR in main: Failed to initialize logging (2).")
            print("Optimization aborted.")
            sys.exit(1)
    elif verbose == "-d" or verbose == "--debug":
        print("################################")
        print("Starting Optimization Workflow #")
        print("################################")
        try:
            Gr = Fflow(config_file, Log, debug=True)
        except:
            print("ERROR in main: Failed to initialize logging (3).")
            print("Optimization aborted.")
            sys.exit(1)
    else:
        print("################################")
        print("Starting Optimization Workflow #")
        print("################################")
        try:
            Gr = Fflow(config_file, Log)
        except:
            print("ERROR in main: Failed to initialize logging (4).")
            print("Optimization aborted.")
            sys.exit(1)
print(f'this is the updated version.')
Gr.run()
