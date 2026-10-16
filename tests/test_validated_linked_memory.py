"""Bounded local engineering qualification. No trajectory/horizon inference."""
import copy
from fractions import Fraction as Q
import math
import unittest
from unittest.mock import patch

import numpy as np
from scipy.integrate import solve_ivp

from signal_space.models import linked_memory as floating
from signal_space.models.operators import SIGMA
from signal_space.numerics.dyadic import Interval as I, norm_upper, pi_interval
from signal_space.numerics import validated_linked_memory as v


def values(data):
    return np.array([float(Q(x)) for x in data['centers']])


def ambient(state):
    wave = np.stack((state[:3].real,state[:3].imag),axis=-1).ravel()
    ps = floating.outer(state[3:])
    return np.r_[wave,[(np.trace(p@s).real/2) for p in ps for s in SIGMA]]


def box_values(data):
    return [I(int(x['lo']),int(x['hi']),x['bits']) for x in data['values']]


class DyadicTests(unittest.TestCase):
    def test_exact_rational_operations_and_norm(self):
        for a in (Q(-7,3),Q(-1,7),Q(0),Q(1,13),Q(12,5)):
            for b in (Q(-2,5),Q(1,11),Q(3)):
                x,y = I.exact(a),I.exact(b)
                for z,exact in ((x+y,a+b),(x-y,a-b),(x*y,a*b),(x/y,a/b)):
                    self.assertTrue(z.contains(exact))
        x=I.exact(2).sqrt()
        self.assertLessEqual(Q(x.lo,1<<96)**2,2)
        self.assertGreaterEqual(x.upper()**2,2)
        self.assertEqual(norm_upper([3,4]),5)
        self.assertLess(norm_upper([Q(1,10**25)]),Q(2,10**25))
        with self.assertRaises(ArithmeticError): I.exact(0).reciprocal()
        with self.assertRaises(ValueError): I.exact(float('nan'))

    def test_pi_against_independent_rational_bounds(self):
        # Classical rational bounds are deliberately independent of Machin.
        p=pi_interval()
        self.assertGreater(Q(p.lo,1<<96),Q(103993,33102))
        self.assertLess(p.upper(),Q(104348,33215))
        for bits in (64,96,128):
            p=pi_interval(bits)
            self.assertGreater(p.radius(),0)
            self.assertLess(p.radius(),Q(1,10**15))

    def test_exponential_tail_obligation_is_exercised(self):
        x=v.variables([I.exact(1)])[0]
        # Under-resolve intentionally so a missing tail is visible independently
        # of rounding. exp(1) > its exact Taylor partial sum through degree 12.
        lower=sum((Q(1,math.factorial(k)) for k in range(13)),Q(0))
        with patch.object(v,'TERMS',2),patch.object(v,'SQUARINGS',2):
            proof=[]
            good=v.exponential([[x]],float('inf'),proof)[0][0]
            self.assertGreater(good.value.re.upper(),lower)
            self.assertGreater(Q(proof[0]['value_tail']),0)
            with patch.object(v.Complex,'widen',lambda self,r:self):
                broken=v.exponential([[x]],float('inf'),[])[0][0]
            self.assertLess(broken.value.re.upper(),lower)
            # D exp(x)=exp(x): also exercises differentiated omitted series.
            self.assertGreater(good.derivative[0].re.upper(),lower)
            self.assertLess(broken.derivative[0].re.upper(),lower)


class LocalBackendTests(unittest.TestCase):
    def enclose(self,box,event=0,**kwargs):
        result=v.evaluate(box,event,**kwargs)
        self.assertEqual(result['status'],'enclosed',result)
        return result

    def test_exact_identity_zero_duration_and_record_polynomial(self):
        box=[I.exact(0) for _ in range(18)]
        box[0]=I.exact(1); box[14]=I.exact(Q(1,2)); box[17]=I.exact(Q(-1,2))
        r=self.enclose(box,duration='0')
        for value,target in zip(box_values(r['gate']),box):
            self.assertTrue(value.contains(target.midpoint()))
        for i,row in enumerate(r['gate']['derivatives']):
            for j,x in enumerate(row):
                self.assertTrue(I(int(x['lo']),int(x['hi'])).contains(int(i==j)))
        self.assertEqual(Q(r['bounds']['gate_hessian_upper']),0)
        for value,target in zip(box_values(r['records']),(1,0,1)):
            self.assertTrue(value.contains(target))
        # Exact polynomial gradient dr1/d(Re z11)=2, dr1/dxAz=1.
        for j,target in ((0,2),(14,1)):
            x=r['records']['derivatives'][0][j]
            self.assertTrue(I(int(x['lo']),int(x['hi'])).contains(target))
        self.assertEqual(r['records']['value_error_norm_upper'],'0')

    def test_active_both_events_diagnostic_ode_all_physical_columns(self):
        for seed,event in (('active-plus',0),('active-minus',1)):
            state=floating.preparations()[seed]
            r=self.enclose(v.source_chart(seed),event)
            np.testing.assert_allclose(values(r['gate']),ambient(floating.gate(state,event,np.pi/2)),atol=3e-14)
            basis=floating.tangent_basis(state)
            initial=np.concatenate((state[None],basis)).ravel()
            sol=solve_ivp(floating.variational_rhs,(0,1),initial,args=(event,np.pi/2,16),
                          method='DOP853',rtol=2e-12,atol=2e-14,max_step=1/16)
            self.assertTrue(sol.success)
            out=sol.y[:,-1].reshape(17,5,2)
            derivatives=[]
            for delta in out[1:]:
                dp=[np.outer(dw,w.conj())+np.outer(w,dw.conj()) for w,dw in zip(out[0,3:],delta[3:])]
                derivatives.append(np.r_[np.stack((delta[:3].real,delta[:3].imag),axis=-1).ravel(),
                                          [np.trace(p@s).real/2 for p in dp for s in SIGMA]])
            jac=np.array([[float(Q(y)) for y in row] for row in r['gate']['derivative_centers']])
            j0=np.array(v.source_contract()['J0'])
            np.testing.assert_allclose(jac@j0,np.array(derivatives).T,atol=2e-10)
            np.testing.assert_allclose(values(r['records']),floating.records(state,event),atol=2e-14)

    def test_dark_commuting_degenerate_and_off_manifold(self):
        for event in (0,1):
            dark=[I.exact(0) for _ in range(18)]
            # Equal wave ports, P=I/2: S repeated, no eigengap division.
            dark[0]=dark[4]=dark[8]=I.exact(Q(1,2))
            r=self.enclose(dark,event)
            for x,target in zip(box_values(r['gate']),dark):
                self.assertTrue(x.contains(target.midpoint()))
            # Indefinite ambient ball is admissible, trace one by coordinates.
            dark[12]=I.exact(Q(7,10))
            tube=v.ball_box(dark,'0.000001')
            r=self.enclose(tube,event)
            self.assertFalse(r['bounds']['physicality_assumed'])
            self.assertGreater(Q(r['bounds']['gate_hessian_upper']),0)
            self.assertGreater(Q(r['bounds']['record_hessian_upper'][0]),0)
        # Isolated commuting A exchanges (e1,0) at kappa=pi/2.
        x=[I.exact(0) for _ in range(18)];x[0]=I.exact(1);x[14]=I.exact(Q(1,2))
        r=self.enclose(x)
        self.assertTrue(box_values(r['gate'])[0].contains(0))
        self.assertTrue(box_values(r['gate'])[4].contains(1))

    def test_invariants_and_covariance_with_exact_rational_controls(self):
        # Use rational coordinates so comparisons do not inherit float seeds.
        box=[I.exact(0) for _ in range(18)]
        box[0]=I.exact(Q(3,5));box[4]=I.exact(Q(1,5));box[10]=I.exact(Q(4,5))
        box[14]=I.exact(Q(1,2));box[17]=I.exact(Q(-1,2))
        def overlap(a,b):
            self.assertLessEqual(a.lo,b.hi);self.assertLessEqual(b.lo,a.hi)
        def invariants(x):
            # Independently reconstruct N and four Hermitian charge components.
            weight=sum((z.square() for z in x[:12]),I.exact(0))
            jx=x[12]+x[15];jy=x[13]+x[16];jz=x[14]+x[17]
            for k in (0,4,8):
                ar,ai,br,bi=x[k:k+4]
                jx=jx+ar*br+ai*bi
                jy=jy+ar*bi-ai*br
                jz=jz+(ar.square()+ai.square()-br.square()-bi.square())/2
            return [weight,jx,jy,jz]
        for event in (0,1):
            initial=invariants(box)
            r3=v.record_jets(v.variables(box),event)[2][0]
            for duration in ('1/3','1'):
                r=self.enclose(box,event,duration=duration)
                out=box_values(r['gate'])
                for a,b in zip(initial,invariants(out)): overlap(a,b)
                overlap(r3,v.record_jets(v.variables(out),event)[2][0])
                self.assertLess(Q(r['gate']['value_error_norm_upper']),Q(1,10**20))
            # Common wave phase i and internal U(2) swap are exact rational
            # transformations; Pauli coordinates transform without spinor phases.
            def transform(x,swap):
                y=list(x)
                for k in (0,4,8):
                    y[k:k+4]=x[k+2:k+4]+x[k:k+2] if swap else [-x[k+1],x[k],-x[k+3],x[k+2]]
                if swap:
                    for k in (12,15): y[k:k+3]=[x[k],-x[k+1],-x[k+2]]
                return y
            base=box_values(self.enclose(box,event)['gate'])
            for swap in (False,True):
                r=self.enclose(transform(box,swap),event)
                for a,b in zip(box_values(r['gate']),transform(base,swap)): overlap(a,b)

    def test_exact_first_word_complement_witness(self):
        box=[I.exact(0) for _ in range(18)]
        box[0]=box[10]=1/I.exact(2).sqrt()
        box[14]=I.exact(Q(1,2));box[17]=I.exact(Q(-1,2))
        for event in (0,1): box=box_values(self.enclose(box,event)['gate'])
        observed=2*sum(((box[k]+box[k+3]).square() for k in (12,13,14)),I.exact(0))
        # PR91 exact c^2=(2/5)sin^2(pi sqrt(5)/4); independent scalar
        # alternating Taylor enclosure, with absolute analytic remainder.
        x=pi_interval()*I.exact(5).sqrt()/4
        sine=I.exact(0)
        power=x
        for k in range(32):
            sine=sine+((-1)**k)*power/math.factorial(2*k+1)
            power=power*x*x
        sine=sine.widen(Q(2**65,math.factorial(65)))  # |x|<2
        expected=Q(2,5)*sine.square()
        self.assertLessEqual(observed.lo,expected.hi)
        self.assertLessEqual(expected.lo,observed.hi)
        self.assertGreater(observed.upper(),Q(38,100))
        self.assertLess(observed.upper(),Q(40,100))
        self.assertLess(observed.radius(),Q(1,10**18))

    def test_source_chart_all_sectors_and_seed_rounding(self):
        c=v.source_contract()
        j0=np.array(c['J0']); np.testing.assert_array_equal(j0.T@j0,np.eye(16))
        for seed in ('active-plus','active-minus'):
            u=[Q(k+1,10**7) for k in range(16)]
            source=v.source_chart(seed,u)
            state=floating.preparations()[seed]
            delta=np.einsum('n,nij->ij',np.array(list(map(float,u))),floating.tangent_basis(state))
            np.testing.assert_allclose([float(x.midpoint()) for x in source],ambient(floating.retract(state,delta)),atol=4e-16)
        self.assertGreater(Q(c['chart_remainder_upper']),Q(1,10**12))
        self.assertGreater(sum(x.radius() for x in v.source_chart()),0)

    def test_invalid_modes_and_resource_failure_have_no_payload(self):
        for kw in ({'bits':53},{'coupling':'machine-pi/2'},{'duration':'2'},
                   {'wall_seconds':0},{'wall_seconds':float('nan')},{'wall_seconds':1e-20}):
            r=v.evaluate(v.source_chart(),**kw)
            self.assertEqual(r['status'],'unresolved',r)
            self.assertNotIn('gate',r)
        for box in ([0]*17,[float('inf')]*18,[5]*18):
            self.assertEqual(v.evaluate(box)['status'],'unresolved')
        source=v.source_chart()
        with patch.object(v,'PYTHON',(0,0,0)):
            self.assertEqual(v.evaluate(source)['status'],'unresolved')

    def test_corruption_local_recomputation(self):
        box=v.source_chart(); r=self.enclose(box)
        self.assertTrue(v.check_local_output(r,box))
        mutations=[lambda p:p['gate']['radii'].__setitem__(0,'0'),
                   lambda p:p['gate']['derivative_centers'][0].__setitem__(0,'100'),
                   lambda p:p['records']['centers'].__setitem__(0,'100'),
                   lambda p:p['proof']['exponentials'][0].pop('value_tail'),
                   lambda p:p.__setitem__('bits',53)]
        for mutate in mutations:
            corrupt=copy.deepcopy(r);mutate(corrupt)
            self.assertFalse(v.check_local_output(corrupt,box))


if __name__=='__main__': unittest.main()
