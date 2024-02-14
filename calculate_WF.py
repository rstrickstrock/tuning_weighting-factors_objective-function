## python script to calculate Weighting Factors (WF) for Relative Conformational Energies (RCE). 

## USEAGE: python calculate_WF.py
##         -> follow CLI instructions

## For exponentially and stepwise decreasing WF target energies are required.
## They need to be provided in a file with one RCE (without names and units, just the value) per row.
## e.g.:
## 
## $ cat TargetEnergies.txt 
## 0.0
## 0.491
## 0.518
## 0.542
## 0.679
## 0.746
## 0.888
## 0.929

import numpy as np
import matplotlib.pyplot as plt
import os

def readEnergyFile(filename):
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()

    Energies = []
    for line in lines:
        try:
            Energies.append(float(line))
        except:
            print(f'Could not cast \'{line}\' to float.')
            print(f'Check \'{filename}\' and ensure only one (float) energy value is given per line.')
            print(f'Application exit.')
            exit()

    return np.array(Energies)


def calcWFUni(NumberOfWF, b):
    WeightingFactors = np.ones(NumberOfWF)*(b/(NumberOfWF-1))
    WeightingFactors[0] = 0
    
    return WeightingFactors


def calcWFLin(NumberOfWF, b, k):
    #c = (NumberOfWF-1)*k
    #print(f'{c}')
    c = 2*((b-((NumberOfWF-1)*k))/((NumberOfWF-2)*(NumberOfWF-1)))
    WeightingFactors = [0]
    i = NumberOfWF - 2
    while i > 0:
        WeightingFactors.append(k+i*c)
        i = i - 1
    WeightingFactors.append(k)
    
    return np.array(WeightingFactors)


def calcWFExp(TargetEnergies, k_B, T, b):
    WeightingFactorsUnscaled = np.exp(-((TargetEnergies)/(k_B*T)))
    #print(f'WeightingFactorsUnscaled = {WeightingFactorsUnscaled}')
    WeightingFactorsUnscaled = np.insert(WeightingFactorsUnscaled, 0, 0)
    #print(f'WeightingFactorsUnscaled = {WeightingFactorsUnscaled}')
    WeightingFactorsUnscaled = WeightingFactorsUnscaled[:-1]
    #print(f'WeightingFactorsUnscaled = {WeightingFactorsUnscaled}')

    return WeightingFactorsUnscaled*(b/np.sum(WeightingFactorsUnscaled))


def calcWFSte(TargetEnergies, k, b):
    WeightingFactorsUnscaled = []
    q = 1
    i = 1
    #cnt = 0
    TmpEnergies = []
    #print(f'{len(TargetEnergies)}')
    #print(f'{TargetEnergies}')
    #print(f'{type(TargetEnergies)}')
    while i < len(TargetEnergies):
        #print(f'{TargetEnergies[i]}')
        #print(f'{type(TargetEnergies[i])}')
        if TargetEnergies[i] < q*k:
            TmpEnergies.append(TargetEnergies[i])
            #cnt = cnt + 1
        else:
            WeightingFactorsUnscaled.append(TmpEnergies)
            TmpEnergies = [TargetEnergies[i]]
            q = q + 1
            #cnt = cnt + 1
        i = i + 1    
    WeightingFactorsUnscaled.append(TmpEnergies)
    #print(f'cnt = {cnt}')
    
    NumberOfGroups = len(WeightingFactorsUnscaled)
    #print(f'{NumberOfGroups}')
    WeightingFactors = []
    for i in range(0, NumberOfGroups):
        for WF in WeightingFactorsUnscaled[i]:
            #print(f'{WF}')
            WeightingFactors.append(NumberOfGroups-i)

    WeightingFactors = np.array(WeightingFactors)
    WeightingFactors = np.insert(WeightingFactors, 0, 0)
    #print(f'{WeightingFactors}')
    #print(f'{len(WeightingFactors)}')
    return (WeightingFactors/np.sum(WeightingFactors))*b

print(f'Please specify the type of intra-domiain balancing (uni/lin/exp/ste).')
IntraDomainBalancing = input()
#print(f'{IntraDomainBalancing}')

## type
if IntraDomainBalancing not in ['uni', 'lin', 'exp', 'ste']:
    print(f'Intra-domain balancing set to \'{IntraDomainBalancing}\'. Needs to be one of [\'uni\', \'lin\', \'exp\', \'ste\'] ')
    print(f'Application exit.')
    exit()

## num of wf
print(f'\nPlease specify the total number of intra-domain weighting factors (type: int)')
#print('Number of weighting factors = ')
NumberOfWF = input()

try:
    NumberOfWF = int(NumberOfWF	)
except:
    print(f'Type of number of weighting factors must be \'int\'. Number of weighting factors = \'{NumberOfWF}\', type(Number of weighting factors) = {type(NumberOfWF)}.')
    print(f'Application exit.')
    exit()

## b
print(f'\nPlease specify the sum of all intra-domain weighting factors \'b\' (type: float)')
#print('b = ')
b = input()

try:
    b = float(b)
except:
    print(f'Type of b must be \'float\'. b = \'{b}\', type(b) = {type(b)}.')
    print(f'Application exit.')
    exit()
    
######################
########## calc uni WF
if IntraDomainBalancing == 'uni':
    WeightingFactors = calcWFUni(NumberOfWF, b)
    print(f'Weighting Factors = {WeightingFactors}')


######################
########## calc lin WF
if IntraDomainBalancing == 'lin':
    ## b
    print(f'\nPlease specify the value for the last weighting factors \'k\' (type: float)')
    #print('k = ')
    k = input()

    try:
        k = float(k)
    except:
        print(f'Type of k must be \'float\'. k = \'{k}\', type(k) = {type(k)}.')
        print(f'Application exit.')
        exit()
        
    WeightingFactors = calcWFLin(NumberOfWF, b, k)
    print(f'Weighting Factors = {WeightingFactors}')
    #print(f'Sum of WF: {sum(np.array(WeightingFactors))}')


######################
########## calc exp WF
if IntraDomainBalancing == 'exp':
    k_B = 1.38064852e-23  # m²*kg*s⁻²*K⁻¹
    nmol = 6.023e23  # particles/mol
    
    ## T
    print(f'\nPlease specify the Temperature \'T\' (unit: Kelvin, type: float)')
    #print('T = ')
    T = input() # K

    try:
        T = float(T) # K
    except:
        print(f'Type of T must be \'float\'. T = \'{T}\', type(T) = {type(T)}.')
        print(f'Application exit.')
        exit()
    
    ## read target energies
    print(f'\nPlease specify the target energies file (press Enter for default: ./TargetEnergies.txt).')
    TargetEnergyFile = input() #filepath
    if TargetEnergyFile == '':
        TargetEnergyFile = 'TargetEnergies.txt'
        
    if not os.path.isfile(TargetEnergyFile):
        print(f'Target energies file \'{TargetEnergyFile}\' does not exist.')
        print(f'Application exit.')
        exit() 
    TargetEnergies = readEnergyFile(TargetEnergyFile) #kcal/mol
    #print(f'TargetEnergies = {TargetEnergies}')
    # get energies per molecule/particle
    TargetEnergies = TargetEnergies*1000/nmol  # cal per particle
    TargetEnergies = TargetEnergies*4.184  # joule per particle = kg*m²*s⁻² per particle
    
    WeightingFactors = calcWFExp(TargetEnergies, k_B, T, b)
    #print(f'WeightingFactors = {WeightingFactors}')
    #print(f'sum WeightingFactors = {np.sum(WeightingFactors)}')


######################
########## calc exp WF
if IntraDomainBalancing == 'ste':
    ## k
    print(f'\nPlease specify the stepsize \'k\' (unit: kcal/mol type: float)')
    #print('k = ')
    k = input()

    try:
        k = float(k)
    except:
        print(f'Type of k must be \'float\'. k = \'{k}\', type(k) = {type(k)}.')
        print(f'Application exit.')
        exit()
        
    ## read target energies
    print(f'\nPlease specify the target energies file (press Enter for default: ./TargetEnergies.txt).')
    TargetEnergyFile = input() #filepath
    if TargetEnergyFile == '':
        TargetEnergyFile = 'TargetEnergies.txt'
        
    if not os.path.isfile(TargetEnergyFile):
        print(f'Target energies file \'{TargetEnergyFile}\' does not exist.')
        print(f'Application exit.')
        exit()     
    TargetEnergies = readEnergyFile(TargetEnergyFile) #kcal/mol
    
    WeightingFactors = calcWFSte(TargetEnergies, k, b)
    #print(f'WeightingFactors = {WeightingFactors}')
    #print(f'sum WeightingFactors = {np.sum(WeightingFactors)}')


###########################
########## save WFs to file  
WeightingFactorsFilename = f'WeightingFactors_{IntraDomainBalancing}_b-{b}_n-{NumberOfWF}.txt' 
if os.path.isfile(WeightingFactorsFilename):
    os.remove(WeightingFactorsFilename)

#print(f'{len(WeightingFactors)}')
f = open(WeightingFactorsFilename, 'w')
for i in range (0,len(WeightingFactors)-1):
    f.write(f'{WeightingFactors[i]}\n')
f.write(str(WeightingFactors[-1]))
f.close()


##################
########## plot WF
WFs = np.linspace(1, NumberOfWF, NumberOfWF)
plt.plot(WFs, WeightingFactors, ':x')
plt.show()




















