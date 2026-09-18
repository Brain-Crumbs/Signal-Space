# 2. Interfaces inherited from Part I {#sec-interfaces}

## 2.1. Records and retained state

Retain Part I's finite-dimensional complex representation, tensor-product composition, local quantum instruments, and trace rule. For a protocol $\mathcal P$, the joint record law is

$$
p(r_1,\ldots,r_n\mid\mathcal P)
=\operatorname{Tr}\!\left[
\mathcal I_{r_n\mid a_n}\circ\cdots\circ
\mathcal I_{r_1\mid a_1}(\rho_0)\right].
\tag{P1}
$$

Adaptive settings depend only on permitted earlier records. Signal, receiver memory, and returning environments must remain in the predictive state whenever later protocols can access them. A reduced channel matrix used below is sufficient for its local analyzer statistics; it is not generally sufficient for arbitrary multitime predictions.

Unread instrument outcomes are summed as completely positive maps. Coherent alternatives are combined only in a specified larger realization. The two alternatives of Part I's channel register therefore provide a usable two-component sector, but no physical spatial direction has yet been assigned to that sector. Measurements along three Pauli axes are three analyzer choices on one qubit, not evidence for three extended spatial coordinates.

## 2.2. Assumption ledger

The following additions are separated by purpose.

**S1. Signal-sector restriction.** Selected trials address a two-dimensional complex signal sector. Any vacuum, loss, leakage, temporal distinguishability, and inaccessible memory are separately accounted for. This sector is chosen as a minimal extension of Part I, not derived as a universal microscopic dimension.

**S2. Analyzer calibration.** The source ensemble is reproducible across settings, and a tomographically complete set of analyzer effects is calibrated. Exposure and efficiency are fixed independently when absolute intensity is reported. Settings that change the source require a larger protocol model.

**S3. Candidate comparison law.** A proposed local comparison between descriptions acts by a single complex linear amplitude map and hence by congruence on the intensity operator. Determinant preservation and orientation preservation are further restrictions when a Lorentz comparison is asserted. Section 5 distinguishes this ansatz from an instrument physically applied in the laboratory.

**K1. Reference-geometry controls.** Sections 6-9 use a supplied flat reference metric and speed $c_0$. These controls assess clock laws; they do not derive their reference geometry.

**K2. Confined-mode control.** The phase-clock example has prescribed reflecting boundaries, a fixed massless wave equation, and a declared mode preparation and readout. Boundary support and external driving are supplied. Binding, recoil, and their energy balance are not derived.

**G1. Conditional continuum interface.** Only Section 10 assumes a smooth four-dimensional tangent structure, a linear coframe, and a common interpretation of its cone by physical probes. Those assumptions are the missing geometric bridge, not conclusions of S1-S3.

Each result below identifies which additions it uses. In particular, satisfying S1-S2 does not establish S3, and satisfying S3 does not establish G1.

## 2.3. Notation and units

We write $X$ for an unnormalized positive signal operator and $\rho_S=X/\operatorname{Tr}X$ for its normalized state. The coordinates $x^a$ of $X$ initially have the units of intensity per declared exposure. The scalar $\gamma=\sqrt{\det X}$ has the same units; it is never a Lorentz factor in this manuscript. The signed diagonal coordinate is $h$, while $\eta$ denotes independently inferred kinematic rapidity.

Outgoing reversal hazards are $q_+$ and $q_-$. The directional mean is $b=\mathbb E\sigma$, with $\sigma=\pm1$. Counts are $N$, an expected count reading is $\mathbb E\widehat\tau$, and the proper time of a specified timelike reference curve is $\tau$. These are different objects. Physical thermodynamic entropy would be $k_B$ times dimensionless entropy; no such energy or temperature normalization is inferred here.

The matrix determinant uses $J=\operatorname{diag}(1,-1,-1,-1)$. For a spacetime metric we use the architecture's convention $\eta_{ab}=-J_{ab}$, so timelike vectors have negative squared length. This explicit sign conversion avoids changing conventions between the cone and the metric.
