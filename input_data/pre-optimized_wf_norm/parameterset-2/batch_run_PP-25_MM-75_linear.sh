#!/bin/bash
#SBATCH --partition=hpc3
#SBATCH --nodes=1
#SBATCH --mem 1G
#SBATCH --time=72:00:00
#SBATCH --job-name=lPP25p2

./run_PP-25_MM-75_linear.sh
