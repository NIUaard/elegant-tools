import subprocess
import numpy as np
import matplotlib.pyplot as plt

quadlist = ['QUAD', 'KQUAD']
bendlist = ['SBEN', 'RBEN', 'CSBEND', 'CSRCSBEND', 'CCBEND']
rflist = ['RFCA', 'RFCW']
sextlist = ['SEXT', 'KSEXT']
octulist = ['OCTU', 'KOCT']

sddspath='/lstr/sahara/aard/philippe/codes/pelegant_metis/epics/extensions/bin/linux-x86_64/'
appspath='/lstr/sahara/aard/philippe/codes/pelegant_metis/oag/apps/bin/linux-x86_64/'

def import_numericaldata(filename, column='s'):
    """
    Import any numerical data from ELEGANT SDDS file.
    """
    sddsoutput = subprocess.run([sddspath+'/sdds2stream', filename,
                                 '-col=' + column],
                                stdout=subprocess.PIPE)
    return np.fromstring(sddsoutput.stdout, sep='\n')

def import_strdata(filename, column='ElementType'):
    """
    Import any string data from ELEGANT SDDS file.
    """
    sddsoutput = subprocess.run([sddspath+'/sdds2stream', filename,
                                 '-col=' + column],
                                stdout=subprocess.PIPE)
    return [x.decode("utf-8") for x in sddsoutput.stdout.split(b'\n')[:-1]]

def load_magnets(filename, typelist):
    """
    Load ELEGANT SDDS magnets file and return quadrupole.
    """
    mag = import_numericaldata(filename, column='Profile')
    magtype = import_strdata(filename)
    
    for idx, each in enumerate(magtype):
        if each not in typelist:
            mag[idx] = 0
        
    return mag    

def load_quad(filename):
    """
    Load ELEGANT SDDS magnets file and return quadrupole.
    """
    mag = import_numericaldata(filename, column='Profile')
    magtype = import_strdata(filename)
    
    quadlist = ['QUAD', 'KQUAD']
    for idx, each in enumerate(magtype):
        if each not in quadlist:
            mag[idx] = 0
        
    return mag

def load_dipole(filename):
    """
    Load ELEGANT SDDS magnets file and return quadrupole.
    """
    mag = import_numericaldata(filename, column='Profile')
    magtype = import_strdata(filename)
    
    quadlist = ['SBEN', 'RBEN', 'CSBEND', 'CSRCSBEND', 'CCBEND']
    for idx, each in enumerate(magtype):
        if each not in quadlist:
            mag[idx] = 0
        
    return mag

def load_octupole(filename):
    """
    Load ELEGANT SDDS magnets file and return quadrupole.
    """
    mag = import_numericaldata(filename, column='Profile')
    magtype = import_strdata(filename)
    
    for idx, each in enumerate(magtype):
        if each not in octulist:
            mag[idx] = 0
        else:
            mag[idx] = 0.8
        
    return mag


def dumpParam(filename):
    command1=appspath+'/sddsanalyzebeam'
    command2=sddspath+'/sddsprintout'
    subprocess.run([command1,filename,"tmpsab"])
    param=['pAverage','Sx','Sy','St', 'enx', 'betax', 'alphax', 'eny', 'betay', 'alphay']
    Z1=subprocess.run([command2,"tmpsab","-col=pAverage","-col=St","-col=Sdelta","-col=s56","-noTitle","-htmlFormat"],stdout=subprocess.PIPE)
    Z2=subprocess.run([command2,"tmpsab","-col=enx","-col=ecnx","-col=alphax","-col=betax","-noTitle","-htmlFormat"],stdout=subprocess.PIPE)
    Z3=subprocess.run([command2,"tmpsab","-col=eny","-col=ecny","-col=alphay","-col=betay","-noTitle","-htmlFormat"],stdout=subprocess.PIPE)

    return(str(Z1.stdout).split('\'')[1].replace('\\n', '', 666), 
           str(Z2.stdout).split('\'')[1].replace('\\n', '', 666), 
           str(Z3.stdout).split('\'')[1].replace('\\n', '', 666))



def plotCS(rootname, eta=False):
    """
    Plot betatron functions and horizontal dispersion if eta=True
    """
    betax = import_numericaldata(rootname+'.twi', column='betax')
    betay = import_numericaldata(rootname+'.twi', column='betay')
    stwi  = import_numericaldata(rootname+'.twi')
    etax  = import_numericaldata(rootname+'.twi', column='etax')
    
    magt  = import_numericaldata(rootname+'.mag', column='Profile')
    smag  = import_numericaldata(rootname+'.mag', column='s')
    plt.figure(figsize=(10, 5))
    grid = plt.GridSpec(10,1, wspace=0.4, hspace=0.3)
    ax1=plt.subplot (grid[0,0])
    ax1.plot (smag, magt, 'C7')
    ax1.axis('off')

    ax2=plt.subplot (grid[1:9,0], sharex = ax1)
    ax2.plot (stwi, betax, label=r'$\beta_x$')
    ax2.plot (stwi, betay, '--', label=r'$\beta_y$')
    plt.legend()

    if eta==True:
        ax2t=ax2.twinx()
        ax2t.plot (stwi, etax,'g', label=r'$\eta_x$')
        ax2t.set_ylabel (r'$\eta_x$ (m)')

    ax2.set_xlabel  (r'distance $s$ (m)')
    ax2.set_ylabel  (r'$\beta$ functions (m)')
    ax2.grid()
    plt.show()


def plotSize(rootname):
    """
    Plot rms beam sizes
    """
    Sx = 1e3*import_numericaldata(rootname+'.s', column='Sx')
    Sy = 1e3*import_numericaldata(rootname+'.s', column='Sy')
    s  = import_numericaldata(rootname+'.s')
    Ss = 1e3*import_numericaldata(rootname+'.s', column='Ss')
    
    magt  = import_numericaldata(rootname+'.mag', column='Profile')
    smag  = import_numericaldata(rootname+'.mag', column='s')
    plt.figure(figsize=(10, 5))
    grid = plt.GridSpec(10,1, wspace=0.4, hspace=0.3)
    ax1=plt.subplot (grid[0,0])
    ax1.plot (smag, magt, 'C7')
    ax1.axis('off')

    ax2=plt.subplot (grid[1:9,0], sharex = ax1)
    ax2.plot (s, Sx, label=r'$\sigma_x$')
    ax2.plot (s, Sy, '--', label=r'$\sigma_y$')
    ax2.set_ylim([0,1.3*np.max([Sx.max(),Sy.max()])])
    plt.legend()

    ax2t=ax2.twinx()
    ax2t.plot (s, Ss,'g', label=r'$\sigma_z$')
    ax2t.set_ylabel (r'$\sigma_z$ (mm)', color='g')
    ax2t.set_ylim([0,1.5*Ss.max()])
    ax2t.tick_params(axis="y", labelcolor='g')
    ax2.set_xlabel  (r'distance $s$ (m)')
    ax2.set_ylabel  (r'rms sizes (mm)')
    ax2.grid()
    plt.show()

def plotEmit(rootname):
    """
    Plot rms beam emittances 
    """
    ex = 1e6*import_numericaldata(rootname+'.s', column='ecnx')
    ey = 1e6*import_numericaldata(rootname+'.s', column='ecny')
    s  = import_numericaldata(rootname+'.s')
    s6  = import_numericaldata(rootname+'.s', column='s6')
    s7  = import_numericaldata(rootname+'.s', column='s7')
    s67 = import_numericaldata(rootname+'.s', column='s67')
    p0  = import_numericaldata(rootname+'.cen', column='pCentral')
    es = 1e6*3e8*p0*np.sqrt(s6**2*s7**2-s67**2)
    
    magt  = import_numericaldata(rootname+'.mag', column='Profile')
    smag  = import_numericaldata(rootname+'.mag', column='s')
    plt.figure(figsize=(10, 5))
    grid = plt.GridSpec(10,1, wspace=0.4, hspace=0.3)
    ax1=plt.subplot (grid[0,0])
    ax1.plot (smag, magt, 'C7')
    ax1.axis('off')

    ax2=plt.subplot (grid[1:9,0], sharex = ax1)
    ax2.plot (s, ex, label=r'$\varepsilon_x$')
    ax2.plot (s, ey, '--', label=r'$\varepsilon_y$')
    ax2.set_ylim([0,1.3*np.max([ex.max(),ey.max()])])
    plt.legend()

    ax2t=ax2.twinx()
    ax2t.plot (s, es,'g', label=r'$\sigma_z$')
    ax2t.set_ylabel (r'$\varepsilon_z$ ($\mu$m)', color='g')
    ax2t.set_ylim([0,1.5*es.max()])
    ax2.set_xlabel  (r'distance $s$ (m)')
    ax2t.tick_params(axis="y", labelcolor='g')
    ax2.set_ylabel  (r'rms emittance ($\mu$m)')
    ax2.grid()
    plt.show()

