"""One-cycle engineering regressions, not the #97 scientific confirmation."""
import copy
from fractions import Fraction as Q
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from signal_space.numerics.dyadic import Interval as I, norm_upper
from signal_space.numerics import validated_linked_memory as local
from signal_space.numerics.record_certificate_math import forced, identity, mm, opnorm, transport
from signal_space.numerics.record_tubes import produce
from signal_space.numerics.record_certificate_check import check, check_file, check_witness, separation_bounds


class ExactMajorantTests(unittest.TestCase):
    def test_linear_reachable_error_and_cancellation(self):
        # A=diag(4,1/4,...), B=A^-1. Product norms would give 16;
        # intact products give the EXACT reachable unit-ball radius 1.
        a,b=identity(96),identity(96)
        a[0][0]=I.exact(4);a[1][1]=I.exact(Q(1,4))
        b[0][0]=I.exact(Q(1,4));b[1][1]=I.exact(4)
        products,norms=transport([identity(96)],a,96)
        products,norms=transport(products,b,96)
        self.assertEqual(norms[0],1)
        self.assertEqual(forced(norms,Q(1,100),[Q(0),Q(0)],96),I.exact(Q(1,100)).upper())
        # Forcing at the first endpoint along e2 is amplified by 4 by B.
        bound=forced(norms,Q(0),[Q(1,100),Q(0)],96)
        self.assertGreaterEqual(bound,Q(1,25))
        self.assertLess(bound,Q(1,25)+Q(1,10**25))
        self.assertEqual(opnorm(identity(96),96),1)

    def test_interval_failure_requires_a_strict_lower_bound(self):
        # Pure arithmetic control, not a physical counterexample: high upper
        # bounds alone cannot establish failure, and equality is not violation.
        lower,failed=separation_bounds([I.exact(0).widen(1),I.exact(Q(1,4000))])
        self.assertFalse(failed)
        lower,failed=separation_bounds([I.exact(Q(1,2000)).widen(Q(1,1000000))])
        self.assertTrue(failed)
        self.assertGreater(lower[0],Q(1,4000))

    def test_known_nonlinear_map_and_no_period_reset(self):
        # Exact scalar f(x)=x+x^2 about x*=0, H=2, J=1.
        # The quadratic remainder recurrence reaches the positive extremum.
        radius=Q(1,100);q=Q(0);forcing=[]
        x=radius
        for n in range(4):
            forcing.append((radius+q)**2)
            q=sum(forcing,Q(0))
            x=x+x*x
            self.assertEqual(radius+q,x)
        self.assertGreater(q,forcing[-1])
        with self.assertRaises(ValueError): forced([Q(1)],radius,forcing,96)


class RecordTubeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets={s:produce(s) for s in ('active-plus','active-minus')}

    def test_both_seeds_all_records_at_a_and_b_endpoints(self):
        for seed,p in self.packets.items():
            self.assertEqual(p['termination'],'completed')
            self.assertEqual([s['event'] for s in p['steps']],[0,1])
            result=check(p)
            self.assertTrue(result['verified'],result)
            self.assertEqual(result['record_endpoint_horizons'],[2,2,2])
            self.assertEqual(result['cycle_horizon'],1)
            for s in p['steps']:
                self.assertEqual(len(s['tangent']),18)
                self.assertTrue(all(len(row)==16 for row in s['tangent']))
                self.assertGreater(Q(s['majorants']['Q']),Q(p['source']['chart_remainder_upper']))
                for row in s['record_terms']:
                    self.assertLess(Q(row['preparation']),Q(1,4000))
                    self.assertLess(Q(row['numerical']),Q(1,4000))
                    self.assertLess(Q(row['readout']),Q(1,4000))

    def test_saved_json_checker_does_not_call_trajectory_producer(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'proof.json'
            path.write_text(json.dumps(self.packets['active-plus']))
            with patch('signal_space.numerics.record_tubes.produce',side_effect=AssertionError('solver called')):
                self.assertTrue(check_file(path)['verified'])
            path.write_text('{"format":1,"format":2}')
            self.assertFalse(check_file(path)['verified'])

    def test_retained_engineering_proofs_and_hashes(self):
        import hashlib
        root=Path(__file__).resolve().parents[1]
        costs=json.loads((root/'docs/research/gross-record-tube-costs.json').read_text())
        for row in costs['rows']:
            proof=root/costs['fixture_proofs'][row['seed']]
            self.assertEqual(hashlib.sha256(proof.read_bytes()).hexdigest(),row['proof_sha256'])
            result=check_file(proof)
            self.assertTrue(result['verified'],result)
            self.assertEqual(result['record_endpoint_horizons'],[2,2,2])

    def test_proof_corruptions_rejected(self):
        mutations={
            'undersized input tube':lambda p:p['steps'][0]['input_domain'].__setitem__(0,p['initial_center'][0]),
            'undersized record tube':lambda p:p['steps'][1]['endpoint_domain'].__setitem__(0,p['steps'][1]['center'][0]),
            'Hessian reduced':lambda p:p['steps'][0]['bounds'].__setitem__('gate_hessian_upper','0'),
            'forcing omitted':lambda p:p['steps'][1]['majorants'].__setitem__('Q_forcing','0'),
            'budget changed':lambda p:p['config']['budgets'].__setitem__('preparation','1'),
            'column dropped':lambda p:p['steps'][1]['tangent'][0].pop(),
            'word reversed':lambda p:p['steps'][0].__setitem__('event',1),
            'inward interval':lambda p:p['steps'][0]['local']['gate']['values'][0].__setitem__('hi',p['steps'][0]['local']['gate']['values'][0]['lo']),
            'cycle reset':lambda p:p['steps'][1]['majorants'].__setitem__('Q',p['source']['chart_remainder_upper']),
            'transition omitted':lambda p:p['steps'][1]['transition_norms'].pop(0),
            'tail omitted':lambda p:p['steps'][0]['local']['proof']['exponentials'][0].pop('value_tail'),
            'false proof margin':lambda p:p['steps'][0]['margins'].__setitem__('Q','-1'),
            'source contract dropped':lambda p:p['source']['J0'][0].pop(),
        }
        for name,mutate in mutations.items():
            p=copy.deepcopy(self.packets['active-plus']);mutate(p)
            self.assertFalse(check(p)['verified'],name)

    def test_chart_remainder_and_adversarial_combined_directions(self):
        # A row's maximizing direction normally combines many columns. These
        # samples diagnose the implementation; the proof covers the entire ball.
        for seed,p in self.packets.items():
            row=p['steps'][1]['records']['derivative_centers'][2]
            tangent=p['steps'][1]['tangent']
            T=np.array([[float(I(int(x['lo']),int(x['hi'])).midpoint()) for x in r] for r in tangent])
            direction=np.array([float(Q(x)) for x in row])@T
            direction/=np.linalg.norm(direction)
            # Freeze rational inputs, inside the physical ball by margin.
            u=[Q(str(float(x)*0.99e-6)) for x in direction]
            self.assertGreater(sum(x != 0 for x in u),4)
            initial=local.source_chart(seed,u)
            source=local.source_chart(seed)
            J0=np.array(p['source']['J0'])
            linear=[sum((Q(int(v))*t for v,t in zip(row,u)),Q(0)) for row in J0]
            remainder=[x-y-z for x,y,z in zip(initial,source,linear)]
            self.assertLessEqual(norm_upper(remainder),sum((x*x for x in u),Q(0)))
            box=initial
            for event in (0,1):
                result=local.evaluate(box,event)
                self.assertEqual(result['status'],'enclosed')
                box=[I(int(x['lo']),int(x['hi'])) for x in result['gate']['values']]
                observed=local.record_jets(local.variables(box),event)
                endpoint=p['steps'][event]
                for l,(value,_) in enumerate(observed):
                    ref=Q(endpoint['record_terms'][l]['readout_center'])
                    self.assertLess((value-ref).magnitude(),Q(endpoint['record_terms'][l]['total']))

    def test_prefix_not_promoted_by_missing_later_endpoint(self):
        p=copy.deepcopy(self.packets['active-plus'])
        p['steps'].pop();p['termination']='unresolved';p['obstruction']='injected later resource stop'
        result=check(p)
        self.assertTrue(result['verified'],result)
        self.assertEqual(result['endpoint_horizon'],1)
        self.assertEqual(result['cycle_horizon'],0)
        self.assertFalse(result['target_met'])
        p['termination']='completed'
        self.assertFalse(check(p)['verified'])

    def test_invalid_modes_fail_closed_and_unproved_flags_ignored(self):
        for kw in ({'gates':0},{'gates':65},{'bits':53},{'wall_seconds':0}):
            with self.assertRaises(ValueError): produce(**kw)
        p=copy.deepcopy(self.packets['active-plus'])
        p['certified']=False
        self.assertTrue(check(p)['verified']) # reconstruct, never trust flags
        p['steps'][0]['record_terms'][0]['total']='0'
        p['certified']=True
        self.assertFalse(check(p)['verified'])

    def test_producer_only_omitted_record_remainder_rejected(self):
        from signal_space.numerics import record_tubes as producer
        original=producer.record_terms
        def missing_remainder(*args):
            rows=original(*args)
            for row in rows:
                row['preparation']=row['linear']
                row['total']=str(Q(row['preparation'])+Q(row['numerical'])+Q(row['readout']))
            return rows
        with patch.object(producer,'record_terms',missing_remainder):
            corrupt=producer.produce(gates=1)
        result=check(corrupt)
        self.assertFalse(result['verified'],result)
        self.assertEqual(result['reason'],'separate allocations / readout products')

    def test_loose_bound_is_unresolved_and_record_prefixes_are_separate(self):
        # Inflate a true curvature bound conservatively. It remains valid
        # mathematics but deliberately cannot certify all allocations.
        original=local.curvature
        def loose(box,event,duration):
            bounds=original(box,event,duration)
            if duration:
                bounds['gate_hessian_upper']=str(max(Q(bounds['gate_hessian_upper']),Q(400000000)))
            return bounds
        with patch.object(local,'curvature',loose):
            p=produce(gates=1)
            result=check(p)
        self.assertTrue(result['verified'],result)
        self.assertFalse(result['target_met'])
        self.assertEqual(result['classification'],'unresolved')
        self.assertGreater(max(result['record_endpoint_horizons']),min(result['record_endpoint_horizons']))
        self.assertTrue(any(Q(row['budgets']['preparation'])<0 for row in p['steps'][0]['margins']['records']))

    def test_counterexample_requires_admissible_validated_lower_bound(self):
        u=['0']*16;u[0]='1/2000000'
        boxes=[local.source_chart(),local.source_chart(u=u)]
        w={'format':'gross.record-witness.v1','seed':'active-plus','bits':96,'u':u,'steps':[]}
        step={'event':0}
        for key,box in zip(('nominal','perturbed'),boxes): step[key]=local.evaluate(box)
        w['steps'].append(step)
        r=check_witness(w)
        self.assertTrue(r['verified'],r)
        self.assertEqual(r['classification'],'unresolved')
        w['claimed_lower_bound']='1'
        self.assertEqual(check_witness(w)['classification'],'unresolved')
        w['u'][0]='1/1000'
        self.assertFalse(check_witness(w)['verified'])
        w['u'][0]='1/2000000'
        w['steps'][0]['perturbed']['gate']['values'][0]['hi']='0'
        self.assertFalse(check_witness(w)['verified'])


if __name__=='__main__': unittest.main()
