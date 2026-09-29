"""Singular-origin collocation, with independent saved-profile checks."""

import numpy as np
from scipy.integrate import solve_bvp, simpson
from scipy.interpolate import CubicHermiteSpline
from signal_space.models.charged_scalar import force, potential, tail


def interpolate(profile, r):
    x = np.asarray(profile["r"])
    curve = CubicHermiteSpline(x, profile["f"], profile["fp"])
    values = curve(np.minimum(r, x[-1]))
    derivatives = curve(np.minimum(r, x[-1]), 1)
    outside = r > x[-1]
    if np.any(outside):
        k = np.sqrt(1 - profile["omega"] ** 2)
        values[outside] = (
            profile["f"][-1] * x[-1] / r[outside] * np.exp(-k * (r[outside] - x[-1]))
        )
        derivatives[outside] = -(k + 1 / r[outside]) * values[outside]
    return np.array([values, derivatives])


def solve_profile(
    omega,
    radius,
    nodes,
    tolerance,
    max_nodes,
    sample_points,
    seed=None,
    seed_radius=4.0,
):
    r = np.linspace(0, radius, nodes)
    if seed is None:
        f = 0.8 / np.cosh(np.minimum(r / seed_radius, 300))
        guess = np.array([f, -f * np.tanh(r / seed_radius) / seed_radius])
    else:
        guess = interpolate(seed, r)
    k = np.sqrt(1 - omega**2)
    result = solve_bvp(
        lambda x, y: np.array([y[1], force(y[0], omega)]),
        lambda a, b: np.array([a[1], b[1] + (k + 1 / radius) * b[0]]),
        r,
        guess,
        S=np.array([[0.0, 0.0], [0.0, -2.0]]),
        tol=tolerance,
        bc_tol=tolerance / 10,
        max_nodes=max_nodes,
    )
    grid = np.linspace(0, radius, sample_points)
    f, fp = result.sol(grid)
    status = "accepted"
    if not result.success:
        status = "failed"
    elif np.max(np.abs(f)) < 1e-5:
        status = "rejected-vacuum"
    elif f[0] <= 0 or np.min(f) < -1e-10:
        status = "rejected-noded"
    if not np.all(np.isfinite(f)) or not np.all(np.isfinite(fp)):
        raise ValueError("non-finite profile")
    return {
        "omega": float(omega),
        "radius": float(radius),
        "r": grid.tolist(),
        "f": f.tolist(),
        "fp": fp.tolist(),
        "status": status,
        "solver_message": result.message,
        "solver_nodes": len(result.x),
        "solver_iterations": result.niter,
        "solver_residual": float(np.max(result.rms_residuals)),
        "collocation": {"x": result.x.tolist(), "coefficients": result.sol.c.tolist()},
    }


def observables(profile, coupling=0.01):
    r, f, fp = (np.asarray(profile[key]) for key in ("r", "f", "fp"))
    omega, radius = profile["omega"], profile["radius"]
    exterior = tail(radius, f[-1], omega, coupling)
    h = r[1] - r[0]
    d1 = (f[:-4] - 8 * f[1:-3] + 8 * f[3:-1] - f[4:]) / (12 * h)
    d2 = (-f[4:] + 16 * f[3:-1] - 30 * f[2:-2] + 16 * f[1:-3] - f[:-4]) / (12 * h * h)
    rhs = force(f[2:-2], omega)
    residual = float(
        np.max(np.abs(d2 + 2 * d1 / r[2:-2] - rhs)) / (1 + np.max(np.abs(rhs)))
    )
    origin_lap = (-f[2] + 16 * f[1] - 15 * f[0]) / (2 * h * h)
    residual = max(
        residual,
        float(abs(origin_lap - force(f[0], omega)) / (1 + abs(force(f[0], omega)))),
    )

    def integrate(rule):
        i = rule(r * r * f * f, x=r) + exterior["i"]
        t = rule(r * r * fp * fp, x=r) + exterior["t"]
        v = rule(r * r * potential(f), x=r) + exterior["i"]
        rq = np.sqrt((rule(r**4 * f * f, x=r) + exterior["r4"]) / i) if i > 0 else 0.0
        factor = 4 * np.pi / coupling
        return {
            "E": float(factor * (t + v + omega**2 * i)),
            "Q": float(factor * 2 * omega * i),
            "radius": float(rq),
            "T": float(factor * t),
            "V": float(factor * v),
            "W": float(factor * omega**2 * i),
        }

    data = integrate(simpson)
    alternate = integrate(np.trapezoid)
    scale = abs(data["T"]) + 3 * abs(data["V"]) + 3 * abs(data["W"])
    k = np.sqrt(1 - omega**2)
    nonlinear_bound = float(
        4
        * np.pi
        / coupling
        * radius**2
        * (abs(f[-1]) ** 4 / (4 * k) + abs(f[-1]) ** 6 / (6 * k))
    )
    tail_start = max(2, int(len(r) * 0.9))
    expected = f[-1] * radius / r[tail_start:] * np.exp(k * (radius - r[tail_start:]))
    tail_fit = float(
        np.max(np.abs(f[tail_start:] - expected)) / max(float(np.max(np.abs(f))), 1e-30)
    )
    data.update(
        {
            "abs_Q": abs(data["Q"]),
            "central_amplitude": float(f[0]),
            "field_residual": residual,
            "virial_defect": abs(data["T"] + 3 * data["V"] - 3 * data["W"])
            / max(scale, 1e-30),
            "energy_identity_defect": abs(
                data["E"] - omega * data["Q"] - 2 * data["T"] / 3
            )
            / max(abs(data["E"]), 1e-30),
            "quadrature_error": {
                key: abs(data[key] - alternate[key]) for key in ("E", "Q", "radius")
            },
            "tail": exterior,
            "tail_nonlinear_bound": nonlinear_bound,
            "tail_fit": tail_fit,
            "tail_fraction": abs(exterior["E"]) / max(abs(data["E"]), 1e-30),
        }
    )
    return data
