#! /bin/bash
thisdir=$(dirname $0)

# Sigma and Epsilon in Gromacs units
#s1=0.350000 #nm
#s2=0.250000 #nm
#e1=0.276144 #kJ/mol
#e2=0.125520 #kJ/mol

#s1=0.175 #nm
#s2=0.148 #nm
#e1=0.509  #kJ/mol
#e2=0.272 #kJ/mol

# convert sigma and epsilon from Gromacs to Amber units
# sigma = sigma*10              from nm to A
# epsilon = epsilon/4.1868      from kJ/mol to K
#s1=3.50000 #A
#s2=2.50000 #A
#e1=0.06596 #K
#e2=0.02998 #K

s1=SIGMA1 #A
s2=SIGMA2 #A
e1=EPSILON1 #K
e2=EPSILON2 #K


OUTPATH=$thisdir"/output/"
working_dir=$thisdir
BINDIR=$thisdir"/bindir/"
TPDUMMY=$thisdir"/ExTrM.template.dat"
HELPSCRIPT=$thisdir"/replace_placeholders.sh"

MOL2=$thisdir"/molec.extrm.bcc.mol2"
LEAPRC=$thisdir"/leaprc.extrm"
W2P=$thisdir"/leaprc.extrm.w2p"

python grow_sander_ff_opt.py $s1 $s2 $e1 $e2 $OUTPATH $BINDIR $TPDUMMY $HELPSCRIPT $MOL2 $LEAPRC $W2P
