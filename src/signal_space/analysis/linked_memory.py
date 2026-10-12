"""Audit saved linked-memory data; analysis never reruns the event evolution."""
import numpy as np

from signal_space.models.linked_memory import (PREPARATIONS, EVENTS, ROTATION, COMMON_PHASE,
    outer, lift, preparations, tangent_basis, retract, physical_features, comparison_constants, complement_derivative)
from signal_space.models.operators import SIGMA
from signal_space.numerics.operators import write_rows
from signal_space.runtime.io import read_json, write_json


def measures(wave, memories, event, kappa):
    i, j, a = EVENTS[event]; p = memories[a - 3]
    blocks = [wave[2 * n:2 * n + 2, 2 * n:2 * n + 2] for n in range(3)]
    d = blocks[i] + blocks[j] - wave[2*i:2*i+2, 2*j:2*j+2] - wave[2*j:2*j+2, 2*i:2*i+2]
    records = np.array([np.trace(blocks[i] @ p).real, np.trace(blocks[j] @ p).real,
                        np.trace(d @ p).real])
    n = np.trace(wave).real
    charge = sum(blocks) + sum(memories)
    c = np.linalg.norm(sum(memories) - np.eye(2))
    overlap = np.trace(memories[0] @ memories[1]).real
    residual = max(np.linalg.norm(wave - wave.conj().T),
        np.linalg.norm(wave @ wave - n * wave),
        max(np.linalg.norm(p @ p - p) for p in memories),
        max(np.linalg.norm(p - p.conj().T) for p in memories),
        max(abs(np.trace(p) - 1) for p in memories),
        max(0., -np.linalg.eigvalsh((wave + wave.conj().T) / 2).min()),
        abs(c * c - 2 * overlap))
    return n, charge, kappa * records[-1], records, c, overlap, float(residual)


def load(path):
    with np.load(path, allow_pickle=False) as z:
        out = dict(z)
    if any(not np.all(np.isfinite(v)) for v in out.values()):
        raise ValueError(f"nonfinite raw data: {path.name}")
    return out


def validate_trace(data, initial, order, cycles, samples, operator=False):
    """Validate saved metadata and state continuity before any scientific check."""
    events = np.tile(order, cycles)
    expected_shape = (len(events), samples, 44) if operator else (len(events), samples, 5, 2)
    if set(data) != {"flow","final","events","times","initial"} or data["flow"].shape != expected_shape:
        raise ValueError("incomplete trace fields or sample shape")
    if not np.array_equal(data["events"],events) or not np.array_equal(data["times"],np.linspace(0,1,samples)):
        raise ValueError("changed trace schedule or sample grid")
    if not np.array_equal(data["initial"],initial): raise ValueError("changed trace preparation")
    expected_start = initial
    if operator:
        w,p=lift(initial);expected_start=np.concatenate((w.ravel(),p.ravel()))
    if data["final"].shape != expected_start.shape or not np.array_equal(data["final"],data["flow"][-1,-1]):
        raise ValueError("final state does not match the saved endpoint")
    if np.max(abs(data["flow"][0,0]-expected_start))>1e-12:
        raise ValueError("trace starts outside the declared preparation")
    if len(events)>1 and np.max(abs(data["flow"][1:,0]-data["flow"][:-1,-1]))>1e-12:
        raise ValueError("discontinuous adjacent gates")


def conditional_budget(parameters, criteria):
    l, k, n = comparison_constants(parameters["kappa"], parameters["initial_error"])
    rows = []
    for cycle in range(parameters["cycles"] + 1):
        # q is between 0 and 2N on both exact trajectories. Avoid overflow by
        # capping the exponential with that independently proved range bound.
        log_bound = np.log(k * parameters["initial_error"]) + l * 2 * cycle
        bound = np.exp(min(log_bound, np.log(2 * n)))
        rows.append({"cycle": cycle, "gate_parameter_total": 2 * cycle,
            "L": l, "record_Lipschitz": k, "preparation_record_bound": bound,
            "preparation_allocation": criteria["preparation_budget"],
            "total_target": criteria["record_target"],
            "ideal_preparation_budget_met": int(bound <= criteria["preparation_budget"]),
            "integration_enclosed": 0, "readout_enclosed": 0, "certified": 0})
    return rows


def analyze(run_path, output, config):
    executions = sorted((run_path / "attempts").glob("*/raw/execution.json"))
    if not executions: raise ValueError("no completed linked-memory attempt")
    raw = executions[-1].parent
    p, a = config["parameters"], config["analysis"]
    execution = read_json(raw / "execution.json")
    if execution["parameters"] != p or execution["preparations"] != list(PREPARATIONS):
        raise ValueError("raw settings differ from the resolved config")
    expected = {f"{name}-{v}.npz" for name in PREPARATIONS for v in
        ("exact", "operator", "operator-fine", "exact-fine", "frozen",
         "isolated-A", "isolated-B", "reverse", "rotated", "common-phase")}
    expected |= {f"{name}-sensitivity.npz" for name in p["sensitivity_preparations"]}
    if set(execution["files"]) != expected or any(not (raw / f).is_file() for f in expected):
        raise ValueError("incomplete nominal, control or sensitivity coverage")
    trajectories, audits, controls, sensitivities, endpoint_cases = [], [], [], [], []
    max_equivalence = max_conservation = max_null = max_description = max_operator_refinement = 0.
    max_tangent = 0.
    analytic_derivatives = {}
    for name in PREPARATIONS:
        exact = load(raw / f"{name}-exact.npz")
        fine_exact = load(raw / f"{name}-exact-fine.npz")
        initial = exact["initial"]
        if not np.array_equal(initial, preparations()[name]):
            raise ValueError("raw initial data differs from the declared preparation")
        validate_trace(exact,initial,(0,1),p["cycles"],p["samples_per_gate"])
        validate_trace(fine_exact,initial,(0,1),p["cycles"],p["refined_samples_per_gate"])
        if exact["flow"].shape != (2*p["cycles"], p["samples_per_gate"], 5, 2):
            raise ValueError("incomplete amplitude samples")
        initial_w, initial_p = lift(initial)
        n0, j0, *_ = measures(initial_w, initial_p, 0, p["kappa"])
        if abs(n0 - 1) > 1e-12 or np.max(abs(np.linalg.norm(initial[3:], axis=1)-1)) > 1e-12:
            raise ValueError("preparation norm outside the locked unit domain")
        analytic_derivatives[name] = float(np.linalg.norm(complement_derivative(initial, 0, p["kappa"])))
        complement_initial = np.linalg.norm(initial_p.sum(axis=0) - np.eye(2)) < a["max_residual"]
        endpoint_max = 0.
        for variant in ("exact", "operator", "operator-fine"):
            data = exact if variant == "exact" else load(raw / f"{name}-{variant}.npz")
            reference = fine_exact if variant == "operator-fine" else exact
            ns = p["refined_samples_per_gate"] if variant == "operator-fine" else p["samples_per_gate"]
            validate_trace(data,initial,(0,1),p["cycles"],ns,operator=variant!="exact")
            if not np.array_equal(data["times"],np.linspace(0,1,ns)):
                raise ValueError("changed within-event sample grid")
            if data["flow"].shape != ((2*p["cycles"], ns, 44) if variant != "exact" else exact["flow"].shape):
                raise ValueError("incomplete operator samples")
            if not np.array_equal(data["events"], np.tile((0, 1), p["cycles"])):
                raise ValueError("changed serial event word")
            for g, event in enumerate(data["events"]):
                first_h = None
                for ti, s in enumerate(data["times"]):
                    state = reference["flow"][g, ti]
                    rw, rp = lift(state)
                    if variant == "exact": wave, memories = rw, rp
                    else:
                        flat = data["flow"][g, ti]
                        wave, memories = flat[:36].reshape(6,6), flat[36:].reshape(2,2,2)
                    n, j, h, r, c, o, algebra = measures(wave, memories, int(event), p["kappa"])
                    if first_h is None: first_h = h
                    residual = max(abs(n-n0), np.linalg.norm(j-j0)/max(1.,np.linalg.norm(j0)),
                                   abs(h-first_h), algebra)
                    reference_records = measures(rw, rp, int(event), p["kappa"])[3]
                    mismatch = max(np.linalg.norm(wave-rw)/max(1.,np.linalg.norm(rw)),
                                   np.linalg.norm(memories-rp), max(abs(r-reference_records)))
                    max_conservation = max(max_conservation, residual)
                    max_equivalence = max(max_equivalence, mismatch)
                    row = {"preparation": name, "variant": variant, "gate": g, "event": int(event),
                        "s": float(s), "total_s": g+s, "complement_defect": c, "overlap": o,
                        "N": n, "r_i": r[0], "r_j": r[1], "q": r[2], "H_event": h,
                        "ledger_residual": residual, "lift_mismatch": mismatch,
                        "J00_real": j[0,0].real, "J11_real": j[1,1].real,
                        "J01_real": j[0,1].real, "J01_imag": j[0,1].imag}
                    for port in range(3): row[f"intensity_{port}"] = np.trace(wave[2*port:2*port+2,2*port:2*port+2]).real
                    for m in range(2):
                        for axis, sigma in zip("xyz", SIGMA): row[f"memory_{m}_{axis}"] = np.trace(memories[m] @ sigma).real
                    if variant == "exact": trajectories.append(row)
                    if variant != "exact": audits.append({k: row[k] for k in
                        ("preparation", "variant", "gate", "s", "ledger_residual", "lift_mismatch")})
                if variant != "exact": endpoint_max = max(endpoint_max, c)
        endpoint_cases.append({"preparation": name, "initially_complementary": bool(complement_initial),
            "max_endpoint_defect": endpoint_max, "initial_constraint_derivative": analytic_derivatives[name]})
        op = load(raw / f"{name}-operator.npz")["flow"]
        op_fine = load(raw / f"{name}-operator-fine.npz")["flow"][:,::2]
        refinement = float(np.max(np.linalg.norm(op-op_fine,axis=-1)))
        max_operator_refinement = max(max_operator_refinement,refinement)
        max_equivalence = max(max_equivalence,refinement)
        for label in ("frozen", "isolated-A", "isolated-B", "reverse", "rotated", "common-phase"):
            data = load(raw / f"{name}-{label}.npz")
            expected_initial=initial.copy()
            if label=="rotated": expected_initial=expected_initial@ROTATION.T
            elif label=="common-phase": expected_initial[:3]*=COMMON_PHASE
            order=(0,) if label=="isolated-A" else (1,) if label=="isolated-B" else (1,0) if label=="reverse" else (0,1)
            validate_trace(data,expected_initial,order,p["cycles"],p["samples_per_gate"])
            flow = data["flow"]
            if flow.shape != ((p["cycles"] if label.startswith("isolated") else 2*p["cycles"]), p["samples_per_gate"],5,2):
                raise ValueError("incomplete control trajectory")
            final = data["final"].copy()
            if label == "rotated": final = final @ ROTATION.conj()
            if label == "common-phase": final[:3] /= COMMON_PHASE
            difference = np.linalg.norm(physical_features(final)-physical_features(exact["final"]))
            control_j0 = sum(outer(data["initial"]))
            charge_defect = max(np.linalg.norm(sum(outer(x))-control_j0) for x in flow.reshape(-1,5,2)) / max(1.,np.linalg.norm(control_j0))
            defect = max(np.linalg.norm(outer(x[3:]).sum(axis=0)-np.eye(2)) for x in flow.reshape(-1,5,2))
            controls.append({"preparation": name, "control": label, "final_physical_difference": difference,
                             "charge_defect": charge_defect, "max_complement_defect": defect})
            if label in ("rotated", "common-phase"):
                restored = flow.copy()
                if label == "rotated": restored = restored @ ROTATION.conj()
                else: restored[...,:3,:] /= COMMON_PHASE
                difference = max(np.linalg.norm(physical_features(x)-physical_features(y))
                    for x,y in zip(restored.reshape(-1,5,2),exact["flow"].reshape(-1,5,2)))
                max_description = max(max_description, difference)
            if name == "initially-commuting" and label.startswith("isolated"): max_null = max(max_null, defect)
        if name == "dark":
            max_null = max(max_null, max(np.linalg.norm(physical_features(x)-physical_features(initial))
                for x in exact["flow"].reshape(-1,5,2)))
        if name in p["sensitivity_preparations"]:
            data = load(raw / f"{name}-sensitivity.npz")
            ng = 2*p["sensitivity_cycles"]
            required_shapes = {"base":(ng,5,2), "directions":(16,5,2), "tangent":(ng,28,16),
                "record_derivatives":(ng,3,16), "finite_differences":(2,ng,28,16),
                "record_errors":(ng,16,2,3), "initial_errors":(16,2),
                "finite_states":(2,16,2,ng,5,2),"finite_initials":(2,16,2,5,2),
                "perturbed_states":(16,2,ng,5,2),"perturbed_initials":(16,2,5,2)}
            if set(data)!=set(required_shapes) or any(data[k].shape != shape for k,shape in required_shapes.items()):
                raise ValueError("missing physical tangent or perturbation sector")
            if not np.array_equal(data["directions"],tangent_basis(initial)) or np.max(abs(data["base"]-exact["flow"][:ng,-1]))>1e-12:
                raise ValueError("changed physical directions or sensitivity base history")
            if (data["initial_errors"].max()>p["initial_error"]*(1+1e-9)
                or data["initial_errors"].min()<p["initial_error"]*(1-1e-8)):
                raise ValueError("perturbation violates the preparation allowance or coverage")
            for direction_index,direction in enumerate(data["directions"]):
                for sign_index,sign in enumerate((-1,1)):
                    expected_initial=retract(initial,sign*p["initial_error"]*direction)
                    if not np.array_equal(data["perturbed_initials"][direction_index,sign_index],expected_initial):
                        raise ValueError("changed signed perturbation preparation")
                    error=np.linalg.norm(expected_initial-initial)
                    if abs(error-data["initial_errors"][direction_index,sign_index])>1e-14:
                        raise ValueError("initial error record does not match actual preparation")
                    for g,changed in enumerate(data["perturbed_states"][direction_index,sign_index]):
                        measured=measures(*lift(changed),g%2,p["kappa"])[3]-measures(*lift(data["base"][g]),g%2,p["kappa"])[3]
                        if np.max(abs(measured-data["record_errors"][g,direction_index,sign_index]))>1e-12:
                            raise ValueError("record error differs from saved perturbed endpoints")
                for h_index,epsilon in enumerate(p["jacobian_steps"]):
                    for sign_index,sign in enumerate((-1,1)):
                        if not np.array_equal(data["finite_initials"][h_index,direction_index,sign_index],retract(initial,sign*epsilon*direction)):
                            raise ValueError("changed centered-difference preparation")
                    for g in range(ng):
                        pair=data["finite_states"][h_index,direction_index,:,g]
                        measured=(physical_features(pair[1])-physical_features(pair[0]))/(2*epsilon)
                        if np.max(abs(measured-data["finite_differences"][h_index,g,:,direction_index]))>1e-12:
                            raise ValueError("finite difference differs from saved endpoints")
            for g, matrix in enumerate(data["tangent"]):
                norm = max(1.,np.linalg.norm(matrix))
                errors = [np.linalg.norm(fd[g]-matrix)/norm for fd in data["finite_differences"]]
                halving = np.linalg.norm(data["finite_differences"][0,g]-data["finite_differences"][1,g])/norm
                max_tangent = max(max_tangent, *errors, halving)
                dr = data["record_derivatives"][g]
                sensitivities.append({"preparation":name, "gate":g, "cycle":(g+1)/2,
                    "singular_amplification":np.linalg.svd(matrix,compute_uv=False)[0],
                    "tangent_error_h":errors[0], "tangent_error_half_h":errors[1], "tangent_step_difference":halving,
                    "wave_record_sensitivity":np.max(np.linalg.norm(dr[:,:12],axis=1)),
                    "memory_A_record_sensitivity":np.max(np.linalg.norm(dr[:,12:14],axis=1)),
                    "memory_B_record_sensitivity":np.max(np.linalg.norm(dr[:,14:],axis=1)),
                    "observed_record_error":abs(data["record_errors"][g]).max()})
    budgets = conditional_budget(p,a)
    limit = a["max_residual"]
    active_derivative = analytic_derivatives["active-plus"]
    complementary_endpoints = max(x["max_endpoint_defect"] for x in endpoint_cases if x["initially_complementary"])
    target = output / "derived"; target.mkdir(parents=True,exist_ok=True)
    for name, rows in (("trajectories",trajectories),("audit",audits),("controls",controls),
                       ("sensitivity",sensitivities),("budget",budgets)):
        write_rows(target / f"{name}.csv",rows)
    write_json(target/"incidence.json",{"events":[list(e) for e in EVENTS],
        "positions":{"z1":[0,1],"z2":[1,1],"z3":[2,1],"A":[.5,0],"B":[1.5,0]},
        "edges":[["z1","A"],["z2","A"],["z2","B"],["z3","B"]],
        "layout_meaning":"supplied incidence; no physical embedding"})
    numerical_ok = max(max_equivalence,max_conservation,max_null,max_description)<=limit
    endpoint_status = "fail" if numerical_ok and complementary_endpoints>5*max(limit,max_equivalence) else "unresolved"
    values = {"coverage":("pass",len(expected)), "coherent-equivalence":("pass" if max_equivalence<=limit else "fail",max_equivalence),
        "conservation":("pass" if max_conservation<=limit else "fail",max_conservation),
        "null-commuting":("pass" if max_null<=limit else "fail",max_null),
        "description-controls":("pass" if max_description<=limit else "fail",max_description),
        "tangent-refinement":("pass" if max_tangent<=a["max_tangent_difference"] else "fail",max_tangent),
        "continuous-complement":("fail" if active_derivative>0 else "unresolved",active_derivative),
        "endpoint-complement":(endpoint_status,complementary_endpoints),
        "prediction-certification":("unresolved",0)}
    summary = {"cycles":p["cycles"], "cases":7, "physical_tangent_dimensions":16,
        "max_equivalence":max_equivalence,"max_conservation":max_conservation,"max_tangent_difference":max_tangent,
        "max_null":max_null,"max_description":max_description,"max_operator_tolerance_difference":max_operator_refinement,
        "numerical_gates_pass":bool(numerical_ok),"coverage":{"expected_files":sorted(expected),
            "samples_per_gate":p["samples_per_gate"],"refined_samples_per_gate":p["refined_samples_per_gate"],
            "preparation_schedule_and_continuity_verified":True},
        "endpoint_cases":endpoint_cases,"analytical_constraint_derivatives":analytic_derivatives,
        "conditional_preparation_horizon_cycles":max(x["cycle"] for x in budgets if x["ideal_preparation_budget_met"]),
        "certified_horizon_cycles":0,"certification_status":"unresolved",
        "certification_obstruction":"Conservative global amplification already loses a full-cycle preparation budget; validated floating residual/roundoff and readout enclosures are absent.",
        "scope":"F0/F2/C1 seed; not the four-ray classification, autonomous clock or any Test 1-11 acceptance."}
    checks={"schema_version":"research-checks-v1","checks":[{"id":k,"status":s,"value":float(v),
        "evidence":"derived/summary.json"} for k,(s,v) in values.items()]}
    summary["criterion_evidence"]={k:{"status":s,"value":float(v)} for k,(s,v) in values.items()}
    write_json(target/"summary.json",summary)
    write_json(output / "checks.json",checks)
    return {"raw_source":executions[-1].relative_to(run_path).as_posix(),"checks":checks,"summary":summary}
