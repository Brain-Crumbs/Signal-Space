# 5. Frame covariance, filtering, and identifiability {#sec-covariance}

## 5.1. A conditional comparison ansatz

Suppose descriptions at two local frames are related by one invertible complex amplitude map $A$ for a specified family of signals. A bilinear intensity then transforms as $X'=AXA^\dagger$. If the same protocol scalar $\det X$ is invariant, $|\det A|=1$; removing an irrelevant overall phase permits a representative in $SL(2,\mathbb C)$.

This is a sufficient construction of the desired action. It is not derived from analyzer counts alone. One must establish that the *same* $A$ compares a spanning collection of preparations, including coherent ones, while detector effects, exposures, and source descriptions transform consistently. Fitting a different $A$ to each source is not a covariance test.

Algebraically, a paired effect transforms dually as $E'=A^{-\dagger}EA^{-1}$, giving $\operatorname{Tr}(E'X')=\operatorname{Tr}(EX)$. However, the transformed effects sum to $A^{-\dagger}A^{-1}$ rather than $I$ when an original POVM sums to $I$. A nonunitary coordinate change therefore also requires a transformed normalization or exposure convention; it cannot be interpreted as an ordinary trace-normalized POVM change with every other laboratory definition held fixed. The operational model must specify which quantities are densities, which measure they use, and which outcomes are compared.

## 5.2. A physical filter has outcomes

A laboratory filter can implement the successful branch

$$
F=kA,\qquad F^\dagger F\leq I,
\qquad
p_{\rm s}=k^2\operatorname{Tr}(A\rho_S A^\dagger).
\tag{F1}
$$

Here $0<k\leq\|A\|_{\rm op}^{-1}$. A complementary operator $G=(I-F^\dagger F)^{1/2}$ completes a valid two-outcome instrument. Conditioned on success,

$$
\rho_{S\mid{\rm s}}
=\frac{A\rho_S A^\dagger}{\operatorname{Tr}(A\rho_S A^\dagger)}.
\tag{F2}
$$

The Lorentz/filtering relation is standard [4]. The successful branch has a selection probability, and discarded failures cannot be treated as absent trials in an unconditioned physical claim.

**Proposition F1 (deterministic-channel restriction).** A map $\rho\mapsto A\rho A^\dagger$ is trace preserving on all normalized states if and only if $A^\dagger A=I$. With $\det A=1$, such maps give the unitary rotation subgroup. A genuine boost followed by normalization is generally nonlinear in mixtures and hence is not a deterministic quantum channel on the qubit alone.

*Proof.* Trace preservation for every density operator means $\operatorname{Tr}[(A^\dagger A-I)\rho]=0$ for every $\rho$, forcing $A^\dagger A=I$. For the nonlinear assertion take $A=\exp(\xi\sigma_3/2)$, $\xi\ne0$. The two eigenstate projectors are individually unchanged by (F2), but their equal mixture $I/2$ maps to $(I+\tanh\xi\,\sigma_3)/2$. This differs from the equal mixture of their individual outputs. $\square$

A passive Lorentz comparison of suitably defined physical quantities remains possible. Proposition F1 only rules out identifying that comparison with a deterministic local qubit filter under unchanged normalization.

## 5.3. Three practical degeneracies

Source anisotropy can produce $h\ne0$ with no relative motion. Detector efficiency imbalance multiplies the two diagonal means differently and can imitate a shift of $h$. Temporal distinguishability or recording can reduce off-diagonal coherence and change $\gamma$ through (S5). These degeneracies can coexist.

Accordingly, a physical covariance test requires independently characterized sources and detectors, an intensity normalization, coherent probes spanning the selected operator space, and a separate motion protocol. The diagonal stationary test is necessary for the proposed hazard interpretation but is far from sufficient for full cone covariance. In particular, a successful reconstruction of $X$ does not make $X$ a complete causal state in the sense of Part I: two joint signal-memory states can have equal $X$ and different future echoes.
