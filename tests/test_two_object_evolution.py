"""Independent action, preparation, record and restart checks for Test 8."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from signal_space.analysis.two_object_evolution import clock_history
from signal_space.experiments.two_object_evolution import TwoObjectEvolutionExperiment
from signal_space.numerics.two_object import AxisGrid
from signal_space.numerics.two_object_evolution import (
    DoubletGrid, charge_density, density, evolve_step, initial_state, quiet_residual,
    local_records, reduce_residual, weighted_norm,
)
from signal_space.numerics.two_object_evolution_worker import (
    restore_checkpoint, restore_fields, save_checkpoint,
    execute,
)
from signal_space.runtime.io import read_json

ROOT = Path(__file__).resolve().parents[1]


class DoubletActionTests(unittest.TestCase):
    def setUp(self):
        self.grid = DoubletGrid(.4, 2., 2.4, .8, 0.)
        rng = np.random.default_rng(27)
        shape = self.grid.volume.shape
        self.fields = (rng.normal(size=(2,*shape))*.03 + 1j*rng.normal(size=(2,*shape))*.03,
                       rng.normal(size=(2,*shape))*.02 + 1j*rng.normal(size=(2,*shape))*.02,
                       rng.normal(size=shape)*.02, rng.normal(size=shape)*.02,
                       rng.normal(size=shape)*.02, rng.normal(size=shape)*.02)

    def test_directional_hamiltonian_derivative_and_charge(self):
        g, s = self.grid, self.fields
        rhs = g.rhs(s)
        eps = 1e-6
        plus = tuple(q+eps*k for q,k in zip(s,rhs))
        minus = tuple(q-eps*k for q,k in zip(s,rhs))
        ep, qp = g.energy_charge(plus)
        em, qm = g.energy_charge(minus)
        self.assertLess(abs((ep-em)/(2*eps)), 2e-8)
        self.assertLess(abs((qp-qm)/(2*eps)), 2e-9)

    def test_force_is_independent_hamiltonian_gradient_for_both_components(self):
        g, fields = self.grid, self.fields
        force = g.rhs(fields)[1]
        eps = 1e-6
        for component, cell in [(0,(1,3)), (1,(2,4))]:
            index = (component, *cell)
            for direction in (1.,1j):
                plus, minus = [q.copy() for q in fields], [q.copy() for q in fields]
                plus[0][index] += eps*direction
                minus[0][index] -= eps*direction
                derivative = (g.energy_charge(plus)[0]-g.energy_charge(minus)[0])/(2*eps)
                expected = -2*g.volume[cell]*np.real(np.conj(direction)*force[index])
                self.assertAlmostEqual(derivative,expected,delta=2e-9)

    def test_zero_second_component_is_the_existing_exact_reduction(self):
        g = self.grid
        fields = [q.copy() for q in self.fields]
        fields[0][1] = fields[1][1] = 0
        scalar = (fields[0][0], fields[1][0], *fields[2:])
        reference = AxisGrid(g.h,g.nr*g.h,g.nz*g.h/2)
        er, qr = reference.energy_charge(scalar)
        ed, qd = g.energy_charge(fields)
        self.assertAlmostEqual(er,ed,delta=2e-12)
        self.assertAlmostEqual(qr,qd,delta=2e-12)
        rhs, expected = g.rhs(fields), reference.rhs(scalar)
        np.testing.assert_allclose(rhs[1][0],expected[1],rtol=1e-13,atol=1e-14)
        self.assertTrue(np.array_equal(rhs[1][1],np.zeros_like(rhs[1][1])))

    def test_global_internal_unitary_covariance(self):
        U = np.asarray([[1,1j],[1j,1]])/np.sqrt(2)
        fields = self.fields
        rotated = (np.einsum('ab,bij->aij',U,fields[0]),
                   np.einsum('ab,bij->aij',U,fields[1]),*fields[2:])
        np.testing.assert_allclose(density(rotated[0]),density(fields[0]),rtol=2e-15,atol=1e-17)
        np.testing.assert_allclose(self.grid.rhs(rotated)[1],
                                  np.einsum('ab,bij->aij',U,self.grid.rhs(fields)[1]),atol=3e-15)
        self.assertAlmostEqual(self.grid.energy_charge(rotated)[0],self.grid.energy_charge(fields)[0],delta=1e-13)

    def test_neutral_reversal_and_exact_null(self):
        s = (*self.fields,0.,0.,0.)
        reversed_state = (*s[:4],-s[4],-s[5],*s[6:])
        first, second = evolve_step(self.grid,s,.002), evolve_step(self.grid,reversed_state,.002)
        for i in range(4): np.testing.assert_array_equal(first[i],second[i])
        for i in (4,5): np.testing.assert_array_equal(first[i],-second[i])
        null = (*s[:4],np.zeros_like(s[4]),np.zeros_like(s[5]),*s[6:])
        advanced = evolve_step(self.grid,null,.002)
        for i in (4,5): self.assertEqual(np.count_nonzero(advanced[i]),0)

    def test_cell_energy_and_charge_balance_match_face_currents(self):
        g, s = self.grid, self.fields
        k = g.rhs(s)
        eps=1e-6
        edot = (g.cell_energy(tuple(q+eps*r for q,r in zip(s,k)))
                -g.cell_energy(tuple(q-eps*r for q,r in zip(s,k))))/(2*eps)
        energy, charge = g.face_fluxes(s)
        np.testing.assert_allclose(edot,-g.volume*g.divergence(*energy),rtol=2e-7,atol=2e-10)
        qdot = charge_density(s[0],k[1])
        np.testing.assert_allclose(qdot,-g.divergence(*charge),rtol=2e-12,atol=2e-14)

    def test_residual_correction_reduces_actual_residual(self):
        g = self.grid
        part = np.stack([np.exp(-np.hypot(g.r[:,None],g.z[None,:])**2), np.zeros_like(g.volume)])*.2
        psi, result = reduce_residual(g,[part],{'iterations':2,'damping':.1,
            'max_linear_iterations':30,'max_correction_fraction':.05})
        self.assertLess(result['final_norm'],result['initial_norm'])
        self.assertAlmostEqual(result['final_norm'],weighted_norm(g,quiet_residual(g,psi)))
        self.assertFalse(result['stationary_pair_established'])


class LocalRecordTests(unittest.TestCase):
    def test_extraction_includes_convective_derivative(self):
        g=DoubletGrid(.05,10.,12.,1.,0.)
        speed, omega=.2,.9
        lorentz=1/np.sqrt(1-speed**2)
        z=g.z[None,:]
        F=np.exp(-(g.r[:,None]**2+z*z)/4)*.1
        phase=np.exp(1j*lorentz*omega*speed*z)
        phi=np.stack([F*phase,np.zeros_like(F,dtype=complex)])
        pi=np.stack([(-1j*lorentz*omega*F+speed*z*F/2)*phase,np.zeros_like(F,dtype=complex)])
        chi=np.broadcast_to(.001+.0002*z,F.shape).copy()
        pchi=np.full_like(F,.0003)
        state=(phi,pi,chi,pchi,np.zeros_like(F),np.zeros_like(F),0.,0.,0.)
        profile={'r':np.linspace(0,20,201),'u':np.exp(-np.linspace(.1,19.9,199)**2),
                 'mode':np.exp(-np.linspace(.1,19.9,199)**2)}
        record=local_records(g,state,{'pair':False,'separation':40.,'tube_radius':8.,'omega_clock':.4},profile)[0]
        self.assertAlmostEqual(record['speed'],speed,delta=1e-4)
        self.assertAlmostEqual(record['dchi_dt'],.0003+record['speed']*.0002,delta=2e-15)
        self.assertAlmostEqual(record['dchi_dtau'],record['dchi_dt']/np.sqrt(1-record['speed']**2),delta=2e-15)

    def test_moving_clock_uses_proper_time_and_sign_invariant_ticks(self):
        omega, speed = .4, .3
        rate=np.sqrt(1-speed**2)
        samples=[]
        for t in np.linspace(0,40,401):
            tau=rate*t
            tube={key:0. for key in ('energy','charge','momentum','energy_flux','charge_flux','momentum_flux',
                                     'energy_sink_rate','charge_sink_rate','momentum_sink_rate')}
            c={'proper_rate':rate,'chi':np.cos(omega*tau),'dchi_dtau':-omega*np.sin(omega*tau),
               'envelope':1.,'center':speed*t,'tube':tube}
            samples.append({'t':t,'clocks':[c]})
        h=clock_history(samples,0,omega)
        np.testing.assert_allclose(h['tau'],rate*h['t'],atol=2e-13)
        np.testing.assert_allclose(h['ticks'],omega*h['tau']/np.pi,atol=2e-14)
        self.assertEqual(len(h['zero_times']),5)
        np.testing.assert_allclose(h['zero_slopes'],omega,rtol=1e-7)
        flipped=deepcopy(samples)
        for s in flipped:
            s['clocks'][0]['chi']*=-1
            s['clocks'][0]['dchi_dtau']*=-1
        np.testing.assert_array_equal(h['ticks'],clock_history(flipped,0,omega)['ticks'])


class ConfigAndRestartTests(unittest.TestCase):
    def test_worker_resumes_midcase_and_case_boundary_without_changing_prior_bytes(self):
        config=read_json(ROOT/'fixtures/research/gross-test-08-evolution-pilot.json')
        cases=[]
        for label in ('pair-base','pair-orthogonal'):
            original=next(c for c in config['parameters']['scenarios'] if c['label']==label)
            cases.append({**original,'duration':.12,'sample_stride':2})
        config['parameters']['scenarios']=cases
        config['parameters']['checkpoint_stride']=3
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            first=root/'attempts/attempt-0001'
            first.mkdir(parents=True)
            request={'attempt_path':str(first),'attempt_id':'attempt-0001','config':config,
                     'config_hash':'b'*64,'code_identity_hash':'c'*64,'seed_ledger':[]}
            path=first/'request.json'
            path.write_text(json.dumps(request))
            self.assertEqual(execute(path),0)
            originals={p.relative_to(first).as_posix():p.read_bytes() for p in first.rglob('*') if p.is_file()}
            for n,checkpoint in enumerate(('checkpoint-0000000003-000.json','checkpoint-0000000006-001.json'),start=2):
                attempt=root/f'attempts/attempt-000{n}'
                attempt.mkdir()
                resumed={**request,'attempt_path':str(attempt),'attempt_id':f'attempt-000{n}',
                         'parent_attempt_id':'attempt-0001','resume_checkpoint':read_json(first/'checkpoints'/checkpoint)}
                p=attempt/'request.json';p.write_text(json.dumps(resumed))
                self.assertEqual(execute(p),0)
                for c in cases:
                    name=c['label']
                    self.assertEqual(read_json(first/'raw'/f'{name}-traces.json'),read_json(attempt/'raw'/f'{name}-traces.json'))
                    with np.load(first/'raw'/f'{name}-final.npz') as a, np.load(attempt/'raw'/f'{name}-final.npz') as b:
                        for key in a.files: np.testing.assert_array_equal(a[key],b[key])
            for relative,content in originals.items(): self.assertEqual((first/relative).read_bytes(),content)

    def test_control_matrix_and_independent_space_time_are_enforced(self):
        plugin=TwoObjectEvolutionExperiment()
        config=read_json(ROOT/'fixtures/research/gross-test-08-evolution-pilot.json')
        plugin.validate(config)
        for label,key,value in [('pair-space','dt',.01),('pair-time','h',.4),
                                ('pair-wide','absorber_width',6.),('pair-reduced','pair',False)]:
            bad=deepcopy(config)
            next(c for c in bad['parameters']['scenarios'] if c['label']==label)[key]=value
            with self.assertRaises(ValueError): plugin.validate(bad)
        with self.assertRaises(ValueError): plugin.validate({**config,'unexpected':True})

    def test_restart_is_exact_and_rejects_corruption(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            first=root/'attempts/attempt-0001'
            second=root/'attempts/attempt-0002'
            for attempt in (first,second): (attempt/'raw').mkdir(parents=True)
            grid=DoubletGrid(.4,2.,2.4,.8,.1)
            rng=np.random.default_rng(13)
            q=rng.normal(size=grid.volume.shape)*.01
            state=(np.stack([q.astype(complex),q*.2j]),np.stack([q*-.9j,q*.1]),q.copy(),q*.01,q*.02,q*.03,0.,0.,0.)
            config={'parameters':{'profile':{'path':'frozen','sha256':'a'*64}}}
            request={'attempt_path':str(first),'attempt_id':'attempt-0001','config':config,
                     'config_hash':'b'*64,'code_identity_hash':'c'*64,'seed_ledger':[]}
            for _ in range(3): state=evolve_step(grid,state,.002)
            checkpoint=save_checkpoint(request,count=3,case_index=0,index=3,state=state,grid=grid,
                samples=[{'t':0.,'tick':3}],cases=[],preparation={'record':'retained'},max_neutral=.02)
            payload=read_json(checkpoint)
            resumed={**request,'attempt_path':str(second),'attempt_id':'attempt-0002',
                     'parent_attempt_id':'attempt-0001','resume_checkpoint':payload}
            saved=restore_checkpoint(resumed)
            replay=restore_fields(resumed,saved,grid)
            self.assertEqual(saved['accumulated_diagnostics']['samples'],[{'t':0.,'tick':3}])
            for _ in range(5):
                state=evolve_step(grid,state,.002)
                replay=evolve_step(grid,replay,.002)
            for a,b in zip(state,replay): np.testing.assert_array_equal(a,b)
            p=root/payload['solver_state']['state']['path']
            p.write_bytes(p.read_bytes()+b'corruption')
            with self.assertRaisesRegex(ValueError,'hash mismatch'): restore_checkpoint(resumed)


if __name__=='__main__': unittest.main()
