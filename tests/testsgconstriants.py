#!/usr/bin/env python
"""Tests space group constraints."""

import unittest

import numpy

from diffpy.srfit.structure.objcryststructure import ObjCrystParSet
from diffpy.srfit.structure.diffpystructure import StructureParSet

def makeLaMnO3_P1():
    from diffpy.Structure import Structure
    stru = Structure()
    stru.readStr(lamno3stru)
    return stru

def makeLaMnO3():
    from pyobjcryst.crystal import Crystal 
    from pyobjcryst.atom import Atom 
    from pyobjcryst.molecule import Molecule
    from pyobjcryst.scatteringpower import ScatteringPowerAtom

    pi = numpy.pi
    # It appears that ObjCryst only supports standard symbols
    crystal = Crystal(5.486341, 5.619215, 7.628206, "P b n m")
    crystal.SetName("LaMnO3")
    # La1
    sp = ScatteringPowerAtom("La1", "La")
    sp.SetBiso(8*pi*pi*0.003)
    atom = Atom(0.996096, 0.0321494, 0.25, "La1", sp)
    crystal.AddScatteringPower(sp)
    crystal.AddScatterer(atom)
    # Mn1
    sp = ScatteringPowerAtom("Mn1", "Mn")
    sp.SetBiso(8*pi*pi*0.003)
    atom = Atom(0, 0.5, 0, "Mn1", sp)
    crystal.AddScatteringPower(sp)
    crystal.AddScatterer(atom)
    # O1
    sp = ScatteringPowerAtom("O1", "O")
    sp.SetBiso(8*pi*pi*0.003)
    atom = Atom(0.0595746, 0.496164, 0.25, "O1", sp)
    crystal.AddScatteringPower(sp)
    crystal.AddScatterer(atom)
    # O2
    sp = ScatteringPowerAtom("O2", "O")
    sp.SetBiso(8*pi*pi*0.003)
    atom = Atom(0.720052, 0.289387, 0.0311126, "O2", sp)
    crystal.AddScatteringPower(sp)
    crystal.AddScatterer(atom)

    return crystal

class TestSGConstraints(unittest.TestCase):

    def testConstrainSpaceGroup(self):
        """Make sure that all Parameters are constrained properly.

        This tests constrainSpaceGroup from
        diffpy.srfit.structure.sgconstraints, which is performed automatically
        when an ObjCrystParSet is created.
        
        """
        pi = numpy.pi

        occryst = makeLaMnO3()
        stru = ObjCrystParSet(occryst, occryst.GetName())

        # Check the orthorhombic lattice
        l = stru.getLattice()
        self.assertTrue( l.alpha.const )
        self.assertTrue( l.beta.const )
        self.assertTrue( l.gamma.const )
        self.assertEquals(pi/2, l.alpha.getValue())
        self.assertEquals(pi/2, l.beta.getValue())
        self.assertEquals(pi/2, l.gamma.getValue())

        self.assertFalse( l.a.const )
        self.assertFalse( l.b.const )
        self.assertFalse( l.c.const )
        self.assertEquals(0, len(l._constraints))

        # Now make sure the scatterers are constrained properly
        scatterers = stru.getScatterers()
        la = scatterers[0]
        self.assertFalse(la.x.const)
        self.assertFalse(la.y.const)
        self.assertTrue(la.z.const)
        self.assertEquals(0, len(la._constraints))

        mn = scatterers[1]
        self.assertTrue(mn.x.const)
        self.assertTrue(mn.y.const)
        self.assertTrue(mn.z.const)
        self.assertEquals(0, len(mn._constraints))

        o1 = scatterers[2]
        self.assertFalse(o1.x.const)
        self.assertFalse(o1.y.const)
        self.assertTrue(o1.z.const)
        self.assertEquals(0, len(o1._constraints))

        o2 = scatterers[3]
        self.assertFalse(o2.x.const)
        self.assertFalse(o2.y.const)
        self.assertFalse(o2.z.const)
        self.assertEquals(0, len(o2._constraints))

        # Make sure we can't constrain these
        self.assertRaises(ValueError, mn.constrain, mn.x, "y")
        self.assertRaises(ValueError, mn.constrain, mn.y, "z")
        self.assertRaises(ValueError, mn.constrain, mn.z, "x")

        # Nor can we make them into variables
        from diffpy.srfit.fitbase.fitrecipe import FitRecipe
        f = FitRecipe()
        self.assertRaises(ValueError, f.addVar, mn.x)

        return

    def testConstrainAsSpaceGroup(self):
        """Test the constrainAsSpaceGroup function."""
        from diffpy.srfit.structure.sgconstraints import constrainAsSpaceGroup

        stru = makeLaMnO3_P1()
        parset = StructureParSet(stru, "LaMnO3")

        xyznames, uijnames = constrainAsSpaceGroup(parset, "P b n m",
                scatterers = parset.getScatterers()[::2],
                constrainadps = True)

        # Make sure that the new parameters were created
        for pname in xyznames + uijnames:
            self.assertNotEquals(None, parset.get(pname) )
            self.assertNotEquals(None, parset.get(pname).getValue() )

        # Test the unconstrained atoms
        for scatterer in parset.getScatterers()[1::2]:
            self.assertFalse(scatterer.x.const)
            self.assertFalse(scatterer.y.const)
            self.assertFalse(scatterer.z.const)
            self.assertFalse(scatterer.U11.const)
            self.assertFalse(scatterer.U22.const)
            self.assertFalse(scatterer.U33.const)
            self.assertFalse(scatterer.U12.const)
            self.assertFalse(scatterer.U13.const)
            self.assertFalse(scatterer.U23.const)
            self.assertEquals(0, len(scatterer._constraints))

        # Test the constrained atoms. We only test the existence of constraints
        # rather than the constraints themselves. These are tested in the
        # diffpy.Structure package.
        for scatterer in parset.getScatterers()[::2]:

            self.assertTrue(scatterer.x.const or scatterer.y.const or
                    scatterer.z.const or scatterer.x.constrained or
                    scatterer.y.constrained or scatterer.z.constrained)

            self.assertTrue(scatterer.U11.const or scatterer.U22.const or
                    scatterer.U33.const or scatterer.U12.const or
                    scatterer.U13.const or scatterer.U23.const or
                    scatterer.U11.constrained or scatterer.U22.constrained or
                    scatterer.U33.constrained or scatterer.U12.constrained or
                    scatterer.U13.constrained or scatterer.U23.constrained)

        return
lamno3stru =\
"""\
title  Cell structure file of LaMnO3.0
format pdffit
scale   1.000000
sharp   0.000000,  0.000000,  1.000000,  3.500000
spcgr   Pbnm
cell    5.486341,  5.619215,  7.628206, 90.000000, 90.000000, 90.000000
dcell   0.000118,  0.000156,  0.000118,  0.000000,  0.000000,  0.000000
ncell          1,         1,         1,        20
atoms
LA          0.99609631        0.03214940        0.25000000       1.0000
            0.00003041        0.00000852        0.00000000       0.0000
            0.00253993        0.00253993        0.00253993
            0.00000214        0.00000214        0.00000214
            0.00000000        0.00000000        0.00000000
            0.00000000        0.00000000        0.00000000
LA          0.49609631        0.46785060        0.75000000       1.0000
            0.00003041        0.00000852        0.00000000       0.0000
            0.00253993        0.00253993        0.00253993
            0.00000214        0.00000214        0.00000214
            0.00000000        0.00000000        0.00000000
            0.00000000        0.00000000        0.00000000
LA          0.00390369        0.96785063        0.75000000       1.0000
            0.00003041        0.00000852        0.00000000       0.0000
            0.00253993        0.00253993        0.00253993
            0.00000214        0.00000214        0.00000214
            0.00000000        0.00000000        0.00000000
            0.00000000        0.00000000        0.00000000
LA          0.50390369        0.53214937        0.25000000       1.0000
            0.00003041        0.00000852        0.00000000       0.0000
            0.00253993        0.00253993        0.00253993
            0.00000214        0.00000214        0.00000214
            0.00000000        0.00000000        0.00000000
            0.00000000        0.00000000        0.00000000
MN          0.00000000        0.50000000        0.00000000       1.0000
            0.00000000        0.00000000        0.00000000       0.0000
            0.00065337        0.00065337        0.00065337
            0.00000165        0.00000165        0.00000165
            0.00000000        0.00000000        0.00000000
            0.00000000        0.00000000        0.00000000
MN          0.50000000        0.00000000        0.00000000       1.0000
            0.00000000        0.00000000        0.00000000       0.0000
            0.00065337        0.00065337        0.00065337
            0.00000165        0.00000165        0.00000165
            0.00000000        0.00000000        0.00000000
            0.00000000        0.00000000        0.00000000
MN          0.00000000        0.50000000        0.50000000       1.0000
            0.00000000        0.00000000        0.00000000       0.0000
            0.00065337        0.00065337        0.00065337
            0.00000165        0.00000165        0.00000165
            0.00000000        0.00000000        0.00000000
            0.00000000        0.00000000        0.00000000
MN          0.50000000        0.00000000        0.50000000       1.0000
            0.00000000        0.00000000        0.00000000       0.0000
            0.00065337        0.00065337        0.00065337
            0.00000165        0.00000165        0.00000165
            0.00000000        0.00000000        0.00000000
            0.00000000        0.00000000        0.00000000
O           0.05957463        0.49616399        0.25000000       1.0000
            0.00001546        0.00001610        0.00000000       0.0000
            0.00082010        0.00082010        0.00082010
            0.00000137        0.00000137        0.00000137
            0.00000000        0.00000000        0.00000000
            0.00000000        0.00000000        0.00000000
O           0.55957460        0.00383601        0.75000000       1.0000
            0.00001546        0.00001610        0.00000000       0.0000
            0.00082010        0.00082010        0.00082010
            0.00000137        0.00000137        0.00000137
            0.00000000        0.00000000        0.00000000
            0.00000000        0.00000000        0.00000000
O           0.94042540        0.50383604        0.75000000       1.0000
            0.00001546        0.00001610        0.00000000       0.0000
            0.00082010        0.00082010        0.00082010
            0.00000137        0.00000137        0.00000137
            0.00000000        0.00000000        0.00000000
            0.00000000        0.00000000        0.00000000
O           0.44042537        0.99616396        0.25000000       1.0000
            0.00001546        0.00001610        0.00000000       0.0000
            0.00082010        0.00082010        0.00082010
            0.00000137        0.00000137        0.00000137
            0.00000000        0.00000000        0.00000000
            0.00000000        0.00000000        0.00000000
O           0.72005206        0.28938726        0.03111255       1.0000
            0.00001528        0.00001560        0.00002506       0.0000
            0.00512371        0.00512371        0.00512371
            0.00000153        0.00000153        0.00000153
            0.00000000        0.00000000        0.00000000
            0.00000000        0.00000000        0.00000000
O           0.22005206        0.21061274        0.96888745       1.0000
            0.00001528        0.00001560        0.00002506       0.0000
            0.00512371        0.00512371        0.00512371
            0.00000153        0.00000153        0.00000153
            0.00000000        0.00000000        0.00000000
            0.00000000        0.00000000        0.00000000
O           0.27994794        0.71061277        0.53111255       1.0000
            0.00001528        0.00001560        0.00002506       0.0000
            0.00512371        0.00512371        0.00512371
            0.00000153        0.00000153        0.00000153
            0.00000000        0.00000000        0.00000000
            0.00000000        0.00000000        0.00000000
O           0.77994794        0.78938723        0.46888745       1.0000
            0.00001528        0.00001560        0.00002506       0.0000
            0.00512371        0.00512371        0.00512371
            0.00000153        0.00000153        0.00000153
            0.00000000        0.00000000        0.00000000
            0.00000000        0.00000000        0.00000000
O           0.27994794        0.71061277        0.96888745       1.0000
            0.00001528        0.00001560        0.00002506       0.0000
            0.00512371        0.00512371        0.00512371
            0.00000153        0.00000153        0.00000153
            0.00000000        0.00000000        0.00000000
            0.00000000        0.00000000        0.00000000
O           0.77994794        0.78938723        0.03111255       1.0000
            0.00001528        0.00001560        0.00002506       0.0000
            0.00512371        0.00512371        0.00512371
            0.00000153        0.00000153        0.00000153
            0.00000000        0.00000000        0.00000000
            0.00000000        0.00000000        0.00000000
O           0.72005206        0.28938726        0.46888745       1.0000
            0.00001528        0.00001560        0.00002506       0.0000
            0.00512371        0.00512371        0.00512371
            0.00000153        0.00000153        0.00000153
            0.00000000        0.00000000        0.00000000
            0.00000000        0.00000000        0.00000000
O           0.22005206        0.21061274        0.53111255       1.0000
            0.00001528        0.00001560        0.00002506       0.0000
            0.00512371        0.00512371        0.00512371
            0.00000153        0.00000153        0.00000153
            0.00000000        0.00000000        0.00000000
            0.00000000        0.00000000        0.00000000
"""

if __name__ == "__main__":

    unittest.main()
