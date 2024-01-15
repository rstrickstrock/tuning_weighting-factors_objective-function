#!/bin/bash
#SBATCH --partition=hpc3
#SBATCH --nodes=1
#SBATCH --mem 50G
#SBATCH --time=00:10:00
#SBATCH --job-name=RCE

module purge
# module list
module load python3/default
module load openmpi/gnu
module load amber/AmberTools18
module load gcc/9.1.0
# module list

./run_mm.sh
