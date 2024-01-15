#   class IO
#
#   start_doc
#   Script:		    io.py
#
#   Author:         Marco Huelsmann
#                   Robin Strickstrock
#
#   Date:           15-03-2022
#
#   Description:    file I/O functionality
#
#   Usage:          by defining an instance
#
#   Arguments:
#
#   Options:
#
#   Output:
#
#   Imported:		os
#                   ConfigParser
#                   sys
#
#   Calling:
#
#   Modifications:
#   end_doc

# ***********************************************************************
# required python modules
# ***********************************************************************
import os
import sys


class IO:

    def __init__(self):
        """ Constructor """
        self.__io_obj = None

    def read_config_file(self, config_file):
        """ reads configuration file "config_file" and returns a config object """
        try:
            from lib.configparser import ConfigParser
        except:
            print("ERROR in IO.read_config_file(): Required Python module 'ConfigParser' not available.")
            print("Optimization aborted.")
            sys.exit(1)

        config = ConfigParser()

        f_ptr = open(config_file)

        config.read_file(f_ptr)
        f_ptr.close()

        return config

    def read_last_parameter(self, filename):
        """ reads the last parameter from a file """
        x = os.popen("tail -1 {}".format(filename)).readlines()
        x = x[0].split(" ")
        parameters = []
        for par in x:
            try:
                parameters.append(float(par))
            except:
                print("ERROR in IO.read_last_parameter(): "
                      "Parameter value '{}' could not be converted to float "
                      "and appended to the parameter string.".format(par))
                print("Optimization aborted.")
                sys.exit(1)

        return parameters

    def get_properties(self, properties_file):
        """ reads properties from a file """
        properties = []

        f = open(properties_file, "r")
        props = f.readlines()
        f.close()

        for prop in props:
            prop = prop.split(" ")
            #print("prop: {}".format(prop))
            for p in prop:
                if len(p) < 1:
                    #   p is probably ''
                    #   go to next element in prop
                    pass
                else:
                    try:
                        p = float(p)
                    except ValueError:
                        #   p is not a float
                        #   go to next element
                        pass
                    else:
                        #   p is a float
                        #   get this float value as property value
                        properties.append(p)

        if len(properties) < 1:
            #   there should be at least one property element
            print("ERROR in IO.get_properties(): "
                  "list of read properties from property file '{}' is empty.".format(properties_file))
            print("Optimization aborted.")
            sys.exit(1)

        return properties

    def __del__(self):
        """ Destructor """
        del self
