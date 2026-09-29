# 10. Conditions for a common operational metric {#sec-geometry}

## 10.1. An intensity cone is not an interval field

The coordinate $x^a$ of $X$ has an operational intensity meaning from Section 3. A tangent displacement has different units and a different transformation obligation. Even a reliable four-current would not determine the metric: one timelike vector field supplies neither a complete coframe nor all null directions.

Suppose a future model produces a smooth four-dimensional region $M$ and a real-linear isomorphism at each point,

$$
\Theta_p:T_pM\longrightarrow\operatorname{Herm}(2),\qquad
\Theta(v)=e^0(v)I+\sum_{i=1}^3e^i(v)\sigma_i,
\tag{G1}
$$

with four linearly independent one-forms $e^a=e^a{}_{\mu}dx^\mu$. Their values have units of length after calibration. Equation (G1) is a coframe, not the intensity operator $X$. An operational model must derive how signal and clock comparisons identify this map, rather than copy intensity coordinates into it by notation.

**Proposition G1 (conditional metric construction).** Assume (G1), a specified time orientation, and the identification of future causal tangent directions with the positive semidefinite cone of $\Theta$. Then

$$
g(v,v)=-\det\Theta(v),\qquad
 g_{\mu\nu}=\eta_{ab}e^a{}_{\mu}e^b{}_{\nu},
\quad \eta=\operatorname{diag}(-1,1,1,1)
\tag{G2}
$$

defines a Lorentzian metric. Local changes $\Theta\mapsto A\Theta A^\dagger$ with $A\in SL(2,\mathbb C)$ preserve it. A positive rescaling $\Theta\mapsto\Omega\Theta$ gives $g\mapsto\Omega^2g$ and preserves its null cone.

*Proof.* Equation (L1) and the invertible coframe give a nondegenerate quadratic form of signature $(-,+,+,+)$. Its polarization defines the bilinear metric. Determinant preservation proves the frame statement, and the determinant's degree two gives conformal scaling. $\square$

The proposition is a construction conditional on a coframe and its physical interpretation. It does not infer a tangent bundle from a causal circuit. Manifold approximation is a separate nontrivial issue in causal approaches to geometry [8].

## 10.2. What calibration must fix

In a tangent space of dimension at least three, two Lorentzian quadratic forms with the same null cone are proportional. An elementary argument in four dimensions makes the limitation explicit. Choose coordinates in which one form is $-(v^0)^2+|\mathbf v|^2$. The other must vanish on every $(1,\mathbf n)$ with $|\mathbf n|=1$. Comparing $\mathbf n$ and $-\mathbf n$ eliminates all mixed time-space terms. Constancy of the remaining spatial quadratic form on the unit sphere makes it a scalar multiple of the identity, with the time coefficient fixed by the null condition. Matching signature and time convention makes the proportionality positive.

Consequently, ideal null directions determine a conformal class, not its scale. At each point, one independently calibrated nonzero timelike reading fixes the remaining positive factor *if* all clock species couple to the same quadratic form. In a supplied coordinate parameter $\lambda$,

$$
\frac{d\tau}{d\lambda}
=\frac{1}{c_0}\sqrt{-g_{\mu\nu}
\frac{dx^\mu}{d\lambda}\frac{dx^\nu}{d\lambda}}.
\tag{G3}
$$

For an actual finite clock $A$, a more appropriate hypothesis is

$$
\frac{d\tau_A}{d\lambda}
=\frac{d\tau}{d\lambda}\,[1+\delta_A],
\tag{G4}
$$

where $\delta_A$ is independently predicted from size, state, acceleration, and environmental response. The cavity control gives $\delta_A=f(\epsilon)-1$ in its stated regime. The count control fails the corresponding mean-curve comparison by (C6), without representing an individual bound clock.

A geometry cannot be validated by defining a separate conformal factor from each device on each trajectory. Calibrate device parameters on separate histories, then test whether the corrected comparisons share one $g$. A residual species-dependent leading rate that cannot be removed by established device physics would obstruct the universal metric hypothesis. A demonstrated finite-size correction that vanishes in a controlled regime has a different status.

A physical volume measure could also constrain scale, but raw reception counts are source- and detector-dependent. Identifying counts with spacetime volume would require an additional universal sampling law. Neither finite records nor intensity tomography supplies one.

## 10.3. The operational reconstruction target

A successful next model must produce a manifold-like regime, enough independent probes to resolve the local cone, controlled finite delays and response latencies, and recurrent subsystems that supply compatible scale calibration. It must also explain why different physical modes have a common characteristic cone. One optical mode on a prescribed background does not establish that universality.

Reconstruction should be assessed on held-out records. A fit uses one shared coframe and declared nuisance parameters for source and apparatus. It then predicts new clock comparisons and exchange histories, including non-collinear preparations and changing motion. Residual coordinate and local Lorentz freedoms are representation choices; unsupported freedom to retune a clock law is not.

Nothing in (G1)-(G4) selects a Levi-Civita connection, gravitational field equations, or the number of physical gravitational polarizations. Torsion, nonmetricity, and physical transport require their own derivation. The pure-frame identity (L8) remains a control against mistaking local basis changes for curvature.
