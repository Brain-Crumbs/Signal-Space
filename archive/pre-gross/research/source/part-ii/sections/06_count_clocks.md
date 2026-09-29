# 6. Statistical rapidity and the count-clock obstruction {#sec-count-clocks}

## 6.1. Exact diagonal specialization

For the classical control from [1,3], a constituent moves at reference velocity $c_0\sigma$, with outgoing hazards $q_+=\gamma e^{-h}$ and $q_-=\gamma e^h$. Writing $b(t)=\mathbb E\sigma(t)$, the master equation gives

$$
\dot b=2\gamma\cosh h\,(\tanh h-b).
\tag{C1}
$$

At fixed positive hazards, stationarity yields

$$
b_* =\tanh h,\qquad
\nu_* =\frac{2q_+q_-}{q_++q_-}
=\gamma\operatorname{sech}h.
\tag{C2}
$$

Here $\nu_*$ counts every reversal; a two-reversal directional recurrence has half this frequency. The stationary occupation matrix is $\operatorname{diag}(q_-,q_+)/(q_-+q_+)$, which explains the ordering in (S6). This relationship depends on the response law, rather than on positivity alone.

The long-run count reading $N/\gamma$ has mean rate $\operatorname{sech}h$. On the supplied reference geometry this equals the proper-time rate of the straight *mean-drift* history. Each locally finite piecewise-null constituent path has zero proper-time length. Its count reading and its mean trajectory therefore refer to different objects. A bound timelike material clock has not been constructed by averaging.

The passive frame transformation provides a useful consistency check. On a null segment, $dt'=e^{-\sigma\xi}dt$. Invariance of the infinitesimal reversal probability $q_\sigma dt$ gives

$$
q'_+=e^\xi q_+,\qquad q'_-=e^{-\xi}q_-,
\qquad \gamma'=\gamma,\quad h'=h-\xi.
\tag{C3}
$$

This is a transformation of the same path process with hazards per transformed coordinate time. It is not the transformation of an arbitrary incoming detector rate. In a nonstationary ensemble, equal-time slices and averaging must also be transformed; transforming an ensemble-mean curve and recomputing a mean on new simultaneity slices need not commute.

## 6.2. Nonstationary discrepancy

Let $\gamma(t)>0$ and $h(t)$ be deterministic bounded functions on a finite test interval. Define

$$
\widehat\tau(T)=\int_0^T\frac{dN(t)}{\gamma(t)},\qquad
\bar\tau(T)=\int_0^T\sqrt{1-b(t)^2}\,dt,
\tag{C4}
$$

where $|b|<1$. The first is a random normalized count; the second is proper time along the reference mean curve. The expected count intensity gives

$$
\frac{d}{dt}\mathbb E\widehat\tau
=\frac{q_+(1+b)+q_-(1-b)}{2\gamma}
=\cosh h-b\sinh h.
\tag{C5}
$$

\Needspace{7\baselineskip}

**Proposition C1 (inherited exact discrepancy).** With $\eta_b=\operatorname{artanh}b$,

$$
\frac{d}{dt}\mathbb E\widehat\tau-\dot{\bar\tau}
=\sqrt{1-b^2}\,[\cosh(h-\eta_b)-1]\geq0.
\tag{C6}
$$

*Proof.* Substitute $b=\tanh\eta_b$ into (C5) and use the hyperbolic subtraction identity. Equality holds precisely when $h=\eta_b$. $\square$

This is the result of earlier Paper III [3], carried through Part I without weakening its qualification. The excess is a relaxation effect relative to a specified ensemble-mean curve. It is neither a laboratory disagreement with relativity nor evidence for a universal correction to proper time.

For a small statistical lag $\delta=h-\eta_b$,

$$
\frac{d}{dt}\mathbb E\widehat\tau-\dot{\bar\tau}
=\tfrac12\sqrt{1-b^2}\,\delta^2+O(\delta^4).
\tag{C7}
$$

The earlier relaxation bound [3] controls $\delta$ under bounded driving and a relaxation rate bounded away from zero. Approximate stationary agreement is therefore a restricted adiabatic result. It does not remove count noise, response memory, or the distinction between mean curves and individual trajectories.

## 6.3. Why a local phase relabeling does not repair the clock

Consider the most general additive readout with fixed state residence rewards and fixed reversal rewards at a given bath setting:

$$
Y(T)=\int_0^T u_{\sigma(t)}\,dt
+\sum_{t_j\leq T}w_{\sigma(t_j^-)}.
\tag{C8}
$$

The coefficients may depend on the prescribed bath and on time, but not on the current ensemble distribution. The jump weight uses the pre-reversal state. This includes counting with unequal tick weights and accumulating a phase at fixed state-dependent rates.

**Proposition C2 (local additive-readout obstruction).** No such readout has expected instantaneous rate $\sqrt{1-b^2}$ for every $b$ in a nonempty open interval of $(-1,1)$ at a fixed bath setting.

*Proof.* Its expected rate is

$$
\frac{d}{dt}\mathbb EY
=\frac{1+b}{2}(u_++q_+w_+)
+\frac{1-b}{2}(u_-+q_-w_-)=A+Bb.
\tag{C9}
$$

This is affine in $b$. The target has strictly negative second derivative, $-(1-b^2)^{-3/2}$. The two functions cannot agree on an open interval. $\square$

The proposition does not exclude coherent composite clocks, additional dynamically relevant memory, nonlinear estimators, or a readout fitted to one preparation. It rules out a universal repair by assigning fixed local phase increments to the original two-state process. A controller that estimates $b$ and programs a phase speed proportional to $\sqrt{1-b^2}$ can enforce the target, but has supplied the desired geometry through feedback.

More generally, the expectation of a fixed observable is affine in the state. Proper time computed from an ensemble-mean velocity is a nonlinear ensemble functional. One should not require that functional to equal a universal one-copy expectation without explaining the physical meaning of the averaging. This helps identify why a bound recurrent subsystem is a cleaner successor than further renormalization of an unbound null transport ensemble.
