export const MODEL_VERSION = 'paper-i-v1';

const finite = Number.isFinite;
const issue = (path, message) => ({ path, message });

/** Validate the semantic constraints that JSON Schema cannot express clearly. */
export function validateScenario(value) {
  const errors = [];
  if (!value || typeof value !== 'object')
    return { ok: false, errors: [issue('$', 'must be an object')] };
  if (value.modelVersion !== MODEL_VERSION)
    errors.push(issue('modelVersion', `must equal ${MODEL_VERSION}`));
  for (const [key, label] of [
    ['c0', 'c0'],
    ['rateScale', 'r*'],
    ['filterWidth', 'h'],
  ])
    if (!finite(value[key]) || value[key] <= 0)
      errors.push(issue(key, `${label} must be finite and > 0`));
  const nodes = Array.isArray(value.nodes) ? value.nodes : [];
  const links = Array.isArray(value.links) ? value.links : [];
  if (nodes.length === 0)
    errors.push(issue('nodes', 'must contain at least one node'));
  if (!Array.isArray(value.links))
    errors.push(issue('links', 'must be an array'));
  const ids = new Set();
  let prior = -Infinity;
  for (const [i, n] of nodes.entries()) {
    const p = `nodes[${i}]`;
    if (!n?.id || ids.has(n.id))
      errors.push(issue(`${p}.id`, 'must be a unique non-empty string'));
    else ids.add(n.id);
    if (!finite(n?.position) || n.position <= prior)
      errors.push(
        issue(`${p}.position`, 'must be finite and strictly increasing'),
      );
    else prior = n.position;
    for (const key of ['omega0', 'relaxationTime'])
      if (!finite(n?.[key]) || n[key] <= 0)
        errors.push(issue(`${p}.${key}`, 'must be finite and > 0'));
    if (!finite(n?.omega) || n.omega <= 0)
      errors.push(issue(`${p}.omega`, 'must be finite and > 0'));
    if (!finite(n?.phi))
      errors.push(issue(`${p}.phi`, 'must be finite (unwrapped radians)'));
    if (!finite(n?.amplitude) || n.amplitude < 0 || n.amplitude > 1)
      errors.push(issue(`${p}.amplitude`, 'must be in [0, 1]'));
    if (!finite(n?.gain) || (finite(n?.omega0) && Math.abs(n.gain) >= n.omega0))
      errors.push(issue(`${p}.gain`, 'must satisfy |gain| < omega0'));
    if (n?.response === 'R0' && n.gain !== 0)
      errors.push(issue(`${p}.gain`, 'must equal 0 when response is R0'));
    if (n?.emission?.law === 'E0') {
      if (!finite(n.emission.nu) || n.emission.nu <= 0)
        errors.push(issue(`${p}.emission.nu`, 'must be finite and > 0 for E0'));
    } else if (n?.emission?.law === 'E1') {
      if (!finite(n.emission.q) || n.emission.q <= 0)
        errors.push(issue(`${p}.emission.q`, 'must be finite and > 0 for E1'));
    } else errors.push(issue(`${p}.emission.law`, 'must select E0 or E1'));
    if (
      finite(n?.omega) &&
      finite(n?.omega0) &&
      finite(n?.gain) &&
      (n.omega < n.omega0 - Math.abs(n.gain) ||
        n.omega > n.omega0 + Math.abs(n.gain))
    )
      errors.push(issue(`${p}.omega`, 'must lie within omega0 ± |gain|'));
  }
  const incoming = new Set(),
    outgoing = new Set(),
    linkIds = new Set();
  for (const [i, l] of links.entries()) {
    const p = `links[${i}]`;
    if (!l?.id || linkIds.has(l.id))
      errors.push(issue(`${p}.id`, 'must be unique'));
    else linkIds.add(l.id);
    if (!ids.has(l?.source))
      errors.push(issue(`${p}.source`, 'must reference a node'));
    if (!ids.has(l?.target))
      errors.push(issue(`${p}.target`, 'must reference a node'));
    if (l?.source === l?.target)
      errors.push(issue(`${p}.target`, 'self-links are not allowed'));
    if (!finite(l?.delay) || l.delay <= 0)
      errors.push(issue(`${p}.delay`, 'must be finite and > 0'));
    const out = `${l?.source}:${l?.sourcePort}`,
      inc = `${l?.target}:${l?.targetPort}`;
    if (outgoing.has(out))
      errors.push(
        issue(`${p}.sourcePort`, 'port already has an outgoing link'),
      );
    else outgoing.add(out);
    if (incoming.has(inc))
      errors.push(
        issue(`${p}.targetPort`, 'port already has an incoming link'),
      );
    else incoming.add(inc);
    const s = nodes.find((n) => n.id === l?.source),
      t = nodes.find((n) => n.id === l?.target);
    if (s && t) {
      const expected =
        t.position > s.position ? ['right', 'left'] : ['left', 'right'];
      if (l.sourcePort !== expected[0] || l.targetPort !== expected[1])
        errors.push(
          issue(
            `${p}.sourcePort`,
            'ports are inconsistent with ordered positions',
          ),
        );
      const derived = Math.abs(t.position - s.position) / value.c0;
      if (
        finite(derived) &&
        Math.abs(l.delay - derived) > 1e-9 * Math.max(1, derived)
      )
        errors.push(issue(`${p}.delay`, 'must equal |x_target-x_source|/c0'));
    }
  }
  const hist = value.initialHistory;
  if (
    !hist ||
    !finite(hist.startTime) ||
    hist.startTime >= 0 ||
    hist.endTime !== 0
  )
    errors.push(issue('initialHistory', 'must span [negative time, 0]'));
  const boundaryDelays = ['left', 'right']
    .map((side) => value.boundaries?.[side])
    .flatMap((b) => {
      if (b?.kind === 'periodic') return [b.closureDelay];
      if (b?.kind === 'mirror') return [2 * (b.exteriorDistance / value.c0)];
      return [];
    });
  const maxDelay = Math.max(0, ...links.map((l) => l.delay), ...boundaryDelays);
  if (hist?.startTime > -maxDelay)
    errors.push(
      issue('initialHistory.startTime', 'must cover at least -tau_max'),
    );
  for (const key of ['nodes', 'filters']) {
    const states = hist?.[key];
    for (const id of ids)
      if (!states || !Object.hasOwn(states, id) || !states[id])
        errors.push(
          issue(
            `initialHistory.${key}.${id}`,
            'state is required for every node',
          ),
        );
    for (const id of Object.keys(states ?? {}))
      if (!ids.has(id))
        errors.push(
          issue(
            `initialHistory.${key}.${id}`,
            'must reference a scenario node',
          ),
        );
  }
  for (const n of nodes) {
    const endpoint = hist?.nodes?.[n?.id];
    if (!endpoint) continue;
    for (const [historyKey, nodeKey] of [
      ['phiAtZero', 'phi'],
      ['omega', 'omega'],
    ])
      if (!finite(endpoint[historyKey]) || endpoint[historyKey] !== n[nodeKey])
        errors.push(
          issue(
            `initialHistory.nodes.${n.id}.${historyKey}`,
            `must equal the node's ${nodeKey} at t=0`,
          ),
        );
  }
  const responses = Array.isArray(hist?.pendingResponses)
    ? hist.pendingResponses
    : [];
  for (const [i, response] of responses.entries())
    if (!ids.has(response?.nodeId))
      errors.push(
        issue(
          `initialHistory.pendingResponses[${i}].nodeId`,
          'must reference a scenario node',
        ),
      );
  const packets = Array.isArray(hist?.pendingPackets)
    ? hist.pendingPackets
    : [];
  for (const [i, packet] of packets.entries()) {
    const p = `initialHistory.pendingPackets[${i}]`;
    for (const endpoint of ['source', 'target'])
      if (!ids.has(packet?.[endpoint]))
        errors.push(
          issue(`${p}.${endpoint}`, 'must reference a scenario node'),
        );

    if (!finite(packet?.emissionTime) || packet.emissionTime > 0)
      errors.push(issue(`${p}.emissionTime`, 'must be finite and <= 0'));
    if (!finite(packet?.arrivalTime) || packet.arrivalTime < 0)
      errors.push(issue(`${p}.arrivalTime`, 'must be finite and >= 0'));
    if (
      finite(packet?.emissionTime) &&
      finite(packet?.arrivalTime) &&
      packet.arrivalTime <= packet.emissionTime
    )
      errors.push(issue(`${p}.arrivalTime`, 'must be after emissionTime'));
  }
  for (const side of ['left', 'right']) {
    const b = value.boundaries?.[side];
    if (!b) errors.push(issue(`boundaries.${side}`, 'is required'));
    else if (!['open', 'driven', 'mirror', 'periodic'].includes(b.kind))
      errors.push(
        issue(
          `boundaries.${side}.kind`,
          'must select open, driven, mirror, or periodic',
        ),
      );
    if (b?.kind === 'driven' && (!finite(b.rate) || b.rate < 0))
      errors.push(issue(`boundaries.${side}.rate`, 'must be finite and >= 0'));
    if (
      b?.kind === 'mirror' &&
      (!finite(b.exteriorDistance) || b.exteriorDistance <= 0)
    )
      errors.push(issue(`boundaries.${side}.exteriorDistance`, 'must be > 0'));
    if (
      b?.kind === 'periodic' &&
      (!finite(b.closureDelay) || b.closureDelay <= 0)
    )
      errors.push(issue(`boundaries.${side}.closureDelay`, 'must be > 0'));
  }
  return { ok: errors.length === 0, errors };
}

export function roundTripScenario(scenario) {
  const parsed = JSON.parse(JSON.stringify(scenario));
  const result = validateScenario(parsed);
  if (!result.ok)
    throw new Error(
      result.errors.map((e) => `${e.path}: ${e.message}`).join('\n'),
    );
  return parsed;
}
