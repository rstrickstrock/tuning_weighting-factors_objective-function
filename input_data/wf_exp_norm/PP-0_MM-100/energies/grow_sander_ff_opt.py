import sys
import os
import subprocess
import shutil
import glob
import fileinput


############################
######## Functions #########
############################
def does_file_exist(myfile):
    # check if file exists
    if not os.path.isfile(myfile):
        print("\n\n !! File (\"{}\") does not exist. Application will exit! !!\n\n".format(myfile))
        sys.exit()
    else:
        pass

def does_dir_exist(mydir, create=False, replace=False):
    # check if directory exists
    #     create=True: creates directory if it does not exist
    #     replace=True: deletes directory and creates a new (empty) one, if it exists
    if not os.path.isdir(mydir):
        if create or replace:
            print("\nCreated directory (\"{}\").".format(mydir))
            os.makedirs(mydir)
        else:
            print("\n\n !! Directory (\"{}\") does not exist. Application will exit! !!\n\n".format(mydir))
            sys.exit()
    else:
        if replace:
            print("\nReplaced directory (\"{}\").".format(mydir))
            shutil.rmtree(mydir)
            os.makedirs(mydir)
        else:
            pass

def psi2xyz(INFILE,OUTFILE):
    START = 'Final optimized geometry and variables:'
    END = 'Cleaning optimization helper files.'
    GEOM = []
    i = 1
    with open(INFILE) as input_data:
        for line in input_data:
            if line.strip() == START:
                break
        # Reads text until the end of the block:
        for line in input_data:  ## This keeps reading the file
            if (i > 5):          ## Skip 5 lines before recording
                if line.strip() == END:
                    break
                GEOM.append(line)
            #else:
            #    print line
            i += 1

    if GEOM[len(GEOM)-1] == '\n':
        GEOM = GEOM[0:len(GEOM)-1]
    number_of_atoms = len(GEOM)
    #print("number of atoms: %s" %(str(number_of_atoms)))
    filename = os.path.basename(INFILE)
    #print("filename: %s" %(filename))

    f=open(OUTFILE,'w')
    f.write(str(number_of_atoms) + '\n')
    f.write(filename + '\n')
    for coord in GEOM:
        if coord.endswith('\n'):
            f.write(coord)
        else:
            f.write(coord + '\n')
    f.close()

def get_mm_mol2_coords(INFILE, MOL2):
    START = '@<TRIPOS>ATOM'
    END = '@<TRIPOS>BOND'
    COORD = []
    ATOMLABEL = []
    RESNAME = []
    ATOMTYPES = []
    CHARGES = []
    LINE = []
    ## Extract unique xyz coordinates
    if MOL2.endswith('.mol2'):
        with open(MOL2) as input_data_1:
            for line in input_data_1:
                if line.strip() == START:
                    break
            # Reads text until the end of the block:
            for line in input_data_1:
                if line.strip() == END:
                    break
                COORD.append(line[19:46])

    if MOL2.endswith('.xyz'):
        i=1
        with open(MOL2) as input_data_1:
            for line in input_data_1:
                if i > 2:
                    COORD.append(line[16:68])
                i+=1

    ## Extract proper labels, atom types and charges
    with open(INFILE) as input_data:
        for line in input_data:
            if line.strip() == START:
                break
        for line in input_data:
            if line.strip() == END:
                break
            ATOMLABEL.append(line[0:18])
            RESNAME.append(line[50:65])
            ATOMTYPES.append(line.split()[5])
            CHARGES.append(line.split()[8])

    ## combine them
    for a, b, c, d, e in zip(ATOMLABEL,COORD,ATOMTYPES,RESNAME,CHARGES):
        LINE.append(a + ' ' + b + ' ' + c + ' ' + d + ' ' + e)
    return LINE


############################
#### Assign Environment ####
############################
args = sys.argv

SIGMA_1 = args[1]
SIGMA_2 = args[2]
EPSILON_1 = args[3]
EPSILON_2 = args[4]
print("Parameters:")
print("  SIGMA_C: {}".format(SIGMA_1))
print("  SIGMA_H: {}".format(SIGMA_2))
print("  EPSILON_C: {}".format(EPSILON_1))
print("  EPSILON_H: {}".format(EPSILON_2))


OUTPATH = args[5]
BINDIR = args[6]
print("\nPaths:")
print("  BINDIR: {}".format(BINDIR))
print("  OUTPATH: {}".format(OUTPATH))

TPDUMMY = args[7]
HELPSCRIPT = args[8]
MOL2_file = args[9]
LEAPRC_file = args[10]
W2P_file = args[11]
print("\nFiles:")
print("  LEAPRC_file: {}".format(LEAPRC_file))
print("  MOL2_file: {}".format(MOL2_file))
print("  HELPSCRIPT: {}".format(HELPSCRIPT))
print("  TPDUMMY: {}".format(TPDUMMY))
print("  W2P_file: {}".format(W2P_file))

MOL2_TEMPLATE = os.path.join(BINDIR, '06_mm_opt/', os.path.basename(MOL2_file))
FF_SOURCE_1 = os.path.join(BINDIR, '06_mm_opt', os.path.basename(LEAPRC_file))
FF_SOURCE_2 = os.path.join(BINDIR, '06_mm_opt', os.path.basename(W2P_file))


############################
##### Check existances #####
############################
does_dir_exist(OUTPATH, replace=True)
does_dir_exist(BINDIR)

does_file_exist(TPDUMMY)
does_file_exist(HELPSCRIPT)
does_file_exist(MOL2_file)
does_file_exist(LEAPRC_file)
does_file_exist(W2P_file)


############################
#### set up input files ####
############################
## parse current parameters
does_dir_exist(os.path.join(BINDIR, "06_mm_opt"))
subprocess.call(HELPSCRIPT + ' %s %s %s %s' % (SIGMA_1,SIGMA_2,EPSILON_1,EPSILON_2), shell=True)

## copy necessary files and adapt paths
shutil.copy2(W2P_file, os.path.join(BINDIR, '06_mm_opt/'))
for line in fileinput.input([os.path.join(os.path.join(BINDIR, '06_mm_opt/'), os.path.basename(W2P_file))], inplace=True):
    print(line.replace('SOURCEDIR', os.path.join(BINDIR, '06_mm_opt')), end='')

shutil.copy2(LEAPRC_file, os.path.join(BINDIR, '06_mm_opt/'))
for line in fileinput.input([os.path.join(os.path.join(BINDIR, '06_mm_opt/'), os.path.basename(LEAPRC_file))], inplace=True):
    print(line.replace('SOURCEDIR', os.path.join(BINDIR, '06_mm_opt')), end='')

shutil.copy2(MOL2_file, MOL2_TEMPLATE)

## create min.in file
with open(os.path.join(BINDIR, '06_mm_opt', 'min.in'), 'w') as f:
    f.write('Constraint Minimization\n')
    f.write('&cntrl\n')
    f.write('imin=1, dielc=1, ntb=0,\n')
    f.write('maxcyc=20000, cut=40.0,\n')
    f.write('ntc=1, ntf=1,\n')
    f.write('drms=0.01, nmropt=0\n')
    f.write('&end\n')

############################
### get Amber head/tail ####
############################
HEAD = []
TAIL = []
with open(os.path.join(BINDIR, '06_mm_opt', 'molec.extrm.bcc.mol2')) as file:
    HEAD = [next(file) for x in range(6)]
    for line in file:
        if '@<TRIPOS>BOND' in line:
            for line in file:
                TAIL.append(line)

HEAD = [s.rstrip() for s in HEAD]
TAIL = [s.rstrip() for s in TAIL]
#print(HEAD)
#print(TAIL)


############################
#### get all molecules #####
############################
QMLOG = glob.glob(BINDIR + '/00_qm_opt/molecule-*-psi.inp.log')
QMLOG=sorted(QMLOG)
#print(QMLOG)


############################
#### RUN MINIMIZATION ######
############################
print("\nMinimization starting:")
for LOG in QMLOG:
    print("\tprocessing: {} ...".format(LOG))
    LOGNAME = LOG.split('/')
    BASENAME = (LOGNAME[-1]).split('.')
    #print(BASENAME)

    ## convert psi to xyz file
    psi2xyz(LOG, os.path.join(OUTPATH, BASENAME[0] + '.xyz'))

    ## get mm mol2 coordinates from xyz file
    MOL2_COORDS = get_mm_mol2_coords(MOL2_TEMPLATE, os.path.join(OUTPATH, BASENAME[0] + '.xyz'))
    #print(MOL2_COORDS)
    
    ## create .mol2 file
    with open(os.path.join(OUTPATH, BASENAME[0] + '.mol2'),'w') as f:
        for item in HEAD:
            f.write("{}\n".format(item))
        for item in MOL2_COORDS:
            f.write("{}\n".format(item))
        f.write("@<TRIPOS>BOND\n")
        for item in TAIL:
            f.write("{}\n".format(item))

    ## create leap.in file
    with open(os.path.join(OUTPATH, BASENAME[0] + '.leap.in'), 'w') as f:
        f.write('logfile ' + os.path.join(OUTPATH, BASENAME[0] + '.leap.log') + '\n')
        f.write('source ' + FF_SOURCE_1 +'\n')
        f.write('source ' + FF_SOURCE_2 +'\n')
        f.write('verbosity 2\n')
        f.write('a = loadmol2 ' + os.path.join(OUTPATH, BASENAME[0] + '.mol2') + '\n')
        f.write('saveamberparm a ' + os.path.join(OUTPATH, BASENAME[0] + '.leap.top ') + os.path.join(OUTPATH, BASENAME[0] + '.leap.crd') + '\n')
        f.write('savepdb a ' + os.path.join(OUTPATH, BASENAME[0] + '.leap.pdb') + '\n')
        f.write('quit\n')

    ## create fnull output "file"
    FNULL = open(os.devnull, 'w')

    ## Run tleap to get filename.top and filename.crd --> used as input for MM minimization or MD
    TLEAP = ['tleap', '-s -f', os.path.join(OUTPATH, BASENAME[0] + '.leap.in')]
    subprocess.call(TLEAP, stdout=FNULL, stderr=subprocess.STDOUT)
    ## check if output files exist
    does_file_exist(os.path.join(OUTPATH, BASENAME[0] + '.leap.top'))
    does_file_exist(os.path.join(OUTPATH, BASENAME[0] + '.leap.crd'))

    ## run actual minimization
    SANDER = ['sander', '-O', '-i', os.path.join(BINDIR, '06_mm_opt', 'min.in'), '-o', os.path.join(OUTPATH, BASENAME[0] + '.min.out'), '-p', os.path.join(OUTPATH, BASENAME[0] + '.leap.top'), '-c', os.path.join(OUTPATH, BASENAME[0] + '.leap.crd'), '-r', os.path.join(OUTPATH, BASENAME[0] + '.min.rst'), '-ref', os.path.join(OUTPATH, BASENAME[0] + '.leap.crd')]
    subprocess.call(SANDER, stdout=FNULL, stderr=subprocess.STDOUT)
    ## check if output files exist
    does_file_exist(os.path.join(OUTPATH, BASENAME[0] + '.min.out'))
    does_file_exist(os.path.join(OUTPATH, BASENAME[0] + '.min.rst'))

print("\nMinimization finished.\n")







