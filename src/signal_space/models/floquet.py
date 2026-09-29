"""SS OPS 1 six-gate routing ansatz. Physical memory rays, not frozen coefficients."""
import numpy as np
from signal_space.models.reciprocal import exact_gate

N = 20  # two complex spinors (8 real) and six CP1 memories (12 real)
LABELS = ('vacuum', 'equal', 'counter')


def ray(w):
    return np.outer(w, w.conj())


def tangent(w):
    return np.array([-w[1].conj(), w[0].conj()])


def unpack(x):
    return x.reshape(2, 2)[:, 0] + 1j * x.reshape(2, 2)[:, 1]


def pack(z):
    return np.column_stack((z.real, z.imag)).ravel()


def background(label):
    u = np.array([1., 0.], complex)
    waves = np.zeros((2, 2), complex)
    if label == 'equal': waves[:] = .5*u
    if label == 'counter': waves[:] = [.5*u, -.5*u]
    rays = [np.array([1, 1])/np.sqrt(2), np.array([1, 1j])/np.sqrt(2), u]
    if label == 'counter': rays = [u, u, u]
    return waves, np.repeat(np.array(rays, complex), 2, axis=0)


def local_coordinates(state, reference):
    out = np.zeros(10)
    out[:8] = np.concatenate([pack(z) for z in state[:2]])
    w = reference[2]; c = np.vdot(tangent(w), ray(state[2]) @ w)
    out[8:] = [c.real, c.imag]
    return out


def perturb(state, column, amount):
    out = state.copy()
    if column < 8:
        z = np.zeros(4); z[column % 4] = amount
        out[column // 4] += unpack(z)
    else:
        out[2] += amount * (1 if column == 8 else 1j) * tangent(state[2])
        out[2] /= np.linalg.norm(out[2])
    return out


def frozen_gate(state):
    a, b, w = state; p = ray(w)
    return np.array([a-p@(a-b), b+p@(a-b), w])


def jacobian(state, h, frozen=False, solver=None):
    flow = solver or (frozen_gate if frozen else lambda s: exact_gate(s, np.pi/2, 0))
    base = flow(state)
    # Memory output chart uses input ray: all registered backgrounds return that ray.
    out = np.column_stack([(local_coordinates(flow(perturb(state,j,h)),state)-
                            local_coordinates(flow(perturb(state,j,-h)),state))/(2*h) for j in range(10)])
    if frozen:
        # A prescribed memory cannot vary; retain identity slots only for dimension bookkeeping.
        out[:8,8:] = 0
    return base, out


def stages(label, h, frozen=False, solver=None):
    waves, memories = background(label)
    inputs=[]; outputs=[]; blocks=[]
    for index in range(6):
        state = np.array([*waves, memories[index]])
        result, block = jacobian(state,h,frozen,solver)
        inputs.append(state); outputs.append(result); blocks.append(block)
        waves = result[:2]
    return np.array(inputs), np.array(outputs), np.array(blocks)


def bloch(blocks, q):
    """Bond gate owns a(m), b(m+e_i), w_i(m); phase exp(+i q_i)."""
    result = np.eye(N, dtype=complex)
    for index, block in enumerate(blocks):
        indices = list(range(8)) + [8+2*index,9+2*index]
        matrix = np.eye(N,dtype=complex)
        phase = np.ones(10,dtype=complex)
        if index % 2: phase[4:8] = np.exp(1j*q[index//2])
        matrix[np.ix_(indices,indices)] = block * phase[None,:] / phase[:,None]
        result = matrix @ result
    return result


def apply_tangent(field, blocks):
    out = field.copy()
    for index,block in enumerate(blocks):
        axis=index//2; idx=list(range(8))+[8+2*index,9+2*index]
        local=out[...,idx].copy()
        if index%2: local[...,4:8]=np.roll(local[...,4:8],-1,axis=axis)
        changed=np.einsum('ij,...j->...i',block,local)
        if index%2: changed[...,4:8]=np.roll(changed[...,4:8],1,axis=axis)
        out[...,idx]=changed
    return out
