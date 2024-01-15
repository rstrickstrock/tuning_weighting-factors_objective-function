#   Loss
#
#   start_doc
#   Script:         loss.py
#
#   Author:         Marco Huelsmann
#                   Robin Strickstrock
#
#   Date:           16-03-2022
#
#   Description:    class Loss (derived from ObjectiveFunction)
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
#   Modifications:
#   end_doc

###############################################################################
#   required python modules
###############################################################################


class Loss:

    def __init__(self, logging_object, verbose, debug, dimension):
        """ Constructor """
        self.__log = logging_object
        Log = self.__log
        self.__verbose = verbose
        self.__debug = debug
        self.__dimension = dimension
        self.__gradients_of_estimations = []

        if self.__debug:
            Log.log("\t\tLoss.__init__(): self.__verbose = {}".format(self.__verbose))
            Log.log("\t\tLoss.__init__(): self.__debug = {}".format(self.__debug))
            Log.log("\t\tLoss.__init__(): self.__dimension = {}".format(self.__dimension))
            Log.log("\t\tLoss.__init__(): self.__gradients_of_estimations = {}".format(self.__gradients_of_estimations))

    def get_dimension(self):
        """ returns dimension """
        return self.__dimension

    def get_gradient_of_estimations(self):
        """ returns gradient of estimations """
        return self.__gradients_of_estimations

    def __del__(self):
        """ Destructor """
        del self
