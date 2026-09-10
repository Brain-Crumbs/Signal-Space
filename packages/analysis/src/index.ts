import type { Snapshot } from '@signal-space/model';

const TAU = 2 * Math.PI;
export interface AnalysisNodeSample {
  phi: number;
  omega: number;
  ticks?: number;
  receptionLeft?: number;
  receptionRight?: number;
}
export interface AnalysisSample {
  time: number;
  nodes: Record<string, AnalysisNodeSample>;
}
export interface AnalysisSeries {
  samples: AnalysisSample[];
  failed?: { code: string; message: string };
}
export interface MeasurementWindow {
  start: number;
  end: number;
}
export interface PairCriteria {
  transientEnd: number;
  windows: MeasurementWindow[];
  frequencyTolerance: number;
  phaseRangeTolerance: number;
  minimumCycles: number;
  perturbation?: {
    time: number;
    recoveryTolerance: number;
    referenceOffset: number;
    /** Matched continuation used for recovery instead of a fixed offset. */
    reference?: AnalysisSeries;
  };
}
export type RegimeStatus =
  | 'candidate-frequency-locking'
  | 'candidate-phase-locking'
  | 'slipping'
  | 'unresolved'
  | 'numerically-failed';
export interface WindowEvidence {
  window: MeasurementWindow;
  duration: number;
  meanFrequency: Record<string, number>;
  frequencyMismatch: number;
  unwrappedPhaseRange: number;
  slipCount: number;
  slipRate: number;
  frequencyModulation: Record<string, { minimum: number; maximum: number }>;
  enoughDuration: boolean;
}
export interface PairClassification {
  status: RegimeStatus;
  definition: string;
  evidence: WindowEvidence[];
  perturbationRecovery?: {
    demonstrated: boolean;
    displaced: boolean;
    postPerturbationSampleCount: number;
    maximumError: number;
    finalError: number;
  };
  failure?: { code: string; message: string };
}

function finite(value: number, name: string) {
  if (!Number.isFinite(value)) throw new RangeError(`${name} must be finite.`);
}
function requireNode(sample: AnalysisSample, id: string) {
  const node = sample.nodes[id];
  if (!node)
    throw new RangeError(`Sample at ${sample.time} has no node ${id}.`);
  return node;
}
function assertSeries(series: AnalysisSeries) {
  if (series.samples.length < 2)
    throw new RangeError('Diagnostics require at least two samples.');
  let previous = -Infinity;
  for (const [index, sample] of series.samples.entries()) {
    finite(sample.time, `samples[${index}].time`);
    if (sample.time <= previous)
      throw new RangeError('Sample times must be strictly increasing.');
    previous = sample.time;
    for (const [id, node] of Object.entries(sample.nodes)) {
      finite(node.phi, `${id}.phi`);
      finite(node.omega, `${id}.omega`);
    }
  }
}
function samplesIn(series: AnalysisSeries, window: MeasurementWindow) {
  finite(window.start, 'window.start');
  finite(window.end, 'window.end');
  if (window.end <= window.start)
    throw new RangeError('A measurement window must have positive duration.');
  const samples = series.samples.filter(
    (s) => s.time >= window.start && s.time <= window.end,
  );
  if (samples[0]?.time !== window.start || samples.at(-1)?.time !== window.end)
    throw new RangeError(
      'Every window requires saved samples at both declared boundaries.',
    );
  return samples;
}

function pairPhaseAt(
  series: AnalysisSeries,
  a: string,
  b: string,
  time: number,
): number {
  const samples = series.samples;
  if (time < samples[0]!.time || time > samples.at(-1)!.time)
    throw new RangeError(
      'Reference series does not cover the perturbation window.',
    );
  if (time === samples[0]!.time) {
    const sample = samples[0]!;
    return requireNode(sample, a).phi - requireNode(sample, b).phi;
  }
  for (let index = 1; index < samples.length; index++) {
    const next = samples[index]!;
    if (next.time < time) continue;
    const previous = samples[index - 1]!;
    if (next.time === time) {
      return requireNode(next, a).phi - requireNode(next, b).phi;
    }
    const previousPhase =
      requireNode(previous, a).phi - requireNode(previous, b).phi;
    const nextPhase = requireNode(next, a).phi - requireNode(next, b).phi;
    const fraction = (time - previous.time) / (next.time - previous.time);
    return previousPhase + fraction * (nextPhase - previousPhase);
  }
  return (
    requireNode(samples.at(-1)!, a).phi - requireNode(samples.at(-1)!, b).phi
  );
}

/** Phase-advance estimator, not an average of correlated instantaneous samples. */
export function meanFrequency(samples: AnalysisSample[], nodeId: string) {
  if (samples.length < 2)
    throw new RangeError('Mean frequency needs two endpoints.');
  const first = samples[0]!,
    last = samples.at(-1)!;
  return (
    (requireNode(last, nodeId).phi - requireNode(first, nodeId).phi) /
    (last.time - first.time)
  );
}
export function wrap(angle: number) {
  finite(angle, 'angle');
  const value = ((((angle + Math.PI) % TAU) + TAU) % TAU) - Math.PI;
  return value === -Math.PI ? Math.PI : value;
}
export function pairPhase(samples: AnalysisSample[], a: string, b: string) {
  return samples.map((sample) => {
    const unwrapped = requireNode(sample, a).phi - requireNode(sample, b).phi;
    return { time: sample.time, unwrapped, wrapped: wrap(unwrapped) };
  });
}
/** Signed net crossings of successive 2π cells from the window's initial phase. */
export function slipCount(unwrapped: number[]) {
  return unwrapped.length < 2
    ? 0
    : Math.floor(unwrapped.at(-1)! / TAU) - Math.floor(unwrapped[0]! / TAU);
}
export function tickChange(samples: AnalysisSample[], nodeId: string) {
  if (samples.length < 2)
    throw new RangeError('Tick change needs two endpoints.');
  const first = requireNode(samples[0]!, nodeId).ticks,
    last = requireNode(samples.at(-1)!, nodeId).ticks;
  if (first === undefined || last === undefined)
    throw new RangeError('Saved tick counters are required.');
  return last - first;
}
export function receptionInventory(samples: AnalysisSample[], nodeId: string) {
  return samples.map((sample) => {
    const node = requireNode(sample, nodeId),
      left = node.receptionLeft ?? 0,
      right = node.receptionRight ?? 0;
    return {
      time: sample.time,
      left,
      right,
      sum: left + right,
      difference: right - left,
    };
  });
}

export interface RetardedPhasePoint {
  time: number;
  sourceTime: number;
  wrapped: number;
  unwrapped: number;
  chi: number;
  access: 'simulator-only' | 'observer-protocol';
}
export function retardedPhase(
  receiver: Array<{ time: number; phi: number }>,
  delayedSource: Array<{ time: number; sourceTime: number; phi: number }>,
  chi: number,
  measurableByProtocol = false,
): RetardedPhasePoint[] {
  finite(chi, 'chi');
  if (receiver.length !== delayedSource.length)
    throw new RangeError('Receiver and delayed-source arrays must align.');
  return receiver.map((entry, index) => {
    const source = delayedSource[index]!;
    if (entry.time !== source.time)
      throw new RangeError('Retarded samples must share evaluation times.');
    const unwrapped = entry.phi - source.phi - chi;
    return {
      time: entry.time,
      sourceTime: source.sourceTime,
      unwrapped,
      wrapped: wrap(unwrapped),
      chi,
      access: measurableByProtocol ? 'observer-protocol' : 'simulator-only',
    };
  });
}

function windowEvidence(
  series: AnalysisSeries,
  a: string,
  b: string,
  window: MeasurementWindow,
  criteria: PairCriteria,
): WindowEvidence {
  const samples = samplesIn(series, window);
  if (samples.length < 2)
    throw new RangeError('Every window needs at least two saved samples.');
  const duration = samples.at(-1)!.time - samples[0]!.time,
    phases = pairPhase(samples, a, b).map((p) => p.unwrapped),
    frequencies = Object.fromEntries(
      [a, b].map((id) => [id, meanFrequency(samples, id)]),
    ),
    frequencyModulation = Object.fromEntries(
      [a, b].map((id) => {
        const values = samples.map((s) => requireNode(s, id).omega);
        return [
          id,
          { minimum: Math.min(...values), maximum: Math.max(...values) },
        ];
      }),
    ),
    slips = slipCount(phases);
  return {
    window,
    duration,
    meanFrequency: frequencies,
    frequencyMismatch: Math.abs(frequencies[a]! - frequencies[b]!),
    unwrappedPhaseRange: Math.max(...phases) - Math.min(...phases),
    slipCount: slips,
    slipRate: slips / duration,
    frequencyModulation,
    enoughDuration:
      duration *
        Math.min(Math.abs(frequencies[a]!), Math.abs(frequencies[b]!)) >=
      criteria.minimumCycles * TAU,
  };
}
export function classifyPair(
  series: AnalysisSeries,
  a: string,
  b: string,
  criteria: PairCriteria,
): PairClassification {
  if (series.failed)
    return {
      status: 'numerically-failed',
      definition: 'The numerical run failed; no physical regime is inferred.',
      evidence: [],
      failure: series.failed,
    };
  assertSeries(series);
  finite(criteria.transientEnd, 'transientEnd');
  if (!criteria.windows.length)
    throw new RangeError('At least one measurement window is required.');
  criteria.windows.forEach((window, index) => {
    finite(window.start, `windows[${index}].start`);
    finite(window.end, `windows[${index}].end`);
    if (window.end <= window.start)
      throw new RangeError('Measurement windows must have positive duration.');
    if (window.start < criteria.transientEnd)
      throw new RangeError(
        'Measurement windows must begin after the declared transient.',
      );
    const previous = criteria.windows[index - 1];
    if (
      previous &&
      (window.start > previous.start ||
        window.end < previous.end ||
        (window.start === previous.start && window.end === previous.end))
    )
      throw new RangeError(
        'Measurement windows must be ordered shortest to longest and each contain the previous window.',
      );
  });
  for (const key of [
    'frequencyTolerance',
    'phaseRangeTolerance',
    'minimumCycles',
  ] as const)
    if (!(criteria[key] >= 0) || !Number.isFinite(criteria[key]))
      throw new RangeError(`${key} must be finite and nonnegative.`);
  if (criteria.perturbation) {
    finite(criteria.perturbation.time, 'perturbation.time');
    finite(
      criteria.perturbation.referenceOffset,
      'perturbation.referenceOffset',
    );
    if (
      !(criteria.perturbation.recoveryTolerance >= 0) ||
      !Number.isFinite(criteria.perturbation.recoveryTolerance)
    )
      throw new RangeError(
        'perturbation.recoveryTolerance must be finite and nonnegative.',
      );
    if (criteria.perturbation.reference) {
      if (criteria.perturbation.reference.failed)
        throw new RangeError(
          'Perturbation reference series must not have failed.',
        );
      assertSeries(criteria.perturbation.reference);
    }
  }
  let evidence: WindowEvidence[];
  try {
    evidence = criteria.windows.map((w) =>
      windowEvidence(series, a, b, w, criteria),
    );
  } catch (error) {
    return {
      status: 'unresolved',
      definition: `Insufficient saved data: ${(error as Error).message}`,
      evidence: [],
    };
  }
  const frequency = evidence.map(
      (e) =>
        e.enoughDuration && e.frequencyMismatch <= criteria.frequencyTolerance,
    ),
    phase = evidence.map(
      (e) => e.unwrappedPhaseRange <= criteria.phaseRangeTolerance,
    ),
    slipping = evidence.map((e) => e.slipCount !== 0);
  let recovery: PairClassification['perturbationRecovery'];
  if (criteria.perturbation) {
    const perturbation = criteria.perturbation,
      postPerturbation = series.samples.filter(
        (sample) => sample.time > perturbation.time,
      ),
      errors = postPerturbation.map((sample) =>
        Math.abs(
          requireNode(sample, a).phi -
            requireNode(sample, b).phi -
            (perturbation.reference
              ? pairPhaseAt(perturbation.reference, a, b, sample.time)
              : perturbation.referenceOffset),
        ),
      ),
      finalError = errors.at(-1) ?? Infinity,
      displaced = errors
        .slice(0, -1)
        .some((error) => error > perturbation.recoveryTolerance);
    recovery = {
      demonstrated: displaced && finalError <= perturbation.recoveryTolerance,
      displaced,
      postPerturbationSampleCount: errors.length,
      maximumError: errors.length ? Math.max(...errors) : Infinity,
      finalError,
    };
  }
  const all = (v: boolean[]) => v.every(Boolean),
    conflict = (v: boolean[]) => v.some(Boolean) && !v.every(Boolean);
  const recoveryEvidence = recovery ? { perturbationRecovery: recovery } : {};
  if (
    evidence.some((e) => !e.enoughDuration) ||
    conflict(frequency) ||
    conflict(phase) ||
    conflict(slipping)
  )
    return {
      status: 'unresolved',
      definition:
        'Nested windows are too short or give conflicting finite-window evidence.',
      evidence,
      ...recoveryEvidence,
    };
  if (all(slipping))
    return {
      status: 'slipping',
      definition:
        'Every declared window contains nonzero unwrapped 2π phase drift.',
      evidence,
      ...recoveryEvidence,
    };
  if (all(frequency) && all(phase) && recovery?.demonstrated)
    return {
      status: 'candidate-phase-locking',
      definition:
        'Frequency mismatch and unwrapped phase range meet tolerances, with declared perturbation recovery.',
      evidence,
      ...recoveryEvidence,
    };
  if (all(frequency))
    return {
      status: 'candidate-frequency-locking',
      definition:
        'Phase-advance mean frequencies meet tolerance; phase attraction is not claimed.',
      evidence,
      ...recoveryEvidence,
    };
  return {
    status: 'unresolved',
    definition:
      'Finite-window evidence meets no declared candidate definition.',
    evidence,
    ...recoveryEvidence,
  };
}

export interface ReplicateEstimate {
  runId: string;
  seed?: string;
  preparationId: string;
  value: number;
  sampleCount: number;
}
export function aggregateReplicates(
  runs: ReplicateEstimate[],
  confidence = 0.95,
) {
  if (runs.length < 2)
    throw new RangeError('At least two independent replicates are required.');
  if (!(confidence > 0 && confidence < 1))
    throw new RangeError('confidence must be between zero and one.');
  if (new Set(runs.map((r) => r.runId)).size !== runs.length)
    throw new RangeError('Replicate run IDs must be unique.');
  const seeds = runs.flatMap((run) =>
    run.seed === undefined ? [] : [run.seed],
  );
  if (new Set(seeds).size !== seeds.length)
    throw new RangeError('Stochastic replicate seeds must be unique.');
  runs.forEach((r) => {
    finite(r.value, 'replicate value');
    if (!Number.isInteger(r.sampleCount) || r.sampleCount < 1)
      throw new RangeError('sampleCount must be positive.');
  });
  const mean = runs.reduce((s, r) => s + r.value, 0) / runs.length,
    variance =
      runs.reduce((s, r) => s + (r.value - mean) ** 2, 0) / (runs.length - 1),
    halfWidth =
      normalQuantile(0.5 + confidence / 2) * Math.sqrt(variance / runs.length);
  return {
    estimator: 'independent-replicate mean with normal-approximation interval',
    confidence,
    mean,
    interval: [mean - halfWidth, mean + halfWidth] as [number, number],
    seedCount: seeds.length,
    replicateCount: runs.length,
    sampleCount: runs.reduce((s, r) => s + r.sampleCount, 0),
    dependence:
      'Samples within a run may be time-correlated; the interval treats runs, not saved samples, as independent.',
    runs: structuredClone(runs),
  };
}
function normalQuantile(p: number): number {
  const a = [
      -39.6968302866538, 220.946098424521, -275.928510446969, 138.357751867269,
      -30.6647980661472, 2.50662827745924,
    ],
    b = [
      -54.4760987982241, 161.585836858041, -155.698979859887, 66.8013118877197,
      -13.2806815528857,
    ],
    c = [
      -0.00778489400243029, -0.322396458041136, -2.40075827716184,
      -2.54973253934373, 4.37466414146497, 2.93816398269878,
    ],
    d = [
      0.00778469570904146, 0.32246712907004, 2.445134137143, 3.75440866190742,
    ];
  if (p < 0.02425) {
    const q = Math.sqrt(-2 * Math.log(p));
    return (
      (((((c[0]! * q + c[1]!) * q + c[2]!) * q + c[3]!) * q + c[4]!) * q +
        c[5]!) /
      ((((d[0]! * q + d[1]!) * q + d[2]!) * q + d[3]!) * q + 1)
    );
  }
  if (p > 0.97575) return -normalQuantile(1 - p);
  const q = p - 0.5,
    r = q * q;
  return (
    ((((((a[0]! * r + a[1]!) * r + a[2]!) * r + a[3]!) * r + a[4]!) * r +
      a[5]!) *
      q) /
    (((((b[0]! * r + b[1]!) * r + b[2]!) * r + b[3]!) * r + b[4]!) * r + 1)
  );
}
export function spatialProfile(
  sample: AnalysisSample,
  orderedNodeIds: string[],
) {
  return orderedNodeIds.map((nodeId, index) => ({
    index,
    nodeId,
    phi: requireNode(sample, nodeId).phi,
    omega: requireNode(sample, nodeId).omega,
  }));
}
export function circularCoherence(sample: AnalysisSample, nodeIds: string[]) {
  if (!nodeIds.length)
    throw new RangeError('Coherence needs at least one node.');
  const re =
      nodeIds.reduce((s, id) => s + Math.cos(requireNode(sample, id).phi), 0) /
      nodeIds.length,
    im =
      nodeIds.reduce((s, id) => s + Math.sin(requireNode(sample, id).phi), 0) /
      nodeIds.length;
  return {
    magnitude: Math.hypot(re, im),
    angle: Math.atan2(im, re),
    interpretation:
      'Wrapped global coherence only; low magnitude does not exclude a traveling spatial pattern.',
  };
}
/** Pearson correlation of two unwrapped spatial profiles; no independence claim. */
export function spatialCorrelation(
  first: AnalysisSample,
  second: AnalysisSample,
  nodeIds: string[],
) {
  if (nodeIds.length < 2)
    throw new RangeError('Spatial correlation needs at least two nodes.');
  const a = nodeIds.map((id) => requireNode(first, id).phi),
    b = nodeIds.map((id) => requireNode(second, id).phi),
    meanA = a.reduce((sum, value) => sum + value, 0) / a.length,
    meanB = b.reduce((sum, value) => sum + value, 0) / b.length,
    covariance = a.reduce(
      (sum, value, index) => sum + (value - meanA) * (b[index]! - meanB),
      0,
    ),
    scaleA = Math.sqrt(a.reduce((sum, value) => sum + (value - meanA) ** 2, 0)),
    scaleB = Math.sqrt(b.reduce((sum, value) => sum + (value - meanB) ** 2, 0));
  return scaleA === 0 || scaleB === 0
    ? undefined
    : covariance / (scaleA * scaleB);
}
export function responseFront(
  onsets: Array<{ nodeId: string; position: number; onsetTime?: number }>,
  perturbation: { position: number; time: number },
  c0: number,
  tolerance: number,
) {
  if (!Number.isFinite(c0) || !(c0 > 0))
    throw new RangeError('c0 must be finite and positive.');
  if (!Number.isFinite(tolerance) || !(tolerance >= 0))
    throw new RangeError('tolerance must be finite and nonnegative.');
  finite(perturbation.position, 'perturbation.position');
  finite(perturbation.time, 'perturbation.time');
  return onsets.map((point, index) => {
    finite(point.position, `onsets[${index}].position`);
    if (point.onsetTime !== undefined)
      finite(point.onsetTime, `onsets[${index}].onsetTime`);
    const causalBound =
      perturbation.time + Math.abs(point.position - perturbation.position) / c0;
    return {
      ...point,
      causalBound,
      status:
        point.onsetTime === undefined
          ? 'not-observed'
          : point.onsetTime + tolerance < causalBound
            ? 'causality-violation'
            : 'causally-admissible',
    };
  });
}
export function summarizeSnapshot(snapshot: Snapshot) {
  return {
    time: snapshot.time,
    nodeCount: Object.keys(snapshot.nodeState).length,
    pendingPacketCount: snapshot.history.pendingPackets.length,
  };
}
