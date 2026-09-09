export const MODEL_VERSION = 'paper-i-v1';

const finite = Number.isFinite;
const issue = (path, message) => ({ path, message });

/** Validate the semantic constraints that JSON Schema cannot express clearly. */
export function validateScenario(value) {
  const errors = [];
  if (!value || typeof value !== 'object') return { ok: false, errors: [issue('$', 'must be an object')] };
  if (value.modelVersion !== MODEL_VERSION) errors.push(issue('modelVersion', `must equal ${MODEL_VERSION}`));
  for (const [key, label] of [['c0', 'c0'], ['rateScale', 'r*'], ['filterWidth', 'h']])
    if (!finite(value[key]) || value[key] <= 0) errors.push(issue(key, `${label} must be finite and > 0`));
  if (!Array.isArray(value.nodes) || value.nodes.length === 0) errors.push(issue('nodes', 'must contain at least one node'));
  const ids = new Set(); let prior = -Infinity;
  for (const [i, n] of (value.nodes ?? []).entries()) {
    const p = `nodes[${i}]`;
    if (!n?.id || ids.has(n.id)) errors.push(issue(`${p}.id`, 'must be a unique non-empty string')); else ids.add(n.id);
    if (!finite(n?.position) || n.position <= prior) errors.push(issue(`${p}.position`, 'must be finite and strictly increasing')); else prior = n.position;
    for (const key of ['omega0', 'relaxationTime']) if (!finite(n?.[key]) || n[key] <= 0) errors.push(issue(`${p}.${key}`, 'must be finite and > 0'));
    if (!finite(n?.omega) || n.omega <= 0) errors.push(issue(`${p}.omega`, 'must be finite and > 0'));
    if (!finite(n?.phi)) errors.push(issue(`${p}.phi`, 'must be finite (unwrapped radians)'));
    if (!finite(n?.amplitude) || n.amplitude < 0 || n.amplitude > 1) errors.push(issue(`${p}.amplitude`, 'must be in [0, 1]'));
    if (!finite(n?.gain) || (finite(n?.omega0) && Math.abs(n.gain) >= n.omega0)) errors.push(issue(`${p}.gain`, 'must satisfy |gain| < omega0'));
    if (finite(n?.omega) && finite(n?.omega0) && finite(n?.gain) && (n.omega < n.omega0-Math.abs(n.gain) || n.omega > n.omega0+Math.abs(n.gain))) errors.push(issue(`${p}.omega`, 'must lie within omega0 ± |gain|'));
  }
  const incoming = new Set(), outgoing = new Set(), linkIds = new Set();
  for (const [i, l] of (value.links ?? []).entries()) {
    const p = `links[${i}]`;
    if (!l?.id || linkIds.has(l.id)) errors.push(issue(`${p}.id`, 'must be unique')); else linkIds.add(l.id);
    if (!ids.has(l?.source)) errors.push(issue(`${p}.source`, 'must reference a node'));
    if (!ids.has(l?.target)) errors.push(issue(`${p}.target`, 'must reference a node'));
    if (l?.source === l?.target) errors.push(issue(`${p}.target`, 'self-links are not allowed'));
    if (!finite(l?.delay) || l.delay <= 0) errors.push(issue(`${p}.delay`, 'must be finite and > 0'));
    const out = `${l?.source}:${l?.sourcePort}`, inc = `${l?.target}:${l?.targetPort}`;
    if (outgoing.has(out)) errors.push(issue(`${p}.sourcePort`, 'port already has an outgoing link')); else outgoing.add(out);
    if (incoming.has(inc)) errors.push(issue(`${p}.targetPort`, 'port already has an incoming link')); else incoming.add(inc);
    const s = value.nodes?.find(n => n.id === l?.source), t = value.nodes?.find(n => n.id === l?.target);
    if (s && t) {
      const expected = t.position > s.position ? ['right','left'] : ['left','right'];
      if (l.sourcePort !== expected[0] || l.targetPort !== expected[1]) errors.push(issue(`${p}.sourcePort`, 'ports are inconsistent with ordered positions'));
      const derived = Math.abs(t.position-s.position)/value.c0;
      if (finite(derived) && Math.abs(l.delay-derived) > 1e-9*Math.max(1, derived)) errors.push(issue(`${p}.delay`, 'must equal |x_target-x_source|/c0'));
    }
  }
  const hist = value.initialHistory;
  if (!hist || !finite(hist.startTime) || hist.startTime >= 0 || hist.endTime !== 0) errors.push(issue('initialHistory', 'must span [negative time, 0]'));
  const maxDelay = Math.max(0, ...(value.links ?? []).map(l => l.delay));
  if (hist?.startTime > -maxDelay) errors.push(issue('initialHistory.startTime', 'must cover at least -tau_max'));
  for (const id of ids) if (!hist?.nodes?.[id]) errors.push(issue(`initialHistory.nodes.${id}`, 'history is required for every node'));
  for (const side of ['left','right']) {
    const b=value.boundaries?.[side];
    if (!b) errors.push(issue(`boundaries.${side}`, 'is required'));
    if (b?.kind==='mirror' && (!finite(b.exteriorDistance)||b.exteriorDistance<=0)) errors.push(issue(`boundaries.${side}.exteriorDistance`, 'must be > 0'));
    if (b?.kind==='periodic' && (!finite(b.closureDelay)||b.closureDelay<=0)) errors.push(issue(`boundaries.${side}.closureDelay`, 'must be > 0'));
  }
  return { ok: errors.length === 0, errors };
}

export function roundTripScenario(scenario) {
  const parsed = JSON.parse(JSON.stringify(scenario));
  const result = validateScenario(parsed);
  if (!result.ok) throw new Error(result.errors.map(e => `${e.path}: ${e.message}`).join('\n'));
  return parsed;
}
