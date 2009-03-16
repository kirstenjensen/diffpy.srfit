#!/usr/bin/env python
"""Tests for refinableobj module."""

import diffpy.srfit.equation.builder as builder
import diffpy.srfit.equation.literals as literals

import unittest

import numpy

from utils import _makeArgs


class TestEquationParser(unittest.TestCase):

    def testParseEquation(self):

        from numpy import exp, sin, divide, sqrt, array_equal, e

        # Scalar equation
        eq = builder.makeEquation("A*sin(0.5*x)+divide(B,C)")
        A = 1
        x = numpy.pi
        B = 4.0
        C = 2.0
        eq.A.setValue(A)
        eq.x.setValue(x)
        eq.B.setValue(B)
        eq.C.setValue(C)
        f = lambda A, x, B, C: A*sin(0.5*x)+divide(B,C)
        self.assertTrue(array_equal(eq(), f(A,x,B,C)))


        # Vector equation
        eq = builder.makeEquation("sqrt(e**(-0.5*(x/sigma)**2))")
        x = numpy.arange(0, 1, 0.05)
        sigma = 0.1
        eq.x.setValue(x)
        eq.sigma.setValue(sigma)
        f = lambda x, sigma : sqrt(e**(-0.5*(x/sigma)**2))
        self.assertTrue(array_equal(eq(), f(x,sigma)))


        # Equation with constants
        consts = {"x" : x}
        eq = builder.makeEquation("sqrt(e**(-0.5*(x/sigma)**2))", consts=consts)
        self.assertTrue("sigma" in eq.args)
        self.assertTrue("x" not in eq.args)
        self.assertTrue(array_equal(eq(sigma=sigma), f(x,sigma)))


        # Equation with user-defined functions
        builder.wrapFunction("myfunc", eq, 1)
        eq2 = builder.makeEquation("c*myfunc(sigma)")
        self.assertTrue(array_equal(eq2(c=2, sigma=sigma), 2*f(x,sigma)))
        self.assertTrue("sigma" in eq2.args)
        self.assertTrue("c" in eq2.args)

        # Equation with partition
        p1 = literals.Partition("p1")
        v1, v2 = _makeArgs(2)
        p1.addArgument(v1)
        p1.addArgument(v2)
        builder.wrapPartition("p1", p1)
        eq = builder.makeEquation("A*p1 + B")
        eq.A.setValue(A)
        eq.B.setValue(B)
        self.assertEquals( (1*1+4)+(1*2+4), eq() )
        

        # Equation with Generator
        g1 = literals.Generator("g1")
        g1.literal = p1
        builder.wrapGenerator("g1", g1)
        eq = builder.makeEquation("A*g1 + B")
        eq.A.setValue(A)
        eq.B.setValue(B)
        self.assertEquals( (1*1+4)+(1*2+4), eq() )
        return

    def testBuildEquation(self):

        from numpy import array_equal

        # simple equation
        sin = builder.sin
        a = builder.ArgumentBuilder(name="a", value = 1)
        A = builder.ArgumentBuilder(name="A", value = 2)
        x = numpy.arange(0, numpy.pi, 0.1)

        beq = A*sin(a*x)
        eq = beq.getEquation()

        self.assertTrue("a" in eq.args)
        self.assertTrue("A" in eq.args)
        self.assertTrue(array_equal(eq(), 2*numpy.sin(x)))


        # custom function
        def _f(a, b):
            return (a-b)*1.0/(a+b)

        f = builder.wrapFunction("f", _f, 2, 1)
        sin = builder.sin
        a = builder.ArgumentBuilder(name="a", value = 2)
        b = builder.ArgumentBuilder(name="b", value = 1)

        beq = sin(f(a,b))
        eq = beq.getEquation()
        self.assertEqual(eq(), numpy.sin(_f(2, 1)))

        # complex function
        sqrt = builder.sqrt
        e = numpy.e
        _x = numpy.arange(0, 1, 0.05)
        x = builder.ArgumentBuilder(name="x", value = _x, const = True)
        sigma = builder.ArgumentBuilder(name="sigma", value = 0.1)
        beq = sqrt(e**(-0.5*(x/sigma)**2))
        eq = beq.getEquation()
        f = lambda x, sigma : sqrt(e**(-0.5*(x/sigma)**2))
        self.assertTrue(array_equal(eq(), numpy.sqrt(e**(-0.5*(_x/0.1)**2))))


        # Equation with partition
        _p1 = literals.Partition("p1")
        v1, v2 = _makeArgs(2)
        _p1.addArgument(v1)
        _p1.addArgument(v2)
        A = builder.ArgumentBuilder(name="A", value = 1)
        B = builder.ArgumentBuilder(name="A", value = 4)
        p1 = builder.wrapPartition("p1", _p1)
        beq = A*p1 + B
        eq = beq.getEquation()
        self.assertEquals( (1*1+4)+(1*2+4), eq() )
        

        # Equation with Generator
        _g1 = literals.Generator("g1")
        _g1.literal = _p1
        g1 = builder.wrapGenerator("g1", _g1)
        geq = A*g1 + B
        eq = geq.getEquation()
        self.assertEquals( (1*1+4)+(1*2+4), eq() )

        return


if __name__ == "__main__":

    unittest.main()

