#!/bin/bash
#SBATCH --partition=hpc3
#SBATCH --nodes=1
#SBATCH --mem 1G
#SBATCH --time=72:00:00
#SBATCH --job-name=lPP95MM05

./run_PP-95_MM-05.sh
