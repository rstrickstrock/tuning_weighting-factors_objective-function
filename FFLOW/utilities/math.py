#   Math
#
#   start_doc
#   Script:         math.py
#
#   Author:         Marco Huelsmann
#                   Robin Strickstrock
#
#   Date:           14-06-2022
#
#   Description:    class Math
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

class Math:
    def __init__(self, logging_object):
        """ Constructor """
        self.__log = logging_object

    def norm(self, v):
        """ returns the euclidean norm of a vector v """
        Log = self.__log
        n = 0.0
        for i in range(len(v)):
            vi = 0.0  # initialize variable
            try:
                vi = float(v[i])
            except:
                Log.errorexit("ERROR in Math.norm(): - "
                              "{}. element of vector v ('{}') can't be cast to float.".format(i, v[i]))
            n = n + pow(vi, 2)

        n = pow(n, 0.5)
        return n

    def scalar_vector_mult(self, s, v):
        """ multiplies a skalar s and a vector v """
        Log = self.__log
        try:
            s = float(s)
        except:
            Log.errorexit("ERROR in Math.scalar_vector_mult(): - "
                          "scalar s ('{}') can't be cast to float.".format(s))

        result = []
        for i in range(len(v)):
            vi = 0.0  # initialize variable
            try:
                vi = float(v[i])
            except:
                Log.errorexit("ERROR in Math.scalar_vector_mult(): - "
                              "{}. element of vector v ('{}') can't be cast to float.".format(i, v[i]))
            result.append(s * vi)

        return result
        
    def __del__(self):
        """ Destructor """
        del self