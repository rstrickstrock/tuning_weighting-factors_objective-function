#   Armijo Step Length Control
#
#   start_doc
#   Script:         armijo_step_length_control.py
#
#   Author:         Marco Huelsmann
#                   Robin Strickstrock
#
#   Date:           18-03-2022
#
#   Description:    class ArmijoStepLengthControl
#
#   Usage:          by defining an instance
#
#   Arguments:
#
#   Options:
#
#   Output:
#
#   Imported:       step_length_control
#                   math
#                   simulations
#                   subprocess
#                   os
#                   time
#
#   Called:
#
#   Modifications:
#   end_doc

###############################################################################
#   required python modules
###############################################################################
from utilities.math import Math
from generic_optimizer.step_length_control import StepLengthControl
from simulation_interface.simulations import Simulations
import os
import subprocess
import time


class ArmijoStepLengthControl(StepLengthControl):

    def __init__(self, logging_object, verbose, debug, loss_function, config):
        """ Constructor """
        self.__log = logging_object
        Log = self.__log
        self.__verbose = verbose
        self.__debug = debug
        self.__config = config
        self.__loss_function = loss_function
        if self.__debug:
            Log.log("\tArmijoStepLengthControl.__init__(): self.__verbose = {}".format(self.__verbose))
            Log.log("\tArmijoStepLengthControl.__init__(): self.__debug = {}".format(self.__debug))
            Log.log("\tArmijoStepLengthControl.__init__(): self.__config = {}".format(self.__config))
            Log.log("\tArmijoStepLengthControl.__init__(): self.__loss_function = {}".format(self.__loss_function))

        self.__math = Math(Log)
        self.__sim = Simulations(Log, self.__verbose, self.__debug)

        self.__cwd = None  # initialize variable
        try:
            self.__cwd = self.__config.get("SYS", "cwd")
        except:
            Log.errorexit("Error in ArmijoStepLengthControl.__init__(): "
                          "could not get cwd from config file.")
        if self.__debug:
            Log.log("\tArmijoStepLengthControl.__init__(): self.__cwd = {}".format(self.__cwd))

        StepLengthControl.__init__(self, Log, self.__verbose, self.__debug, self.__config)
        self.__sl_max_iterations = self.get_sl_max_iterations()
        self.__sl_method = self.get_sl_method()
        if self.__debug:
            Log.log("\tArmijoStepLengthControl.__init__(): self.__sl_max_iterations = {}"
                    "".format(self.__sl_max_iterations))
            Log.log("\tArmijoStepLengthControl.__init__(): self.__sl_method = {}".format(self.__sl_method))

        #   get parameters for armijo step length control
        self.__armijo_sigma = None  # initialize variable
        try:
            self.__armijo_sigma = float(self.__config.get("OPT", "armijo_sigma"))
        except ValueError:
            Log.errorexit("ERROR in ArmijoStepLengthControl.__init__(): "
                          "armijo_sigma must be a float.")
        except:
            Log.errorexit("ERROR in ArmijoStepLengthControl.__init__(): "
                          "Parameter 'armijo_sigma' not indicated in 'OPT'.")
        if self.__debug:
            Log.log("\tArmijoStepLengthControl.__init__(): self.__armijo_sigma = {}".format(self.__armijo_sigma))

        if self.__armijo_sigma <= 0 or self.__armijo_sigma >= 1:
            Log.errorexit("ERROR in ArmijoStepLengthControl.__init__(): "
                          "parameter 'armijo_sigma' ({}) must be 0 < armijo_sigma < 1.".format(self.__armijo_sigma))

        # TODO:
        #   for algorithm "trust region" and "exact" parameter beta is needed.
        #   not implemented, yet

        #   get number of parallel armijo evaluations
        # TODO:
        #   currently no parallelization implemented. Max value = Min value = 1.
        self.__armijo_parallel_evaluations = None  # initialize variable
        try:
            self.__armijo_parallel_evaluations = int(self.__config.get("OPT", "armijo_parallel_evaluations"))
        except ValueError:
            Log.errorexit("ERROR in ArmijoStepLengthControl.__init__(): "
                          "armijo_parallel_evaluations must be an integer.")
        except:
            Log.errorexit("ERROR in ArmijoStepLengthControl.__init__(): "
                          "Parameter 'armijo_parallel_evaluations' not indicated in 'OPT'.")
        if self.__debug:
            Log.log("\tArmijoStepLengthControl.__init__(): self.__armijo_parallel_evaluations = {}"
                    "".format(self.__armijo_parallel_evaluations))

        if self.__armijo_parallel_evaluations <= 0:
            Log.errorexit("ERROR in ArmijoStepLengthControl.__init__(): "
                          "Parameter 'armijo_parallel_evaluations' must be greater than 0.")

        if not self.__armijo_parallel_evaluations == 1:
            Log.errorexit("ERROR in ArmijoStepLengthControl.__init__(): "
                          "Currently 'armijo_parallel_evaluations' must be 1.")

        #   get initial armijo step length
        self.__initial_step_length = None  # initialize variable
        try:
            self.__initial_step_length = self.__config.get("OPT", "armijo_initial_sl")
        except:
            Log.errorexit("ERROR in ArmijoStepLengthControl.__init__(): "
                          "No armijo_initial_sl defined.")
        if self.__debug:
            Log.log("\tArmijoStepLengthControl.__init__(): self.__initial_step_length = {}"
                    "".format(self.__initial_step_length))
        try:
            self.__initial_step_length = float(self.__initial_step_length)
        except:
            Log.errorexit("ERROR in ArmijoStepLengthControl.__init__(): "
                          "Given value for armijo_initial_sl ('{}')must be a float.".format(self.__step_length))

        if self.__armijo_parallel_evaluations > self.__sl_max_iterations:
            Log.log("WARNING: number of parallel armijo evaluations ({}) > number of max iterations ({}). "
                    "Set number of max. parallel evaluations to {}!".format(self.__armijo_parallel_evaluations,
                                                                            self.__sl_max_iterations,
                                                                            self.__sl_max_iterations))

    def get_armijo_sigma(self):
        """ return sigma for armijo step length control """
        Log = self.__log
        try:
            return self.__armijo_sigma
        except:
            Log.errorexit("ERROR in ArmijoStepLengthControl.get_armijo_sigma(): "
                          "could not get sigma for armijo slc.")

    def get_armijo_parallel_evaluations(self):
        """ return number of parallel evaluations for armijo slc """
        Log = self.__log
        try:
            return self.__armijo_parallel_evaluations
        except:
            Log.errorexit("ERROR in ArmijoStepLengthControl.get_armijo_parallel_evaluations(): "
                          "could not get number of parallel evaluations for armijo slc.")

    def calculate_step_length(self, min_parameters, max_parameters, current_parameter_set, current_iteration, f0,
                              descent):
        """ calculate step length based on armijo algorithm """
        Log = self.__log
        math = self.__math
        Sim = self.__sim
        Log.log("Calculating step length for optimization step {}".format(current_iteration))

        current_sl_iteration = 1
        if self.__debug:
            Log.log("\tArmijoStepLengthControl.calculate_step_length(): current_sl_iteration = {}"
                    "".format(current_sl_iteration))
        # normalize decent vector to length 1, multiply with initial step length
        norm_descent = None  # initialize variable
        try:
            norm_descent = math.norm(descent)
        except:
            Log.errorexit("ERROR in ArmijoStepLengthControl.calculate_step_length(): "
                          "Could not calculate 'norm_descent = math.norm(descent)'.")
        if self.__debug:
            Log.log("\tArmijoStepLengthControl.calculate_step_length(): norm_descent = {}".format(norm_descent))

        try:
            descent = math.scalar_vector_mult((1 / norm_descent), descent)
        except:
            Log.errorexit("ERROR in ArmijoStepLengthControl.calculate_step_length(): "
                          "Could not calculate 'descent = math.scalar_vector_mult((1 / norm_descent), descent)'.")
        if self.__debug:
            Log.log("\tArmijoStepLengthControl.calculate_step_length(): descent = {}".format(descent))

        # set step length to initial step length
        step_length = self.__initial_step_length
        if self.__debug:
            Log.log("\tArmijoStepLengthControl.calculate_step_length(): step_length = {}".format(step_length))

        # iteratively half step length until f_x < f0
        # TODO: implement parallel armijo evaluations

        while True:
            # check if step length generates feasible parameters within constraints
            x_new = self.is_step_length_feasible(min_parameters, max_parameters, current_parameter_set, descent,
                                                 step_length)
            if self.__debug:
                Log.log("\t\tArmijoStepLengthControl.calculate_step_length(): x_new = {}".format(x_new))

            # if x_new is not feasible: x_new = False, else it contains the parameters
            if not x_new:
                # step_length is too large, new_parameter_set is out of pre-defined boundaries
                # half step length and try again
                step_length = 0.5 * step_length
                if self.__debug:
                    Log.log("\t\tArmijoStepLengthControl.calculate_step_length(): step_length not feasible.")
                    Log.log("\t\tArmijoStepLengthControl.calculate_step_length(): step_length = {}"
                            "".format(step_length))
            else:
                # use x_new to calculate loss-function value. Compare it to f0.
                # If 'better' (less) accept new parameters / step length,
                # if 'worse' (higher) discard and half step length
                sim_type = str("a")
                JobIDs = []

                # TODO: put starting the simulations in a function/loop? (see optimization_algorithm)
                #  #  basically hardcoded without the possibility to add further
                #  #  consider: for section in config.get_setcions() == PhysProp || QMMM
                sim_results_dirs_pp = []  # collect paths of sim results to do the evaluation and get results
                steering_script_pp = self.__config.get("PhysProp", "steering_script")
                steering_script_pp = os.path.join(self.__cwd, steering_script_pp)
                simulation_cwd_pp = os.path.join(self.__cwd, "PhysProp")
                if self.__debug:
                    Log.log("\t\tArmijoStepLengthControl.calculate_step_length(): steering_script_pp = {}"
                            "".format(steering_script_pp))
                    Log.log("\t\tArmijoStepLengthControl.calculate_step_length(): simulation_cwd_pp = {}"
                            "".format(simulation_cwd_pp))

                # physprop simulation
                execute_sim_command, sim_results_dir = Sim.create_execute_simulation_command(steering_script_pp,
                                                                                             simulation_cwd_pp,
                                                                                             sim_type,
                                                                                             str(current_iteration),
                                                                                             str(current_sl_iteration),
                                                                                             x_new,
                                                                                             verbose=self.__verbose)
                if self.__debug:
                    Log.log("\t\tArmijoStepLengthControl.calculate_step_length(): execute_sim_command = {}"
                            "".format(execute_sim_command))
                    Log.log("\t\tArmijoStepLengthControl.calculate_step_length(): sim_results_dir = {}"
                            "".format(sim_results_dir))

                sim_results_dirs_pp.append(sim_results_dir)

                sim_pp = None  # initialize variable
                try:
                    sim_pp = subprocess.Popen(execute_sim_command, stdout=subprocess.PIPE)
                except:
                    Log.errorexit("ERROR in ArmijoStepLengthControl.calculate_step_length(): "
                                  "Failed to run subprocess.Popen(...) for pp part of {}.{}.{}."
                                  "".format(sim_type, current_iteration, current_sl_iteration))
                if self.__debug:
                    Log.log("\t\tArmijoStepLengthControl.calculate_step_length(): sim_pp = {}"
                            "".format(sim_pp))

                # get jobID
                sim_stdout = None  # initialize variable
                try:
                    sim_stdout = sim_pp.stdout.read()
                except:
                    Log.errorexit("ERROR in ArmijoStepLengthControl.calculate_step_length(): "
                                  "Failed to execute sim_pp.stdout.read().")
                if self.__debug:
                    Log.log("\t\tArmijoStepLengthControl.calculate_step_length(): sim_stdout = {}"
                            "".format(sim_stdout))

                batch_job_id = None  # initialize variable
                try:
                    batch_job_id = Sim.get_job_id(sim_stdout)
                except:
                    Log.errorexit("ERROR in ArmijoStepLengthControl.calculate_step_length(): "
                                  "Failed to execute Sim.get_job_id().")
                if self.__debug:
                    Log.log("\t\tArmijoStepLengthControl.calculate_step_length(): batch_job_id = {}"
                            "".format(batch_job_id))

                # check & wait for script to terminate
                while 1:
                    if sim_pp.poll() == 0:
                        break
                    else:
                        time.sleep(1)

                Log.log("Submitted batch job {}".format(batch_job_id))
                JobIDs.append(batch_job_id)

                # qmmm simulation
                sim_results_dirs_qm = []  # collect paths of sim results to do the evaluation and get results
                steering_script_qm = self.__config.get("QMMM", "steering_script")
                steering_script_qm = os.path.join(self.__cwd, steering_script_qm)
                simulation_cwd_qm = os.path.join(self.__cwd, "QMMM")
                if self.__debug:
                    Log.log("\t\tArmijoStepLengthControl.calculate_step_length(): steering_script_qm = {}"
                            "".format(steering_script_qm))
                    Log.log("\t\tArmijoStepLengthControl.calculate_step_length(): simulation_cwd_qm = {}"
                            "".format(simulation_cwd_qm))

                x_new_amber = Sim.lj_parameters_gmx2amber(x_new, ["sig", "sig", "eps", "eps"])
                if self.__debug:
                    Log.log("\t\tArmijoStepLengthControl.calculate_step_length(): x_new_amber = {}"
                            "".format(x_new_amber))
                execute_sim_command, sim_results_dir = Sim.create_execute_simulation_command(steering_script_qm,
                                                                                             simulation_cwd_qm,
                                                                                             sim_type,
                                                                                             str(current_iteration),
                                                                                             str(current_sl_iteration),
                                                                                             x_new_amber,
                                                                                             verbose=self.__verbose)
                if self.__debug:
                    Log.log("\t\tArmijoStepLengthControl.calculate_step_length(): execute_sim_command = {}"
                            "".format(execute_sim_command))
                    Log.log("\t\tArmijoStepLengthControl.calculate_step_length(): sim_results_dir = {}"
                            "".format(sim_results_dir))

                sim_results_dirs_qm.append(sim_results_dir)

                sim_qm = None  # initialize variable
                try:
                    sim_qm = subprocess.Popen(execute_sim_command, stdout=subprocess.PIPE)
                except:
                    Log.errorexit("ERROR in ArmijoStepLengthControl.calculate_step_length(): "
                                  "Failed to run subprocess.Popen(...) for qm part of {}.{}.{}."
                                  "".format(sim_type, current_iteration, current_sl_iteration))
                if self.__debug:
                    Log.log("\t\tArmijoStepLengthControl.calculate_step_length(): sim_qm = {}"
                            "".format(sim_qm))

                # get jobID
                sim_stdout = None  # initialize variable
                try:
                    sim_stdout = sim_qm.stdout.read()
                except:
                    Log.errorexit("ERROR in ArmijoStepLengthControl.calculate_step_length(): "
                                  "Failed to execute sim_qm.stdout.read().")
                if self.__debug:
                    Log.log("\t\tArmijoStepLengthControl.calculate_step_length(): sim_stdout = {}"
                            "".format(sim_stdout))

                batch_job_id = None  # initialize variable
                try:
                    batch_job_id = Sim.get_job_id(sim_stdout)
                except:
                    Log.errorexit("ERROR in ArmijoStepLengthControl.calculate_step_length(): "
                                  "Failed to execute Sim.get_job_id().")
                if self.__debug:
                    Log.log("\t\tArmijoStepLengthControl.calculate_step_length(): batch_job_id = {}"
                            "".format(batch_job_id))
                # check & wait for script to terminate
                while 1:
                    if sim_qm.poll() == 0:
                        break
                    else:
                        time.sleep(1)

                Log.log("Submitted batch job {}".format(batch_job_id))
                JobIDs.append(batch_job_id)

                # wait for jobs to finish
                Sim.wait_for_slurm_cluster_jobs(JobIDs)

                # get simulation results
                eval_script_pp = self.__config.get("PhysProp", "eval_script")
                eval_script_pp = os.path.join(self.__cwd, eval_script_pp)
                collect_script_pp = self.__config.get("PhysProp", "collect_script")
                collect_script_pp = os.path.join(self.__cwd, collect_script_pp)
                cleanup_script_pp = self.__config.get("PhysProp", "cleanup_script")
                cleanup_script_pp = os.path.join(self.__cwd, cleanup_script_pp)
                if self.__debug:
                    Log.log("\t\tArmijoStepLengthControl.calculate_step_length(): eval_script_pp = {}"
                            "".format(eval_script_pp))
                    Log.log("\t\tArmijoStepLengthControl.calculate_step_length(): collect_script_pp = {}"
                            "".format(collect_script_pp))
                simulation_results_pp = Sim.get_simulation_results(sim_results_dirs_pp, eval_script_pp,
                                                                   collect_script_pp, cleanup_script_pp)
                if self.__verbose or self.__debug:
                    Log.log("\t\tArmijoStepLengthControl.calculate_step_length(): simulation_results_pp = {}"
                            "".format(simulation_results_pp))

                eval_script_qm = self.__config.get("QMMM", "eval_script")
                eval_script_qm = os.path.join(self.__cwd, eval_script_qm)
                collect_script_qm = self.__config.get("QMMM", "collect_script")
                collect_script_qm = os.path.join(self.__cwd, collect_script_qm)
                if self.__debug:
                    Log.log("\t\tArmijoStepLengthControl.calculate_step_length(): eval_script_qm = {}"
                            "".format(eval_script_qm))
                    Log.log("\t\tArmijoStepLengthControl.calculate_step_length(): collect_script_qm = {}"
                            "".format(collect_script_qm))
                simulation_results_qm = Sim.get_simulation_results(sim_results_dirs_qm, eval_script_qm,
                                                                   collect_script_qm)
                if self.__verbose or self.__debug:
                    Log.log("\t\tArmijoStepLengthControl.calculate_step_length(): simulation_results_qm = {}"
                            "".format(simulation_results_qm))

                if not len(simulation_results_pp) == len(simulation_results_qm) == 1:
                    Log.errorexit("ERROR in ArmijoStepLengthControl.calculate_step_length(): "
                                  "len(simulation_results_pp) != len(simulation_results_qm != 1.\n"
                                  "simulation_results_pp: {}\n"
                                  "simulation_results_qm: {}".format(simulation_results_pp, simulation_results_qm))

                f_new = None  # initialize variable
                try:
                    f_new = self.__loss_function.get_function_value([simulation_results_pp, simulation_results_qm])
                except:
                    Log.errorexit("ERROR in ArmijoStepLengthControl.calculate_step_length(): "
                                  "f_new = self.__loss_function.get_function_value([simulation_results_pp, "
                                  "simulation_results_qm]) failed.")
                try:
                    f_new = float(f_new)
                except:
                    Log.errorexit("ERROR in ArmijoStepLengthControl.calculate_step_length(): "
                                  "Could not cast f_new to float. f_new = {}".format(f_new))
                if self.__verbose or self.__debug:
                    Log.log("\t\tArmijoStepLengthControl.calculate_step_length(): f_new = {}"
                            "".format(f_new))

                # check if new parameters perform better
                # if they do, return step length and loss function value
                # else repeat with halved step length

                if f_new < f0:
                    Log.log("Calculation of step length finished.")
                    return step_length, f_new
                else:
                    step_length = 0.5 * step_length
                    if self.__debug:
                        Log.log("\t\tArmijoStepLengthControl.calculate_step_length(): step_length = {}"
                                "".format(step_length))

                # increase current_sl_iteration. Is only increased if step_length is feasible.
                # results in possibility that step_length is halved more than max_sl_iterations times.
                current_sl_iteration = current_sl_iteration + 1
                if self.__debug:
                    Log.log("\tArmijoStepLengthControl.calculate_step_length(): current_sl_iteration = {}"
                            "".format(current_sl_iteration))

            # check if max sl iterations are performed
            if current_sl_iteration == self.__sl_max_iterations:
                Log.log("WARNING: ArmijoStepLengthControl.calculate_step_length() - "
                        "exceed max step length iterations of {}"
                        "returning step_length = 0.0 and f_new = -1.0".format(self.__sl_max_iterations))
                return 0.0, -1.0

    def __del__(self):
        """ Destructor """
        del self
