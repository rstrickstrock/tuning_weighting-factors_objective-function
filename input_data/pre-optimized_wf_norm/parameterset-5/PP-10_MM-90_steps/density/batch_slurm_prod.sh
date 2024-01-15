#!/bin/bash
#SBATCH --partition=hpc3
#SBATCH --nodes=1
#SBATCH --mem 20G
#SBATCH --time=02:00:00
#SBATCH --job-name=density

gmx grompp -f prod.mdp -c equilibrated.gro -t equilibrated.cpt -p topol.top -o prod.tpr

gmx mdrun -v -deffnm prod

