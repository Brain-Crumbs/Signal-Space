import { useEffect, useRef, useState } from 'react';
import { createSample, sampleIds } from '@signal-space/experiments';
import type { SampleId } from '@signal-space/experiments';
import { summarizeSnapshot } from '@signal-space/analysis';
import type { Snapshot } from '@signal-space/model';
import type { RunEvent, WorkerCommand } from '@signal-space/sim';

export function App() {
  const [sample, setSample] = useState<SampleId>('isolated');
  const [status, setStatus] = useState('Ready');
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [snapshot, setSnapshot] = useState<Snapshot>();
  const [error, setError] = useState('');
  const workerRef = useRef<Worker | null>(null);
  const runIdRef = useRef('');
  useEffect(() => () => workerRef.current?.terminate(), []);
  function run() {
    workerRef.current?.terminate();
    const runId = crypto.randomUUID();
    runIdRef.current = runId;
    setRunning(true);
    setStatus('Validating');
    setProgress(0);
    setSnapshot(undefined);
    setError('');
    try {
      const worker = new Worker(new URL('./worker.ts', import.meta.url), {
        type: 'module',
      });
      workerRef.current = worker;
      const fail = (message: string) => {
        setError(message);
        setStatus('Failed');
        setRunning(false);
        worker.terminate();
      };
      worker.onerror = () =>
        fail(
          'The worker could not run. Try again or inspect the browser console.',
        );
      worker.onmessageerror = () =>
        fail('The worker response could not be read.');
      worker.onmessage = ({ data }: MessageEvent<RunEvent>) => {
        if (data.runId !== runIdRef.current) return;
        if (data.type === 'progress') {
          setProgress(data.fraction);
          setStatus(data.stage === 'validating' ? 'Validating' : 'Preparing');
        }
        if (data.type === 'snapshot') setSnapshot(data.snapshot);
        if (data.type === 'failed') fail(data.error.message);
        if (data.type === 'cancelled' || data.type === 'completed') {
          setStatus(data.type === 'completed' ? 'Completed' : 'Cancelled');
          setRunning(false);
          worker.terminate();
        }
      };
      worker.postMessage({
        type: 'run',
        request: { runId, mode: 'inspect', scenario: createSample(sample) },
      } satisfies WorkerCommand);
    } catch (failure) {
      setError(
        failure instanceof Error ? failure.message : 'Could not start worker.',
      );
      setStatus('Failed');
      setRunning(false);
    }
  }
  function cancel() {
    setStatus('Cancelling');
    workerRef.current?.postMessage({
      type: 'cancel',
      runId: runIdRef.current,
    } satisfies WorkerCommand);
  }
  const summary = snapshot ? summarizeSnapshot(snapshot) : undefined;
  return (
    <main>
      <header>
        <p className="eyebrow">PAPER I / LOCAL MATHEMATICS WORKSPACE</p>
        <h1>Signal Space</h1>
        <p>Inspect a clock network’s initial preparation.</p>
      </header>
      <section className="controls" aria-label="Run controls">
        <div>
          <label htmlFor="sample">Sample network</label>
          <select
            id="sample"
            value={sample}
            disabled={running}
            onChange={(e) => {
              setSample(e.target.value as SampleId);
              setSnapshot(undefined);
              setProgress(0);
              setStatus('Ready');
              setError('');
            }}
          >
            {sampleIds.map((id) => (
              <option key={id} value={id}>
                {id === 'isolated' ? 'Isolated clock' : 'Reciprocal pair'}
              </option>
            ))}
          </select>
        </div>
        <button onClick={run} disabled={running}>
          Inspect preparation
        </button>
        <button className="secondary" onClick={cancel} disabled={!running}>
          Cancel
        </button>
      </section>
      <section className="results" aria-label="Preparation result">
        <div className="status">
          <h2>Initial state</h2>
          <span role="status">{status}</span>
        </div>
        <progress aria-label="Run progress" max={1} value={progress} />
        {error && <p role="alert">{error}</p>}
        {snapshot && summary ? (
          <>
            <p>
              {summary.nodeCount} clock{summary.nodeCount === 1 ? '' : 's'} · t
              = {summary.time} s · {summary.pendingPacketCount} pending packets
            </p>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Clock</th>
                    <th>Phase (rad, unwrapped)</th>
                    <th>Frequency (rad s⁻¹)</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(snapshot.nodeState).map(([id, node]) => (
                    <tr key={id}>
                      <th>{id}</th>
                      <td>{node.phi}</td>
                      <td>{node.omega}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <details>
              <summary>Complete initial snapshot</summary>
              <pre>{JSON.stringify(snapshot, null, 2)}</pre>
            </details>
          </>
        ) : (
          <p className="empty">
            Choose a sample and inspect its preparation to see the supplied
            clock state.
          </p>
        )}
      </section>
      <aside>
        <strong>Workspace smoke check</strong>
        <p>
          This checks the supplied preparation at t = 0. Envelope evolution is
          available through the CLI and shared worker API; interactive evolution
          controls follow in T17. The displayed state is simulator truth.
        </p>
      </aside>
    </main>
  );
}
