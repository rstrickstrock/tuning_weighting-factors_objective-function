#!/bin/bash
script_path=$(dirname $0)
sim_cwd=$1
sim_type=$2
iteration=$3
direction=$4
sig1=$5
sig2=$6
eps1=$7
eps2=$8

sim_cwd=$sim_cwd/$sim_type.$iteration.$direction
#echo $sim_cwd
# create working dir and copy all necessary files
mkdir $sim_cwd
cp $script_path/batch_slurm_prod.sh $script_path/prod.mdp $sim_cwd
cp $script_path/equilibrated/equilibrated.cpt $script_path/equilibrated/equilibrated.gro $sim_cwd
ln -s $script_path/force-field.ff $sim_cwd/force-field.ff

#adapt parameters
#sed 's/day/night/' <old >new
sed "s/opls_135 opls_135    1    /opls_135 opls_135    1    $sig1    $eps1/" <$script_path/equilibrated/topol.top >$script_path/topol.tmp
sed "s/opls_136 opls_136    1    /opls_136 opls_136    1    $sig1    $eps1/" <$script_path/topol.tmp >$script_path/topol1.tmp
sed "s/opls_140 opls_140    1    /opls_140 opls_140    1    $sig2    $eps2/" <$script_path/topol1.tmp >$script_path/topol.tmp

rm $script_path/topol1.tmp
mv $script_path/topol.tmp $sim_cwd/topol.top

#copy files for simulation evaluation
cp $script_path/batch_slurm_eval_PhysProp.sh $sim_cwd

# execute simulation
cd $sim_cwd
sbatch batch_slurm_prod.sh

