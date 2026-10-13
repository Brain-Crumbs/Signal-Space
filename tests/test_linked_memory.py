"""Independent analytical controls for the v0.3 seed; no campaign acceptance."""
from copy import deepcopy
from pathlib import Path
import tempfile
import sys
import unittest
import numpy as np
from scipy.integrate import solve_ivp

from signal_space.models.linked_memory import (preparations, EVENTS, gate, word, outer, lift,
    amplitude_rhs, operator_rhs, gate_tangent, tangent_basis, feature_tangent,
    physical_features, variational_rhs, retract, complement_derivative, records,
    record_tangent, ROTATION, comparison_constants)
from signal_space.numerics.linked_memory import trace, sensitivity, PartialTraceError
from signal_space.experiments.linked_memory import LinkedMemoryExperiment
from signal_space.contracts.validation import ContractError
from signal_space.analysis.linked_memory import conditional_budget,validate_trace,record_derivative_comparisons
from signal_space.runtime.runner import ResearchRuntime
from signal_space.runtime.io import read_json

ROOT=Path(__file__).resolve().parents[1]


class LinkedMemoryTests(unittest.TestCase):
    def setUp(self):
        self.plugin=LinkedMemoryExperiment()
        self.config=self.plugin.schema()["default"]
        self.p=self.config["parameters"]
        self.k=self.p["kappa"]
        self.states=preparations()

    def test_closed_schema_and_horizon_rejection(self):
        self.plugin.validate(self.config)
        for mutate in (lambda c:c["parameters"].update(frozen=True),
                       lambda c:c["parameters"].update(**{"lambda":.1}),
                       lambda c:c["parameters"]["events"][0].__setitem__(0,False),
                       lambda c:c["analysis"].update(max_residual=.01),
                       lambda c:c["parameters"].update(cycles=1,sensitivity_cycles=2),
                       lambda c:c["parameters"].update(cycles=65)):
            changed=deepcopy(self.config);mutate(changed)
            with self.assertRaises(ContractError): self.plugin.validate(changed)

    def test_nominal_norms_coherence_loss_and_dark_word(self):
        for state in self.states.values():
            self.assertAlmostEqual(np.linalg.norm(state[:3])**2,1)
            np.testing.assert_allclose(np.linalg.norm(state[3:],axis=1),1)
        plus,minus=self.states["coherence-plus"],self.states["coherence-minus"]
        np.testing.assert_array_equal(outer(plus[:3]),outer(minus[:3]))
        self.assertEqual(records(plus,0)[-1],0)
        self.assertAlmostEqual(self.k*records(minus,0)[-1],self.k)
        self.assertGreater(np.linalg.norm(lift(plus)[0]-lift(minus)[0]),1)
        np.testing.assert_allclose(word(self.states["dark"],self.k,3),self.states["dark"],atol=2e-14)

    def test_commuting_full_word_claim_has_exact_obstruction(self):
        state=self.states["initially-commuting"]
        self.assertEqual(np.linalg.norm(complement_derivative(state,0,self.k)),0)
        after=gate(state,0,self.k)
        np.testing.assert_allclose(after[0],0,atol=1e-15)
        np.testing.assert_allclose(after[1],[1/np.sqrt(2),0],atol=1e-15)
        self.assertAlmostEqual(np.linalg.norm(complement_derivative(after,1,self.k)),self.k/np.sqrt(2))
        for event in (0,1):
            final=word(state,self.k,4,order=(event,))
            np.testing.assert_allclose(outer(final[3:]),outer(state[3:]),atol=2e-14)
        self.assertAlmostEqual(np.linalg.norm(complement_derivative(self.states["active-plus"],0,self.k)),np.sqrt(2)*self.k/3)

    def test_operator_lift_rhs_and_charge_transfer(self):
        state=self.states["active-plus"]
        for event in (0,1):
            derivative=amplitude_rhs(0,state,event,self.k)
            w,p=lift(state); dw,eta=derivative[:3].ravel(),derivative[3:]
            z=state[:3].ravel()
            dp=np.array([np.outer(v,u.conj())+np.outer(u,v.conj()) for u,v in zip(state[3:],eta)])
            lifted=np.concatenate(((np.outer(dw,z.conj())+np.outer(z,dw.conj())).ravel(),dp.ravel()))
            np.testing.assert_allclose(operator_rhs(0,np.concatenate((w.ravel(),p.ravel())),event,self.k),lifted,atol=1e-15)
            charge=sum(np.outer(v,u.conj())+np.outer(u,v.conj()) for u,v in zip(state,derivative))
            self.assertLess(np.linalg.norm(charge),1e-14)
            derivative[EVENTS[event][2]]*=0
            missing=sum(np.outer(v,u.conj())+np.outer(u,v.conj()) for u,v in zip(state,derivative))
            self.assertGreater(np.linalg.norm(missing),.1)
            inactive=set(range(5))-set(EVENTS[event])
            for wire in inactive: np.testing.assert_array_equal(gate(state,event,self.k)[wire],state[wire])

    def test_covariance_word_order_and_frozen_control(self):
        state=self.states["active-plus"]
        out=word(state,self.k,2)
        np.testing.assert_allclose(word(state@ROTATION.T,self.k,2)@ROTATION.conj(),out,atol=2e-14)
        phased=state.copy();phased[:3]*=np.exp(.37j)
        result=word(phased,self.k,2);result[:3]/=np.exp(.37j)
        np.testing.assert_allclose(physical_features(result),physical_features(out),atol=3e-14)
        self.assertGreater(np.linalg.norm(physical_features(word(state,self.k,order=(1,0)))-physical_features(word(state,self.k))),1e-3)
        frozen=gate(state,0,self.k,.5,frozen=True)
        self.assertGreater(np.linalg.norm(sum(outer(frozen))-sum(outer(state))),.01)

    def test_frechet_tangent_matches_independent_variational_equation(self):
        for name in ("active-plus","dark"):
            state=self.states[name];basis=tangent_basis(state)
            np.testing.assert_allclose(np.array([[np.vdot(x,y).real for y in basis] for x in basis]),np.eye(16),atol=1e-15)
            for event in (0,1):
                exact,delta=gate_tangent(state,basis,event,self.k)
                solved=solve_ivp(variational_rhs,(0,1),np.concatenate((state[None],basis)).ravel(),
                    args=(event,self.k,16),method="DOP853",rtol=1e-12,atol=1e-14,max_step=1/32)
                self.assertTrue(solved.success)
                ode=solved.y[:,-1].reshape(17,5,2)
                np.testing.assert_allclose(exact,ode[0],atol=2e-11)
                np.testing.assert_allclose(delta,ode[1:],atol=2e-10)

    def test_chain_rule_and_record_derivatives_refine(self):
        state=self.states["active-plus"];basis=tangent_basis(state)
        current,delta=state.copy(),basis.copy()
        for event in (0,1): current,delta=gate_tangent(current,delta,event,self.k)
        exact=feature_tangent(current,delta)
        analytic_records=record_tangent(current,delta,1)
        for epsilon in self.p["jacobian_steps"]:
            for n,direction in enumerate(basis):
                pair=[word(retract(state,sign*epsilon*direction),self.k) for sign in (-1,1)]
                np.testing.assert_allclose((physical_features(pair[1])-physical_features(pair[0]))/(2*epsilon),exact[:,n],atol=3e-8)
                np.testing.assert_allclose((records(pair[1],1)-records(pair[0],1))/(2*epsilon),analytic_records[:,n],atol=2e-8)

    def test_sampling_and_cancellation_retain_completed_gate(self):
        state=self.states["active-plus"]
        base=trace(state,self.p,1)
        fine=trace(state,self.p,1,refinement=2)
        np.testing.assert_allclose(base["flow"],fine["flow"][:,::2],atol=1e-15)
        self.assertGreater(np.linalg.norm(base["flow"][0,8]-base["flow"][0,0]),.1)
        calls=[]
        def cancel():calls.append(1);return len(calls)>1
        with self.assertRaises(PartialTraceError) as caught:trace(state,self.p,1,cancelled=cancel)
        self.assertEqual(caught.exception.arrays["flow"].shape[0],1)
        np.testing.assert_allclose(caught.exception.arrays["state"],base["flow"][0,-1])

    def test_saved_record_derivatives_cover_both_steps_every_prefix_and_sector(self):
        p=deepcopy(self.p);p["sensitivity_cycles"]=2
        limit=self.config["analysis"]["max_tangent_difference"]
        for name in p["sensitivity_preparations"]:
            data=sensitivity(self.states[name],p)
            clean=record_derivative_comparisons(data,p)
            self.assertEqual(clean.shape,(4,3))
            self.assertLess(clean.max(),limit)
            for g in range(4):
                for sector in (slice(0,12),slice(12,14),slice(14,16)):
                    with self.subTest(name=name,prefix=g,sector=sector):
                        changed={**data,"record_derivatives":data["record_derivatives"].copy()}
                        changed["record_derivatives"][g,:,sector]+=1
                        errors=record_derivative_comparisons(changed,p)
                        self.assertTrue(np.all(errors[g,:2]>limit))
                        np.testing.assert_array_equal(np.delete(errors,g,axis=0),np.delete(clean,g,axis=0))
                for h in range(2):
                    with self.subTest(name=name,prefix=g,step=h):
                        changed={**data,"finite_states":data["finite_states"].copy()}
                        changed["finite_states"][h,:,:,g]=0
                        errors=record_derivative_comparisons(changed,p)
                        self.assertGreater(errors[g,h],limit)
                        self.assertLess(errors[g,1-h],limit)
                        self.assertGreater(errors[g,2],limit)

    def test_global_bound_and_record_conversion_do_not_reset(self):
        l,k,n=comparison_constants(self.k,1e-6)
        self.assertGreater(l,6*self.k)
        rows=conditional_budget(self.p,self.config["analysis"])
        self.assertEqual(max(row["cycle"] for row in rows if row["ideal_preparation_budget_met"]),0)
        self.assertTrue(all(row["certified"]==0 for row in rows))
        self.assertTrue(all(rows[i+1]["preparation_record_bound"]>=rows[i]["preparation_record_bound"] for i in range(len(rows)-1)))
        state=self.states["active-plus"]
        for direction in tangent_basis(state):
            other=retract(state,1e-6*direction)
            self.assertLessEqual(max(abs(records(other,0)-records(state,0))),k*np.linalg.norm(other-state))

    def test_invalid_trace_metadata_and_continuity_are_rejected(self):
        state=self.states["active-plus"]
        original=trace(state,self.p,1);original["initial"]=state
        validate_trace(original,state,(0,1),1,17)
        for key,change in (("times",lambda x:x.fill(0)),("events",lambda x:x.__setitem__(1,0)),
            ("initial",lambda x:x.__setitem__((0,0),x[0,0]+.1)),
            ("final",lambda x:x.__setitem__((0,0),x[0,0]+.1)),
            ("flow",lambda x:x.__setitem__((1,0,0,0),x[1,0,0,0]+.1))):
            corrupted={k:v.copy() for k,v in original.items()};change(corrupted[key])
            with self.assertRaises(ValueError):validate_trace(corrupted,state,(0,1),1,17)

    def test_sensitivity_cancellation_retains_prefix_and_completion_masks(self):
        p=deepcopy(self.p);p["sensitivity_cycles"]=1
        calls=[]
        def cancel():calls.append(1);return len(calls)>2
        with self.assertRaises(PartialTraceError) as caught:sensitivity(self.states["active-plus"],p,cancel)
        saved=caught.exception.arrays
        self.assertEqual(saved["base"].shape,(2,5,2))
        self.assertEqual(saved["tangent"].shape,(2,28,16))
        self.assertFalse(saved["finite_completed"].any())
        self.assertFalse(saved["perturbations_completed"].any())

    def test_registered_engineering_fixture_packages_without_promoting_acceptance(self):
        # Crosses the actual schema, subprocess, JSON, report and export boundaries.
        # The horizon is the locked one-cycle fixture, never the campaign config.
        sys.path.insert(0,str(ROOT/".agents/scripts"))
        from experiment_contract import validate_plan,verify_runtime_config,validate_bundle
        from package_experiment import package
        from run_experiment import assessment
        plan_path=ROOT/"docs/research/plans/gross-linked-memory-smoke-v2.json"
        plan=read_json(plan_path);validate_plan(plan)
        config=read_json(verify_runtime_config(plan,ROOT))
        self.assertEqual(config["parameters"]["cycles"],1)
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);runtime=ResearchRuntime()
            run=runtime.run(config,folder/"runs")
            self.assertEqual(run["state"],"completed")
            analysis=runtime.analyze(folder/"runs",run["run_id"])
            report=runtime.report(folder/"runs",run["run_id"])
            path=Path(run["path"]);manifest=read_json(path/"manifest.json")
            checks=read_json(path/analysis["path"]/"checks.json")
            statuses={c["id"]:c["status"] for c in checks["checks"]}
            self.assertTrue(all(statuses[k]=="pass" for k in
                ("coverage","coherent-equivalence","conservation","null-commuting","description-controls","tangent-refinement")))
            self.assertEqual(statuses["continuous-complement"],"fail")
            self.assertEqual(statuses["prediction-certification"],"unresolved")
            self.assertEqual(analysis["summary"]["certified_horizon_cycles"],0)
            mentor=folder/"assessment.md";mentor.write_text(assessment(manifest,analysis,checks))
            package(path,plan_path,path/report["path"]/"interpretations.json",mentor,folder/"reader",ROOT/"src/signal_space")
            validate_bundle(folder/"reader",path)
            self.assertTrue(runtime.verify(folder/"runs",run["run_id"])["valid"])

            # Mutate only a disposable copy, never sealed canonical evidence.
            import shutil
            from signal_space.analysis.linked_memory import analyze
            copied=folder/"corrupted";shutil.copytree(path,copied)
            raw=next(copied.glob("attempts/*/raw/active-plus-sensitivity.npz"))
            with np.load(raw,allow_pickle=False) as archive: changed=dict(archive)
            changed["record_derivatives"].fill(0)
            np.savez_compressed(raw,**changed)
            corrupted=analyze(copied,folder/"corrupted-analysis",config)
            check=next(c for c in corrupted["checks"]["checks"] if c["id"]=="tangent-refinement")
            self.assertEqual(check["status"],"fail")
            self.assertGreater(corrupted["summary"]["max_record_derivative_difference"],config["analysis"]["max_tangent_difference"])
            self.assertEqual(corrupted["summary"]["certification_status"],"unresolved")


if __name__=="__main__":unittest.main()
