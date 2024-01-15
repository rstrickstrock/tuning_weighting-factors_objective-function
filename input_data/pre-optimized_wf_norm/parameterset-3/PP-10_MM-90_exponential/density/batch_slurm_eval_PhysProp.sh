#! /bin/bash
#SBATCH --partition=hpc3
#SBATCH --nodes=1
#SBATCH --mem 20G
#SBATCH --time=00:05:00
#SBATCH --job-name=eval_density

echo -e "density\n" | gmx energy -f prod.edr -o density
