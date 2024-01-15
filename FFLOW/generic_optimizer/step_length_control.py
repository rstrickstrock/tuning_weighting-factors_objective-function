#   Step Length Control
#
#   start_doc
#   Script:         step_length_control.py
#
#   Author:         Marco Huelsmann
#                   Robin Strickstrock
#
#   Date:           18-03-2022
#
#   Description:    class StepLengthControl
#
#   Usage:          by defining an instance
#
#   Arguments:
#
#   Options:
#
#   Output:
#
#   Imported:       math
#
#   Called:
#
#   Modifications:
#   end_doc

###############################################################################
#   required python modules
###############################################################################
from utilities.math import Math


class StepLengthControl:
    def __init__(self, logging_object, verbose, debug, config):
        """ Constructor """
        self.__log = logging_object
        Log = self.__log
        self.__verbose = verbose
        self.__debug = debug
        self.__config = config
        if self.__debug:
            Log.log("\t\tStepLengthControl.__init__(): self.__verbose = {}".format(self.__verbose))
            Log.log("\t\tStepLengthControl.__init__(): self.__debug = {}".format(self.__debug))
            Log.log("\t\tStepLengthControl.__init__(): self.__config = {}".format(self.__config))

        self.__math = Math(Log)

        #   list all available/implemented step length control algorithms
        available_step_length_control_algorithms = ["armijo"]
        #   get sl control method
        try:
            self.__sl_method = self.__config.get("OPT", "sl_method")
        except:
            Log.errorexit("ERROR in StepLengthControl.__init__(): "
                          "No sl_method defined.")
        if self.__debug:
            Log.log("\t\tStepLengthControl.__init__(): self.__sl_method = {}".format(self.__sl_method))

        #   check if sl control method is available
        if self.__sl_method not in available_step_length_control_algorithms:
            Log.errorexit("ERROR in StepLengthControl.__init__(): "
                          "step length control method ({}) not available. "
                          "must be in '{}'.".format(self.__sl_method, available_step_length_control_algorithms))

        #   get number of max iterations for the determination of the step length
        #   check if number of max iterations is an integer
        try:
            self.__sl_max_iterations = int(self.__config.get("OPT", "sl_max_iterations"))
        except ValueError:
            Log.errorexit("ERROR in StepLengthControl.__init__(): "
                          "sl_max_iterations must be an integer.")
        except:
            Log.errorexit("ERROR in StepLengthControl.__init__(): "
                          "No sl_max_iterations defined.")
        if self.__debug:
            Log.log("\t\tStepLengthControl.__init__(): self.__sl_max_iterations = {}".format(self.__sl_max_iterations))

        self.__initial_step_length = None  # initialize variable
        self.__sl_current_iterations = 0
        if self.__debug:
            Log.log("\t\tStepLengthControl.__init__(): self.__initial_step_length = {}"
                    "".format(self.__initial_step_length))
            Log.log("\t\tStepLengthControl.__init__(): self.__sl_current_iterations = {}"
                    "".format(self.__sl_current_iterations))

    def get_sl_method(self):
        """ return step length method """
        Log = self.__log
        try:
            return self.__sl_method
        except:
            Log.errorexit("ERROR in StepLengthControl.get_sl_method(): "
                          "could not get step length method.")

    def get_sl_max_iterations(self):
        """ return max number of step length control iterations """
        Log = self.__log
        try:
            return self.__sl_max_iterations
        except:
            Log.errorexit("ERROR in StepLengthControl.get_sl_max_iterations(): "
                          "could not get number of max step length iterations.")

    def get_current_sl_iteration(self):
        """ return number of step length iterations """
        Log = self.__log
        try:
            return self.__sl_current_iterations
        except:
            Log.errorexit("ERROR in StepLengthControl.get_current_iteration(): "
                          "could not get number of current step length iterations.")

    def get_step_length(self):
        """ get the current step length """
        Log = self.__log
        try:
            return self.__step_length
        except:
            Log.errorexit("ERROR in StepLengthControl.get_step_length(): "
                          "could not get step length.")

    def set_step_length(self, step_length):
        """ set current step length to a user defined value """
        Log = self.__log
        try:
            self.__step_length = float(step_length)
        except ValueError:
            Log.errorexit("ERROR in StepLengthControl.set_step_length(): "
                          "step length ({}) must be a float.".format(step_length))
        except:
            Log.errorexit("ERROR in StepLengthControl.set_step_length(): "
                          "could not set step length.")
        if self.__debug:
            Log.log("\t\tStepLengthControl.set_step_length(): self.__step_length = {}".format(self.__step_length))

    def is_step_length_feasible(self, min_parameters, max_parameters, current_parameter_set, descent, step_length):
        """ checks if step length is feasible x: lower bound <= ||x + sl * descent|| <= upper bound
        and returns updated parameter set """
        Log = self.__log
        math = self.__math
        step = None  # initialize variable
        try:
            step = math.scalar_vector_mult(step_length, descent)
        except:
            Log.errorexit("ERROR in StepLengthControl.is_step_length_feasible: "
                          "could not calculate 'step = math.scalar_vector_mult(step_length, descent)'.")
        if self.__debug:
            Log.log("\t\tStepLengthControl.is_step_length_feasible(): step = {}".format(step))

        if not len(current_parameter_set) == len(step):
            Log.errorexit("ERROR in StepLengthControl.is_step_length_feasible: "
                          "step ('{}') and current_parameter_set ('{}') must contain same number of elements."
                          "".format(step, current_parameter_set))

        new_parameter_set = []
        for i in range(len(step)):
            new_parameter = None  # initialize variable
            try:
                new_parameter = float(current_parameter_set[i]) + float(step[i])
            except:
                Log.log("ERROR in StepLengthControl.is_step_length_feasible: "
                        "Failed to calculate float(current_parameter_set[i]) + float(step[i]): "
                        "float({}) + float({})".format(current_parameter_set[i], step[i]))
            if self.__debug:
                Log.log("\t\t\tStepLengthControl.is_step_length_feasible(): new_parameter = {}".format(new_parameter))

            # check if parameter is feasible, returns false if not
            if float(new_parameter) > float(max_parameters[i]):
                Log.log("\t\t\tStepLengthControl.is_step_length_feasible(): parameters  out of boundaries: too large")
                return False
            if float(new_parameter) < float(min_parameters[i]):
                Log.log("\t\t\tStepLengthControl.is_step_length_feasible(): parameters  out of boundaries: too small")
                return False

            new_parameter_set.append(new_parameter)

        if self.__debug:
            Log.log("\t\tStepLengthControl.is_step_length_feasible(): new_parameter_set = {}".format(new_parameter_set))
        return new_parameter_set

    def __del__(self):
        """ Destructor """
        del self
