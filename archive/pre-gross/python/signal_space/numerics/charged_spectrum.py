"""Coupled exp(sigma*t) spectrum projected to first-order delta Q=0.

w=r U, z=r V makes dr the physical r²dr measure. Dirichlet at 0,R
selects the regular Friedrichs extension, with centrifugal ell(ell+1)/r².
"""

import numpy as np
from scipy.linalg import eig, null_space, solve_banded
from signal_space.numerics.charged_radial import interpolate


def generator(f, omega, radius, ell):
    n = len(f)
    dr = radius / (n + 1)
    r = np.arange(1, n + 1) * dr
    lap = (
        np.diag(np.full(n, 2 / dr**2))
        + np.diag(np.full(n - 1, -1 / dr**2), 1)
        + np.diag(np.full(n - 1, -1 / dr**2), -1)
    )
    v = 1 - omega**2 + ell * (ell + 1) / r**2
    plus = lap + np.diag(v - 6 * f * f + 15 * f**4)
    minus = lap + np.diag(v - 2 * f * f + 3 * f**4)
    zero, eye = np.zeros((n, n)), np.eye(n)
    a = np.block(
        [
            [zero, zero, eye, zero],
            [zero, zero, zero, eye],
            [-plus, zero, zero, -2 * omega * eye],
            [zero, -minus, 2 * omega * eye, zero],
        ]
    )
    return a, plus, minus, r


def spectrum(profile, nodes, ell_max):
    radius, omega = profile["radius"], profile["omega"]
    r = np.arange(1, nodes + 1) * radius / (nodes + 1)
    f, fp = interpolate(profile, r)
    # Re-solve the SAME stationary action on the spectral Dirichlet regulator.
    # This preserves its exact discrete U(1) zero mode and charge invariant;
    # projecting an inconsistent continuum background could hide leakage.
    original = f.copy()
    dr = radius / (nodes + 1)
    w = r * f
    converged = False
    for iteration in range(40):
        padded = np.pad(w, (1, 1))
        residual = (
            (2 * w - padded[:-2] - padded[2:]) / dr**2
            + (1 - omega**2) * w
            - 2 * w**3 / r**2
            + 3 * w**5 / r**4
        )
        if np.max(abs(residual)) < 1e-11:
            converged = True
            break
        bands = np.zeros((3, nodes))
        bands[0, 1:] = -1 / dr**2
        bands[2, :-1] = -1 / dr**2
        bands[1] = 2 / dr**2 + 1 - omega**2 - 6 * w * w / r**2 + 15 * w**4 / r**4
        delta = solve_banded((1, 1), bands, -residual)
        rate = 1.0
        for trial in range(15):
            candidate = w + rate * delta
            pad = np.pad(candidate, (1, 1))
            rr = (
                (2 * candidate - pad[:-2] - pad[2:]) / dr**2
                + (1 - omega**2) * candidate
                - 2 * candidate**3 / r**2
                + 3 * candidate**5 / r**4
            )
            if np.linalg.norm(rr) < np.linalg.norm(residual):
                break
            rate *= 0.5
        w = candidate
    f = w / r
    background_error = float(
        np.max(abs(f - original)) / max(np.max(abs(original)), 1e-30)
    )
    if not converged or np.min(f) < 0 or np.max(f) < 1e-5 or background_error > 0.25:
        raise ValueError("spectral stationary regulator failed or changed branch")
    rows = []
    for ell in range(ell_max + 1):
        a, plus, minus, r = generator(f, omega, radius, ell)
        c = np.concatenate([4 * omega * r * f, np.zeros(2 * nodes), -2 * r * f])
        basis = null_space(c[None, :]) if ell == 0 else np.eye(4 * nodes)
        reduced = basis.T @ a @ basis
        values, small_vectors = eig(reduced)
        vectors = basis @ small_vectors
        norm_a = np.linalg.norm(a, ord=np.inf)
        residuals = np.linalg.norm(a @ vectors - vectors * values, axis=0) / (
            norm_a + np.abs(values)
        )
        defects = (
            np.abs(c @ vectors) / max(np.linalg.norm(c), 1e-30)
            if ell == 0
            else np.zeros(len(values))
        )
        target = (
            np.concatenate([np.zeros(nodes), r * f, np.zeros(2 * nodes)])
            if ell == 0
            else np.concatenate([r * fp, np.zeros(3 * nodes)])
        )
        symmetry_residual = (
            float(
                np.linalg.norm(a @ target)
                / (max(np.linalg.norm(target), 1e-30) * norm_a)
            )
            if ell in (0, 1)
            else None
        )
        overlaps = (
            np.abs(target @ vectors) / max(np.linalg.norm(target), 1e-30)
            if ell in (0, 1)
            else None
        )
        symmetry_index = int(np.argmax(overlaps)) if overlaps is not None else None
        rows.append(
            {
                "ell": ell,
                "nodes": nodes,
                "radius": radius,
                "convention": "exp(sigma*t)",
                "sigma_real": values.real.tolist(),
                "sigma_imag": values.imag.tolist(),
                "residuals": residuals.tolist(),
                "charge_defects": defects.tolist(),
                "max_growth": float(np.max(values.real)),
                "max_residual": float(np.max(residuals)),
                "max_charge_defect": float(np.max(defects)),
                "constraint_leakage": (
                    float(
                        np.linalg.norm(c @ a) / (max(np.linalg.norm(c), 1e-30) * norm_a)
                    )
                    if ell == 0
                    else 0.0
                ),
                "symmetry_name": (
                    "phase" if ell == 0 else "translation" if ell == 1 else None
                ),
                "symmetry_residual": symmetry_residual,
                "symmetry_mode_index": symmetry_index,
                "symmetry_overlap": (
                    float(overlaps[symmetry_index]) if overlaps is not None else None
                ),
                "symmetry_splitting": (
                    float(abs(values[symmetry_index]))
                    if symmetry_index is not None
                    else None
                ),
                "r": r.tolist(),
                "eigenvectors_real": vectors.real.T.tolist(),
                "eigenvectors_imag": vectors.imag.T.tolist(),
            }
        )
    # Globally valid pointwise stiffness bound; gyroscopic terms do no work.
    # Bound every Hermite interval, not only grid nodes. Hermite basis has
    # nonnegative endpoint weights summing to one and |h10|,|h11|<=4/27.
    x = np.asarray(profile["r"])
    y = np.asarray(profile["f"])
    dy = np.asarray(profile["fp"])
    amplitude = np.maximum(abs(y[:-1]), abs(y[1:])) + 4 / 27 * np.diff(x) * (
        abs(dy[:-1]) + abs(dy[1:])
    )
    splus = np.minimum(amplitude**2, 0.2)
    sminus = np.minimum(amplitude**2, 1 / 3)
    centrifugal = (ell_max + 1) * (ell_max + 2) / x[1:] ** 2
    interior = min(
        np.min(1 - omega**2 - 6 * splus + 15 * splus**2 + centrifugal),
        np.min(1 - omega**2 - 2 * sminus + 3 * sminus**2 + centrifugal),
    )
    # Linear exterior is monotone; drop centrifugal term there.
    exterior = 1 - omega**2 - 6 * y[-1] ** 2
    bound = float(min(interior, exterior))
    return {
        "background_relative_error": background_error,
        "background_r": r.tolist(),
        "background_f": f.tolist(),
        "background_residual": float(np.max(abs(residual))),
        "sectors": rows,
        "higher_sector_lower_bound": float(bound),
        "higher_sectors_bounded": bool(bound > 0),
        "boundary": "Dirichlet transformed fields; independent volume refinement required",
    }
