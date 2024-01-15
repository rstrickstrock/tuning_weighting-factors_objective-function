#   main FFLOW class script
#
#   start_doc
#   Script:         Fflow.py
#
#   Author:         Robin Strickstrock
#                   Marco Huelsmann
#
#   Date:           26-10-2023
#
#   Description:    main FFLOW class script
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
#                   sys
#                   loss_function
#                   armijo_step_length_control
#                   steepest_descent
#
#   Called:		    all required subscripts
#
#   Modifications:
#   end_doc
###############################################################################
#   required python modules
###############################################################################
import os
from simulation_interface.loss_function import LossFunction
from simulation_interface.force_field_constraints import ForceFieldConstraints
from generic_optimizer.armijo_step_length_control import ArmijoStepLengthControl
from utilities.io import IO
from generic_optimizer.steepest_descent import SteepestDescent
IO = IO()

class Fflow:

    def __init__(self, config_file, logging_object, verbose=False, debug=False):
        """ Constructor """
        ############################################
        #   logging
        ############################################
        self.__log = logging_object
        Log = self.__log

        ############################################
        #   verbose or debug mode
        ############################################
        self.__verbose = verbose
        Log.log("Verbose =  {} #".format(self.__verbose))

        self.__debug = debug
        Log.log("Debug =  {} #".format(self.__debug))

        ############################################
        #   print title
        ############################################
        # self.__print_title()

        ############################################
        #   set config file
        ############################################
        self.__config_file = config_file
        Log.log("Config File = {} #".format(self.__config_file))
        if self.__debug:
            Log.log("Fflow.__init__(): self.__config_file = {}".format(self.__config_file))

        ############################################
        #   set current working directory basedir
        ############################################
        self.__current_working_directory_basedir = os.path.dirname(self.__config_file)
        Log.log("current working directory = {} #\n".format(self.__current_working_directory_basedir))
        if self.__debug:
            Log.log("Fflow.__init__(): current working directory basedir = "
                    "{}".format(self.__current_working_directory_basedir))

        ############################################
        #   initialize variables
        ############################################
        self.__working_directories = []
        self.__initial_guess = None
        self.__dimension = None
        self.__min_ffparameter_values = None
        self.__max_ffparameter_values = None
        if self.__debug:
            Log.log("Fflow.__init__(): self.__working_directories = {}".format(self.__working_directories))
            Log.log("Fflow.__init__(): self.__initial_guess = {}".format(self.__initial_guess))
            Log.log("Fflow.__init__(): self.__dimension = {}".format(self.__dimension))
            Log.log("Fflow.__init__(): self.__min_ffparameter_values = {}".format(self.__min_ffparameter_values))
            Log.log("Fflow.__init__(): self.__max_ffparameter_values = {}".format(self.__max_ffparameter_values))

    def run(self):
        Log = self.__log
        Log.log("######################")
        Log.log("Starting optimization#\n\n")
        ############################################
        #   reading configuration file
        ############################################
        config = None  # initialize variable
        try:
            config = IO.read_config_file(self.__config_file)
        except:
            Log.errorexit("ERROR in Fflow.run(): could not read config file.")
        if self.__debug:
            Log.log("Fflow.run(): config = {}".format(config))

        ############################################
        #   get objective function
        ############################################
        objective_function = None  # initialize variable
        try:
            objective_function = config.get("OPT", "objective_function")
        except:
            Log.errorexit("ERROR in Fflow.run(): No objective function indicated.")
        if self.__verbose or self.__debug:
            Log.log("Fflow.run(): objective_function = {}".format(objective_function))

        if objective_function not in ["Physical_Properties_Loss", "QM_MM_Loss", "PhysProp_QMMM_Loss"]:
            Log.errorexit("ERROR in Fflow.run(): Invalid objective function: {}".format(objective_function))

        ############################################
        #   create working dir(s) for optimization
        ############################################
        if objective_function == "PhysProp_QMMM_Loss":
            working_directory = os.path.join(self.__current_working_directory_basedir, "PhysProp")
            try:
                os.stat(working_directory)
            except:
                os.mkdir(working_directory)
                self.__working_directories.append(working_directory)
                if self.__verbose or self.__debug:
                    Log.log("Fflow.run(): added working directory: {}".format(working_directory))
            else:
                Log.errorexit("CRITICAL WARNING: current working directory '{}' already exists. "
                              "To prevent data loss optimization will exit.".format(working_directory))

            working_directory = os.path.join(self.__current_working_directory_basedir, "QMMM")
            try:
                os.stat(working_directory)
            except:
                os.mkdir(working_directory)
                self.__working_directories.append(working_directory)
                if self.__verbose or self.__debug:
                    Log.log("Fflow.run(): added working directory: {}".format(working_directory))
            else:
                Log.errorexit("CRITICAL WARNING: current working directory '{}' already exists. "
                              "To prevent data loss optimization will exit.".format(working_directory))
        else:
            working_directory = os.path.join(self.__current_working_directory_basedir, "SimulationData")
            try:
                os.stat(working_directory)
            except:
                os.mkdir(working_directory)
                self.__working_directories.append(working_directory)
                if self.__verbose or self.__debug:
                    Log.log("Fflow.run(): added working directory: {}".format(working_directory))
            else:
                Log.errorexit("CRITICAL WARNING: current working directory '{}' already exists. "
                              "To prevent data loss optimization will exit.".format(working_directory))
        if self.__verbose or self.__debug:
            Log.log("Fflow.run(): self.__working_directories = {}".format(self.__working_directories))

        ############################################
        #   initial guess // parameter file
        ############################################
        #   get parameter file
        parameter_file = None  # initialize variable
        try:
            parameter_file = config.get("OPT", "parameter_file")
        except:
            Log.errorexit("ERROR in Fflow.run(): "
                          "No parameter file specified in {}".format(self.__config_file))
        else:
            parameter_file = os.path.join(self.__current_working_directory_basedir, parameter_file)
        if self.__verbose or self.__debug:
            Log.log("Fflow.run(): parameter_file = {}".format(parameter_file))
        try:
            os.stat(parameter_file)
        except:
            Log.errorexit("ERROR in Fflow.run(): "
                          "Parameter file '{}' does not exist. "
                          "Make sure to have the parameter file in the current working directory"
                          " '{}'.".format(parameter_file, self.__current_working_directory_basedir))
        if self.__verbose or self.__debug:
            Log.log("Fflow.run(): parameter file = {}".format(parameter_file))

        #   read initial guess from parameter file
        try:
            self.__initial_guess = IO.read_last_parameter(parameter_file)
        except:
            Log.errorexit("ERROR in Fflow.run(): "
                          "Could not read last parameters from file '{}'".format(parameter_file))
        if self.__verbose or self.__debug:
            Log.log("Fflow.run(): initial guess = {}".format(self.__initial_guess))

        # get optimization dimension
        try:
            self.__dimension = len(self.__initial_guess)
        except:
            Log.errorexit("ERROR in Fflow.run(): "
                          "could not get dimension from initial guess: '{}'".format(self.__initial_guess))
        if self.__debug:
            Log.log("Fflow.run(): dimension = {}".format(self.__dimension))

        ############################################
        #   initialize objective function (i.e. loss-function)
        ############################################
        if objective_function != "PhysProp_QMMM_Loss":
            Log.errorexit("Error in Fflow.run(): "
                          "Currently, 'objective_function' must be 'PhysProp_QMMM_Loss'.")

        loss_function = None  # initialize variable

        try:
            loss_function = LossFunction(Log, self.__verbose, self.__debug, self.__dimension, objective_function,
                                         self.__current_working_directory_basedir, config)
        except:
            Log.errorexit("ERROR in Fflow.run(): "
                          "Could not initialize loss_function.")
        if self.__debug:
            Log.log("Fflow.run(): loss_function = {}".format(loss_function))
        if self.__verbose:
            Log.log("Fflow.run(): LossFunction initialized.")

        ############################################
        #   initialize constraints
        ############################################
        constraints_type = None  # initialize variable
        constraints = None  # initialize variable
        try:
            constraints_type = config.get("OPT", "constraints")
        except:
            Log.errorexit("ERROR in Fflow.run(): "
                          "Could not initialize constraints.")
        if self.__debug:
            Log.log("Fflow.run(): constraints_type = {}".format(constraints_type))

        if constraints_type == "Force_Field_Constraints":
            try:
                constraints = ForceFieldConstraints(Log, self.__verbose, self.__debug, self.__initial_guess, config)
            except:
                Log.errorexit("ERROR in Fflow.run(): "
                              "Could not initialize constraints.")
        else:
            #   currently, only Force Field Constraints implemented / possible
            Log.errorexit("ERROR in Fflow.run(): "
                          "Option 'constraints' in 'OPT' must be set to 'Force_Field_Constraints' "
                          "(currently, only this type of constraints is available).")
        if self.__debug:
            Log.log("Fflow.run(): constraints = {}".format(constraints))
        if self.__verbose:
            Log.log("Fflow.run(): ForceFieldConstraints initialized.")

        # TODO: check if those values are needed here
        min_max_values = constraints.get_boundary()
        self.__min_ffparameter_values = min_max_values[0]
        self.__max_ffparameter_values = min_max_values[1]
        if self.__debug:
            Log.log("Fflow.run(): min_max_values = {}".format(min_max_values))
            Log.log("Fflow.run(): self.__min_ffparameter_values = {}".format(self.__min_ffparameter_values))
            Log.log("Fflow.run(): self.__max_ffparameter_values = {}".format(self.__max_ffparameter_values))

        ############################################
        #   Optimization Problem // still necessary?
        ############################################

        ############################################
        #   Optimization Algorithm
        ############################################
        algorithm_type = None  # initialize variable
        try:
            algorithm_type = config.get("OPT", "algorithm")
        except:
            Log.errorexit("ERROR in Fflow.run(): "
                          "Could not read 'algorithm' from section 'OPT'")
        if self.__debug:
            Log.log("Fflow.run(): algorithm_type = {}".format(algorithm_type))

        #   initialize object for step length control
        step_length_control = None  # initialize variable
        try:
            step_length_control = ArmijoStepLengthControl(Log, self.__verbose, self.__debug, loss_function, config)
        except:
            Log.errorexit("ERROR in Fflow.run(): "
                          "could not initialize step length control.")
        if self.__debug:
            Log.log("Fflow.run(): step_length_control = {}".format(step_length_control))
        if self.__verbose:
            Log.log("Fflow.run(): ArmijoStepLengthControl initialized-")

        optimization_object = None  # initialize variable
        if algorithm_type == "steepest_descent":
            try:
                optimization_object = SteepestDescent(Log, self.__verbose, self.__debug, loss_function, constraints,
                                                      step_length_control, config)
            except:
                Log.errorexit("Error in Fflow.run(): "
                              "could not initialize optimization object.")
        else:
            Log.errorexit("Error in Fflow.run(): "
                          "Currently, algorithm_type must be 'steepest_descent'.")
        if self.__debug:
            Log.log("Fflow.run(): optimization_object = {}".format(optimization_object))
        if self.__verbose:
            Log.log("Fflow.run(): SteepestDescent initialized.")

        is_finished = None  # initialize variable
        try:
            is_finished = optimization_object.execute_optimization()
        except:
            Log.errorexit("Error in Fflow.run(): "
                          "could not perform optimization_object.execute_optimization().")
        if self.__debug:
            Log.log("Fflow.run(): is_finished = {}".format(is_finished))

        if is_finished:
            print("NIIIIIIIICE!!!")
        else:
            Log.errorexit("ERROR in Fflow.py: Is finished is not 'True' :(")

    def __print_title(self):
        ###############################################################################
        #   Title
        ###############################################################################
        print("")
        print(" ================================================== ")
        print(" || GROW V. 2.0 - The modern way of optimization || ")
        print(" ================================================== ")
        print("")
        print(" Author/Concept:        Marco Huelsmann ")
        print(" Additional Authors:    Andreas Kraemer")
        print("                        Astrid Maass")
        print("                        Janina Hemmersbach")
        print("                        Doron Dominic Heinrich")
        print("                        Markus Huber")
        print("                        Karl N. Kirschner")
        print("                        Sonja Kopp")
        print("                        Ottmar Kraemer-Fuhrmann")
        print("                        Thomas J. Mueller")
        print("                        Thorsten Koeddermann")
        print("                        Robin Strickstrock")
        print("                        Andre Tissen")
        print("")
        print(" When using GROW, please reference: ")
        print("   M. Huelsmann, T. Koeddermann, J. Vrabec, D. Reith ")
        print("   GROW: A Gradient-based Optimization Workflow for the Automated ")
        print("   Development of Molecular Models")
        print("   Computer Physics Communications 181 (2010), 499-513 ")
        print("")

    def get_working_directories(self):
        """ return list of working directories """
        return self.__working_directories

    def __del__(self):
        """ Destructor """
        del self
