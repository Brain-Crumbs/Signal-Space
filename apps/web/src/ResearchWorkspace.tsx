import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { ResearchPlot, parsePlotCsv } from './ResearchPlot.js';
import type { FigureSpec, PlotRow } from './ResearchPlot.js';
import { SchemaForm } from './SchemaForm.js';
import {
  ResearchApi,
  ResearchApiError,
  type ArtifactRecord,
  type ExperimentDescription,
  type JsonSchema,
  type ResearchConfig,
  type ResourceEstimate,
  type RunManifest,
  type RuntimeEvent,
} from './researchApi.js';

type WorkspaceTab = 'prepare' | 'audit' | 'compare' | 'reports';
type ConnectionState = 'offline' | 'connecting' | 'connected' | 'disconnected';

const TERMINAL = new Set([
  'completed',
  'cancelled',
  'interrupted',
  'failed',
  'analyzed',
  'archived',
]);

function sessionValue(key: string, fallback: string) {
  return sessionStorage.getItem(key) ?? fallback;
}

function latestAttempt(run?: RunManifest) {
  return run?.attempts.at(-1);
}

function artifactFor(run: RunManifest, predicate: (path: string) => boolean) {
  return run.artifacts.find((artifact) => predicate(artifact.path));
}

function displayTime(value: string) {
  const date = new Date(value);
  return Number.isNaN(date.valueOf()) ? value : date.toLocaleString();
}

function same(left: unknown, right: unknown) {
  return JSON.stringify(left) === JSON.stringify(right);
}

function ConfigDiff({
  left,
  right,
  runs,
}: {
  left: ResearchConfig | undefined;
  right: ResearchConfig | undefined;
  runs: [RunManifest | undefined, RunManifest | undefined];
}) {
  if (!left || !right)
    return (
      <p className="empty">
        Choose two runs to load their exact configurations.
      </p>
    );
  const dimensions: Array<[string, unknown, unknown, boolean]> = [
    ['Model', left.model_id, right.model_id, left.model_id === right.model_id],
    ['Units', left.units, right.units, same(left.units, right.units)],
    [
      'Geometry',
      (left as unknown as Record<string, unknown>).geometry ?? 'not declared',
      (right as unknown as Record<string, unknown>).geometry ?? 'not declared',
      same(
        (left as unknown as Record<string, unknown>).geometry,
        (right as unknown as Record<string, unknown>).geometry,
      ),
    ],
    [
      'Boundary',
      (left as unknown as Record<string, unknown>).boundary ?? 'not declared',
      (right as unknown as Record<string, unknown>).boundary ?? 'not declared',
      same(
        (left as unknown as Record<string, unknown>).boundary,
        (right as unknown as Record<string, unknown>).boundary,
      ),
    ],
    [
      'Parameters',
      left.parameters,
      right.parameters,
      same(left.parameters, right.parameters),
    ],
  ];
  const compatible = dimensions.slice(0, 4).every((row) => row[3]);
  return (
    <div>
      <p
        className={`comparison-verdict ${compatible ? 'compatible' : 'incompatible'}`}
        role="status"
      >
        {compatible
          ? 'Compatible for side-by-side inspection. Values are not combined.'
          : 'Incompatible comparison. Differences are preserved and no aggregate is computed.'}
      </p>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Dimension</th>
              <th>Run A</th>
              <th>Run B</th>
              <th>Match</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th>Technical state</th>
              <td>{runs[0]?.technical_state}</td>
              <td>{runs[1]?.technical_state}</td>
              <td>retained</td>
            </tr>
            {dimensions.map(([label, a, b, matches]) => (
              <tr key={label}>
                <th>{label}</th>
                <td>
                  <code>{typeof a === 'string' ? a : JSON.stringify(a)}</code>
                </td>
                <td>
                  <code>{typeof b === 'string' ? b : JSON.stringify(b)}</code>
                </td>
                <td>{matches ? 'same' : 'different'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function ResearchWorkspace() {
  const [endpoint, setEndpoint] = useState(() =>
    sessionValue('signal-space-runtime-endpoint', 'http://127.0.0.1:8765'),
  );
  const [token, setToken] = useState(() =>
    sessionValue('signal-space-runtime-token', ''),
  );
  const [connection, setConnection] = useState<ConnectionState>('offline');
  const [connectionError, setConnectionError] = useState('');
  const [api, setApi] = useState<ResearchApi>();
  const [experiments, setExperiments] = useState<ExperimentDescription[]>([]);
  const [schema, setSchema] = useState<JsonSchema>();
  const [config, setConfig] = useState<ResearchConfig>();
  const [resolvedConfig, setResolvedConfig] = useState<ResearchConfig>();
  const [estimate, setEstimate] = useState<ResourceEstimate>();
  const [prepareState, setPrepareState] = useState('Not validated');
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [tab, setTab] = useState<WorkspaceTab>('prepare');
  const [runs, setRuns] = useState<RunManifest[]>([]);
  const [selectedRunId, setSelectedRunId] = useState('');
  const [events, setEvents] = useState<RuntimeEvent[]>([]);
  const [streamWarning, setStreamWarning] = useState('');
  const [runConfig, setRunConfig] = useState<ResearchConfig>();
  const [compareIds, setCompareIds] = useState<[string, string]>(['', '']);
  const [compareConfigs, setCompareConfigs] = useState<
    [ResearchConfig | undefined, ResearchConfig | undefined]
  >([undefined, undefined]);
  const [reportText, setReportText] = useState('');
  const [plotRows, setPlotRows] = useState<PlotRow[]>([]);
  const [figureSpec, setFigureSpec] = useState<FigureSpec>();
  const [reportLoading, setReportLoading] = useState(false);
  const cursorRef = useRef('');
  const eventKeysRef = useRef(new Set<string>());

  const selectedRun = runs.find((run) => run.run_id === selectedRunId);
  const selectedExperiment = experiments.find(
    (experiment) => experiment.experiment_id === config?.experiment_id,
  );
  const runActive = selectedRun
    ? !TERMINAL.has(selectedRun.technical_state)
    : false;

  const handleError = useCallback((error: unknown) => {
    const problem =
      error instanceof Error ? error.message : 'Unexpected workspace failure.';
    setMessage(problem);
    if (error instanceof ResearchApiError && error.code === 'DISCONNECTED') {
      setConnection('disconnected');
      setConnectionError(
        'Connection lost. Saved packages remain intact; reconnect to resume from the last acknowledged event.',
      );
    }
  }, []);

  const loadSchema = useCallback(
    async (client: ResearchApi, experimentId: string) => {
      const response = await client.schema(experimentId);
      const initial = response.schema.default;
      if (!initial || typeof initial !== 'object')
        throw new Error(
          'Experiment schema does not provide a preparation template.',
        );
      setSchema(response.schema);
      setConfig(structuredClone(initial) as ResearchConfig);
      setResolvedConfig(undefined);
      setEstimate(undefined);
      setPrepareState('Not validated');
    },
    [],
  );

  const connect = useCallback(async () => {
    setConnection('connecting');
    setConnectionError('');
    setMessage('');
    try {
      const client = new ResearchApi(endpoint.trim(), token.trim());
      const [experimentResponse, runResponse] = await Promise.all([
        client.experiments(),
        client.runs(),
      ]);
      if (experimentResponse.experiments.length === 0)
        throw new Error('The runtime has no registered experiments.');
      const first = experimentResponse.experiments[0];
      if (!first) throw new Error('The runtime experiment response is empty.');
      await loadSchema(client, first.experiment_id);
      sessionStorage.setItem('signal-space-runtime-endpoint', endpoint.trim());
      sessionStorage.setItem('signal-space-runtime-token', token.trim());
      setApi(client);
      setExperiments(experimentResponse.experiments);
      setRuns(runResponse.runs);
      setSelectedRunId(
        (current) => current || runResponse.runs[0]?.run_id || '',
      );
      setCompareIds([
        runResponse.runs[0]?.run_id ?? '',
        runResponse.runs[1]?.run_id ?? '',
      ]);
      setConnection('connected');
    } catch (error) {
      setConnection('disconnected');
      setConnectionError(
        error instanceof Error
          ? error.message
          : 'Could not connect to runtime.',
      );
    }
  }, [endpoint, loadSchema, token]);

  const mergeEvents = useCallback((incoming: RuntimeEvent[]) => {
    setEvents((current) => {
      const merged = [...current];
      const lastByAttempt = new Map<string, number>();
      current.forEach((event) =>
        lastByAttempt.set(event.attempt_id, event.sequence),
      );
      incoming.forEach((event) => {
        const key = `${event.attempt_id}:${event.sequence}`;
        if (eventKeysRef.current.has(key)) return;
        const previous = lastByAttempt.get(event.attempt_id);
        if (previous !== undefined && event.sequence !== previous + 1)
          setStreamWarning(
            `Event gap detected for ${event.attempt_id}: expected ${previous + 1}, received ${event.sequence}.`,
          );
        eventKeysRef.current.add(key);
        lastByAttempt.set(event.attempt_id, event.sequence);
        merged.push(event);
      });
      return merged;
    });
    const last = incoming.at(-1);
    if (last) cursorRef.current = last.cursor;
  }, []);

  const refreshRun = useCallback(
    async (client: ResearchApi, runId: string) => {
      const [manifest, stream] = await Promise.all([
        client.run(runId),
        client.events(runId, cursorRef.current),
      ]);
      setRuns((current) => {
        const next = current.filter((run) => run.run_id !== manifest.run_id);
        return [manifest, ...next].sort((a, b) =>
          b.updated_at.localeCompare(a.updated_at),
        );
      });
      mergeEvents(stream.events);
      return manifest;
    },
    [mergeEvents],
  );

  useEffect(() => {
    cursorRef.current = '';
    eventKeysRef.current = new Set();
    setEvents([]);
    setStreamWarning('');
    setRunConfig(undefined);
    setReportText('');
    setPlotRows([]);
    setFigureSpec(undefined);
  }, [selectedRunId]);

  useEffect(() => {
    if (!api || !selectedRunId || connection !== 'connected') return;
    let disposed = false;
    let timer: number | undefined;
    const poll = async () => {
      try {
        const manifest = await refreshRun(api, selectedRunId);
        if (!disposed && !TERMINAL.has(manifest.technical_state))
          timer = window.setTimeout(poll, 500);
      } catch (error) {
        if (
          error instanceof ResearchApiError &&
          error.code === 'INVALID_CURSOR'
        ) {
          setStreamWarning(
            'The stored event cursor is no longer present. The authoritative log was reloaded and the gap remains visible.',
          );
          cursorRef.current = '';
          eventKeysRef.current = new Set();
          setEvents([]);
          timer = window.setTimeout(poll, 100);
        } else handleError(error);
      }
    };
    void poll();
    return () => {
      disposed = true;
      if (timer !== undefined) window.clearTimeout(timer);
    };
  }, [api, connection, handleError, refreshRun, selectedRunId]);

  const fetchArtifactText = useCallback(
    async (run: RunManifest, artifact: ArtifactRecord) => {
      if (!api) throw new Error('Connect the runtime first.');
      const response = await api.artifact(run.run_id, artifact.id);
      return response.text();
    },
    [api],
  );

  useEffect(() => {
    if (!selectedRun || !api) return;
    const artifact = artifactFor(
      selectedRun,
      (path) => path === selectedRun.config_path,
    );
    if (!artifact) return;
    fetchArtifactText(selectedRun, artifact)
      .then((text) => setRunConfig(JSON.parse(text) as ResearchConfig))
      .catch(handleError);
  }, [api, fetchArtifactText, handleError, selectedRun]);

  useEffect(() => {
    if (!api || compareIds.some((id) => !id)) return;
    let disposed = false;
    Promise.all(
      compareIds.map(async (id) => {
        const run = runs.find((candidate) => candidate.run_id === id);
        if (!run) return undefined;
        const artifact = artifactFor(run, (path) => path === run.config_path);
        if (!artifact) return undefined;
        return JSON.parse(
          await fetchArtifactText(run, artifact),
        ) as ResearchConfig;
      }),
    )
      .then((values) => {
        if (!disposed) setCompareConfigs([values[0], values[1]]);
      })
      .catch(handleError);
    return () => {
      disposed = true;
    };
  }, [api, compareIds, fetchArtifactText, handleError, runs]);

  async function validateDraft() {
    if (!api || !config) return;
    setBusy(true);
    setMessage('');
    setPrepareState('Validating');
    try {
      const validated = await api.validate(config);
      const calculated = await api.estimate(validated.config);
      setConfig(validated.config);
      setResolvedConfig(structuredClone(validated.config));
      setEstimate(calculated);
      setPrepareState(calculated.accepted ? 'Validated' : 'Resource rejected');
    } catch (error) {
      setPrepareState('Validation failed');
      handleError(error);
    } finally {
      setBusy(false);
    }
  }

  async function startRun() {
    if (!api || !config) return;
    setBusy(true);
    setMessage('');
    setPrepareState('Validating');
    try {
      const validated = await api.validate(config);
      const calculated = await api.estimate(validated.config);
      setConfig(validated.config);
      setResolvedConfig(structuredClone(validated.config));
      setEstimate(calculated);
      if (!calculated.accepted) {
        setPrepareState('Resource rejected');
        return;
      }
      const started = await api.start(validated.config);
      setPrepareState('Run created');
      setSelectedRunId(started.run_id);
      setTab('audit');
    } catch (error) {
      setPrepareState('Start failed');
      handleError(error);
    } finally {
      setBusy(false);
    }
  }

  async function runAction(action: 'cancel' | 'resume' | 'analyze' | 'report') {
    if (!api || !selectedRun) return;
    setBusy(true);
    setMessage('');
    try {
      await api.action(selectedRun.run_id, action);
      await refreshRun(api, selectedRun.run_id);
      if (action === 'report') setTab('reports');
    } catch (error) {
      handleError(error);
    } finally {
      setBusy(false);
    }
  }

  async function loadReport() {
    if (!selectedRun) return;
    setReportLoading(true);
    setMessage('');
    try {
      const markdown = artifactFor(selectedRun, (path) =>
        path.endsWith('/report.md'),
      );
      const plot = artifactFor(selectedRun, (path) =>
        path.endsWith('/plot-data/recurrence.csv'),
      );
      const spec = artifactFor(selectedRun, (path) =>
        path.endsWith('/figures/recurrence.figure.json'),
      );
      if (!markdown || !plot || !spec)
        throw new Error('The selected run has no complete generated report.');
      const [markdownText, plotText, specText] = await Promise.all([
        fetchArtifactText(selectedRun, markdown),
        fetchArtifactText(selectedRun, plot),
        fetchArtifactText(selectedRun, spec),
      ]);
      setReportText(markdownText);
      setPlotRows(parsePlotCsv(plotText));
      setFigureSpec(JSON.parse(specText) as FigureSpec);
    } catch (error) {
      handleError(error);
    } finally {
      setReportLoading(false);
    }
  }

  async function downloadArtifact(artifact: ArtifactRecord) {
    if (!api || !selectedRun) return;
    try {
      const response = await api.artifact(selectedRun.run_id, artifact.id);
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = artifact.path.split('/').at(-1) ?? artifact.id;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      handleError(error);
    }
  }

  const reportArtifacts = useMemo(
    () =>
      selectedRun?.artifacts.filter((artifact) =>
        ['report', 'figure', 'plot-data', 'raw', 'derived', 'check'].includes(
          artifact.kind,
        ),
      ) ?? [],
    [selectedRun],
  );

  return (
    <section className="workspace-shell" aria-labelledby="workspace-heading">
      <div className="section-heading">
        <div>
          <p className="eyebrow">LOCAL EXPERIMENT WORKSPACE</p>
          <h2 id="workspace-heading">Prepare, run, audit, compare</h2>
        </div>
        <span className={`connection-chip ${connection}`}>{connection}</span>
      </div>
      <p className="section-intro">
        The browser submits closed configurations to the same local runtime as
        the CLI. Numerical work stays outside React; this interface reads saved
        packages and never labels infrastructure output as a physics result.
      </p>

      <div className="runtime-connection" aria-label="Runtime connection">
        <div>
          <label htmlFor="runtime-endpoint">Loopback runtime URL</label>
          <input
            id="runtime-endpoint"
            value={endpoint}
            onChange={(event) => setEndpoint(event.target.value)}
            disabled={connection === 'connecting'}
          />
        </div>
        <div>
          <label htmlFor="runtime-token">Ephemeral bearer token</label>
          <input
            id="runtime-token"
            type="password"
            value={token}
            onChange={(event) => setToken(event.target.value)}
            disabled={connection === 'connecting'}
            autoComplete="off"
          />
        </div>
        <button
          onClick={() => void connect()}
          disabled={!token || connection === 'connecting'}
        >
          {connection === 'connected'
            ? 'Reconnect'
            : connection === 'connecting'
              ? 'Connecting…'
              : 'Connect runtime'}
        </button>
      </div>
      {connectionError && (
        <div className="recovery-banner" role="alert">
          <span>{connectionError}</span>
          <button
            className="secondary"
            onClick={() => void connect()}
            disabled={!token}
          >
            Retry connection
          </button>
        </div>
      )}

      <nav className="workspace-tabs" aria-label="Experiment workspace views">
        {(['prepare', 'audit', 'compare', 'reports'] as const).map((value) => (
          <button
            key={value}
            className={tab === value ? 'active' : ''}
            aria-current={tab === value ? 'page' : undefined}
            onClick={() => setTab(value)}
          >
            {value === 'prepare'
              ? '1 · Prepare'
              : value === 'audit'
                ? '2 · Run audit'
                : value === 'compare'
                  ? '3 · Compare'
                  : '4 · Reports'}
          </button>
        ))}
      </nav>

      {message && (
        <p className="workspace-message" role="alert">
          {message}
        </p>
      )}

      {tab === 'prepare' && (
        <div className="workspace-panel" aria-label="Experiment preparation">
          {connection !== 'connected' || !config || !schema ? (
            <p className="empty">
              Connect the local runtime to load registered experiment schemas
              and saved runs.
            </p>
          ) : (
            <>
              <div className="workspace-toolbar">
                <div>
                  <label htmlFor="experiment-select">Experiment</label>
                  <select
                    id="experiment-select"
                    value={config.experiment_id}
                    disabled={busy}
                    onChange={(event) => {
                      if (api)
                        void loadSchema(api, event.target.value).catch(
                          handleError,
                        );
                    }}
                  >
                    {experiments.map((experiment) => (
                      <option
                        key={experiment.experiment_id}
                        value={experiment.experiment_id}
                      >
                        {experiment.name}
                      </option>
                    ))}
                  </select>
                </div>
                <span className="state-chip" role="status">
                  {prepareState}
                </span>
              </div>
              {selectedExperiment && (
                <div className="experiment-summary">
                  <p>
                    <strong>Equation:</strong>{' '}
                    <code>{selectedExperiment.equations.join(', ')}</code>
                  </p>
                  {selectedExperiment.equation_sources?.map((source) => (
                    <a
                      key={source.path}
                      href={`#catalog-${source.catalog_id ?? ''}`}
                    >
                      {source.label}
                    </a>
                  ))}
                  <div className="capability-row">
                    {selectedExperiment.capabilities.map((capability) => (
                      <span key={capability}>{capability}</span>
                    ))}
                  </div>
                  {!!selectedExperiment.unavailable_capabilities?.length && (
                    <p className="unavailable">
                      <strong>Unavailable in this fixture:</strong>{' '}
                      {selectedExperiment.unavailable_capabilities.join(', ')}.
                    </p>
                  )}
                </div>
              )}
              <SchemaForm
                schema={schema}
                value={config}
                disabled={busy}
                onChange={(next) => {
                  setConfig(next);
                  setResolvedConfig(undefined);
                  setEstimate(undefined);
                  setPrepareState('Edited · creates a new run');
                }}
              />
              <div className="action-row">
                <button
                  className="secondary"
                  onClick={() => void validateDraft()}
                  disabled={busy}
                >
                  Validate & estimate
                </button>
                <button onClick={() => void startRun()} disabled={busy}>
                  Validate & start run
                </button>
              </div>
              {estimate && (
                <section
                  className="estimate-card"
                  aria-label="Resource estimate"
                >
                  <div className="section-heading">
                    <h3>Resource estimate</h3>
                    <span
                      className={`state-chip ${estimate.accepted ? 'pass' : 'fail'}`}
                    >
                      {estimate.accepted ? 'within limits' : 'rejected'}
                    </span>
                  </div>
                  <dl className="metric-grid">
                    <div>
                      <dt>CPU</dt>
                      <dd>{estimate.estimate.cpu_seconds} s</dd>
                    </div>
                    <div>
                      <dt>Memory</dt>
                      <dd>{estimate.estimate.memory_mb} MB</dd>
                    </div>
                    <div>
                      <dt>Output</dt>
                      <dd>{estimate.estimate.disk_mb} MB</dd>
                    </div>
                    <div>
                      <dt>Wall time</dt>
                      <dd>
                        {estimate.estimate.wall_seconds} s ·{' '}
                        {estimate.estimate.wall_time_class}
                      </dd>
                    </div>
                  </dl>
                </section>
              )}
              {resolvedConfig && (
                <details>
                  <summary>Exact resolved CLI/UI configuration</summary>
                  <pre>{JSON.stringify(resolvedConfig, null, 2)}</pre>
                </details>
              )}
            </>
          )}
        </div>
      )}

      {tab === 'audit' && (
        <div className="workspace-panel" aria-label="Run audit">
          <div className="workspace-toolbar">
            <div className="run-picker">
              <label htmlFor="run-select">Saved run</label>
              <select
                id="run-select"
                value={selectedRunId}
                onChange={(event) => setSelectedRunId(event.target.value)}
              >
                <option value="">Choose a run</option>
                {runs.map((run) => (
                  <option key={run.run_id} value={run.run_id}>
                    {run.run_id} · {run.technical_state}
                  </option>
                ))}
              </select>
            </div>
            {selectedRun && (
              <span className={`state-chip ${selectedRun.technical_state}`}>
                {selectedRun.technical_state}
              </span>
            )}
          </div>
          {!selectedRun ? (
            <p className="empty">No saved run selected.</p>
          ) : (
            <>
              <div className="run-identity-grid">
                <div>
                  <span>Run ID</span>
                  <code>{selectedRun.run_id}</code>
                </div>
                <div>
                  <span>Attempt ID</span>
                  <code>
                    {latestAttempt(selectedRun)?.attempt_id ?? 'not started'}
                  </code>
                </div>
                <div>
                  <span>Model</span>
                  <code>{selectedRun.model_id}</code>
                </div>
                <div>
                  <span>Config SHA-256</span>
                  <code>{selectedRun.config_hash}</code>
                </div>
                <div>
                  <span>Code revision</span>
                  <code>{selectedRun.code_identity.revision}</code>
                </div>
                <div>
                  <span>Scientific outcome</span>
                  <strong
                    className={`classification ${selectedRun.scientific_classification}`}
                  >
                    {selectedRun.scientific_classification}
                  </strong>
                </div>
              </div>
              <div className="action-row">
                <button
                  className="secondary"
                  onClick={() => void runAction('cancel')}
                  disabled={busy || !runActive}
                >
                  Cancel
                </button>
                <button
                  className="secondary"
                  onClick={() => void runAction('resume')}
                  disabled={
                    busy ||
                    !latestAttempt(selectedRun)?.checkpoint ||
                    latestAttempt(selectedRun)?.state === 'completed'
                  }
                >
                  Resume attempt
                </button>
                <button
                  onClick={() => void runAction('analyze')}
                  disabled={
                    busy || runActive || selectedRun.attempts.length === 0
                  }
                >
                  Analyze saved output
                </button>
                <button
                  onClick={() => void runAction('report')}
                  disabled={busy || selectedRun.analyses.length === 0}
                >
                  Regenerate report
                </button>
              </div>
              {latestAttempt(selectedRun)?.failure && (
                <div className="failure-card" role="alert">
                  <strong>{latestAttempt(selectedRun)?.failure?.code}</strong>
                  <span>
                    {latestAttempt(selectedRun)?.failure?.message ??
                      'No worker detail was recorded.'}
                  </span>
                </div>
              )}
              {streamWarning && (
                <p className="stream-warning" role="alert">
                  {streamWarning}
                </p>
              )}
              <section className="audit-section">
                <h3>Lifecycle events</h3>
                {events.length === 0 ? (
                  <p className="empty compact">
                    Waiting for append-only events…
                  </p>
                ) : (
                  <ol className="event-list">
                    {events.map((event) => (
                      <li key={`${event.attempt_id}:${event.sequence}`}>
                        <span>
                          {event.attempt_id} · {event.sequence}
                        </span>
                        <strong>{event.type}</strong>
                        <small>
                          {event.stage} · {displayTime(event.timestamp)}
                        </small>
                      </li>
                    ))}
                  </ol>
                )}
              </section>
              <section className="audit-section">
                <h3>Attempts and recovery</h3>
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Attempt</th>
                        <th>Parent</th>
                        <th>State</th>
                        <th>Checkpoint</th>
                        <th>Failure</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedRun.attempts.map((attempt) => (
                        <tr key={attempt.attempt_id}>
                          <th>{attempt.attempt_id}</th>
                          <td>{attempt.parent_attempt_id ?? '—'}</td>
                          <td>{attempt.state}</td>
                          <td>
                            {attempt.checkpoint
                              ? `step ${attempt.checkpoint.step}`
                              : '—'}
                          </td>
                          <td>{attempt.failure?.code ?? '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
              <section className="audit-section">
                <h3>Acceptance and classification</h3>
                <ul className="criteria-list">
                  {selectedRun.acceptance_criteria.map((criterion) => (
                    <li key={criterion.id}>
                      <strong>{criterion.id}</strong>
                      <span>{criterion.description}</span>
                      <code>
                        {criterion.evidence ?? 'unresolved · no evidence yet'}
                      </code>
                    </li>
                  ))}
                </ul>
                {selectedRun.known_gaps.map((gap) => (
                  <p className="known-gap" key={gap}>
                    {gap}
                  </p>
                ))}
              </section>
              <details>
                <summary>Exact resolved configuration and provenance</summary>
                <pre>
                  {runConfig
                    ? JSON.stringify(runConfig, null, 2)
                    : 'Loading saved configuration…'}
                </pre>
                <pre>
                  {JSON.stringify(
                    {
                      code_identity: selectedRun.code_identity,
                      seed_ledger: selectedRun.seed_ledger,
                    },
                    null,
                    2,
                  )}
                </pre>
              </details>
            </>
          )}
        </div>
      )}

      {tab === 'compare' && (
        <div className="workspace-panel" aria-label="Run comparison">
          <div className="compare-pickers">
            {([0, 1] as const).map((index) => (
              <div key={index}>
                <label htmlFor={`compare-${index}`}>
                  Run {index === 0 ? 'A' : 'B'}
                </label>
                <select
                  id={`compare-${index}`}
                  value={compareIds[index]}
                  onChange={(event) =>
                    setCompareIds((current) =>
                      index === 0
                        ? [event.target.value, current[1]]
                        : [current[0], event.target.value],
                    )
                  }
                >
                  <option value="">Choose a run</option>
                  {runs.map((run) => (
                    <option key={run.run_id} value={run.run_id}>
                      {run.run_id} · {run.technical_state}
                    </option>
                  ))}
                </select>
              </div>
            ))}
          </div>
          <ConfigDiff
            left={compareConfigs[0]}
            right={compareConfigs[1]}
            runs={[
              runs.find((run) => run.run_id === compareIds[0]),
              runs.find((run) => run.run_id === compareIds[1]),
            ]}
          />
        </div>
      )}

      {tab === 'reports' && (
        <div className="workspace-panel" aria-label="Reports and artifacts">
          <div className="workspace-toolbar">
            <div className="run-picker">
              <label htmlFor="report-run-select">Saved run</label>
              <select
                id="report-run-select"
                value={selectedRunId}
                onChange={(event) => setSelectedRunId(event.target.value)}
              >
                <option value="">Choose a run</option>
                {runs.map((run) => (
                  <option key={run.run_id} value={run.run_id}>
                    {run.run_id} · {run.reports.length} report(s)
                  </option>
                ))}
              </select>
            </div>
            <button
              onClick={() => void loadReport()}
              disabled={!selectedRun?.reports.length || reportLoading}
            >
              {reportLoading ? 'Loading…' : 'Preview latest report'}
            </button>
          </div>
          {!selectedRun ? (
            <p className="empty">
              Choose a run to inspect immutable artifacts.
            </p>
          ) : (
            <>
              {figureSpec && <ResearchPlot rows={plotRows} spec={figureSpec} />}
              {reportText && (
                <article className="report-preview">
                  <h3>Regenerated report source</h3>
                  <pre>{reportText}</pre>
                </article>
              )}
              <section className="audit-section">
                <h3>Data, figures, checks and exports</h3>
                <p className="section-intro">
                  Every preview is loaded by cataloged artifact ID. Raw data
                  remains downloadable beside derived and presentation outputs.
                </p>
                <div className="artifact-grid">
                  {reportArtifacts.map((artifact) => (
                    <div key={artifact.id} className="artifact-card">
                      <span>{artifact.kind}</span>
                      <strong>{artifact.path.split('/').at(-1)}</strong>
                      <small>
                        {artifact.media_type} · {artifact.size.toLocaleString()}{' '}
                        bytes
                      </small>
                      <code>{artifact.sha256.slice(0, 16)}…</code>
                      <button
                        className="secondary"
                        onClick={() => void downloadArtifact(artifact)}
                      >
                        Download
                      </button>
                    </div>
                  ))}
                </div>
              </section>
            </>
          )}
        </div>
      )}
    </section>
  );
}
