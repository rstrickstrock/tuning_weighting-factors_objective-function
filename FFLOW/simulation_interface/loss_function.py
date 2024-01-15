#   Lossfunction
#
#   start_doc
#   Script:         loss_function.py
#
#   Author:         Marco Huelsmann
#                   Robin Strickstrock
#
#   Date:           16-03-2022
#
#   Description:    class LossFunction (derived from Loss)
#
#   Usage:          by defining an instance
#
#   Arguments:
#
#   Options:
#
#   Output:
#
#   Imported:       os
#                   Loss
#                   IO
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
import math
from generic_optimization_problem.loss import Loss
from utilities.io import IO
IO = IO()


class LossFunction(Loss):

    def __init__(self, logging_object, verbose, debug, dimension, objective_function, cwd_basedir, config):
        """ Constructor """
        self.__log = logging_object
        Log = self.__log
        self.__verbose = verbose
        self.__debug = debug
        self.__dimension = dimension
        self.__objective_function = objective_function
        self.__current_working_directory_basedir = cwd_basedir
        self.__config = config
        # TODO: add loss_value_normalization option in config-file and read it from there instead of setting it here
        self.__loss_value_normalization = True
        #self.__loss_value_normalization = False

        if self.__debug:
            Log.log("\tLossFunction.__init__(): self.__verbose = {}".format(self.__verbose))
            Log.log("\tLossFunction.__init__(): self.__debug = {}".format(self.__debug))
            Log.log("\tLossFunction.__init__(): self.__dimension = {}".format(self.__dimension))
            Log.log("\tLossFunction.__init__(): self.__objective_function = {}".format(self.__objective_function))
            Log.log("\tLossFunction.__init__(): self.__current_working_directory_basedir = {}"
                    "".format(self.__current_working_directory_basedir))
            Log.log("\tLossFunction.__init__(): self.__config = {}".format(self.__config))
            Log.log("\tLossFunction.__init__(): self.__loss_value_normalization = {}"
                    "".format(self.__loss_value_normalization))

        Loss.__init__(self, logging_object, self.__verbose, self.__debug, self.__dimension)

        #   get sections in config file
        self.__sections = list(self.__config.sections())
        if self.__debug:
            Log.log("\tLossFunction.__init__(): sections = {}".format(self.__sections))

        ############################################
        # initialize weights and targets
        ############################################
        self.__targets = []
        self.__weights = []
        section = None  # initialize variable
        if "PhysProp" in self.__sections:
            section = "PhysProp"
            self._init_targets(section)
            self._init_weights(section)

        if "QMMM" in self.__sections:
            section = "QMMM"
            self._init_targets(section)
            self._init_weights(section)

        if section is None:
            #   neither sections "PhysProp" nor "QMMM" defined in the config file
            #   currently PhysProp and QMMM are implemented, so on of them must be defined
            Log.errorexit("ERROR in LossFunction.__init__(): "
                          "None of the following sections defined in the config file: ['PhysProp', 'QMMM'].")

        if self.__verbose or self.__debug:
            Log.log("\tLossFunction.__init__(): targets initialized: {}".format(self.__targets))
            Log.log("\tLossFunction.__init__(): weights initialized: {}".format(self.__weights))

    def get_sections(self):
        """ returns sections defined via config file """
        return self.__sections

    def get_targets(self):
        """ returns targets """
        return self.__targets


    def _init_targets(self, section):
        """ initialize optimization targets """
        Log = self.__log
        #   get targets file
        target_file = None  # initialize variable
        try:
            target_file = self.__config.get(section, "target")
        except:
            Log.errorexit("ERROR in LossFunction._init_targets(): "
                          "No target file in section '{}' defined.".format(section))
        if self.__debug:
            Log.log("\tLossFunction._init_targets(): target_file = {}".format(target_file))

        target_file = os.path.join(self.__current_working_directory_basedir, target_file)
        try:
            os.stat(target_file)
        except:
            Log.errorexit("ERROR in LossFunction._init_targets(): "
                          "target file '{}' not found. Make sure to have the parameter file in the current working "
                          "directory '{}'.".format(target_file, self.__current_working_directory_basedir))
        else:
            if self.__debug:
                Log.log("\tLossFunction._init_targets(): target_file = {}".format(target_file))

            #   read target values from file
            targets = None  # initialize variable
            try:
                targets = IO.get_properties(target_file)
            except:
                Log.errorexit("ERROR in LossFunction._init_targets(): "
                              "Could not read targets from target file '{}'".format(target_file))
            if self.__debug:
                Log.log("\tLossFunction._init_targets(): targets = {}".format(targets))

            try:
                self.__targets.append(targets)
            except:
                Log.errorexit("ERROR in LossFunction._init_targets(): "
                              "Could not append current targets to list of targets.")
            if self.__debug:
                Log.log("\tLossFunction._init_targets(): following target values from section '{}' appended to "
                        "target value list: {}".format(section, targets))

    def _init_weights(self, section):
        """ initializes weights for the optimization"""
        #   reads weights from config file and converts them to float.
        #   if number of weights match number of targets: do nothing
        #   if number of weights equals 1 and is less than number of targets: use the same weight for every target
        Log = self.__log

        wghts = None  # initialize variable
        try:
            wghts = self.__config.get(section, "weights")
        except:
            Log.errorexit("ERROR in LossFunction._init_weights(): "
                          "could not extract 'weight(s)' from section '{}'".format(section))
        if self.__debug:
            Log.log("\tLossFunction._init_weights(): wghts = {}".format(wghts))

        wghts = wghts.split(" ")
        if self.__debug:
            Log.log("\tLossFunction._init_weights(): wghts = {}".format(wghts))

        weights = []
        for wght in wghts:
            try:
                weights.append(float(wght))
            except:
                Log.errorexit("ERROR in LossFunction._init_weights(): "
                              "Could not convert '{}' to float and append to 'weights'.".format(wght))
        if self.__debug:
            Log.log("\tLossFunction._init_weights(): weights = {}".format(weights))

        #   check if number of weights matches number of targets.
        #   if number of weights = 1 and number of targets != 1 use the same weight for every property
        number_of_weights = len(weights)
        if self.__debug:
            Log.log("\tLossFunction._init_weights(): number_of_weights = {}".format(number_of_weights))

        #   get number of targets.
        #   Targets ALWAYS get initialized before the corresponding weights
        #   last element in self.__targets targets of interest for the weights initialized here
        number_of_targets = None  # initialize variable
        try:
            number_of_targets = len(self.__targets[-1])
        except:
            Log.errorexit("ERROR in LossFunction._init_weights(): "
                          "Could not get number of targets corresponding to the weights "
                          "for section '{}'.".format(section))
        if self.__debug:
            Log.log("\tLossFunction._init_weights(): number_of_targets = {}".format(number_of_targets))

        final_weights = None  # initialize this variable
        if number_of_targets == number_of_weights:
            #    #targets match #weights
            final_weights = weights
        elif number_of_weights == 1 and number_of_targets > 1:
            #   use the single weight given in the config file for every property
            final_weights = []
            for i in range(0, number_of_targets):
                final_weights.append(weights[0])
        else:
            Log.errorexit("ERROR in LossFunction._init_weights(): "
                          "#weights ({}) do not match #targets ({}) OR #weights({}) "
                          "is not equal to 1".format(number_of_weights, number_of_targets, number_of_weights))
        if self.__debug:
            Log.log("\tLossFunction._init_weights(): final_weights = {}".format(final_weights))

        try:
            self.__weights.append(final_weights)
        except:
            Log.errorexit("ERROR in LossFunction._init_weights(): "
                          "Could not append weights '{}' to list of weights".format(final_weights))
        if self.__debug:
            Log.log("\tLossFunction._init_weights(): following weights from section '{}' appended to "
                    "list of weights: {}".format(section, final_weights))

    def get_function_value(self, estimations):
        """ evaluates the loss function for estimations of a parameter set X.
        make sure in estimations are PhysProp values first, followed bei QMMM values. """
        # TODO: remove hardcoded order of properties, maybe use pandas.
        Log = self.__log
        if len(estimations) != 2:
            Log.errorexit("ERROR in LossFunction.get_function_value(): "
                          "Currently, 'estimations' needs to contain two lists. \n"
                          "estimations[0] = physical properties \n"
                          "estimations[1] = qm mm properties \n")
        estimations_pp = None  # initialize variable
        try:
            estimations_pp = estimations[0]
        except:
            Log.errorexit("ERROR in LossFunction.get_function_value(): "
                          "Could not extract PhysProp estimations from 'estimations'. ")
        if self.__debug:
            Log.log("\tLossFunction.get_function_value(): estimations_pp = {}".format(estimations_pp))

        targets_pp = None  # initialize variable
        try:
            targets_pp = self.__targets[0]
        except:
            Log.errorexit("ERROR in LossFunction.get_function_value(): "
                          "Could not extract PhysProp targets from self.__targets[0]. ")
        if self.__debug:
            Log.log("\tLossFunction.get_function_value(): targets_pp = {}".format(targets_pp))

        weights_pp = None  # initialize variable
        try:
            weights_pp = self.__weights[0]
        except:
            Log.errorexit("ERROR in LossFunction.get_function_value(): "
                          "Could not extract PhysProp weights from self.__weights[0]. ")

        if len(estimations_pp) != len(targets_pp):
            Log.errorexit("ERROR in LossFunction.get_function_value(): "
                          "len(estimations_pp) =! len(targets_pp). ")
        if self.__debug:
            Log.log("\tLossFunction.get_function_value(): weights_pp = {}".format(weights_pp))

        estimations_qm = None  # initialize variable
        try:
            estimations_qm = estimations[1]
        except:
            Log.errorexit("ERROR in LossFunction.get_function_value(): "
                          "Could not extract QMMM estimations from 'estimations'. ")
        if self.__debug:
            Log.log("\tLossFunction.get_function_value(): estimations_qm = {}".format(estimations_qm))

        targets_qm = None  # initialize variable
        try:
            targets_qm = self.__targets[1]
        except:
            Log.errorexit("ERROR in LossFunction.get_function_value(): "
                          "Could not extract QMMM targets from self.__targets[1]. ")
        if self.__debug:
            Log.log("\tLossFunction.get_function_value(): targets_qm = {}".format(targets_qm))

        weights_qm = None  # initialize variable
        try:
            weights_qm = self.__weights[1]
        except:
            Log.errorexit("ERROR in LossFunction.get_function_value(): "
                          "Could not extract QMMM weights from self.__weights[1]. ")
        if self.__debug:
            Log.log("\tLossFunction.get_function_value(): weights_qm = {}".format(weights_qm))

        if len(estimations_qm) != len(targets_qm):
            if len(estimations_qm) == 1:
                try:
                    estimations_qm = estimations_qm[0]
                except:
                    Log.errorexit("ERROR in LossFunction.get_function_value(): "
                                  "Could not execute 'estimations_qm = estimations_qm[0]'.")
                if self.__debug:
                    Log.log("\tLossFunction.get_function_value(): estimations_qm = {}".format(estimations_qm))
            else:
                Log.errorexit("ERROR in LossFunction.get_function_value(): "
                              "len(estimations_qm) =! len(targets_qm) "
                              "and len(estimations_qm) != 1, indicating the form estimations_qm = [[esti1, esti2,..]]")

        loss_fkt_value = 0.0
        if self.__debug:
            Log.log(f'\tLossFunction.get_function_value(): loss_fkt_value: {loss_fkt_value} (initialized)')

        if self.__loss_value_normalization:
            # TODO: add normalization_factor value in config-file and read it from there instead of setting it here
            normalization_factor = 1000.0
            if self.__debug:
                Log.log(f'\tLossFunction.get_function_value(): set normalization_factor: {normalization_factor} (PP)')
        for i in range(len(estimations_pp)):
            if self.__debug:
                Log.log(f'\t\tLossFunction.get_function_value(): \n'
                        f'\t\tloss function value = {loss_fkt_value}\n'
                        f'\t\ti = {i}\n'
                        f'\t\tweights_pp[{i}] = {weights_pp[i]}\n'
                        f'\t\ttargets_pp[{i}] = {targets_pp[i]}\n'
                        f'\t\testimations_pp[{i}]: {estimations_pp[i]}'
                        f'')
            if targets_pp[i] == 0:
                targets_pp[i] = 2.2e-12
                estimations_pp[i] = estimations_pp[i] + 2.2e-12
                Log.log(f'WARNING: LossFunction._get_function_value(): targets_pp[{i}] = 0!\n'
                        f'\t targets_pp[{i}] set to 2.2e-12. Also added 2.2e-12 to estimations_pp[{i}].'
                        f'')
            this_estimation_pp = None  # initialize variable
            try:
                if len(estimations_pp[i]) == 1:
                    this_estimation_pp = estimations_pp[i][0]
            except:
                this_estimation_pp = estimations_pp[i]
            if self.__debug:
                Log.log(f'\tLossFunction.get_function_value(): this_estimation_pp: {this_estimation_pp}')

            # TODO: add option for normalization
            loss_value = 0.0  # initialize variable
            if self.__debug:
                Log.log(f'\tLossFunction.get_function_value(): loss_value = {loss_value} (initialized).')
            try:
                loss_value = pow((1.0 - (this_estimation_pp/targets_pp[i])), 2)
            except:
                Log.errorexit(f'ERROR in LossFunction.get_function_value(): '
                              f'Could not calculate loss value for PP element(s).')
            if self.__debug:
                Log.log(f'\t\tLossFunction.get_function_value(): loss_value({i}): {loss_value}'
                        f'')

            if self.__loss_value_normalization:
                try:
                    loss_value = self._normalize(normalization_factor, loss_value)
                except:
                    Log.errorexit(f'ERROR in LossFunction.get_function_value(): '
                                  f'Could not normalize loss value for PP element(s).')
                if self.__debug:
                    Log.log(f'\t\tLossFunction.get_function_value(): normalized loss_value({i}): {loss_value}'
                            f'')

            try:
                loss_fkt_value = loss_fkt_value + weights_pp[i] * loss_value
            except:
                Log.errorexit(f'ERROR in LossFunction.get_function_value(): '
                              f'Could not update loss function value for PP element(s).')
            if self.__debug:
                Log.log(f'\t\tLossFunction.get_function_value(): loss_fkt_value: {loss_fkt_value} '
                        f'(updated, intermediate result)'
                        f'')

        if self.__loss_value_normalization:
            # TODO: add normalization_factor value in config-file and read it from there instead of setting it here
            normalization_factor = 1.0
            if self.__debug:
                Log.log(f'\tLossFunction.get_function_value(): set normalization_factor: {normalization_factor} (QM)')
        for i in range(len(estimations_qm)):
            if self.__debug:
                Log.log(f'\tLossFunction.get_function_value(): \n'
                        f'\t\tloss function value = {loss_fkt_value}\n'
                        f'\t\ti = {i}\n'
                        f'\t\tweights_qm[{i}] = {weights_qm[i]}\n'
                        f'\t\ttargets_qm[{i}] = {targets_qm[i]}\n'
                        f'\t\testimations_qm[{i}] = {estimations_qm[i]}'
                        f'')
            if targets_qm[i] == 0:
                targets_qm[i] = 2.2e-12
                estimations_qm[i] = estimations_qm[i] + 2.2e-12
                Log.log(f'"WARNING: LossFunction._get_function_value(): targets_qm[{i}] = 0!\n'
                        f'"\t targets_qm[{i}] set to 2.2e-12. Also added 2.2e-12 to estimations_qm[{i}].'
                        f'')
            this_estimation_qm = None  # initialize variable
            try:
                if len(estimations_qm[i]) == 1:
                    this_estimation_qm = estimations_qm[i][0]
            except:
                this_estimation_qm = estimations_qm[i]
            if self.__debug:
                Log.log(f'\tLossFunction.get_function_value(): this_estimation_qm: {this_estimation_qm}')

            # TODO: add option for normalization
            loss_value = 0.0  # initialize variable
            if self.__debug:
                Log.log(f'\tLossFunction.get_function_value(): loss_value = {loss_value} (initialized).')
            try:
                loss_value = pow((1 - (this_estimation_qm/targets_qm[i])), 2)
            except:
                Log.errorexit(f'ERROR in LossFunction.get_function_value(): '
                              f'Could not calculate loss value for QM element(s).')
            if self.__debug:
                Log.log(f'\t\tLossFunction.get_function_value(): loss_value({i}): {loss_value}'
                        f'')

            if self.__loss_value_normalization:
                try:
                    loss_value = self._normalize(normalization_factor, loss_value)
                except:
                    Log.errorexit(f'ERROR in LossFunction.get_function_value(): '
                                  f'Could not normalize loss value for QM element(s).')
                if self.__debug:
                    Log.log(f'\t\t\tLossFunction.get_function_value(): normalized loss_value({i}): {loss_value}'
                            f'')

            try:
                loss_fkt_value = loss_fkt_value + weights_qm[i] * loss_value
            except:
                Log.errorexit(f'ERROR in LossFunction.get_function_value(): '
                              f'Could not update loss function value for QM element(s).')
            if self.__debug:
                Log.log(f'\tLossFunction._get_function_value(): loss_fkt_value = {loss_fkt_value} '
                        f'(updated, intermediate result)'
                        f'')

        try:
            loss_fkt_value = float(loss_fkt_value)
        except:
            Log.errorexit(f'ERROR in LossFunction.get_function_value(): '
                          'Could not convert \'loss_fkt_value\' to float.')
        if self.__verbose or self.__debug:
            Log.log(f'\tLossFunction.get_function_value(): loss_fkt_value = {loss_fkt_value}')

        return loss_fkt_value

    def _normalize(self, c, x):
        """
        normlaize loss function value to be between 0 and 1
        :param c: tuning factor, the higher c, the sharper the edge
        :param x: loss value that is to be normalized
        :return: normalized_value
        """
        Log = self.__log
        normalized_value = 1.0 - math.exp(-c*x)
        if self.__debug:
            Log.log(f'\t\t\tLossFunction._normalize(): normalized_value={normalized_value}.')

        return normalized_value

    def __del__(self):
        """ Destructor """
        del self

