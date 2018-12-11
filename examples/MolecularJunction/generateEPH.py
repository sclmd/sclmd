#!/applications/mbrsoft/bin/python
#import matplotlib.pyplot as PP
import sys, string, os, time, glob
import Scientific.IO.NetCDF as nc
import numpy as N
import numpy.linalg as LA

from Inelastica import SiestaIO as SIO
from md import *
from phbath import *
from ebath import *
#from siesta import *
from matrix import *
from myio import *


# Map atomnumbers into elemental labels
PeriodicTable = {'H':1,1:'H','D':1001,1001:'D','He':2,2:'He','Li':3,3:'Li','Be':4,4:'Be','B':5,5:'B','C':6,6:'C','N':7,7:'N','O':8,8:'O','F':9,9:'F','Ne':10,10:'Ne','Na':11,11:'Na','Mg':12,12:'Mg','Al':13,13:'Al','Si':14,14:'Si','P':15,15:'P','S':16,16:'S','Cl':17,17:'Cl','Ar':18,18:'Ar','K':19,19:'K','Ca':20,20:'Ca','Sc':21,21:'Sc','Ti':22,22:'Ti','V':23,23:'V','Cr':24,24:'Cr','Mn':25,25:'Mn','Fe':26,26:'Fe','Co':27,27:'Co','Ni':28,28:'Ni','Cu':29,29:'Cu','Zn':30,30:'Zn','Ga':31,31:'Ga','Ge':32,32:'Ge','As':33,33:'As','Se':34,34:'Se','Br':35,35:'Br','Kr':36,36:'Kr','Rb':37,37:'Rb','Sr':38,38:'Sr','Y':39,39:'Y','Zr':40,40:'Zr','Nb':41,41:'Nb','Mo':42,42:'Mo','Tc':43,43:'Tc','Ru':44,44:'Ru','Rh':45,45:'Rh','Pd':46,46:'Pd','Ag':47,47:'Ag','Cd':48,48:'Cd','In':49,49:'In','Sn':50,50:'Sn','Sb':51,51:'Sb','Te':52,52:'Te','I':53,53:'I','Xe':54,54:'Xe','Cs':55,55:'Cs','Ba':56,56:'Ba','La':57,57:'La','Ce':58,58:'Ce','Pr':59,59:'Pr','Nd':60,60:'Nd','Pm':61,61:'Pm','Sm':62,62:'Sm','Eu':63,63:'Eu','Gd':64,64:'Gd','Tb':65,65:'Tb','Dy':66,66:'Dy','Ho':67,67:'Ho','Er':68,68:'Er','Tm':69,69:'Tm','Yb':70,70:'Yb','Lu':71,71:'Lu','Hf':72,72:'Hf','Ta':73,73:'Ta','W':74,74:'W','Re':75,75:'Re','Os':76,76:'Os','Ir':77,77:'Ir','Pt':78,78:'Pt','Au':79,79:'Au','Hg':80,80:'Hg','Tl':81,81:'Tl','Pb':82,82:'Pb','Bi':83,83:'Bi','Po':84,84:'Po','At':85,85:'At','Rn':86,86:'Rn','Fr':87,87:'Fr','Ra':88,88:'Ra','Ac':89,89:'Ac','Th':90,90:'Th','Pa':91,91:'Pa','U':92,92:'U','Np':93,93:'Np','Pu':94,94:'Pu','Am':95,95:'Am','Cm':96,96:'Cm','Bk':97,97:'Bk','Cf':98,98:'Cf','Es':99,99:'Es','Fm':100,100:'Fm','Md':101,101:'Md','No':102,102:'No'}

AtomicMassTable={'H':1.00794, 'He':4.002602, 'Li':6.941, 'Be':9.012182, \
    'B':10.811, 'C':12.0107, 'N':14.0067, 'O':15.9994, \
    'F':18.9984032, 'Ne':20.1791, 'Na':22.98976928, 'Mg':24.3050, \
    'Al':26.9815386, 'Si':28.0855, 'P':30.973762, 'S':32.065, \
    'Cl':35.453, 'Ar':39.948, 'K':39.0983, 'Ca':40.078, \
    'Sc':44.955912, 'Ti':47.867, 'V':50.9415, 'Cr':51.9961, \
    'Mn':54.938045, 'Fe':55.845, 'Co':58.933195, 'Ni':58.6934, \
    'Cu':63.546, 'Zn':65.38, 'Ga':69.723, 'Ge':72.64, \
    'As':74.92160, 'Se':78.96, 'Br':79.904, 'Kr':83.798, \
    'Rb':85.4678, 'Sr':87.62, 'Y':88.90585, 'Zr':91.224, \
    'Nb':92.90638, 'Mo':95.96, 'Tc':98, 'Ru':101.07, \
    'Rh':102.90550, 'Pd':106.42, 'Ag':107.8682, 'Cd':112.411, \
    'In':114.818, 'Sn':118.710, 'Sb':121.760, 'Te':127.60, \
    'I':126.90447, 'Xe':131.293, 'Cs':132.9054519, 'Ba':137.327, \
    'La':138.90547, 'Ce':140.116, 'Pr':140.90765, 'Nd':144.242, \
    'Pm':145, 'Sm':150.36, 'Eu':151.964, 'Gd':157.25, \
    'Tb':158.92535, 'Dy':162.500, 'Ho':164.93032, 'Er':167.259, \
    'Tm':168.93421, 'Yb':173.054, 'Lu':174.9668, 'Hf':178.49, \
    'Ta':180.94788, 'W':183.84, 'Re':186.207, 'Os':190.23, \
    'Ir':192.217, 'Pt':195.084, 'Au':196.966569, 'Hg':200.59, \
    'Tl':204.3833, 'Pb':207.2, 'Bi':208.98040, 'Po':209, \
    'At':210, 'Rn':222, 'Fr':223, 'Ra':226, 'Ac':227, \
    'Th':232.03806, 'Pa':231.03586, 'U':238.02891, 'Np':237, \
    'Pu':244, 'Am':243, 'Cm':247, 'Bk':247, 'Cf':251, \
    'Es':252, 'Fm':257, 'Md':258, 'No':259, 'Lr':262, \
    'Rf':265, 'Db':268, 'Sg':271, 'Bh':272, 'Hs':270, \
    'Mt':276, 'Ds':281, 'Rg':280, 'Cn':285, 'Uut':284, \
    'Uuq':289, 'Uup':288, 'Uuh':293, 'Uus':294, 'Uuo':294}
#-------------------------------------------------------------------------------------
#user input parameters
#print 'PhononNetCDF : Calculate MAMA using HSSigma and Heph NetCDF file'
args = sys.argv[1:]
if len(args) != 3:
    print "Usage : /usr/bin/python %s <T> <dT> <eV>"%(sys.argv[0])
    #print 'PhononNetCDF : Calculate MAMA using HSSigma and Heph NetCDF file'
    sys.exit()
else:
    T=float(args[0])
    dT=float(args[1])
    eV=float(args[2])
    print "Average Temperature: %s\n"%T
    print "Temperature Difference: %s\n"%(dT)
    print "Applied bias (muL-muR): %s\n"%(eV)

#--------------------------------------------------------------------------------------
curcof = 243414.
nrep = 8
dt = 15
#dt = 8
nmd = 2**13
hwcut=0.03
Orderw0 = [5, 2, 4, 3, 1, 6, 7, 8, 9, 14, 11, 12, 13, 10]
#-------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------
#readin the phonon self-energies, and corresponding structure file
eph=ReadEPHNCFile("oldMD/Sig.nc")
mathmd=ReadMDNCFile("oldMD/oldMD.nc")
olddynxyz=N.array([mathmd.xyz[i-1][0] for i in mathmd.dynatom])
print olddynxyz

#--------------------------------------------------------------------------------------
import Inelastica.SiestaIO as SIO
#read in the relaxed structure
#cell   3x3 unit vectors
#snr    species numbers defined in fdf
#anr    atomic numbers 
#xyzonly    xyz coordinates
#natoms number of atoms

#copy 
os.system("cp ../CGrun/*.vps ../CGrun/*.psf .")
print "read in structure information"
fn=glob.glob("../CGrun/*.XV")
print fn

#fullstru="SIESTASTRUCT.fdf"
#geom2geom fn fullstru 1 1 1
nperlayer=9
nl=6
nr=7
cut=nl-2
#cut=0
#siesta order
#Five atom chain,generated from Mads mathematica code
Orderw =[nperlayer*nl+i for i in Orderw0] #python index
geom=cutlayers(fn[0],nperlayer,cut,cut,"STRUCT.fdf",Orderw)
cell, xyzonly, snr, anr = geom.pbc,geom.xyz,geom.snr,geom.anr

#xyz with element labels
#for example ['Au',0,0,0]
xyz = [[PeriodicTable[a],b[0],b[1],b[2]] for (a,b) in zip(anr,xyzonly)]

#slist are list of dynamical atoms(system) in python index
slist=N.array(range(len(xyz)))
slist=slist[nperlayer*(nl-cut):-nperlayer*(nr-cut)]
print "the following atoms are dynamic:\n"
print slist
print len(slist)

dynxyz=N.array([xyzonly[i] for i in slist])

dmax=N.max(N.abs((olddynxyz[0:5]-olddynxyz[0])-(dynxyz[0:5]-dynxyz[0])))
dmax2=N.max(N.abs((olddynxyz[-5:]-olddynxyz[-1])-(dynxyz[-5:]-dynxyz[-1])))
print "max different should not be larger than 0.2:",dmax,dmax2
if dmax > 0.2: 
    print "The system is not placed in the right way."
    print "The self-energy can not be used!!!"
    print "----------------------------"
    print dynxyz[0:5]-dynxyz[0]-(olddynxyz[0:5]-olddynxyz[0])
    print "----------------------------"
    print 
    print "----------------------------"
    print dynxyz[-5:]-dynxyz[-1]-(olddynxyz[-5:]-olddynxyz[-1])
    print "----------------------------"
    print 
    print "----------------------------"
    stopppp
        



#--------------------------------------------------------------------------------------
#readin dynamical matrix and reorder it
fn=glob.glob("../PHrun/*Dev*.nc")
dyn,U,hw=ReadDynmat(fn[0],Orderw0)

#--------------------------------------------------------------------------------------
#readin the electronic force
fn=glob.glob("../Lambda*/avLambda.nc")
print fn
eV,eta,xim,xip,zeta1,zeta2=ReadwbLambda(fn[0])


#eV=0.5
#print eV
#!#

#cut low frequencies
icut=33
eta[:,icut:]=0.
eta[icut:,:]=0.
xim[:,icut:]=0.
xim[icut:,:]=0.
xip[:,icut:]=0.
xip[icut:,:]=0.
zeta1[:,icut:]=0.
zeta1[icut:,:]=0.
zeta2[:,icut:]=0.
zeta2[icut:,:]=0.



#to real space
eta=mm(U.T,eta,U)
xim=mm(U.T,xim,U)
xip=mm(U.T,xip,U)
zeta1=mm(U.T,zeta1,U) #renormalization already included in the structure
zeta2=mm(U.T,zeta2,U)

WriteEPHNCfile("EPH.nc",eph.wl,hw,U,dyn,eph.SigL,eph.SigR,eta,xim,xip,zeta1,zeta2)
#--------------------------------------------------------------------------------------

#######################################################################################

