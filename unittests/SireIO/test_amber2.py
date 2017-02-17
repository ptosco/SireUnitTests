
from Sire.IO import *
from Sire.Mol import *
from Sire.CAS import *
from Sire.System import *
from Sire.Move import *
from Sire.MM import *
from Sire.FF import *
from Sire.Units import *
from Sire.Vol import *
from Sire.Maths import *
from Sire.Base import *
from Sire.Qt import *

import os,re,sys
import shutil

from nose.tools import assert_equal, assert_almost_equal

combining_rules = "arithmetic"
temperature = 25 * celsius
pressure = 1 * atm
coulomb_cutoff = 1000 * angstrom
coulomb_feather = 999.5 * angstrom
lj_cutoff = 1000 * angstrom
lj_feather = 999.5 * angstrom
#############################################################

def _pvt_compare_molecules(mol1, mol2, verbose):
    # compare the residues
    assert_equal( mol1.nResidues(), mol2.nResidues() )

    for i in range(0,mol1.nResidues()):
        res1 = mol1.residue( ResIdx(i) )
        res2 = mol2.residue( ResIdx(i) )

        if verbose:
            print("%s versus %s" % (res1,res2))

        assert_equal( res1.name(), res2.name() )
        assert_equal( res1.number(), res2.number() )

    # compare the atoms
    assert_equal( mol1.nAtoms(), mol2.nAtoms() )

    for i in range(0,mol1.nAtoms()):
        atom1 = mol1.atom( AtomIdx(i) )
        atom2 = mol2.atom( AtomIdx(i) )

        if verbose:
            print("%s versus %s" % (atom1,atom2))

        assert_equal( atom1.name(), atom2.name() )
        assert_equal( atom1.number(), atom2.number() )

        for p in ["coordinates", "charge", "LJ", "mass", "element", "ambertype"]:
            p1 = atom1.property(p)
            p2 = atom2.property(p)

            print(" -- %s versus %s" % (p1,p2))
            assert_equal( p1, p2 )

    # compare the connectivity
    conn1 = mol1.property("connectivity")
    conn2 = mol2.property("connectivity")

    if verbose:
        print("\nConnectivity")
        print(conn1)
        print(conn2)

    assert_equal( conn1.nConnections(), conn2.nConnections() )

    for i in range(0,mol1.nAtoms()):
        idx = AtomIdx(i)

        assert_equal( conn1.nConnections(idx), conn2.nConnections(idx) )

        bonded1 = conn1.connectionsTo(idx)
        bonded2 = conn2.connectionsTo(idx)

        assert_equal( len(bonded1), len(bonded2) )

        for atom in bonded1:
            assert( atom in bonded2 )

    # compare the bond, angle, dihedral and improper functions
    bonds1 = mol1.property("bond")
    bonds2 = mol2.property("bond")

    assert_equal( bonds1.nFunctions(), bonds2.nFunctions() )

    for func in bonds1.potentials():
        p1 = func.function()
        p2 = bonds2.potential(func.atom0(), func.atom1())

        if verbose:
            print("%s-%s = %s versus %s" % (func.atom0(), func.atom1(), \
                                            p1, p2))

        assert_equal( p1, p2 )

    angles1 = mol1.property("angle")
    angles2 = mol2.property("angle")

    assert_equal( angles1.nFunctions(), angles2.nFunctions() )

    for func in angles1.potentials():
        p1 = func.function()
        p2 = angles2.potential(func.atom0(), func.atom1(), func.atom2())

        if verbose:
            print("%s-%s-%s = %s versus %s" % (func.atom0(), func.atom1(), \
                                               func.atom2(), p1, p2))

        assert_equal( p1, p2 )

    dihedrals1 = mol1.property("dihedral")
    dihedrals2 = mol2.property("dihedral")

    assert_equal( dihedrals1.nFunctions(), dihedrals2.nFunctions() )

    for func in dihedrals1.potentials():
        p1 = func.function()
        p2 = dihedrals2.potential(func.atom0(), func.atom1(), \
                                  func.atom2(), func.atom3())

        if verbose:
            print("%s-%s-%s-%s = %s versus %s" % (func.atom0(), func.atom1(), \
                                                  func.atom2(), func.atom3(), \
                                                  p1, p2))

        assert_equal( p1, p2 )

    impropers1 = mol1.property("improper")
    impropers2 = mol2.property("improper")

    assert_equal( impropers1.nFunctions(), impropers2.nFunctions() )

    for func in impropers1.potentials():
        p1 = func.function()
        p2 = impropers2.potential(func.atom0(), func.atom1(), \
                                  func.atom2(), func.atom3())

        if verbose:
            print("%s-%s-%s-%s = %s versus %s" % (func.atom0(), func.atom1(), \
                                                  func.atom2(), func.atom3(), \
                                                  p1, p2))

        assert_equal( p1, p2 )


def test_one_molecule(verbose = False):
    try:
        # check if we have this
        r = AmberRst()
    except:
        return

    rst_file = "../io/ose.crd"
    top_file = "../io/ose.top"

    # Load the molecule using the old and new parser
    if verbose:
        print("Loading single molecule using old parser...")

    mol1 = Amber().readCrdTop(rst_file, top_file)[0].moleculeAt(0).molecule()

    if verbose:
        print("Loading single molecule using new parser...")

    mol2 = MoleculeParser.read(rst_file, top_file)[MolIdx(0)].molecule()

    _pvt_compare_molecules(mol1, mol2, verbose)

def test_lots_of_molecules(verbose = False):
    try:
        # check if we have this
        r = AmberRst()
    except:
        return

    rst_file = "../io/proteinbox.crd"
    top_file = "../io/proteinbox.top"

    # Load the box of molecules using the old and new parser
    if verbose:
        print("Loading box of molecules using old parser...")

    (mols1,space1) = Amber().readCrdTop(rst_file, top_file)

    if verbose:
        print("Loading box of molecules using new parser...")

    system2 = MoleculeParser.read(rst_file, top_file)
    
    if verbose:
        print("Comparing all molecules in the boxes...")

    mols2 = system2[MGIdx(0)]
    space2 = system2.property("space")

    assert_equal( space1, space2 )
    assert_equal( mols1.nMolecules(), mols2.nMolecules() )

    for i in range(0, mols1.nMolecules()):
        if verbose:
            print("\nComparing molecule %d..." % (i+1))

        _pvt_compare_molecules( mols1[MolIdx(i)].molecule(), mols2[MolIdx(i)].molecule(), verbose )

def _pvt_test_rst(verbose = False):
    rst_file = "../io/proteinbox.crd"

    rst = AmberRst(rst_file)

    if verbose:
        print(rst)

    assert_equal( len(rst.coordinates()), 56056 )

def _pvt_test_parm(verbose = False):
    top_file = "../io/proteinbox.top"

    prm = AmberParm(top_file)

    if verbose:
        print(prm)

    flags = prm.flags()

    if verbose:
        print(flags) 

    assert_equal( len(flags), 44 )

    pointers = prm.intData("POINTERS")

    if verbose:
        print(pointers)

    assert_equal( len(pointers), 31 )

    atom_names = prm.stringData("ATOM_NAME")
    charges = prm.floatData("CHARGE")
    atomic_numbers = prm.intData("ATOMIC_NUMBER")
    masses = prm.floatData("MASS")
    atom_type_indexes = prm.intData("ATOM_TYPE_INDEX")

    nats = len(atom_names)

    assert_equal( len(charges), nats )
    assert_equal( len(atomic_numbers), nats )
    assert_equal( len(masses), nats )
    assert_equal( len(atom_type_indexes), nats )

    system = prm.toSystem()

    print(system)

def _pvt_test_nrg(verbose=False):

    top_file = "../io/proteinbox.top"
    crd_file = "../io/proteinbox.crd"

    #top_file = "../io/ose.top"
    #crd_file = "../io/ose.crd"

    system = MoleculeParser.read(crd_file, top_file)
    print(system)

    return

    amber = Amber2()
    system = amber.readRstParm(crd_file, top_file)
    # Overload, we want to calc the energy in a non periodic box for comparison with Sander
    space = Cartesian()

    moleculeNumbers = system.molNums()
    moleculeList = []

    for moleculeNumber in moleculeNumbers:
        molecule = system[moleculeNumber].molecule()
        moleculeList.append(molecule)

    system = System()

    solute = MoleculeGroup("solute", moleculeList[0])

    # Add these groups to the System
    system.add(solute)

    # Now solute bond, angle, dihedral energy
    solute_intraff = InternalFF("solute_intraff")
    solute_intraff.add(solute)

    # Now solute intramolecular CLJ energy
    solute_intraclj = IntraCLJFF("solute_intraclj")
    solute_intraclj.add(solute)

    # Here is the list of all forcefields
    forcefields = [ solute_intraff, solute_intraclj ]
 
    # Add these forcefields to the system
    for forcefield in forcefields:
        system.add(forcefield)

    system.setProperty( "space", space )
    system.setProperty( "switchingFunction", 
                        HarmonicSwitchingFunction(coulomb_cutoff, coulomb_feather,
                                                  lj_cutoff, lj_feather) ) 
    system.setProperty( "combiningRules", VariantProperty(combining_rules) )

    total_nrg = solute_intraclj.components().total() + solute_intraff.components().total()

    e_total = system.totalComponent()
    system.setComponent( e_total, total_nrg )

    if verbose:
        print("\nTotal energy ")
        print(system.energy())

        print("Components energies ")
        for component in list(system.energyComponents().keys()):
            print(component, system.energyComponents().value(component) * kcal_per_mol)

        print("The AMBER14/sander energies for this system are ") 
        print("""
   NSTEP       ENERGY          RMS            GMAX         NAME    NUMBER
      1      -3.4880E+01     1.3388E+01     6.2845E+01     C2         20

 BOND    =        5.1844  ANGLE   =       10.0783  DIHED      =       20.1271
 VDWAALS =       -1.7278  EEL     =     -256.9757  HBOND      =        0.0000
 1-4 VDW =       10.6377  1-4 EEL =      177.7958  RESTRAINT  =        0.0000
""")

        diff = abs( -34.880 - system.energy().value() )
        print("Difference = %s" % diff)

    e_bond = system.energy( solute_intraff.components().bond() ).value()
    e_ang = system.energy( solute_intraff.components().angle() ).value()
    e_dih = system.energy( solute_intraff.components().dihedral() ).value() + \
            system.energy( solute_intraff.components().improper() ).value()
    
    assert_almost_equal( e_bond, 5.1844, 2 )
    assert_almost_equal( e_ang, 10.0783, 2 )
    assert_almost_equal( e_dih, 20.1271, 2 )

    e_coul = system.energy( solute_intraclj.components().coulomb() ).value()
    e_lj = system.energy( solute_intraclj.components().lj() ).value()

    assert_almost_equal( e_coul, -256.9757 + 177.7958, 2 )
    assert_almost_equal( e_lj, -1.7278 + 10.6377, 2 )

    assert_almost_equal( system.energy().value(), -34.880, 2 )

if __name__ == "__main__":
    test_one_molecule(True)
    test_lots_of_molecules(True)

    #test_rst(True)
    #test_parm(True)
    #test_nrg(True)
