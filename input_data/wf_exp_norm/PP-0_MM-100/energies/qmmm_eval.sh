#! /bin/bash
eval_cwd=$1
#echo "eval_cwd: $eval_cwd"

cd $eval_cwd
sbatch batch_slurm_eval_RCE.sh
