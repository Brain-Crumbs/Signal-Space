# 3. An operational positive signal operator {#sec-signal-operator}

## 3.1. Intensity from calibrated trials

Consider repeated trials of the selected channel sector with density operator $\rho_S$. Let $\mathcal J\geq0$ be the mean number of carriers in that sector per fixed exposure. Define

$$
X=\mathcal J\rho_S,\qquad
\mathbb E n_E=\operatorname{Tr}(EX)
\tag{S1}
$$

for a calibrated analyzer effect $0\leq E\leq I$, where $n_E$ is its count per exposure. For multiple carriers the second relation is an additive first-moment model: $X$ can equivalently be the sum of their one-carrier reduced operators. It does not require Poisson arrivals or independent carriers. Higher count correlations and temporal memory require additional data.

If a trial contains either vacuum or one carrier, $\mathcal J$ is its occupation probability and is bounded by one. Aggregated exposures allow unrestricted nonnegative intensity. Neither construction makes elapsed time fundamental: a fixed number of locally controlled trials can define exposure before seconds are assigned. To quote a rate per unit time, a separately calibrated time exposure is necessary.

**Proposition S1 (operational reconstruction).** Under S1-S2, the six calibrated projective analyzer means along the three Pauli axes determine a unique Hermitian operator $X$. They admit the quantum intensity model precisely when the reconstructed operator is positive semidefinite and the exposure normalizations agree.

*Proof.* Write $\sigma_0=I$ and let $\sigma_1,\sigma_2,\sigma_3$ be the Pauli matrices. Set

$$
X=x^0 I+\sum_{i=1}^3x^i\sigma_i,
\qquad
x^a=\tfrac12\operatorname{Tr}(\sigma_aX).
\tag{S2}
$$

For $E_{i,\pm}=(I\pm\sigma_i)/2$,

$$
\mu_{i,\pm}=\operatorname{Tr}(E_{i,\pm}X)=x^0\pm x^i.
\tag{S3}
$$

Thus $x^i=(\mu_{i,+}-\mu_{i,-})/2$, while every setting yields the same $x^0=(\mu_{i,+}+\mu_{i,-})/2$. These four real coordinates uniquely specify $X$. Its eigenvalues are $x^0\pm|\mathbf x|$, so positivity is equivalent to $x^0\geq|\mathbf x|$. Conversely, every such nonzero operator has the form (S1), with $\mathcal J=2x^0$ and a valid density operator. The zero operator represents no selected carriers. $\square$

This is finite qubit tomography with retained intensity, not a reconstruction of quantum theory. Pairwise nonnegative counts alone are insufficient: the combined contrasts must also obey $|\mathbf x|\leq x^0$. Finite noisy estimates can violate positivity. A constrained likelihood fit with a declared count law is then appropriate; a negative fitted eigenvalue should not be reinterpreted as a physical spacelike signal.

## 3.2. Coherence supplies the transverse coordinates

The diagonal basis gives

$$
X=\begin{pmatrix}
x^0+x^3&x^1-i x^2\\
x^1+i x^2&x^0-x^3
\end{pmatrix}.
\tag{S4}
$$

The real and imaginary coherences supply two additional coordinates beyond two diagonal intensities. They are read through incompatible analyzer settings on reproducibly prepared trials. They are not simultaneous preexisting classical outcome labels.

The reduced state from Part I's reception experiment has off-diagonal magnitude proportional to the memory overlap and temporal overlap. Complete unread recording removes that coherence. At fixed diagonal entries, dephasing $X_{01}\mapsto\zeta X_{01}$ with $|\zeta|\leq1$ gives

$$
\det X_{\rm after}-\det X_{\rm before}
=(1-|\zeta|^2)|X_{01}|^2\geq0.
\tag{S5}
$$

Thus ordinary record formation can change the determinant coordinate without moving the apparatus. This is an immediate control against identifying every change of $X$ with a geometric interval or velocity. Conversely, scalar attenuation $X\mapsto\lambda X$ changes its scale without changing its normalized state. Source power, decoherence, and motion must be separately identified by the observation law.

## 3.3. Intensity is not a response hazard

The quantity in (S1) describes incident carriers in selected trials. The hazard $q_+$ describes the probability per reference time of leaving the receiver's plus state. A physical response law can connect them, for example through a specified state-dependent interaction cross section and bath approximation. Positivity does not supply that law.

One may build an apparatus whose calibrated diagonal response data are represented by

$$
X_q=\operatorname{diag}(q_-,q_+).
\tag{S6}
$$

The reversed ordering follows the earlier Signal Space stationary occupations. Equation (S6) is a distinct specialization with units of inverse reference time, not an identification of arbitrary measured $X$ with hazards. A complete three-directional response model must specify how off-diagonal inputs alter receiver dynamics and what physical comparisons preserve that law.
