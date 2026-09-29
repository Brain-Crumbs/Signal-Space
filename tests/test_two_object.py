"""Independent axisymmetric controls for the Test 8 spatial foundation."""
import numpy as np
import unittest

from signal_space.numerics.two_object import AxisGrid, step_rk4


class TwoObjectNumericsTests(unittest.TestCase):
 def test_axis_regular_manufactured_laplacian_and_constant_null(self):
    grid = AxisGrid(.2, 4, 6)
    rho = grid.r[:, None]
    z = grid.z[None, :]
    manufactured = rho**2 + z**2
    lap = grid.laplacian(manufactured)
    # Δ(rho²+z²)=4+2=6 in three spatial dimensions, including the axis cell.
    assert np.max(abs(lap[1:-1, 1:-1] - 6)) < 1e-11
    assert np.max(abs(lap[0, 1:-1] - 6)) < 1e-11
    assert np.array_equal(grid.laplacian(np.ones_like(manufactured)),
                          np.zeros_like(manufactured))


 def test_neutral_face_flux_is_antisymmetric_and_no_boundary_flux(self):
    grid = AxisGrid(.25, 3, 4)
    rng = np.random.default_rng(438)
    neutral = rng.normal(size=(grid.nr, grid.nz))
    Z = 1 + .2 * rng.random(neutral.shape)
    assert abs(np.sum(grid.volume * grid.laplacian(neutral, Z))) < 1e-12
    # The face bilinear form is negative definite up to constants.
    assert np.sum(grid.volume * neutral * grid.laplacian(neutral, Z)) < 0


 def test_action_gradient_matches_canonical_core_acceleration(self):
    grid = AxisGrid(.5, 3, 4)
    rng = np.random.default_rng(221)
    shape=(grid.nr,grid.nz)
    phi=.15*rng.normal(size=shape)+.09j*rng.normal(size=shape)
    chi=.04*rng.normal(size=shape)
    a=.2*rng.normal(size=shape)
    pia=.12*rng.normal(size=shape)
    zero=np.zeros(shape)
    state=(phi,np.zeros_like(phi),chi,zero,a,pia)
    acceleration=grid.rhs(state)[1]
    i,j=2,4;delta=1e-6
    def energy(perturb):
        q=phi.copy();q[i,j]+=perturb
        return grid.energy_charge((q,state[1],chi,zero,a,pia))[0]
    # For complex phi, dE/dRe(phi)=-2 V d(pi_real)/dt.
    derivative=(energy(delta)-energy(-delta))/(2*delta)
    assert abs(derivative + 2*grid.volume[i,j]*acceleration[i,j].real) < 2e-8
    derivative=(energy(1j*delta)-energy(-1j*delta))/(2*delta)
    assert abs(derivative + 2*grid.volume[i,j]*acceleration[i,j].imag) < 2e-8


 def test_exact_zero_neutral_and_charge_in_short_evolution(self):
    grid=AxisGrid(.5,3,4)
    rho=grid.r[:,None]; z=grid.z[None,:]
    phi=.2*np.exp(-rho**2-z**2)
    zero=np.zeros_like(phi)
    state=(phi.astype(complex),(-.9j*phi).astype(complex),zero.copy(),zero.copy(),
           zero.copy(),zero.copy())
    q0=grid.energy_charge(state)[1]
    for _ in range(20):
        state=step_rk4(grid,state,.02)
    assert not np.any(state[4]) and not np.any(state[5])
    assert abs(grid.energy_charge(state)[1]-q0)/q0 < 1e-8


if __name__ == '__main__':
    unittest.main()
