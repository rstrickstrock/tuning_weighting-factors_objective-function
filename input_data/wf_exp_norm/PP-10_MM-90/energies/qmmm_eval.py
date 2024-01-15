import os
import sys
import glob

#print(sys.argv)
# cwd
this_file = sys.argv[0]
this_file_abs = os.path.abspath(this_file)
cwd = os.path.dirname(this_file_abs)
# result dir
result_dir = os.path.join(cwd, "output")
# result files
result_file_extension = "*.min.out"

# list for energies
energies = []

def get_energy(filename):
    START = 'FINAL RESULTS'
    END = 'BOND'
    LINES = []
    with open(filename) as input_data:
        # skip to START
        for line in input_data:
            if START in line.strip():
                #print("start")
                break
        for line in input_data:
            # stop at END
            if END in line.strip():
                #print("end")
                break
            LINES.append(line.split())
    # remove empty entries
    LINES = [x for x in LINES if x]
    #print("LINES: {}".format(LINES))
    moleculeName = os.path.basename(filename).split("-")
    moleculeName = str(moleculeName[0] + "-" + moleculeName[1])
    #print(moleculeName)
    try:
        energy = str(LINES[1][1])
    except:
        energy = str("1.0000E+02")
    #print(energy)
    return moleculeName, energy

def get_relative_energies(energylist):
    emin = energylist[0][1]
    #print(emin)
    relative_energies = []
    for i in range(len(energylist)):
        relative_energies.append([energylist[i][0], str(float(energylist[i][1])-float(emin))])
    return relative_energies

# get result files
result_files = glob.glob(os.path.join(result_dir, result_file_extension))

# get energies for molecules
for res in result_files:
    #print(res)
    moleculeName, energy = get_energy(res)
    #print(moleculeName)
    #print(energy)
    energies.append([moleculeName, energy])    
#print(energies)
# write energies to file
with open(os.path.join(result_dir, "Energy.raw.extrm.txt"), 'w') as f:
    for e in energies:
        f.write("{} {}\n".format(e[0], e[1]))

# get relative energies
relative_energies = get_relative_energies(energies)
#print(relative_energies)
# write rel energies to file
with open(os.path.join(result_dir, "Energy.rel.extrm.txt"), 'w') as f:
    for e in relative_energies:
        f.write("{} {}\n".format(e[0], e[1]))


