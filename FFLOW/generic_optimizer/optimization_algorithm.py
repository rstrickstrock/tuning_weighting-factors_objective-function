#   Optimization Algorithm
#
#   start_doc
#   Script:         optimization_algorithm.py
#
#   Author:         Marco Huelsmann
#                   Robin Strickstrock
#
#   Date:           17-05-2022
#
#   Description:    class OptimizationAlgorithm
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
#                   subprocess
#                   time
#                   simulations
#
#   Called:
#
#   Modifications:
#   end_doc

###############################################################################
#   required python modules
###############################################################################
import os
import subprocess
import time
from simulation_interface.simulations import Simulations


class OptimizationAlgorithm:

    def __init__(self, logging_object, verbose, debug, loss_function, constraints, step_length_control, config):
        """ Constructor """
        self.__log = logging_object
        Log = self.__log

        self.__verbose = verbose
        self.__debug = debug
        self.__loss_function = loss_function
        self.__constraints = constraints
        self.__step_length_control = step_length_control
        self.__config = config
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.__init__(): self.__verbose = {}".format(self.__verbose))
            Log.log("\t\tOptimizationAlgorithm.__init__(): self.__debug = {}".format(self.__debug))
            Log.log("\t\tOptimizationAlgorithm.__init__(): self.__loss_function = {}".format(self.__loss_function))
            Log.log("\t\tOptimizationAlgorithm.__init__(): self.__constraints = {}".format(self.__constraints))
            Log.log("\t\tOptimizationAlgorithm.__init__(): self.__step_length_control = {}"
                    "".format(self.__step_length_control))
            Log.log("\t\tOptimizationAlgorithm.__init__(): self.__config = {}".format(self.__config))

        self.__sim = Simulations(Log, self.__verbose, self.__debug)

        self.__cwd = None  # initialize variable
        try:
            self.__cwd = self.__config.get("SYS", "cwd")
        except:
            Log.errorexit("Error in OptimizationAlgorithm.__init__(): "
                          "could not get cwd from config file.")
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.__init__(): self.__cwd = {}".format(self.__cwd))

        # get number of maximum optimization iterations
        try:
            self.__max_opt_iterations = self.__config.get("OPT", "max_opt_iterations")
        except:
            Log.errorexit("Error in OptimizationAlgorithm.__init__(): "
                          "Could not get 'max_opt_iterations' from section 'OPT' in config file.")
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.__init__(): self.__max_opt_iterations = {}"
                    "".format(self.__max_opt_iterations))

        # initialize iteration counter and set current iterations to 0.
        self.__current_iteration = 0
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.__init__(): self.__current_iteration = {}"
                    "".format(self.__current_iteration))

        # initialize current parameter set and set it to initial parameters.
        try:
            self.__x = constraints.get_initial_parameters()
        except:
            Log.errorexit("Error in OptimizationAlgorithm.__init__(): "
                          "could not get initial parameter set from constraints.")
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.__init__(): self.__x = {}".format(self.__x))

        # get tolerance for a successful optimization (stop criterion)
        threshold = None  # initialize variable
        try:
            threshold = self.__config.get("OPT", "threshold")
        except:
            Log.errorexit("Error in OptimizationAlgorithm.__init__(): "
                          "could not get 'tolerance' from section 'OPT' in config file.")
        try:
            self.__threshold = float(threshold)
        except:
            Log.errorexit("Error in OptimizationAlgorithm.__init__(): "
                          "'threshold' in section 'OPT' must be a float.")
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.__init__(): self.__threshold = {}".format(self.__threshold))

    def get_loss_function(self):
        """ returns loss function object """
        return self.__loss_function

    def get_constraints(self):
        """ returns contraints object """
        return self.__constraints

    def get_step_length_control(self):
        """ returns step length control object """
        return self.__step_length_control

    def get_current_iteration(self):
        """ returns the current interation in the optimization """
        return self.__current_iteration

    def get_current_parameter_set(self):
        """ returns the current parameter set """
        return self.__x

    def set_current_parameter_set(self, x):
        """ updates current parameter set to new value(s) x
        expects a list containing len(dim) float values! """
        Log = self.__log
        optimization_dimension = self.__constraints.get_dimension()
        this_dimension = None  # initialize variable
        try:
            this_dimension = len(x)
        except:
            Log.errorexit("Error in OptimizationAlgorithm.set_current_parameter_set(): "
                          "'x' seems to have no length ( = dimension ).")
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.set_current_parameter_set(): this_dimension = {}".format(this_dimension))

        if optimization_dimension != this_dimension:
            Log.errorexit("Error in OptimizationAlgorithm.set_current_parameter_set(): "
                          "new parameter set does not have the correct dimension.")

        self.__x = x
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.set_current_parameter_set(): self.__x = {}".format(self.__x))

    def get_dimension(self):
        """ returns dimension of optimization """
        return self.__constraints.get_dimension()

    def get_threshold(self):
        """ returns the threshold, a stop criterion for the optimization """
        return self.__threshold

    def set_threshold(self, new_threshold):
        """ sets the threshold (to a different value) """
        Log = self.__log
        t = None  # initialize variable
        try:
            t = float(new_threshold)
        except:
            Log.errorexit("Error in OptimizationAlgorithm.set_threshold(): "
                          "'t' must be a float.")
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.set_threshold(): t = {}".format(t))

        self.__threshold = t
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.set_threshold(): self.__threshold = {}".format(self.__threshold))

    def execute_optimization_step(self, current_parameter_set, current_iteration):
        """ Function to overload. Execute a single iteration of the optimization """
        pass

    def execute_optimization(self):
        """ runs the optimization """
        Log = self.__log
        Log.log("Executing Optimization Algorithm.")
        # indicator if maximum optimization iterations are reached
        is_last_iteration = False

        # initialize estimation for first optimization step.
        # TODO: Sort of hardcoded; improve for a later software version
        estimations_pp = []
        estimations_qm = []
        targets = self.__loss_function.get_targets()
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.execute_optimization(): targets = {}".format(targets))

        for esti in targets[0]:
            try:
                estimations_pp.append(float(0.0))
            except:
                Log.errorexit("Error in OptimizationAlgorithm.execute_optimization(): "
                              "could not set initial PhysProp estimations to 0.")
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.execute_optimization(): estimations_pp = {}".format(estimations_pp))

        for esti in targets[1]:
            try:
                estimations_qm.append(float(0.0))
            except:
                Log.errorexit("Error in OptimizationAlgorithm.execute_optimization(): "
                              "could not set initial QMMM estimations to 0.")
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.execute_optimization(): estimations_qm = {}".format(estimations_qm))

        estimations = [estimations_pp, estimations_qm]
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.execute_optimization(): estimations = {}".format(estimations))

        # get max loss value to start optimization with.
        # before first optimization step, estimations are all set to 0 by previous code.
        loss_value = self.__loss_function.get_function_value(estimations)
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.execute_optimization(): loss_value = {}".format(loss_value))
        if loss_value < self.__threshold:
            Log.errorexit("\n!!! WARNING !!!\n"
                          "\tThe initial loss value when all estimations are set to 0 is: {}\n"
                          "\tThe stop criterion 'threshold' for the optimization set in config file is: {}\n"
                          "\tPlease adapt the value for 'threshold' in the config file."
                          "\n".format(loss_value, self.__threshold))

        for iteration in range(1, int(self.__max_opt_iterations)+1):  # +1, because python starts at 0 not at 1.
            self.__current_iteration = int(iteration)
            if self.__debug:
                Log.log("\t\t\tOptimizationAlgorithm.execute_optimization(): self.__current_iteration = {}"
                        "".format(self.__current_iteration))

            # check if stop criterion is met: loss_function(estimations(x)) <= threshold
            if loss_value > self.__threshold:
                # get new estimations based on used optimization algorithm
                current_parameter_set = self.__x
                Log.log("Starting optimization step {}".format(self.__current_iteration))
                [new_parameter_set, new_loss_value] = self.execute_optimization_step(current_parameter_set,
                                                                                     self.__current_iteration)
                if self.__debug:
                    Log.log("\t\t\tOptimizationAlgorithm.execute_optimization(): new_parameter_set = {}"
                            "".format(new_parameter_set))
                    Log.log("\t\t\tOptimizationAlgorithm.execute_optimization(): new_loss_value = {}"
                            "".format(new_loss_value))
                # set new loss value from new parameter set
                loss_value = new_loss_value
                # set new parameter set as current parameter set
                self.set_current_parameter_set(new_parameter_set)
            else:
                Log.log("\n\n\n"
                        "#######################\n"
                        "Optimization finished.#\n"
                        "x_opt = {} #"
                        "\n\n\n".format(self.__x))
                return True

    def get_gradient(self, current_parameter_set, h=0.01):
        """ calculate gradient for current parameter set """
        # TODO: if default value for h, how to determine/what value?
        # for every dimension/direction calculate the descent/slope with a difference quotient
        # parameters for every difference are stored in new_parameter_sets
        Log = self.__log
        Sim = self.__sim
        Log.log("Getting gradient.")

        gradient_parameter_sets = []
        dimension = len(current_parameter_set)
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): dimension = {}".format(dimension))

        for i in range(dimension):
            # I can not just use 'new_set = current_parameter_set' because they become the same object and changes in
            # new_set are also applied in current_parameter_set # WTF!?
            direction_parameter_set = []
            for par in current_parameter_set:
                direction_parameter_set.append(float(par))
            direction_parameter_set[i] = direction_parameter_set[i] + h
            if self.__debug:
                Log.log("\t\t\tOptimizationAlgorithm.get_gradient(): direction_parameter_set = {}"
                        "".format(direction_parameter_set))
            gradient_parameter_sets.append(direction_parameter_set)
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): gradient_parameter_sets = {}"
                    "".format(gradient_parameter_sets))

        ############################################
        # Start simulation for current parameter set

        # starting simulations for the calculation of the gradient, sim_type = 'g'
        sim_type = str("g")
        JobIDs = []

        # TODO: put starting the simulations in a function/loop?
        #  basically hardcoded without the possibility to add further
        #  consider: for section in config.get_setcions() == PhysProp || QMMM

        # pp simulations
        sim_results_dirs_pp = []  # collect paths of sim results to do the evaluation and get results
        steering_script_pp = self.__config.get("PhysProp", "steering_script")
        steering_script_pp = os.path.join(self.__cwd, steering_script_pp)
        simulation_cwd_pp = os.path.join(self.__cwd, "PhysProp")
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): steering_script_pp = {}".format(steering_script_pp))
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): simulation_cwd_pp = {}".format(simulation_cwd_pp))

        execute_sim_command, sim_results_dir = Sim.create_execute_simulation_command(steering_script_pp,
                                                                                     simulation_cwd_pp,
                                                                                     sim_type,
                                                                                     str(self.__current_iteration),
                                                                                     "0",
                                                                                     current_parameter_set,
                                                                                     verbose=self.__verbose)
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): execute_sim_command = {}".format(execute_sim_command))
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): sim_results_dir = {}".format(sim_results_dir))
        sim_results_dirs_pp.append(sim_results_dir)

        sim_pp = None  # initialize variable
        try:
            sim_pp = subprocess.Popen(execute_sim_command, stdout=subprocess.PIPE)
        except:
            Log.errorexit("ERROR in OptimizationAlgorithm.get_gradient(): Failed to run 0. subprocess.Popen(...)")
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): sim_pp = {}".format(sim_pp))

        # get jobID
        sim_stdout = None  # initialize variable
        try:
            sim_stdout = sim_pp.stdout.read()
        except:
            Log.errorexit("ERROR in OptimizationAlgorithm.get_gradient(): Failed to execute sim_pp.stdout.read().")
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): sim_stdout = {}".format(sim_stdout))

        batch_job_id = None  # initialize variable
        try:
            batch_job_id = Sim.get_job_id(sim_stdout)
        except:
            Log.errorexit("ERROR in OptimizationAlgorithm.get_gradient(): Failed to execute Sim.get_job_id().")
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): batch_job_id = {}".format(batch_job_id))

        # check & wait for script to terminate
        while 1:
            if sim_pp.poll() == 0:
                break
            else:
                time.sleep(1)

        Log.log("\t\tOptimizationAlgorithm.get_gradient(): Submitted batch job {}".format(batch_job_id))
        JobIDs.append(batch_job_id)

        # Start simulations for every optimization dimension to determine gradient
        for direction in range(dimension):
            # direction is a parameter set and is used to calculate the slope for a single dimension
            execute_sim_command, sim_results_dir = Sim.create_execute_simulation_command(steering_script_pp,
                                                                                         simulation_cwd_pp,
                                                                                         sim_type,
                                                                                         str(self.__current_iteration),
                                                                                         str(direction + 1),
                                                                                         gradient_parameter_sets[direction],
                                                                                         verbose=self.__verbose)
            if self.__debug:
                Log.log("\t\t\tOptimizationAlgorithm.get_gradient(): execute_sim_command = {}"
                        "".format(execute_sim_command))
                Log.log("\t\t\tOptimizationAlgorithm.get_gradient(): sim_results_dir = {}"
                        "".format(sim_results_dir))
            sim_results_dirs_pp.append(sim_results_dir)

            try:
                sim_pp = subprocess.Popen(execute_sim_command, stdout=subprocess.PIPE)
            except:
                Log.errorexit("ERROR in OptimizationAlgorithm.get_gradient(): Failed to run {}. subprocess.Popen(...)"
                              "".format(direction))
            if self.__debug:
                Log.log("\t\t\tOptimizationAlgorithm.get_gradient(): sim_pp = {}".format(sim_pp))

            try:
                sim_stdout = sim_pp.stdout.read()
            except:
                Log.errorexit("ERROR in OptimizationAlgorithm.get_gradient(): Failed to execute sim_pp.stdout.read().")
            if self.__debug:
                Log.log("\t\t\tOptimizationAlgorithm.get_gradient(): sim_stdout = {}".format(sim_stdout))

            try:
                batch_job_id = Sim.get_job_id(sim_stdout)
            except:
                Log.errorexit("ERROR in OptimizationAlgorithm.get_gradient(): Failed to execute Sim.get_job_id().")
            if self.__debug:
                Log.log("\t\t\tOptimizationAlgorithm.get_gradient(): batch_job_id = {}".format(batch_job_id))

            # check & wait for script to terminate
            while 1:
                if sim_pp.poll() == 0:
                    break
                else:
                    time.sleep(1)

            Log.log("\t\t\tOptimizationAlgorithm.get_gradient(): Submitted batch job {}".format(batch_job_id))
            JobIDs.append(batch_job_id)

        # qmmm simulations
        sim_results_dirs_qm = []  # collect paths of sim results to do the evaluation and get results
        steering_script_qm = self.__config.get("QMMM", "steering_script")
        steering_script_qm = os.path.join(self.__cwd, steering_script_qm)
        simulation_cwd_qm = os.path.join(self.__cwd, "QMMM")
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): steering_script_qm = {}".format(steering_script_qm))
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): simulation_cwd_qm = {}".format(simulation_cwd_qm))

        current_parameter_set_amber = Sim.lj_parameters_gmx2amber(current_parameter_set,
                                                                  ["sig", "sig", "eps", "eps"])
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): current_parameter_set_amber = {}"
                    "".format(current_parameter_set_amber))

        execute_sim_command, sim_results_dir = Sim.create_execute_simulation_command(steering_script_qm,
                                                                                     simulation_cwd_qm,
                                                                                     sim_type,
                                                                                     str(self.__current_iteration),
                                                                                     "0",
                                                                                     current_parameter_set_amber,
                                                                                     verbose=self.__verbose)
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): execute_sim_command = {}"
                    "".format(execute_sim_command))
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): sim_results_dir = {}"
                    "".format(sim_results_dir))
        sim_results_dirs_qm.append(sim_results_dir)

        sim_qm = None  # initialize variable
        try:
            sim_qm = subprocess.Popen(execute_sim_command, stdout=subprocess.PIPE)
        except:
            Log.errorexit("ERROR in OptimizationAlgorithm.get_gradient(): Failed to run 0. subprocess.Popen(...)")
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): sim_qm = {}".format(sim_qm))

        # get jobID
        sim_stdout = None  # initialize variable
        try:
            sim_stdout = sim_qm.stdout.read()
        except:
            Log.errorexit("ERROR in OptimizationAlgorithm.get_gradient(): Failed to execute sim_qm.stdout.read().")
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): sim_stdout = {}".format(sim_stdout))

        batch_job_id = None  # initialize variable
        try:
            batch_job_id = Sim.get_job_id(sim_stdout)
        except:
            Log.errorexit("ERROR in OptimizationAlgorithm.get_gradient(): Failed to execute Sim.get_job_id().")
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): batch_job_id = {}".format(batch_job_id))

        # check & wait for script to terminate
        while 1:
            if sim_qm.poll() == 0:
                break
            else:
                time.sleep(1)

        Log.log("\t\tOptimizationAlgorithm.get_gradient(): Submitted batch job {}".format(batch_job_id))
        JobIDs.append(batch_job_id)

        for direction in range(dimension):
            # direction is a parameter set and is used to calculate the slope for a single dimension
            current_parameter_set_amber = Sim.lj_parameters_gmx2amber(gradient_parameter_sets[direction],
                                                                      ["sig", "sig", "eps", "eps"])
            if self.__debug:
                Log.log("\t\t\tOptimizationAlgorithm.get_gradient(): current_parameter_set_amber = {}"
                        "".format(current_parameter_set_amber))
            execute_sim_command, sim_results_dir = Sim.create_execute_simulation_command(steering_script_qm,
                                                                                         simulation_cwd_qm,
                                                                                         sim_type,
                                                                                         str(self.__current_iteration),
                                                                                         str(direction + 1),
                                                                                         current_parameter_set_amber,
                                                                                         verbose=self.__verbose)
            if self.__debug:
                Log.log("\t\t\tOptimizationAlgorithm.get_gradient(): execute_sim_command = {}"
                        "".format(execute_sim_command))
                Log.log("\t\t\tOptimizationAlgorithm.get_gradient(): sim_results_dir = {}"
                        "".format(sim_results_dir))
            sim_results_dirs_qm.append(sim_results_dir)

            try:
                sim_qm = subprocess.Popen(execute_sim_command, stdout=subprocess.PIPE)
            except:
                Log.errorexit("ERROR in OptimizationAlgorithm.get_gradient(): Failed to run {}. subprocess.Popen(...)"
                              "".format(direction))
            if self.__debug:
                Log.log("\t\t\tOptimizationAlgorithm.get_gradient(): sim_qm = {}".format(sim_qm))

            try:
                sim_stdout = sim_qm.stdout.read()
            except:
                Log.errorexit("ERROR in OptimizationAlgorithm.get_gradient: Failed to execute sim_pp.stdout.read().")
            if self.__debug:
                Log.log("\t\t\tOptimizationAlgorithm.get_gradient(): sim_stdout = {}".format(sim_stdout))

            try:
                batch_job_id = Sim.get_job_id(sim_stdout)
            except:
                Log.errorexit("ERROR in OptimizationAlgorithm.get_gradient(): Failed to execute Sim.get_job_id().")
            if self.__debug:
                Log.log("\t\t\tOptimizationAlgorithm.get_gradient(): batch_job_id = {}".format(batch_job_id))

            # check & wait for script to terminate
            while 1:
                if sim_qm.poll() == 0:
                    break
                else:
                    time.sleep(1)

            Log.log("\t\t\tOptimizationAlgorithm.get_gradient(): Submitted batch job {}".format(batch_job_id))
            JobIDs.append(batch_job_id)

        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): JobIDs = {}".format(JobIDs))
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): sim_results_dirs_pp = {}".format(sim_results_dirs_pp))
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): sim_results_dirs_qm = {}".format(sim_results_dirs_qm))

        Sim.wait_for_slurm_cluster_jobs(JobIDs)

        ############################################
        # Start evaluation for current parameter set
        eval_script_pp = self.__config.get("PhysProp", "eval_script")
        eval_script_pp = os.path.join(self.__cwd, eval_script_pp)
        collect_script_pp = self.__config.get("PhysProp", "collect_script")
        collect_script_pp = os.path.join(self.__cwd, collect_script_pp)
        cleanup_script_pp = self.__config.get("PhysProp", "cleanup_script")
        cleanup_script_pp = os.path.join(self.__cwd, cleanup_script_pp)
        simulation_results_pp = Sim.get_simulation_results(sim_results_dirs_pp, eval_script_pp, collect_script_pp,
                                                           cleanup_script_pp)
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): eval_script_pp = {}".format(eval_script_pp))
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): collect_script_pp = {}".format(collect_script_pp))
        if self.__verbose or self.__debug:
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): simulation_results_pp = {}"
                    "".format(simulation_results_pp))

        eval_script_qm = self.__config.get("QMMM", "eval_script")
        eval_script_qm = os.path.join(self.__cwd, eval_script_qm)
        collect_script_qm = self.__config.get("QMMM", "collect_script")
        collect_script_qm = os.path.join(self.__cwd, collect_script_qm)
        simulation_results_qm = Sim.get_simulation_results(sim_results_dirs_qm, eval_script_qm, collect_script_qm)
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): eval_script_qm = {}".format(eval_script_qm))
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): collect_script_qm = {}".format(collect_script_qm))
        if self.__verbose or self.__debug:
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): simulation_results_qm = {}"
                    "".format(simulation_results_qm))

        if not len(simulation_results_pp) == len(simulation_results_qm):
            Log.errorexit("ERROR in OptimizationAlgorithm.get_gradient(): "
                          "len(simulation_results_pp) != len(simulation_results_qm.\n"
                          "{}\n"
                          "{}".format(simulation_results_pp, simulation_results_qm))

        # evaluate loss function for x
        f0 = None  # initialize variable
        try:
            f0 = self.__loss_function.get_function_value([simulation_results_pp[0], simulation_results_qm[0]])
        except:
            Log.errorexit("ERROR in OptimizationAlgorithm.get_gradient(): "
                          "f0 = self.__loss_function.get_function_value([simulation_results_pp[0], "
                          "simulation_results_qm[0]]) failed.")
        try:
            f0 = float(f0)
        except:
            Log.errorexit("ERROR in OptimizationAlgorithm.get_gradient(): "
                          "Could not cast f0 to float. f0 = {}".format(f0))
        if self.__verbose or self.__debug:
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): f0 = {}".format(f0))

        grad = []
        for i in range(1, len(simulation_results_pp)):
            # evaluate loss function for x+h
            fi = None  # initialize variable
            try:
                fi = self.__loss_function.get_function_value([simulation_results_pp[i], simulation_results_qm[i]])
            except:
                Log.errorexit("ERROR in OptimizationAlgorithm.get_gradient(): "
                              "fi = self.__loss_function.get_function_value([simulation_results_pp[{}], "
                              "simulation_results_qm[{}]) failed.".format(i, i))
            try:
                fi = float(fi)
            except:
                Log.errorexit("ERROR in OptimizationAlgorithm.get_gradient(): "
                              "Could not cast fi to float. fi = {}".format(fi))
            if self.__debug:
                Log.log("\t\t\tOptimizationAlgorithm.get_gradient(): fi = {}".format(fi))

            g = None  # initialize variable
            try:
                g = (fi - f0)/h
            except:
                Log.errorexit("ERROR in OptimizationAlgorithm.get_gradient(): "
                              "Could not calculate gradient direction: (fi - f0)/h \n"
                              "({} - {})/{}}".format(fi, f0, h))
            if self.__debug:
                Log.log("\t\t\tOptimizationAlgorithm.get_gradient(): g = {}".format(g))

            grad.append(g)

        if self.__verbose or self.__debug:
            Log.log("\t\tOptimizationAlgorithm.get_gradient(): grad = {}".format(grad))
        Log.log("Finished getting gradient.")
        Log.log("Gradient grad = {}".format(grad))
        return f0, grad

    def get_step_length(self, min_parameters, max_parameters, current_parameter_set, f0, descent):
        """ calculates step length based on armijo algorithm for the calculation of the new parameter set """
        Log = self.__log
        [step_length, f_new] = self.__step_length_control.calculate_step_length(min_parameters, max_parameters,
                                                                                current_parameter_set, f0, descent)
        if self.__debug:
            Log.log("\t\tOptimizationAlgorithm.get_step_length(): step_length = {}".format(step_length))
            Log.log("\t\tOptimizationAlgorithm.get_step_length(): f_new = {}".format(f_new))

        return step_length, f_new

    def __del__(self):
        """ Destructor """
        del self
