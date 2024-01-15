#   Constraints
#
#   start_doc
#   Script:         constraints.py
#
#   Author:         Marco Huelsmann
#                   Robin Strickstrock
#
#   Date:           18-03-2022
#
#   Description:    class Constraints
#
#   Usage:          NOT USED!!!!
#
#   Arguments:
#
#   Options:
#
#   Output:
#
#   Imported:       trace
#
#   Called:
#
#   Modifications:
#   end_doc

###############################################################################
#   required python modules
###############################################################################
from utilities.log import Trace
Tr = Trace()


class Constraints:
    def __init__(self, verbose, dimension, initial_guess):
        """ Constructor """
        self.__verbose = verbose
        self.__dimension = dimension
        self.__initial_guess = initial_guess
        print("This is not used.")

    #def get_boundary(self):
    #    """ return the boundary vectors """
    #    return [self.__min_ffparameter_values, self.__max_ffparameter_values]

    #def is_feasible(self, x):
    #    """ decides if a vector x is feasible in the sense of the box constraints """
        #   returns True (feasible) or False (not feasible)
    #    for i in range(len(x)):
    #        if x[i] < self.__min_ffparameter_values[i] or x[i] > self.__max_ffparameter_values[i]:
    #            return False

    #    return True

    def __del__(self):
        """ Destructor """
        del self
