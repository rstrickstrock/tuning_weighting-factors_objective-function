#   Steepest Descent
#
#   start_doc
#   Script:         steepest_descent.py
#
#   Author:         Marco Huelsmann
#                   Robin Strickstrock
#
#   Date:           17-05-2022
#
#   Description:    class SteepestDescent
#
#   Usage:          by defining an instance
#
#   Arguments:
#
#   Options:
#
#   Output:
#
#   Imported:       optimization_algorithm
#                   os
#                   sys
#                   math
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
from generic_optimizer.optimization_algorithm import OptimizationAlgorithm
from utilities.math import Math

class SteepestDescent(OptimizationAlgorithm):

    def __init__(self, logging_object, verbose, debug, loss_function, constraints, step_length_control, config):
        """ Constructor """
        self.__log = logging_object
        Log = self.__log

        self.__math = Math(Log)

        self.__verbose = verbose
        self.__debug = debug
        self.__loss_function = loss_function
        self.__constraints = constraints
        self.__step_length_control = step_length_control
        self.__config = config
        if self.__debug:
            Log.log("\tSteepestDescent.__init__(): self.__verbose = {}".format(self.__verbose))
            Log.log("\tSteepestDescent.__init__(): self.__debug = {}".format(self.__debug))
            Log.log("\tSteepestDescent.__init__(): self.__loss_function = {}".format(self.__loss_function))
            Log.log("\tSteepestDescent.__init__(): self.__constraints = {}".format(self.__constraints))
            Log.log("\tSteepestDescent.__init__(): self.__step_length_control = {}".format(self.__step_length_control))
            Log.log("\tSteepestDescent.__init__(): self.__config = {}".format(self.__config))

        OptimizationAlgorithm.__init__(self, Log, self.__verbose, self.__debug, self.__loss_function,
                                       self.__constraints, self.__step_length_control, self.__config)

    def execute_optimization_step(self, current_parameter_set, current_iteration):
        """ Overloads the abstract function in OptimizationAlgorithm.
        Performs optimization step with the steepest descent algorithm
        returns estimations and updated parameter set """
        Log = self.__log
        math = self.__math
        Log.log("Executing optimization Step {}".format(current_iteration))
        # get gradient to determine the steepest descent
        # also get loss_function evaluation for current parameter set, to check for stopping criterion
        [f0, grad] = self.get_gradient(current_parameter_set)
        if self.__verbose or self.__debug:
            Log.log("\tSteepestDescent.execute_optimization_step(): f0 = {}".format(f0))
            Log.log("\tSteepestDescent.execute_optimization_step(): gradient = {}".format(grad))

        # direction of steepest descent: negative gradient
        descent = []  # initialize variable
        for i in range(len(grad)):
            try:
                descent.append(-grad[i])
            except:
                Log.errorexit("ERROR in SteepestDescent.execute_optimization_step(): "
                              "Failed: descent.append(-grad[i]). grad[i] = {}".format(grad[i]))
        if self.__debug:
            Log.log("\tSteepestDescent.execute_optimization_step(): descent = {}".format(descent))

        min_parameters = None  # initialize variable
        max_parameters = None  # initialize variable
        try:
            min_parameters = self.__constraints.get_min_parameters()
        except:
            Log.errorexit("ERROR in SteepestDescent.execute_optimization_step(): "
                          "Failed to get min force-field parameters from constraints.")
        try:
            max_parameters = self.__constraints.get_max_parameters()
        except:
            Log.errorexit("ERROR in SteepestDescent.execute_optimization_step(): "
                          "Failed to get max force-field parameters from constraints.")
        if self.__debug:
            Log.log("\tSteepestDescent.execute_optimization_step(): min_parameters = {}".format(min_parameters))
            Log.log("\tSteepestDescent.execute_optimization_step(): max_parameters = {}".format(max_parameters))

        [step_length, f_new] = self.__step_length_control.calculate_step_length(min_parameters, max_parameters,
                                                                                current_parameter_set,
                                                                                current_iteration, f0, descent)
        if self.__debug:
            Log.log("\tSteepestDescent.execute_optimization_step(): step_length = {}".format(step_length))
            Log.log("\tSteepestDescent.execute_optimization_step(): f_new = {}".format(f_new))

        norm_descent = None  # initialize variable
        try:
            norm_descent = math.norm(descent)
        except:
            Log.errorexit("ERROR in SteepestDescent.execute_optimization_step(): "
                          "Failed to calculate 'norm_descent = math.norm(descent)'.")
        if self.__debug:
            Log.log("\tSteepestDescent.execute_optimization_step(): norm_descent = {}".format(norm_descent))

        try:
            descent = math.scalar_vector_mult((1 / norm_descent), descent)
        except:
            Log.errorexit("ERROR in SteepestDescent.execute_optimization_step(): "
                          "Failed to calculate 'descent = math.scalar_vector_mult((1 / norm_descent), descent)'.")
        if self.__debug:
            Log.log("\tSteepestDescent.execute_optimization_step(): descent = {}".format(descent))

        step = None  # initialize variable
        try:
            step = math.scalar_vector_mult(step_length, descent)
        except:
            Log.errorexit("ERROR in SteepestDescent.execute_optimization_step(): "
                          "Failed to calculate 'step = math.scalar_vector_mult(step_length, descent)'.")
        if self.__debug:
            Log.log("\tSteepestDescent.execute_optimization_step(): step = {}".format(step))

        x_new = []  # initialize variable
        for i in range(len(step)):
            new_parameter = None  # initialize variable
            try:
                new_parameter = float(current_parameter_set[i]) + float(step[i])
            except:
                Log.errorexit("ERROR in SteepestDescent.execute_optimization_step(): "
                              "Failed to calculate float(current_parameter_set[i]) + float(step[i]): "
                              "float({}) + float({})".format(current_parameter_set[i], step[i]))
            if self.__debug:
                Log.log("\t\tSteepestDescent.execute_optimization_step(): new_parameter = {}".format(new_parameter))

            x_new.append(new_parameter)

        if self.__verbose:
            Log.log("\tSteepestDescent.execute_optimization_step(): \n"
                    "\tf_old = {}\n"
                    "\tf_new = {}\n"
                    "\tx_new = {}".format(f0, f_new, x_new))
        if self.__debug:
            Log.log("\tSteepestDescent.execute_optimization_step(): x_new = {}".format(x_new))

        Log.log("f_old = {}, f_new = {}, x_new = {} #".format(f0, f_new, x_new))
        return x_new, f_new

    def __del__(self):
        """ Destructor """
        del self
