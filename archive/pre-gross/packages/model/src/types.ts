/** Paper I model contract v1. SI units are used unless a UnitSystem declares scales. */
export type Port = 'left' | 'right';
export type Emission = { law: 'E0'; nu: number } | { law: 'E1'; q: number };
export type Boundary =
  | { kind: 'open' }
  | { kind: 'driven'; rate: number }
  | { kind: 'mirror'; exteriorDistance: number }
  | { kind: 'periodic'; closureDelay: number };

export interface ClockNode {
  id: string;
  position: number;
  omega0: number;
  omega: number;
  phi: number;
  amplitude: number;
  gain: number;
  relaxationTime: number;
  emission: Emission;
  response: 'R0' | 'R1' | 'R2';
}
export interface DirectedLink {
  id: string;
  source: string;
  target: string;
  sourcePort: Port;
  targetPort: Port;
  delay: number;
}
export interface InitialHistory {
  startTime: number;
  endTime: 0;
  nodes: Record<string, { phiAtZero: number; omega: number }>;
  pendingPackets: Packet[];
  filters: Record<string, { left: number; right: number }>;
  pendingResponses: Array<{
    nodeId: string;
    dueTime: number;
    payload: unknown;
  }>;
  rngState?: { algorithm: string; state: string };
}
export interface Packet {
  id: string;
  source: string;
  target: string;
  emissionTime: number;
  arrivalTime: number;
  port: Port;
}
export interface Intervention {
  time: number;
  kind: 'remove-pulse' | 'add-probe' | 'change-parameter';
  target: string;
  value?: unknown;
}
export interface ObservationProtocol {
  sampleTimes: number[];
  visible: Array<
    'local-phase' | 'local-frequency' | 'arrival-time' | 'reported-count'
  >;
  detectorLatency: number;
}
export interface SolverSettings {
  method: 'rk4' | 'dopri5' | 'event';
  step?: number;
  absoluteTolerance: number;
  relativeTolerance: number;
}
export interface UnitSystem {
  time: 's';
  length: 'm';
  angle: 'rad';
  rate: 's^-1';
  angularFrequency: 'rad s^-1';
  density: 's^-1';
}
export interface Scenario {
  modelVersion: 'paper-i-v1';
  id: string;
  c0: number;
  rateScale: number;
  filterWidth: number;
  nodes: ClockNode[];
  links: DirectedLink[];
  boundaries: { left: Boundary; right: Boundary };
  initialHistory: InitialHistory;
  interventions: Intervention[];
  observation: ObservationProtocol;
  solver: SolverSettings;
  units: UnitSystem;
}
export interface RunManifest {
  schemaVersion: 1;
  runId: string;
  scenarioId: string;
  modelVersion: 'paper-i-v1';
  codeRevision: string;
  createdAt: string;
  seed?: string;
  solver: SolverSettings;
}
export interface Snapshot {
  schemaVersion: 1;
  time: number;
  nodeState: Record<string, { phi: number; omega: number }>;
  history: InitialHistory;
}
export interface ObserverRecord {
  time: number;
  nodeId: string;
  localPhase?: number;
  localFrequency?: number;
  arrivalTime?: number;
  reportedCount?: number;
}
export interface PhysicalOutput {
  manifest: RunManifest;
  samples: Array<{
    time: number;
    nodes: Record<string, { phi: number; omega: number }>;
  }>;
  packets: Packet[];
}
