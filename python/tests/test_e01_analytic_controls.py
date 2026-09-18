"""Continuum specification controls, not an E01 solver or stability finding."""
import math
import unittest
import numpy as np


class AnalyticControlsTest(unittest.TestCase):
    def test_gaussian_energy_charge_radius_and_coupling_normalization(self):
        # Nonstationary manufactured profile: independent Gaussian integrals (§13).
        a, w, omega, coupling = 0.63, 1.7, 0.93, 0.01
        r = np.linspace(0, 14 * w, 60001)
        f = a * np.exp(-r*r/(2*w*w))
        fp = -r*f/(w*w)
        integral = a*a*math.pi**1.5*w**3
        exact_e = ((1+omega**2)*integral + 3*integral/(2*w*w)
                   - integral**2/(2**1.5*math.pi**1.5*w**3)
                   + integral**3/(3**1.5*math.pi**3*w**6))/coupling
        for lam in (coupling, 1.0):
            q = 8*math.pi*omega/lam*np.trapezoid(r*r*f*f, r)
            e = 4*math.pi/lam*np.trapezoid(r*r*(omega**2*f*f+fp*fp+f*f-f**4+f**6), r)
            self.assertAlmostEqual(q/(2*omega*integral/lam), 1, places=12)
            self.assertAlmostEqual(e/(exact_e*coupling/lam), 1, places=12)
        radius2 = np.trapezoid(r**4*f*f, r)/np.trapezoid(r*r*f*f, r)
        self.assertAlmostEqual(radius2, 1.5*w*w, places=12)

    def test_origin_and_exterior_three_dimensional_measure(self):
        f0, omega = 0.7, 0.93
        force = (1-omega**2)*f0-2*f0**3+3*f0**5
        second_derivative = force/3
        self.assertAlmostEqual(3*second_derivative, force)
        k, radius, fr, lam = math.sqrt(1-omega**2), 8.0, 0.001, 0.01
        r = np.linspace(radius, radius+40/k, 100001)
        f = fr*radius/r*np.exp(-k*(r-radius))
        fp = -(k+1/r)*f
        self.assertAlmostEqual(fp[0]+(k+1/radius)*fr, 0)
        amplitude = fr**2*radius**2
        i = np.trapezoid(r*r*f*f, r)
        t = np.trapezoid(r*r*fp*fp, r)
        r4 = np.trapezoid(r**4*f*f, r)
        self.assertAlmostEqual(i/(amplitude/(2*k)), 1, places=6)
        self.assertAlmostEqual(t/(amplitude*(k/2+1/radius)), 1, places=6)
        self.assertAlmostEqual(r4/(amplitude*(radius**2/(2*k)+radius/(2*k*k)+1/(4*k**3))), 1, places=6)
        self.assertGreater(4*math.pi/lam*t, 0)

    def test_fixed_charge_dilation_and_virial_energy_identity(self):
        # Choose integrals satisfying the stationary dilation identity only.
        # This does not assert that a profile exists with those integrals.
        t, v = 2.7, 4.1
        w = t/3+v
        energy = lambda scale: scale*t+scale**3*v+scale**-3*w
        h = 1e-4
        derivative = (energy(1-2*h)-8*energy(1-h)+8*energy(1+h)-energy(1+2*h))/(12*h)
        self.assertAlmostEqual(derivative, 0, places=9)
        self.assertAlmostEqual(energy(1)-2*w, 2*t/3, places=12)

    def test_potential_hessian_and_exp_sigma_vacuum_signs(self):
        omega, f = 0.93, 0.71
        effective = lambda u, v: (1-omega**2)*((f+u)**2+v*v)-((f+u)**2+v*v)**2+((f+u)**2+v*v)**3
        h = 1e-4
        plus = (effective(h, 0)-2*effective(0, 0)+effective(-h, 0))/(2*h*h)
        minus = (effective(0, h)-2*effective(0, 0)+effective(0, -h))/(2*h*h)
        self.assertAlmostEqual(plus, 1-omega**2-6*f*f+15*f**4, places=6)
        self.assertAlmostEqual(minus, 1-omega**2-2*f*f+3*f**4, places=6)
        for p in (0, 0.2, 2):
            a = p*p+1-omega**2
            for sign in (-1, 1):
                sigma = 1j*(math.sqrt(p*p+1)+sign*omega)
                determinant = (a+sigma*sigma)**2+4*omega*omega*sigma*sigma
                self.assertLess(abs(determinant), 1e-12)
