#!/bin/bash
#SBATCH --partition=hpc3
#SBATCH --nodes=1
#SBATCH --mem 1G
#SBATCH --time=72:00:00
#SBATCH --job-name=uPP25MM75

./run_PP-25_MM-75.sh
