#   class Log
#
#   start_doc
#   Script:         log.py
#
#   Author:         Marco Huelsmann
#                   Robin Strickstrock
#
#   Date:           15-03-2022
#
#   Description:    error handling functionality, logging
#
#   Usage:          by defining an instance
#
#   Arguments:
#
#   Options:
#
#   Output:
#
#   Imported:		sys
#                   os
#                   subprocess
#
#   Called:
#
#   Modifications:
#   end_doc

# ***********************************************************************
# required python modules
# ***********************************************************************
import sys
import os
import subprocess


# ***********************************************************************
# class Log
# ***********************************************************************

class Log:

    def __init__(self, config):
        """ Constructor """
        self.__config = config
        print(f'Log.__init__(): self.__config set.')

        # get current working directory
        self.__cwd = None  # initialize variable
        try:
            self.__cwd = self.__config.get("SYS", "cwd")
        except:
            print(f'ERROR in Log.__init__(): Could not get \"cwd\" from config file in section [SYS]')
            print(f'Optimization aborted.')
            sys.exit(1)
        print(f'Log.__init__(): self.__cwd set to {self.__cwd}.')

        # get name for logging file
        self.__log_file = None  # initialize variable
        try:
            self.__log_file = self.__config.get("SYS", "logfile")
        except:
            print(f'ERROR in Log.__init__(): Could not get \"logfile\" from config file in section [SYS]')
            print(f'Optimization aborted.')
            sys.exit(1)
        try:
            self.__log_file = str(self.__log_file)
        except:
            print(f'ERROR in Log.__init__(): Could not cast logfile ({self.__log_file}) to string.')
            print(f'Optimization aborted.')
            sys.exit(1)
        print(f'Log.__init__(): self.__log_file set to {self.__log_file}')

        # check if file extension is set and get logfile's basename
        logfile_extension = ".log"
        logfile_basename = None  # initialize variable
        if self.__log_file.endswith(".log"):
            # already ends with '.log', cut '.log' to get basename
            logfile_basename = self.__log_file[:-4]
        else:
            # does not end with '.log', just the basename given
            logfile_basename = self.__log_file

        try:
            logfile_basename = str(logfile_basename)
        except:
            print(f'ERROR in Log.__init__(): Could not cast logfile_basename ({logfile_basename}) to string.')
            print(f'Optimization aborted.')
            sys.exit(1)

        # check if logging file exists and create not existing logging file
        iteration = 0
        while True:
            if iteration == 0:
                self.__log_file = os.path.join(self.__cwd, logfile_basename + logfile_extension)
            else:
                self.__log_file = os.path.join(self.__cwd, logfile_basename + "_" + str(iteration) + logfile_extension)
            print(f'Log.__init__(): self.__log_file set to {self.__log_file}')

            if os.path.isfile(self.__log_file):
                iteration = iteration + 1
            else:
                f = open(self.__log_file, 'w')
                f.write(f'##################################\n')
                f.write(f'# Starting Optimization Workflow #\n')
                f.write(f'##################################\n')
                f.close()
                break

    def errorexit(self, errmsg="Severe error.", tool=False):
        """ gives out general error message in case of severe error """
        f = open(self.__log_file, 'a')
        if not tool:
            f.write(f'\n\n{errmsg}\n\n')
            f.write(f'Optimization aborted #.\n\n')

            print(f'\n\n{errmsg}\n\n')
            print(f'Optimization aborted.\n\n')
        else:
            f.write(f'\n\nSimulation tool error, aborting #\n\n')
            print(f'Simulation tool error, aborting')
        f.close()

        if not tool:
            del self

        sys.exit(1)

    def log(self, msg="empty"):
        """ writes msg to logfile """
        # if msg ends with '\n' do not break line, otherwise do
        try:
            msg = str(msg)
        except:
            self.errorexit(f'ERROR in Log.log() - logging message ({msg}) can not be cast to string')
        if msg.endswith('\n'):
            break_line = False
        else:
            break_line = True

        f = open(self.__log_file, 'a')
        f.write(msg)
        if break_line:
            f.write(f'\n')
        f.close()
        print(f'{msg}')

    def __del__(self):
        """ Destructor """
        del self
