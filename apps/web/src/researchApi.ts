import type {
  ArtifactRecord,
  ResearchConfig as SyntheticConfig,
  ScientificClassification,
  TechnicalState,
} from '@signal-space/research-contracts';

// The generated E00 type describes its closed fixture schema. The workspace
// transports other registered plugins through their own server-validated schemas.
export interface ResearchConfig extends Omit<
  SyntheticConfig,
  'schema_version' | 'experiment_id' | 'model_id' | 'analysis'
> {
  schema_version: string;
  experiment_id: string;
  model_id: string;
  analysis: Record<string, unknown>;
}

export interface ExperimentDescription {
  experiment_id: string;
  version: string;
  model_id: string;
  name: string;
  claims: string;
  equations: string[];
  equation_sources?: Array<{
    label: string;
    path: string;
    catalog_id?: string;
  }>;
  capabilities: string[];
  unavailable_capabilities?: string[];
}

export interface JsonSchema {
  'x-presets'?: Array<{ name: string; config: ResearchConfig }>;
  title?: string;
  type?: string | string[];
  const?: unknown;
  default?: unknown;
  minimum?: number;
  exclusiveMinimum?: number;
  maximum?: number;
  enum?: unknown[];
  description?: string;
  items?: JsonSchema;
  minLength?: number;
  maxLength?: number;
  required?: string[];
  properties?: Record<string, JsonSchema>;
}

export interface AttemptRecord {
  attempt_id: string;
  parent_attempt_id: string | null;
  state: string;
  path: string;
  created_at: string;
  updated_at: string;
  exit_code: number | null;
  checkpoint: { path: string; sha256: string; step: number } | null;
  failure: {
    code: string;
    recoverable: boolean;
    message: string | null;
  } | null;
}

export interface AnalysisRecord {
  analysis_id: string;
  path: string;
  created_at: string;
  raw_source: string;
  classification: ScientificClassification;
  summary: Record<string, unknown>;
}

export interface ReportRecord {
  report_id: string;
  analysis_id: string;
  path: string;
  created_at: string;
  outputs: Record<string, unknown>;
}

export interface RunManifest {
  run_id: string;
  experiment_id: string;
  experiment_version: string;
  model_id: string;
  created_at: string;
  updated_at: string;
  technical_state: TechnicalState;
  scientific_classification: ScientificClassification;
  config_hash: string;
  config_path: string;
  attempts: AttemptRecord[];
  analyses: AnalysisRecord[];
  reports: ReportRecord[];
  artifacts: ArtifactRecord[];
  acceptance_criteria: Array<{
    id: string;
    description: string;
    evidence: string | null;
  }>;
  completeness: Record<string, boolean>;
  known_gaps: string[];
  code_identity: {
    revision: string;
    tree_state: string;
    dirty_patch_hash: string;
    runtime_version: string;
  };
  seed_ledger: Record<string, number>;
}

export interface RuntimeEvent {
  sequence: number;
  timestamp: string;
  type: string;
  stage: string;
  payload: Record<string, unknown>;
  attempt_id: string;
  cursor: string;
}

export interface ResourceEstimate {
  accepted: boolean;
  estimate: {
    cpu_seconds: number;
    memory_mb: number;
    disk_mb: number;
    wall_seconds: number;
    wall_time_class: string;
  };
  limits: Record<string, number>;
  rejected_limits: string[];
}

interface ApiErrorBody {
  error?: { code?: string; message?: string };
}

export class ResearchApiError extends Error {
  constructor(
    message: string,
    readonly code: string,
    readonly status: number,
  ) {
    super(message);
  }
}

export class ResearchApi {
  readonly endpoint: string;

  constructor(
    endpoint: string,
    private readonly token: string,
  ) {
    this.endpoint = endpoint.replace(/\/$/, '');
  }

  private async request<T>(path: string, body?: unknown): Promise<T> {
    let response: Response;
    try {
      response = await fetch(`${this.endpoint}${path}`, {
        method: body === undefined ? 'GET' : 'POST',
        headers: {
          Authorization: `Bearer ${this.token}`,
          ...(body === undefined ? {} : { 'Content-Type': 'application/json' }),
        },
        ...(body === undefined ? {} : { body: JSON.stringify(body) }),
      });
    } catch (error) {
      throw new ResearchApiError(
        error instanceof Error ? error.message : 'Runtime is unreachable.',
        'DISCONNECTED',
        0,
      );
    }
    if (!response.ok) {
      let parsed: ApiErrorBody = {};
      try {
        parsed = (await response.json()) as ApiErrorBody;
      } catch {
        // Keep the status fallback for non-JSON proxy/network responses.
      }
      throw new ResearchApiError(
        parsed.error?.message ?? `Runtime request failed (${response.status}).`,
        parsed.error?.code ?? 'REQUEST_FAILED',
        response.status,
      );
    }
    return (await response.json()) as T;
  }

  experiments() {
    return this.request<{ experiments: ExperimentDescription[] }>(
      '/v1/experiments',
    );
  }

  schema(experimentId: string) {
    return this.request<{ experiment_id: string; schema: JsonSchema }>(
      `/v1/experiments/${encodeURIComponent(experimentId)}/schema`,
    );
  }

  runs() {
    return this.request<{ runs: RunManifest[] }>('/v1/runs');
  }

  validate(config: ResearchConfig) {
    return this.request<{ config: ResearchConfig }>('/v1/validate', config);
  }

  estimate(config: ResearchConfig) {
    return this.request<ResourceEstimate>('/v1/estimate', config);
  }

  start(config: ResearchConfig) {
    return this.request<{ run_id: string; state: string }>('/v1/runs', config);
  }

  run(runId: string) {
    return this.request<RunManifest>(`/v1/runs/${encodeURIComponent(runId)}`);
  }

  events(runId: string, cursor = '') {
    const query = cursor ? `?cursor=${encodeURIComponent(cursor)}` : '';
    return this.request<{ events: RuntimeEvent[] }>(
      `/v1/runs/${encodeURIComponent(runId)}/events${query}`,
    );
  }

  action(runId: string, action: 'cancel' | 'resume' | 'analyze' | 'report') {
    return this.request<Record<string, unknown>>(
      `/v1/runs/${encodeURIComponent(runId)}/${action}`,
      {},
    );
  }

  async artifact(runId: string, artifactId: string): Promise<Response> {
    let response: Response;
    try {
      response = await fetch(
        `${this.endpoint}/v1/runs/${encodeURIComponent(runId)}/artifacts/${encodeURIComponent(artifactId)}`,
        { headers: { Authorization: `Bearer ${this.token}` } },
      );
    } catch (error) {
      throw new ResearchApiError(
        error instanceof Error ? error.message : 'Runtime is unreachable.',
        'DISCONNECTED',
        0,
      );
    }
    if (!response.ok)
      throw new ResearchApiError(
        `Artifact request failed (${response.status}).`,
        'ARTIFACT_REQUEST_FAILED',
        response.status,
      );
    return response;
  }
}

export type { ArtifactRecord };
