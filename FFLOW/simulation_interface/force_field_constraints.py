#   Force Field Constraints
#
#   start_doc
#   Script:         force_field_constraints.py
#
#   Author:         Marco Huelsmann
#                   Robin Strickstrock
#
#   Date:           18-03-2022
#
#   Description:    class ForceFieldConstraints
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


class ForceFieldConstraints:

    def __init__(self, logging_object, verbose, debug, initial_guess, config):
        """ Constructor """
        self.__log = logging_object
        Log = self.__log
        self.__verbose = verbose
        self.__debug = debug
        self.__initial_guess = initial_guess
        self.__config = config
        if self.__debug:
            Log.log("\tForceFieldConstraints.__init__(): self.__verbose = {}".format(self.__verbose))
            Log.log("\tForceFieldConstraints.__init__(): self.__debug = {}".format(self.__debug))
            Log.log("\tForceFieldConstraints.__init__(): self.__initial_guess = {}".format(self.__initial_guess))
            Log.log("\tForceFieldConstraints.__init__(): self.__config = {}".format(self.__config))

        #   get number of parameters:
        self.__number_of_parameters = len(self.__initial_guess)
        if self.__debug:
            Log.log("\tForceFieldConstraints.__number_of_parameters: self.__verbose = {}"
                    "".format(self.__number_of_parameters))

        #    initialize boundaries for parameter space
        self.__boundaries = []  # initialize variable
        self.__negative_parameters = False  # initialize variable and set default value to 'False'
        try:
            self.__init_boundary()
        except:
            Log.errorexit("ERROR in ForceFieldConstraints.__init__(): "
                          "could not initialize force field parameter boundaries.")

        #   calculate min/max values for parameters
        self.__min_ffparameter_values = []
        self.__max_ffparameter_values = []
        try:
            self.__admissible_domain()
        except:
            Log.errorexit("ERROR in ForceFieldConstraints.__init__(): "
                          "could not calculate min/max vector for force-field parameters.")
        else:
            if self.__verbose or self.__debug:
                Log.log("ForceFieldConstraints - parameter boundaries initialized\n"
                        "\tInitial guess:  {}\n"
                        "\tmin parameters: {}\n"
                        "\tmax parameters: {}".format(self.__initial_guess, self.__min_ffparameter_values,
                                                      self.__max_ffparameter_values))

    def __init_boundary(self):
        """ Set lower and upper boundary for loss function's feasible parameter values """
        Log = self.__log
        boundary = None  # initialize variable
        try:
            boundary = self.__config.get("OPT", "boundary")
        except:
            Log.errorexit("ERROR in ForceFieldConstraints.__init_boundary(): "
                          "Could not get 'boundary' from section 'OPT'.")
        if self.__debug:
            Log.log("\tForceFieldConstraints.__init_boundary(): boundary = {}".format(boundary))

        boundaries = []
        boundary = boundary.split(" ")
        for bound in boundary:
            try:
                bound = float(bound)
            except:
                Log.errorexit("ERROR in ForceFieldConstraints.__init_boundary(): "
                              "Could not convert '{}' to float.".format(bound))
            if self.__debug:
                Log.log("\t\tForceFieldConstraints.__init_boundary(): bound = {}".format(bound))
            if bound < 0:
                Log.errorexit("ERROR in ForceFieldConstraints.__init_boundary(): "
                              "boundary '{}' must not be less than 0".format(bound))

            try:
                boundaries.append(float(bound))
            except:
                Log.errorexit("ERROR in ForceFieldConstraints.__init_boundary(): "
                              "Could not append boundary '{}' to boundaries".format(bound))
        if self.__debug:
            Log.log("\tForceFieldConstraints.__init_boundary(): boundaries = {}".format(boundaries))
        #   number_of_boundaries must either equal 1 (every parameter has the same relative boundary)
        #   or match the number of parameters
        number_of_boundaries = len(boundaries)
        if self.__debug:
            Log.log("\tForceFieldConstraints.__init_boundary(): number_of_boundaries = {}".format(number_of_boundaries))
        if number_of_boundaries == 0:
            #   should not happen
            Log.errorexit("ERROR in ForceFieldConstraints.__init_boundary(): "
                          "there are no boundaries in '{}'".format(boundaries))
        elif number_of_boundaries > 1:
            #   more than one boundary, there must be a boundary defined for every parameter
            if number_of_boundaries != self.__number_of_parameters:
                #   number of boundaries do NOT match number of parameters
                Log.errorexit("ERROR in ForceFieldConstraints.__init_boundary(): "
                              "Number of boundaries ({}) do not match the number of "
                              "parameters ({}).".format(number_of_boundaries, self.__number_of_parameters))
            else:
                #   everything is fine.
                pass
        else:
            #   number_of_boundaries == 1, check if there are more than one parameter
            if self.__number_of_parameters > 1:
                #   more than one parameter: use the same boundary for every parameter
                try:
                    boundary = boundaries[0]
                except:
                    Log.errorexit("ERROR in ForceFieldConstraints.__init_boundary(): "
                                  "Are there no boundaries in 'boundaries'?")
                if self.__debug:
                    Log.log("\tForceFieldConstraints.__init_boundary(): boundary = {}".format(boundary))

                boundaries = []
                for i in range(0, self.__number_of_parameters):
                    try:
                        boundaries.append(boundary)
                    except:
                        Log.errorexit("ERROR in ForceFieldConstraints.__init_boundary(): "
                                      "Could not duplicate the single boundary to be used for multiple parameters.")
                if self.__debug:
                    Log.log("\tForceFieldConstraints.__init_boundary(): boundaries = {}".format(boundaries))
            else:
                #   everything is fine
                pass

        #   final test if there is a boundary for every parameter
        if not len(boundaries) == self.__number_of_parameters:
            Log.errorexit("ERROR in ForceFieldConstraints.__init_boundary(): "
                          "Number of boundaries ({}) do NOT match "
                          "number of parameters ({})".format(len(boundaries), self.__number_of_parameters))

        #   check if negative parameter space is allowed:
        negative_parameters = False  # initialize variable with default value 'False' to prohibit negative parameters
        try:
            negative_parameters = self.__config.get("OPT", "negative_parameters")
        except:
            #   not specified if parameters can be negative
            #   stick to default and do not allow negative parameter values
            pass
        else:
            negative_list = ["False", "FALSE", "false", "No", "NO", "no"]
            positive_list = ["True", "TRUE", "true", "Yes", "YES", "yes"]
            if negative_parameters is False or negative_parameters in negative_list:
                negative_parameters = False
            elif negative_parameters is True or negative_parameters in positive_list:
                negative_parameters = True
            else:
                Log.errorexit("ERROR in ForceFieldConstraints.__init_boundary():"
                              "invalid option 'negative_parameters' in section 'OPT' ({})."
                              "Value must be 'True' or 'False'.".format(negative_parameters))
        if self.__debug:
            Log.log("\tForceFieldConstraints.__init_boundary(): negative_parameters = {}"
                    "".format(negative_parameters))
        try:
            self.__boundaries = boundaries
            self.__negative_parameters = negative_parameters
        except:
            Log.errorexit("ERROR in ForceFieldConstraints.__init_boundary(): "
                          "failed to initialize boundaries.")
        if self.__debug:
            Log.log("\tForceFieldConstraints.__init_boundary(): self.__boundaries = {}".format(self.__boundaries))
            Log.log("\tForceFieldConstraints.__init_boundary(): self.__negative_parameters = {}"
                    "".format(self.__negative_parameters))

    def __admissible_domain(self):
        """ Computes min/max values for force-field parameters
            min/max values are determined by the initial guess
            +/- 'initial guess' * 'boundary',
            where is a %-value boundary """
        Log = self.__log
        #   check if there is a boundary for every parameter
        number_of_parameters = len(self.__initial_guess)
        number_of_boundaries = len(self.__boundaries)
        if self.__debug:
            Log.log("\tForceFieldConstraints.__admissible_domain(): number_of_parameters = {}"
                    "".format(number_of_parameters))
            Log.log("\tForceFieldConstraints.__admissible_domain(): number_of_boundaries = {}"
                    "".format(number_of_boundaries))
        if number_of_parameters != number_of_boundaries:
            Log.errorexit("ERROR in ForceFieldConstraints.__admissible_domain: "
                          "Number of parameters ({}) do NOT match numbers of boundaries "
                          "({}".format(number_of_parameters, number_of_boundaries))

        factor = None           # initialize variable
        lower_parameter = None  # initialize variable
        upper_parameter = None  # initialize variable

        for i in range(number_of_parameters):
            try:
                #   boundaries given in %
                factor = float(self.__boundaries[i] * 0.01)
            except:
                Log.errorexit("ERROR in ForceFieldConstraints.__admissible_domain: "
                              "Could not calculate force-field boundaries.")
            if self.__debug:
                Log.log("\t\tForceFieldConstraints.__admissible_domain(): factor = {}".format(factor))
            if factor < 0:
                #   boundaries (i.e. factor) must not be negative
                Log.errorexit("ERROR in ForceFieldConstraints.__admissible_domain: "
                              "boundary ({}) must not be negative.".format(self.__boundaries[i]))

            try:
                lower_parameter = float(self.__initial_guess[i] - (self.__initial_guess[i]*factor))
            except:
                Log.errorexit("ERROR in ForceFieldConstraints.__admissible_domain: "
                              "Could not calculate lower parameter boundary.")
            if self.__debug:
                Log.log("\t\tForceFieldConstraints.__admissible_domain(): lower_parameter = {}".format(lower_parameter))

            if not self.__negative_parameters and lower_parameter < 0:
                #   parameter is negative but are defined not to be negative
                #   set parameter to 0.000001 instead.
                #   do not set to 0, in case parameter is used in a denominator
                lower_parameter = float(0.000001)
                Log.log("WARNING: Lower parameter boundary would be less than 0. "
                        "negative parameters are not specifically allowed in the config file "
                        "and the lower parameter boundary is set to 0.000001.")

            try:
                upper_parameter = float(self.__initial_guess[i] + (self.__initial_guess[i]*factor))
            except:
                Log.errorexit("ERROR in ForceFieldConstraints.__admissible_domain: "
                              "Could not calculate upper parameter boundary.")
            if self.__debug:
                Log.log("\t\tForceFieldConstraints.__admissible_domain(): upper_parameter = {}".format(upper_parameter))

            self.__min_ffparameter_values.append(lower_parameter)
            self.__max_ffparameter_values.append(upper_parameter)

        if self.__debug:
            Log.log("\tForceFieldConstraints.__admissible_domain(): self.__min_ffparameter_values = {}"
                    "".format(self.__min_ffparameter_values))
            Log.log("\tForceFieldConstraints.__admissible_domain(): self.__max_ffparameter_values = {}"
                    "".format(self.__max_ffparameter_values))

    def get_boundary(self):
        """ return the boundary (min/max allowd values) vectors """
        return [self.__min_ffparameter_values, self.__max_ffparameter_values]

    def get_min_parameters(self):
        """ returns vector with min force-field parameters """
        return self.__min_ffparameter_values

    def get_max_parameters(self):
        """ returns vector with max force-field parameters """
        return self.__max_ffparameter_values

    def get_initial_parameters(self):
        """ returns initial parameter set """
        return self.__initial_guess

    def get_dimension(self):
        """ returns dimension of optimization """
        return self.__number_of_parameters

    def is_feasible(self, x):
        """ decides if a vector x is feasible in the sense of the box constraints
        returns True (feasible) or False (not feasible) """
        Log = self.__log
        if not len(x) == len(self.__max_ffparameter_values):
            Log.errorexit("ERROR in ForceFieldConstraints.is_feasible(): "
                          "Parameter ({}) and constraints ({}) vector have different lengths"
                          ".".format(len(x), len(self.__max_ffparameter_values)))

        for i in range(len(x)):
            if x[i] < self.__min_ffparameter_values[i] or x[i] > self.__max_ffparameter_values[i]:
                return False

        return True

    def __del__(self):
        """ Destructor """
        del self
