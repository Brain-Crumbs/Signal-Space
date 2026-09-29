\Needspace{9\baselineskip}

# 4. Lorentz-cone structure and its scope {#sec-cone}

## 4.1. Cone and logarithmic coordinates

For (S2), the Pauli product identity gives

$$
\det X=(x^0)^2-|\mathbf x|^2=x^T Jx.
\tag{L1}
$$

Strict positivity corresponds to the interior of the future Lorentz cone. Nonzero rank-one operators form its boundary; $X=0$ is the apex. For $X>0$, define

$$
\gamma=\sqrt{\det X},\qquad
h=\operatorname{artanh}\frac{|\mathbf x|}{x^0}.
\tag{L2}
$$

With $\mathbf n=\mathbf x/|\mathbf x|$ when $\mathbf x\ne0$,

$$
X=\gamma e^{h\mathbf n\cdot\boldsymbol\sigma}
=\gamma\bigl(\cosh h\,I+\sinh h\,\mathbf n\cdot\boldsymbol\sigma\bigr).
\tag{L3}
$$

Here $h\geq0$; the axis is immaterial at $h=0$. In a fixed diagonal axis one may instead use signed $h$, giving

$$
q_-=\gamma e^h,\qquad q_+=\gamma e^{-h},
\qquad h=\tfrac12\ln(q_-/q_+).
\tag{L4}
$$

The normalized operator is

$$
\rho_S=\frac12\bigl(I+\tanh h\,\mathbf n\cdot\boldsymbol\sigma\bigr).
\tag{L5}
$$

Normalization removes $\gamma$. At a fixed nonzero intensity the pure-state limit has $h\to\infty$ and $\gamma\to0$; the product in (L3) remains finite. A pure qubit in a stationary apparatus therefore lies on the algebraic null boundary. It is not thereby a photon or a null worldline. Operational spatial meaning requires more than cone membership.

## 4.2. Congruence and the Lorentz action

**Proposition L1 (standard cone representation).** For $A\in SL(2,\mathbb C)$, the real-linear map $X\mapsto AXA^\dagger$ preserves positivity and determinant and induces a proper orthochronous Lorentz transformation. Every such Lorentz transformation is induced, with kernel $\{I,-I\}$.

*Proof.* Positivity is preserved by invertible congruence, and $\det(AXA^\dagger)=|\det A|^2\det X=\det X$. Its real coordinate matrix is

$$
\Lambda(A)^a{}_b
=\tfrac12\operatorname{Tr}(\sigma_a A\sigma_b A^\dagger),
\qquad \Lambda(A)^T J\Lambda(A)=J.
\tag{L6}
$$

Continuity from identity and preservation of the positive cone select the proper orthochronous component. Unitary determinant-one matrices give all spatial rotations. Positive determinant-one matrices $\exp(\xi\mathbf n\cdot\boldsymbol\sigma/2)$ give all pure boosts. A proper orthochronous Lorentz map can first have its action on the time axis undone by a boost; the remaining map fixes that axis and is a spatial rotation. Hence these matrices cover the full group. If $AXA^\dagger=X$ for every Hermitian $X$, using $X=I$ makes $A$ unitary and using the Pauli matrices makes $A$ scalar. Determinant one leaves $A=\pm I$. $\square$

The factor of one half is essential: applying $A=\exp(\xi\sigma_3/2)$ to $X=\gamma I$ produces $X'=\gamma\exp(\xi\sigma_3)$, with cone coordinate $h=\xi$.

For a boost along $\mathbf n$, decompose $\mathbf x=x_\parallel\mathbf n+\mathbf x_\perp$. Direct multiplication gives

$$
\begin{aligned}
x'^0&=x^0\cosh\xi+x_\parallel\sinh\xi,\\
x'_\parallel&=x_\parallel\cosh\xi+x^0\sinh\xi,\\
\mathbf x'_\perp&=\mathbf x_\perp.
\end{aligned}
\tag{L7}
$$

These are active algebraic boosts. A passive reference-frame boost used below carries the opposite sign. Collinear signed rapidities add; non-collinear boosts do not reduce to addition of three scalar log-rate ratios.

## 4.3. What the representation does and does not select

The real vector space of Hermitian $2\times2$ matrices has dimension four. Choosing this sector supplies a local $1+3$ quadratic cone. It does not prove that an event network has four-dimensional tangent spaces, that three directions extend spatially, or that all excitations propagate on this cone. Larger channel spaces also have positive cones, whose determinants are generally higher-degree invariants. Selecting the two-component sector is an explanatory input.

The general congruence with $A\in GL(2,\mathbb C)$ scales the quadratic form by $|\det A|^2$. Restricting to $SL(2,\mathbb C)$ is therefore a scale condition. Arbitrary gain or exposure changes are not secretly excluded by quantum composition.

Noncommuting boosts can generate a Wigner rotation even in flat spacetime. A loop of mere frame changes has a stronger cancellation: if $G_{ji}=A_jA_i^{-1}$, then

$$
G_{ik}G_{kj}G_{ji}=I.
\tag{L8}
$$

A nontrivial sequence of physical boosts and a nontrivial spacetime curvature holonomy are different statements. Deriving curvature requires a physical transport connection over spacetime loops, not only noncommuting local matrices.
