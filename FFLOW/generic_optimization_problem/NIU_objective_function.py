#   objective function
#
#   start_doc
#   Script:         loss.py
#
#   Author:         Marco Huelsmann
#                   Robin Strickstrock
#
#   Date:           16-03-2022
#
#   Description:    class ObjectiveFunction
#
#   Usage:          by defining an instance
#
#   Arguments:
#
#   Options:
#
#   Output:
#
#   Imported:
#
#   Called:
#
#   Modifications: CURRENTLY NOT IN USE!!!
#   end_doc


class ObjectiveFunction:

    def __init__(self, verbose, dimension):
        """ Constructor """
        self.__verbose = verbose
        self.__dimension = dimension
        if self.__verbose:
            print("NIU_objective_function.py: Dimension: {}".format(self.__dimension))

    ############################################
    #   virtual methods
    ############################################

#    def get_function_values(self, parameter_set):
#        """ returns a list of function values for a given parameter set"""
#        print("got function values in '{}'".format(__name__))
#        pass

#    def get_function_value(self, x):
#        """ return the objective function value of a vector x """
#        pass

#    def get_gradient(self, x):
#        """ return the gradient of the objective function at x """
#        pass

#    def get_hessian(self, x):
#        """ return the Hessian of the objective function at x """
#        pass

    def __del__(self):
        """ Destructor """
        del self
