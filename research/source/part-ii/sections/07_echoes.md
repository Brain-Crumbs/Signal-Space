# 7. Independent rapidity from exchanges {#sec-echoes}

## 7.1. Instantaneous reflection control

In the reference flat $1+1$ geometry, place the observer at $x=0$ with calibrated proper time equal to $t$. A smooth timelike reflector remains at $x>0$ on the interval of interest. For an instantaneous reflection at $(t,x)$, let $s$ and $r=\mathcal R(s)$ be emission and return readings. Then

$$
s=t-x/c_0,\qquad r=t+x/c_0,
\qquad t=\frac{s+r}{2},\quad x=\frac{c_0(r-s)}2.
\tag{E1}
$$

Differentiating along the reflector gives

$$
\mathcal R'=\frac{1+b}{1-b},\qquad
\eta_{\rm echo}=\tfrac12\ln\mathcal R',\qquad
\frac{d\tau}{ds}=\sqrt{\mathcal R'}.
\tag{E2}
$$

Here $b=\dot x/c_0$ is the reflector's actual reference velocity. The logarithmic echo coordinate is operationally distinct from the hazard coordinate $h$. Radar-time constructions and their observer dependence are discussed in [5]. Equations (E1)-(E2) require their stated reference geometry and response law.

For a small error $\delta\mathcal R'$ in a positive derivative, the first-order rapidity error is $\delta\eta_{\rm echo}=\delta\mathcal R'/(2\mathcal R')$. Differentiation amplifies timestamp noise, so a practical estimate must specify the fit window, smoothness assumptions, and uncertainty propagation. Exact derivatives in a synthetic control are not finite-sample measurements.

## 7.2. Response latency is a distinct unknown

If reception and re-emission occur at separate events $a$ and $b$ on the responding object,

$$
s=t_a-x_a/c_0,\qquad r=t_b+x_b/c_0.
\tag{E3}
$$

The ordinary midpoint is then a combination of two events rather than a unique reflection event. A stationary relay at distance $L$ with coordinate response delay $d(s)$ produces

$$
\mathcal R(s)=s+2L/c_0+d(s),\qquad
\eta_{\rm app}=\tfrac12\ln[1+d'(s)].
\tag{E4}
$$

Whenever $1+d'>0$, the same uncorrected echo map can be interpreted as an instantaneous moving reflector over a suitable finite interval. Thus echoes alone cannot generally separate motion from an unrestricted latency law. A constant delay biases distance but not the slope in this stationary example; a variable delay can bias both.

Latency must be independently measured, constrained by a previously fitted response model, or resolved by additional local records. For a moving responder, subtracting a laboratory delay from the return reading is not generically sufficient: (E3) must be propagated through the responder's trajectory. Probe recoil and state changes similarly belong in the local instrument and response dynamics.

## 7.3. A comparison with predictive content

The proposed diagonal test fixes detector gains, exposure, source preparation, and response calibration using separate records. It then estimates $q_\pm$, predicts $b$ using the residence law, and compares $h=\tfrac12\ln(q_-/q_+)$ against $\eta_{\rm echo}$ on new histories. Equilibrium predicts equality only for the stated hazard process; a transient predicts the explicit lag and excess of (C1) and (C6).

For a full cone test, a common transformation must also predict transverse coherent preparations and their analyzer records. A diagonal fit cannot validate the non-collinear action. Protocols with deliberately changed source anisotropy, detector imbalance, temporal overlap, and response latency provide negative controls. Geometry should explain the remaining common relation, not absorb each apparatus change into a separately fitted boost.
