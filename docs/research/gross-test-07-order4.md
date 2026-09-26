# Test 7 follow-up: formal fourth order and a held-out local response

This is a separately registered follow-up to the **failed** Test 7, not a changed acceptance decision for run `run-b1677e67610c5870`. It retains the SS OCF 1 flat radial Hamiltonian, frozen $\omega_Q=0.9$, $\Omega_\chi=0.41274991$, $\epsilon=0.2$, and the Test 6 core, eigenmode, phase and local $r=0.1$ calibration. The already inspected Test 7 histories test the derived coefficient diagnostically. The new shell with center 22 and width 3.25 is a locked held-out prediction, including signs and amplitudes specified in `fixtures/research/gross-test-07-order4.json`.

## Derivation from the registered discrete action

Set $u=r\Phi$, $w=r\chi$, $b=ra$, and let $G$ be the implemented radial gradient and $T=G^\top$ the discrete adjoint. The neutral canonical momentum is $p=Z(s)\dot b$, with $s=|u/r|^2$, $Z=1+\epsilon s$, $U=s-s^2+s^3$, $V=.25-.4s+.2s^2$, and the clock quartic coefficient $.1$. Dots denote derivatives of flat radial time. Write

$$u=u_0+A^2u_2+A^4u_4+\cdots,\quad w=w_0+A^2w_2+A^4w_4+\cdots,$$
$$b=Ab_1+A^3b_3+\cdots,\quad p=Ap_1+A^3p_3+\cdots.$$

Define $s_0=|u_0/r|^2$, $s_2=2\Re(\bar u_0u_2)/r^2$, $s_4=(|u_2|^2+2\Re(\bar u_0u_4))/r^2$, $Z_0=1+\epsilon s_0$, $Z_2=\epsilon s_2$. The first and third neutral orders satisfy

$$\dot b_1=p_1/Z_0,\quad \dot p_1=-T[(1+\epsilon F s_0)Gb_1],$$
$$\dot b_3=p_3/Z_0-Z_2p_1/Z_0^2,\quad \dot p_3=-T[(1+\epsilon F s_0)Gb_3+\epsilon(Fs_2)Gb_1],$$

where $F$ averages site densities to faces. Thus the neutral cubic coefficient responds to the second-order density; it is not a new interaction. Define $j_2=((p_1/Z_0)^2-F^\top[(Gb_1)^2])/r^2$ and $j_4=(2(p_1/Z_0)(p_3/Z_0-Z_2p_1/Z_0^2)-2F^\top[(Gb_1)(Gb_3)])/r^2$; $F^\top$ here is the code's face-adjoint average. With $c_k=w_k/r$, $C(s,c)=U'(s)+\frac12V'(s)c^2$ and $M(s)=V(s)$, extract $C_0$, $C_2$ and $C_4$ algebraically:

$$C_2=(-2+6s_0+.2c_0^2)s_2+(-.4+.4s_0)c_0c_2,$$
$$C_4=(-2+6s_0+.2c_0^2)s_4+3s_2^2+.4s_2c_0c_2+(-.4+.4s_0)(c_0c_4+c_2^2/2).$$

For the frozen quiet solution and the previously registered second-order tangent system, the new fourth-order accelerations are

$$\ddot u_4=\Delta_hu_4-C_0u_4-C_2u_2-C_4u_0+\frac{\epsilon}{2}(j_2u_2+j_4u_0),$$
$$\ddot w_4=\Delta_hw_4-M_0w_4-M_2w_2-M_4w_0-.1(3c_0^2w_4+3c_0c_2w_2),$$

with $M_0=V(s_0)$, $M_2=V'(s_0)s_2$, $M_4=V'(s_0)s_4+.2s_2^2$. The implementation evolves all these coefficients together with the quiet and second-order equations, at every RK4 substep. Initial orders 2–4 are zero. No coefficient is fitted to any receiver record.

For the actual **local quadrature** $z=\chi-i\dot\chi/\Omega_\chi$, set $z=z_0+A^2z_2+A^4z_4$. The phase correction is

$$\theta_2=A^2\Im(z_2/z_0),\qquad \theta_4=A^4\Im[z_4/z_0-\tfrac12(z_2/z_0)^2].$$

The square term matters even when the field coefficient $w_4$ is small. All comparisons use the same first-rise and last-fall $|a|=10^{-4}$ local markers and subtract quiet phase at those same times. That quiet comparison is a counterfactual diagnostic.

## Information boundary and numerical controls

The new predictor receives only the frozen calibrated receiver, the upstream $a,a_t,a_r$ history at $R_s=14$, and the declared clock phase. The prescribed held-out packet parameters are used only in a separate acquisition and receiver; the forecast reads a saved surface file. The primary inverse uses the known exterior $Z(r)$ with travel time $\int_{R_s}^r dr'/\sqrt{Z(r')}$, characteristic $(R_sa_t+\sqrt{Z(R_s)}(a+R_sa_r))/2$, and leading $Z^{-1/4}$ amplitude transport. The old vacuum inversion is retained as a control. This optical approximation is not an exact discrete inverse and does not silently change the action. Surface, inverse and all forecasts are SHA-256 locked before the first new receiver starts.

Run $R=80$, $h=.1,.05,.025$, $dt=.01,.01,.005$ respectively; independently halve $dt$ at $h=.1$. The finest grid interpolates the frozen fine calibration. Duration is 65; output interval is $.05$ rather than Test 7's $.1$. Compare linear threshold crossings with cubic Hermite crossings using saved local $a_t$, also after decimation back to $.1$. Compare the unchanged Test 7 marker limit $.1$ and interval allowance $\max(5\%\text{ of observed record},\text{direct numerical budget})$. A marker or record can remain failed or unresolved. The original Test 7 two failures stay failed regardless of this follow-up's classification.

Neither optical transport nor a fourth-order clock response tests two-object exchange, recoil, observer invariance, gravity, angular stability or emergent spacetime. Test 8 remains blocked unless a separate acceptance decision establishes its prerequisite.
