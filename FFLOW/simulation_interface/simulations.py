#   Simulations
#
#   start_doc
#   Script:         simulations.py
#
#   Author:         Robin Strickstrock
#
#   Date:           27-05-2022
#
#   Description:    class Simulations
#
#   Usage:          by defining an instance
#
#   Arguments:
#
#   Options:
#
#   Output:
#
#   Imported:      subprocess
#                  time
#                  os
#
#   Called:
#
#   Modifications:
#   end_doc

###############################################################################
#   required python modules
###############################################################################
import subprocess
import time
import os


class Simulations:
    def __init__(self, logging_object, verbose, debug):
        """ Constructor """
        self.__log = logging_object
        Log = self.__log
        self.__verbose = verbose
        self.__debug = debug
        if self.__debug:
            Log.log("\t\tSimulations.__init__(): self.__verbose = {}".format(self.__verbose))
            Log.log("\t\tSimulations.__init__(): self.__debug = {}".format(self.__debug))

    def create_execute_simulation_command(self, steering_script, sim_cwd, sim_type, current_iteration, direction,
                                          parameters, script_type='sh', verbose=False):
        """ creates command string to be called via subprocess.Popen().
        Using this command will start gmx MD calculations. Per default shell scripts (type='sh') are called. """
        Log = self.__log
        command = []
        try:
            command.append(str(script_type))
        except:
            Log.errorexit("ERROR in Simulations.create_execute_simulation_command(): "
                          "could not append type: {}".format(script_type))

        try:
            command.append(str(steering_script))
        except:
            Log.errorexit("ERROR in Simulations.create_execute_simulation_command(): "
                          "could not append steering_script: {}".format(steering_script))

        try:
            command.append(str(sim_cwd))
        except:
            Log.errorexit("ERROR in Simulations.create_execute_simulation_command(): "
                          "could not append simulation cwd: {}".format(sim_cwd))

        try:
            command.append(str(sim_type))
        except:
            Log.errorexit("ERROR in Simulations.create_execute_simulation_command(): "
                          "could not append simulation type: {}".format(sim_type))

        try:
            command.append(str(current_iteration))
        except:
            Log.errorexit("ERROR in Simulations.create_execute_simulation_command(): "
                          "could not append current iteration: {}".format(current_iteration))

        try:
            command.append(str(direction))
        except:
            Log.errorexit("ERROR in Simulations.create_execute_simulation_command(): "
                          "could not append (number of gradient) direction: {}".format(direction))

        for parameter in parameters:
            try:
                command.append(str(parameter))
            except:
                Log.errorexit("ERROR in Simulations.create_execute_simulation_command(): "
                              "could not append parameter: {}".format(parameter))

        simulation_results_dir = os.path.join(sim_cwd, sim_type + "." + current_iteration + "." + direction)

        if self.__debug:
            Log.log("\t\tSimulations.create_execute_simulation_command(): command = {}".format(command))
            Log.log("\t\tSimulations.create_execute_simulation_command(): simulation_results_dir = {}"
                    "".format(simulation_results_dir))

        return command, simulation_results_dir

    def lj_parameters_gmx2amber(self, parameters, parameter_type):
        """ converts gromacs lennard-jones parameters to amber units.
        needs a list of the parameters and a list containing the type ("sig"/"eps") for each parameter """
        Log = self.__log

        # checking for same lengths
        is_same_length = None  # initialize variable
        try:
            is_same_length = (len(parameters) == len(parameter_type))
        except:
            Log.errorexit("Error in Simulations.lj_parameters_gmx2amber(): "
                          "could not compare length of lists 'parameters' and 'type'.")
        if self.__debug:
            Log.log("\t\tSimulations.lj_parameters_gmx2amber(): is_same_length = {}".format(is_same_length))

        if not is_same_length:
            Log.errorexit("Error in Simulations.lj_parameters_gmx2amber(): "
                          "lists 'parameters' and 'type' are not the same length.")

        converted_parameters = []
        for i in range(len(parameter_type)):
            par = None  # initialize variable
            try:
                par = float(parameters[i])
            except:
                Log.errorexit("Error in Simulations.lj_parameters_gmx2amber(): "
                              "could not convert parameter '{}' to float.".format(parameters[i]))
            if self.__debug:
                Log.log("\t\t\tSimulations.lj_parameters_gmx2amber(): par = {}".format(par))

            # convert parameter depending on type sig or eps
            if parameter_type[i] == "sig":
                par = par*10.0  # convert units
                par = par*1.12246205  # R_min = 2^(1/6) * sigma; 2^(1/6) ~= 1.12246205
                par = par/2  # R* = R_min/2
            elif parameter_type[i] == "eps":
                par = par/4.1868  # convert untis
            else:
                Log.errorexit("Error in Simulations.lj_parameters_gmx2amber(): "
                              "type[{}] ('{}') must be 'sig' or 'eps'.".format(i, parameter_type[i]))
            if self.__debug:
                Log.log("\t\t\tSimulations.lj_parameters_gmx2amber(): par = {}".format(par))

            converted_parameters.append(par)

        if self.__debug:
            Log.log("\t\tSimulations.lj_parameters_gmx2amber(): converted_parameters = {}".format(converted_parameters))

        return converted_parameters

    def get_job_id(self, string):
        """ returns slurm ID for job started with the sbatch command. """
        Log = self.__log
        job_id = [int(s) for s in string.split() if s.isdigit()]
        if self.__debug:
            Log.log("\t\tSimulations.get_job_id(): job_id = {}".format(job_id))

        # check if there is only one number:
        if len(job_id) > 1:
            Log.errorexit("Error in Simulations.algorithm.get_job_ID(): "
                          "string '{}' contains more than one number. Only one JOB ID is expected.".format(string))

        return job_id[0]

    def wait_for_slurm_cluster_jobs(self, JobIDs, check_interval_time=int(30)):
        """ wait until all slurm cluster jobs given in JobIDs are finised """
        Log = self.__log
        # print("JobIDs: {}".format(JobIDs))

        # check if 'check_interval_time' is an integer
        try:
            check_interval_time = float(check_interval_time)
        except:
            Log.errorexit("ERROR in Simulations.wait_for_slurm_cluster_jobs(): "
                          "parameter 'check_interval'({}) must be an integer.".format(check_interval_time))
        if self.__debug:
            Log.log("\t\tSimulations.wait_for_slurm_cluster_jobs(): check_interval_time = {}"
                    "".format(check_interval_time))

        all_jobs_terminated = False
        while not all_jobs_terminated:
            # if a job is not terminated this variable will be switched to 'False' again and the while loop continues.
            all_jobs_terminated = True
            for ID in JobIDs:
                if self.__verbose:
                    Log.log("Simulations.wait_for_slurm_cluster_jobs(): checking Job with ID: {}".format(ID))
                if self.__debug:
                    Log.log("\t\t\tSimulations.wait_for_slurm_cluster_jobs(): ID = {}".format(ID))

                check_job_status = subprocess.Popen(['squeue', '-j', str(ID)], stdout=subprocess.PIPE)
                check_job_status = check_job_status.stdout.read()
                if self.__debug:
                    Log.log("\t\t\tSimulations.wait_for_slurm_cluster_jobs(): check_job_status = {}"
                            "".format(check_job_status))

                if str(check_job_status).find(str(ID)) > 0:
                    # if variable 'check_job_status' contains the job ID, the job is still running.
                    # otherwise, it only contains the column titles but no job information and returns '-1'.
                    # wait the specified amount of time [s] and check again.
                    Log.log("Some jobs are still running. Next check in {}s.".format(check_interval_time))

                    # set all_jobs_terminated to 'False' to enter the next check iteration after check_int_time seconds
                    all_jobs_terminated = False
                    time.sleep(check_interval_time)
                    break

        # as soon all jobs have finished, the main script can advance.
        Log.log("All cluster jobs with IDs {} have terminated (successfully).".format(JobIDs))
        return

    def get_simulation_results(self, result_dirs, eval_script, collect_script,  cleanup_script=None, eval_script_type='sh',
                               collect_script_type='sh', cleanup_script_type='sh'):
        """ returns a list of simulation results """
        Log = self.__log
        results = []
        JobIDs = []

        # evaluation
        for directory in result_dirs:
            if self.__verbose or self.__debug:
                Log.log("\t\t\tSimulations.get_simulation_results(): \n"
                        "\t\t\t\teval_script: {}\n"
                        "\t\t\t\tresult_dirs: {}\n"
                        "\t\t\t\tcollect_script: {}\n"
                        "\t\t\t\tcleanup_script: {}".format(eval_script, directory, collect_script, cleanup_script))

            evaluation = None  # initialize variable
            try:
                evaluation = subprocess.Popen([eval_script_type, eval_script, directory], stdout=subprocess.PIPE)
            except:
                Log.errorexit("ERROR in Simulation.get_simulation result(): "
                              "Failed for sims in cwd: {}".format(directory))
            if self.__debug:
                Log.log("\t\t\tSimulations.get_simulation_results(): evaluation = {}".format(evaluation))

            # get jobID
            sim_stdout = None  # initialize variable
            try:
                sim_stdout = evaluation.stdout.read()
            except:
                Log.errorexit("ERROR in Simulation.get_simulation_results(): Failed to execute eval.stdout.read().")
            if self.__debug:
                Log.log("\t\t\tSimulations.get_simulation_results(): sim_stdout = {}".format(sim_stdout))

            batch_job_id = None  # initialize variable
            try:
                batch_job_id = self.get_job_id(sim_stdout)
            except:
                Log.errorexit("ERROR in Simulation.get_simulation_results(): Failed to execute self.get_job_id().")
            if self.__verbose:
                Log.log("Simulation.get_simulation_result(): JobID for collecting results: {}".format(batch_job_id))
            if self.__debug:
                Log.log("\t\t\tSimulations.get_simulation_results(): batch_job_id = {}".format(batch_job_id))

            # check & wait for script to terminate
            while 1:
                if evaluation.poll() == 0:
                    break
                else:
                    time.sleep(1)

            Log.log("Submitted batch job {}".format(batch_job_id))
            JobIDs.append(batch_job_id)

        if self.__debug:
            Log.log("\t\tSimulations.get_simulation_results(): JobIDs = {}".format(JobIDs))

        self.wait_for_slurm_cluster_jobs(JobIDs)

        # collect results
        for directory in result_dirs:
            collect = None  # initialize variable
            try:
                collect = subprocess.Popen([collect_script_type, collect_script, directory], stdout=subprocess.PIPE)
            except:
                Log.errorexit("ERROR in Simulation.get_simulation_result(): Failed to collect sim results.")
            if self.__debug:
                Log.log("\t\t\tSimulations.get_simulation_results(): collect = {}".format(collect))

            result = []  # initialize variable
            while True:
                res = None  # initialize variable
                try:
                    res = collect.stdout.readline()
                except:
                    Log.errorexit("ERROR in Simulation.get_simulation result(): Failed to read stdout: "
                                  "'collect sim results'.")
                if self.__debug:
                    Log.log("\t\t\t\tSimulations.get_simulation_results(): res = {}".format(res))

                if not res:
                    break

                # res contains something like: b'696.551\n'
                # if self.__verbose:
                #     print("simulation.get_simulation_result() - result: {}".format(res))

                try:
                    res = float(res)
                except:
                    Log.errorexit("ERROR in Simulation.get_simulation_result(): "
                                  "Failed to cast 'result' to float. result = '{}'".format(res))

                result.append(res)
            if self.__debug:
                Log.log("\t\t\tSimulations.get_simulation_results(): result = {}".format(result))

            results.append(result)

            # cleanup simulation working directory: eg. delete unnecessary trajectories that use much disk space
            # variable cleanup_script=None by default. Change if something should be executed.
            if cleanup_script is not None:
                if self.__debug:
                    Log.log("\t\t\tSimulations.get_simulation_results(): executing cleanup script")
                cleanup = None  # initialize variable
                try:
                    cleanup = subprocess.Popen([cleanup_script_type, cleanup_script, directory], stdout=subprocess.PIPE)
                except:
                    Log.errorexit("ERROR in Simulation.get_simulation_result(): Failed execute cleanup script.")
                if self.__debug:
                    Log.log("\t\t\tSimulations.get_simulation_results(): cleanup = {}".format(cleanup))

            time.sleep(0.5)

        if self.__debug:
            Log.log("\t\tSimulations.get_simulation_results(): results = {}".format(results))

        return results

    def __del__(self):
        """ Destructor """
        del self
