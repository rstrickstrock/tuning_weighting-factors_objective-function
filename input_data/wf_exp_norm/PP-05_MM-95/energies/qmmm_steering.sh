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
# create working dir and copy all necessary files
mkdir $sim_cwd
cp $script_path/batch_slurm_RCE.sh $sim_cwd
cp -r $script_path/bindir $sim_cwd
cp $script_path/ExTrM.template.dat $script_path/replace_placeholders.sh $sim_cwd
cp $script_path/molec.extrm.bcc.mol2 $script_path/leaprc.extrm $script_path/leaprc.extrm.w2p $sim_cwd
#cp $script_path/frcmod.extrm.w2p $sim_cwd
cp $script_path/grow_sander_ff_opt.py $sim_cwd

#adapt parameters
sed "s/s1=SIGMA1 #A/s1=$sig1 #A/" <$script_path/run_mm.sh >$script_path/run_mm.tmp
sed "s/s2=SIGMA2 #A/s2=$sig2 #A/" <$script_path/run_mm.tmp >$script_path/run_mm1.tmp
sed "s/e1=EPSILON1 #K/e1=$eps1 #K/" <$script_path/run_mm1.tmp >$script_path/run_mm.tmp
sed "s/e2=EPSILON2 #K/e2=$eps2 #K/" <$script_path/run_mm.tmp >$sim_cwd/run_mm.sh

rm $script_path/run_mm.tmp $script_path/run_mm1.tmp
chmod +x $sim_cwd/run_mm.sh

#copy files for simulation evaluation
cp $script_path/batch_slurm_eval_RCE.sh $sim_cwd
cp $script_path/qmmm_eval.py $sim_cwd

# execute simulation
cd $sim_cwd
sbatch batch_slurm_RCE.sh
