#!/bin/bash
#SBATCH --partition=hpc3
#SBATCH --nodes=1
#SBATCH --mem 1G
#SBATCH --time=00:05:00
#SBATCH --job-name=eval_RCE

module purge
# module list
module load python3/default
module load openmpi/gnu
module load amber/AmberTools18
module load gcc/9.1.0
# module list

python qmmm_eval.py
