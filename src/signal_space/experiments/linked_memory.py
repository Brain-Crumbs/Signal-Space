"""Separately registered v0.3 F0/F2/C1 seed, using unchanged SS OPS 1."""
from copy import deepcopy
from pathlib import Path
from signal_space.contracts.schema import check
from signal_space.contracts.validation import ContractError
from signal_space.experiments.base import ExperimentPlugin
from signal_space.runtime.io import read_json, write_json

ROOT = Path(__file__).resolve().parents[3]
CRITERIA = {
    "coverage": "Seven deterministic preparations, both operator tolerances, all controls and all 16 physical tangent directions are saved.",
    "coherent-equivalence": "Pure coherent lift and local records agree with exact_gate; direct tolerance halving is <=1e-9.",
    "conservation": "Within-gate H, total N/J, memory constraints and coherent purity residuals are <=1e-9 at both tolerances.",
    "null-commuting": "Exact dark word and isolated commuting gates preserve their analytically specified projectors within 1e-9.",
    "description-controls": "Fixed common U(2) and common wave phase preserve invariant histories within 1e-9.",
    "tangent-refinement": "Differentiated exact word agrees with centered chart differences at 1e-5 and 5e-6 within relative 1e-4 over the stated horizon.",
    "continuous-complement": "Universal continuous complementarity; a derived nonzero constraint derivative falsifies it.",
    "endpoint-complement": "Universal endpoint complementarity; a defect resolved by five numerical budgets falsifies it, sampled agreement alone is unresolved.",
    "prediction-certification": "End-to-end 1e-3 record-error certificate from initial error <=1e-6; missing validated integration/roundoff or readout enclosures remains unresolved.",
}


class LinkedMemoryExperiment(ExperimentPlugin):
    experiment_id = "gross.linked-memory-persistence.v1"
    model_id = "signal-space.ss-ops-1.v1"
    version = "1.0.0"

    def describe(self):
        return {"experiment_id":self.experiment_id,"model_id":self.model_id,"version":self.version,
            "name":"GROSS v0.3 linked-memory persistence and finite-horizon sensitivity",
            "claims":"Pure coherent representation, supplied two-event word, persistence and conditional finite-time bounds only.",
            "equations":["Operator Program v0.2 section 5, lambda=0"],
            "equation_sources":[{"label":"Linked-memory protocol","path":"docs/research/gross-linked-memory.md","catalog_id":"gross-linked-memory"}],
            "capabilities":["analysis","report","coherent-operator-lift","physical-tangent-map"],
            "unavailable_capabilities":["resume","checkpoint","autonomous clock","four-ray classification","validated interval certificate"]}

    def schema(self):
        value=read_json(ROOT/"contracts/research/linked-memory.schema.json")
        value["default"]=read_json(ROOT/"fixtures/research/gross-linked-memory.json")
        return value

    def validate(self,config):
        check(config,self.schema())
        if config["parameters"]["sensitivity_cycles"]>config["parameters"]["cycles"]:
            raise ContractError("sensitivity horizon exceeds nominal horizon")
        return deepcopy(config)

    def acceptance_criteria(self,config):
        return [{"id":k,"description":v,"evidence":None} for k,v in CRITERIA.items()]

    def known_gaps(self,config):
        return ["F0/F2/C1 seed only; no four-ray-frame classification or Test 1-11 acceptance.",
            "Gate parameter and ordering are supplied, not proper time or emerged physical space.",
            "Global Lipschitz comparison is conservative; validated floating residual/roundoff and readout enclosures are absent.",
            "Finite-time singular amplification is not Floquet stability without verified recurrence.",
            "Original preparation 2 commutes only initially; isolated gates are persistence controls, its full word is not.",
            "No restart; failed/partial attempts remain evidence and require a new bounded run."]

    def estimate(self,config):
        p=config["parameters"]
        return {"cpu_seconds":18+2*p["cycles"]+p["sensitivity_cycles"],
            "wall_seconds":20+2.5*p["cycles"]+1.2*p["sensitivity_cycles"],
            "memory_mb":384,"disk_mb":16+1.5*p["cycles"],"wall_time_class":"short",
            "basis":"Conservative serial engineering envelope; see readiness evidence. No campaign measurement."}

    def prepare(self,config,run_path,attempt_path,resume):
        if resume: raise ValueError("linked-memory v1 does not support resume")
        value={"model":self.model_id,"parameters":config["parameters"],"units":config["units"],
            "source":"docs/research/gross-linked-memory.md","preparation_revision":"commuting-word-correction-v1"}
        write_json(attempt_path/"preparation.json",value)
        return value

    def run(self,request_path):
        import os
        if any(os.environ.get(k)!="1" for k in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS")):
            raise ValueError("linked-memory plan permits one native numerical thread")
        from signal_space.numerics.linked_memory import execute
        return execute(request_path)

    def analyze(self,run_path,analysis_path,config):
        from signal_space.analysis.linked_memory import analyze
        return analyze(run_path,analysis_path,config)

    def classify(self,checks,config):
        statuses={c["id"]:c["status"] for c in checks["checks"]}
        if set(statuses)!=set(CRITERIA) or statuses["coverage"]!="pass": return "unresolved"
        if "fail" in statuses.values(): return "fail"
        if "unresolved" in statuses.values(): return "unresolved"
        return "pass"

    def report(self,run_path,report_path,manifest,analysis,render_provenance):
        from signal_space.reporting.linked_memory import render_report
        return render_report(run_path,report_path,manifest,analysis,render_provenance)
