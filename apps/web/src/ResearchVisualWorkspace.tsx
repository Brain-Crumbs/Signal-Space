import { useEffect, useState } from 'react';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { ScientificChart } from './ScientificChart.js';
import {
  chartPoints,
  loadExploration,
  numeric,
  saveDownload,
  viewExport,
  type Exploration,
  type ChartPoint,
} from './researchVisuals.js';
import type { ResearchApi, RunManifest, RuntimeEvent } from './researchApi.js';

function useExploration(api: ResearchApi, run: RunManifest) {
  const [data, setData] = useState<Exploration>();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const reportId = run.reports.at(-1)?.report_id;
  useEffect(() => {
    let disposed = false;
    setData(undefined);
    setError('');
    setLoading(true);
    loadExploration(api, run)
      .then((value) => {
        if (!disposed) setData(value);
      })
      .catch((e) => {
        if (!disposed) setError(String(e));
      })
      .finally(() => {
        if (!disposed) setLoading(false);
      });
    return () => {
      disposed = true;
    };
    // Immutable report identity controls reload, not manifest polling.
  }, [api, run.run_id, reportId]);
  return { data, error, loading };
}
export function ResearchVisualWorkspace({
  api,
  run,
}: {
  api: ResearchApi;
  run: RunManifest;
}) {
  const { data, error, loading } = useExploration(api, run);
  if (loading) return <p role="status">Loading saved research charts…</p>;
  if (error) return <p role="alert">{error}</p>;
  if (!data)
    return (
      <p>
        Interactive data is not available for this report. Analyze saved output
        and regenerate the report to enable exploration; this does not rerun the
        solver.
      </p>
    );
  return (
    <Explorer
      key={`${run.run_id}:${run.reports.at(-1)?.report_id}`}
      data={data}
      run={run}
    />
  );
}
function Explorer({ data, run }: { data: Exploration; run: RunManifest }) {
  const storageKey = `research-view:${run.run_id}:${run.reports.at(-1)?.report_id}`;
  const [selection, setSelection] = useState<{
    point: string;
    overlay: string;
    sector: string;
  }>(() => {
    try {
      const stored = JSON.parse(localStorage.getItem(storageKey) ?? 'null') as {
        point: string;
        overlay: string;
        sector: string;
      } | null;
      if (
        stored &&
        ['point', 'overlay', 'sector'].every(
          (key) =>
            typeof (stored as unknown as Record<string, unknown>)[key] ===
            'string',
        )
      )
        return stored;
    } catch {
      /* A malformed local preference never changes evidence. */
    }
    return { point: '', overlay: '', sector: 'all' };
  });
  const points = chartPoints(
    data,
    data.views.find((v) => v.id === 'energy')!,
  );
  const point = points.some((p) => p.id === selection.point)
    ? selection.point
    : (points[0]?.id ?? '');
  const update = (value: Partial<typeof selection>) => {
    const next = { ...selection, ...value };
    setSelection(next);
    try {
      localStorage.setItem(storageKey, JSON.stringify(next));
    } catch {
      /* Storage is optional. */
    }
  };
  const criterion = data.selection.points.find((p) => p.point === point);
  const provenance = viewExport(run, data, { ...selection, point });
  return (
    <section className="research-visuals" aria-label="Research visual explorer">
      <header>
        <p className="eyebrow">Saved evidence · stationary solutions</p>
        <h3>Explore the charged branch</h3>
        <p>
          Select a solution to link its shape, perturbations and numerical
          checks. Frequency is a scan parameter, not elapsed time.
        </p>
      </header>
      <div className="visual-summary">
        <span>
          Scientific outcome: <strong>{data.selection.outcome}</strong>
        </span>
        <span>
          Declared coverage:{' '}
          <strong>{data.selection.coverage ? 'complete' : 'incomplete'}</strong>
        </span>
        <span>{points.length} accepted base solutions</span>
      </div>
      <p>
        {data.normalization}.{' '}
        {data.downsampling === 'none'
          ? 'Saved data is not downsampled.'
          : data.downsampling}
      </p>
      <div className="chart-tools">
        <label>
          Selected solution
          <select
            aria-label="Selected solution"
            value={point}
            onChange={(e) => update({ point: e.target.value })}
          >
            {points.map((p) => (
              <option key={p.id} value={p.id}>
                {p.id} · ω={p.row.omega} · {p.group}
              </option>
            ))}
          </select>
        </label>
        <label>
          Overlay profile
          <select
            aria-label="Overlay profile"
            value={selection.overlay}
            onChange={(e) => update({ overlay: e.target.value })}
          >
            <option value="">None</option>
            {points.map((p) => (
              <option key={p.id} value={p.id}>
                {p.id} · ω={p.row.omega}
              </option>
            ))}
          </select>
        </label>
        <label>
          Angular sector
          <select
            aria-label="Angular sector"
            value={selection.sector}
            onChange={(e) => update({ sector: e.target.value })}
          >
            <option value="all">All sectors</option>
            {[
              ...new Set((data.tables.spectra ?? []).map((r) => String(r.ell))),
            ].map((ell) => (
              <option key={ell}>{ell}</option>
            ))}
          </select>
        </label>
        <button
          type="button"
          onClick={() =>
            saveDownload(
              `${run.run_id}-view.json`,
              JSON.stringify(provenance, null, 2),
            )
          }
        >
          Export reproducible view
        </button>
      </div>
      <div className="visual-chart-grid">
        {data.views
          .filter((v) => v.dataset === 'branch')
          .map((v) => (
            <ScientificChart
              key={v.id}
              title={v.title}
              xLabel={`${v.x_label} (${v.x_unit})`}
              yLabel={`${v.y_label} (${v.y_unit})`}
              points={chartPoints(data, v)}
              selected={point}
              onSelect={(id) => update({ point: id })}
              reference={v.reference}
              provenance={provenance}
            />
          ))}
      </div>
      <h3>Solution {point || 'unavailable'}</h3>
      <p>
        Scientific status: <strong>{criterion?.status ?? 'unresolved'}</strong>.
        Solver acceptance alone is not evidence of stability.
      </p>
      <div className="criterion-grid">
        {Object.entries(criterion?.criteria ?? {}).map(([key, value]) => (
          <div key={key}>
            <strong>
              {key}: {value.status}
            </strong>
            <br />
            <small>{value.evidence}</small>
          </div>
        ))}
      </div>
      <div className="visual-chart-grid">
        {data.views
          .filter((v) => v.dataset !== 'branch')
          .map((v) => {
            const rows = point
              ? chartPoints(data, v, point, selection.sector)
              : [];
            if (
              v.dataset === 'profiles' &&
              selection.overlay &&
              selection.overlay !== point
            )
              rows.push(...chartPoints(data, v, selection.overlay));
            return (
              <ScientificChart
                key={`${v.id}:${point}:${selection.overlay}:${selection.sector}`}
                title={v.title}
                xLabel={`${v.x_label} (${v.x_unit})`}
                yLabel={`${v.y_label} (${v.y_unit})`}
                points={rows}
                line={v.line}
                threshold={
                  v.threshold ??
                  (['spectra', 'breakup'].includes(v.dataset) ? 0 : undefined)
                }
                reference={v.reference}
                provenance={provenance}
              />
            );
          })}
      </div>
      <p>
        Spectrum convention: exp(σt). Positive Re σ requires mode-specific
        refinement evidence before classification. Binding bars show three times
        the combined numerical error, not statistical confidence.
      </p>
      <details>
        <summary>Mode matching, residuals and numerical budgets</summary>
        <pre>
          {JSON.stringify(
            Array.isArray(data.spectral_budgets)
              ? data.spectral_budgets.filter((b) => b.point === point)
              : data.spectral_budgets,
            null,
            2,
          )}
        </pre>
      </details>
      <details>
        <summary>Failed points, pending tasks and coverage</summary>
        <pre>{JSON.stringify(data.failures, null, 2)}</pre>
        <pre>
          {JSON.stringify(
            data.tables.branch?.filter((r) => r.status !== 'accepted'),
            null,
            2,
          )}
        </pre>
      </details>
      <ul>
        {data.selection.limitations.map((s) => (
          <li key={s}>{s}</li>
        ))}
      </ul>
      <small>
        Run {run.run_id} · Analysis {run.reports.at(-1)?.analysis_id} · Report{' '}
        {run.reports.at(-1)?.report_id}
      </small>
    </section>
  );
}

export function LiveResearchProgress({ events }: { events: RuntimeEvent[] }) {
  const completed = events.filter((e) => e.type === 'point-completed');
  if (!completed.length) return null;
  const latest = completed.at(-1)!;
  const points: ChartPoint[] = completed.flatMap((e) =>
    numeric(e.payload.omega)
      ? [
          {
            id: e.cursor,
            x: e.payload.omega,
            y: Number(e.payload.step),
            group: `${e.payload.lane ?? 'base'} / ${e.payload.kind} / ${e.payload.status}`,
            label: `${e.attempt_id}: ${JSON.stringify(e.payload)}`,
            row: { attempt: e.attempt_id, status: String(e.payload.status) },
          },
        ]
      : [],
  );
  const branch: ChartPoint[] = completed.flatMap((e) => {
    const o = e.payload.observables as Record<string, unknown> | undefined;
    return e.payload.lane === 'base' &&
      ['seed', 'continue'].includes(String(e.payload.kind)) &&
      o &&
      numeric(o.Q) &&
      numeric(o.E)
      ? [
          {
            id: e.cursor,
            x: o.Q,
            y: o.E,
            group: `${e.attempt_id} / ${e.payload.branch}`,
            label: JSON.stringify(e.payload),
            row: { point: String(e.payload.point_id), attempt: e.attempt_id },
          },
        ]
      : [];
  });
  return (
    <section aria-label="Provisional run progress" className="research-visuals">
      <h3>Scan progress</h3>
      <p>
        Provisional solver output · not independently analyzed.{' '}
        {completed.length} point events; latest pending task count:{' '}
        {String(latest.payload.pending)}. Adaptive continuation can add tasks.
      </p>
      <div className="visual-chart-grid">
        <ScientificChart
          title="Completed and failed tasks"
          xLabel="ω (m)"
          yLabel="Task index (per attempt)"
          points={points}
          provenance={{ events }}
        />
        {branch.length > 0 && (
          <ScientificChart
            title="Provisional energy and charge"
            xLabel="Q (dimensionless)"
            yLabel="E (m)"
            points={branch}
            provenance={{ events }}
          />
        )}
      </div>
    </section>
  );
}

export function SavedFigureGallery({
  api,
  run,
}: {
  api: ResearchApi;
  run: RunManifest;
}) {
  const [images, setImages] = useState<
    Array<{ path: string; url: string; hash: string }>
  >([]);
  const [error, setError] = useState('');
  const report = run.reports.at(-1);
  useEffect(() => {
    let disposed = false;
    const urls: string[] = [];
    setImages([]);
    setError('');
    const figures = run.artifacts.filter(
      (a) =>
        a.kind === 'figure' &&
        a.path.startsWith(`${report?.path}/`) &&
        a.media_type === 'image/png',
    );
    Promise.all(
      figures.map(async (a) => {
        const blob = await (await api.artifact(run.run_id, a.id)).blob();
        if (disposed) return undefined;
        const url = URL.createObjectURL(blob);
        urls.push(url);
        return { path: a.path, url, hash: a.sha256 };
      }),
    )
      .then((values) => {
        if (!disposed)
          setImages(values.filter((v): v is NonNullable<typeof v> => !!v));
      })
      .catch((e) => {
        if (!disposed) setError(String(e));
      });
    return () => {
      disposed = true;
      urls.forEach((url) => URL.revokeObjectURL(url));
    };
  }, [api, run.run_id, report?.report_id]);
  return (
    <section aria-label="Saved figure gallery">
      <h3>Saved figures</h3>
      {error && <p role="alert">{error}</p>}
      <div className="visual-chart-grid">
        {images.map((img) => (
          <figure key={img.path}>
            <img
              src={img.url}
              alt={
                img.path.split('/').at(-1)?.replace('.png', '') ??
                'Saved figure'
              }
            />
            <figcaption>
              {img.path.split('/').at(-1)} · SHA-256 {img.hash.slice(0, 16)}…
            </figcaption>
          </figure>
        ))}
      </div>
    </section>
  );
}
export function RenderedResearchReport({ source }: { source: string }) {
  return (
    <Markdown
      remarkPlugins={[remarkGfm, remarkMath]}
      rehypePlugins={[rehypeKatex]}
      components={{
        img: ({ alt }) => <em>{alt} — see saved figure gallery.</em>,
        a: ({ children, href }) =>
          href?.startsWith('https://') ? (
            <a href={href} target="_blank" rel="noreferrer">
              {children}
            </a>
          ) : (
            <span>{children}</span>
          ),
      }}
    >
      {source}
    </Markdown>
  );
}
export function ResearchComparison({
  api,
  left,
  right,
}: {
  api: ResearchApi;
  left: RunManifest;
  right: RunManifest;
}) {
  const a = useExploration(api, left);
  const b = useExploration(api, right);
  const [leftPoint, setLeftPoint] = useState('');
  const [rightPoint, setRightPoint] = useState('');
  if (a.loading || b.loading) return <p>Loading comparison charts…</p>;
  if (a.error || b.error) return <p role="alert">{a.error || b.error}</p>;
  if (!a.data || !b.data)
    return (
      <p>
        Generate an interactive report for both runs to compare saved branches
        and profiles.
      </p>
    );
  const choices = (d: Exploration) =>
    chartPoints(
      d,
      d.views.find((v) => v.id === 'energy')!,
    );
  const selectedA = choices(a.data).some((p) => p.id === leftPoint)
    ? leftPoint
    : choices(a.data)[0]?.id;
  const selectedB = choices(b.data).some((p) => p.id === rightPoint)
    ? rightPoint
    : choices(b.data)[0]?.id;
  const provenance = {
    left: viewExport(left, a.data, { point: selectedA }),
    right: viewExport(right, b.data, { point: selectedB }),
  };
  return (
    <section aria-label="Visual run comparison">
      <h3>Compare saved evidence</h3>
      <p>
        Left: {left.run_id} · Right: {right.run_id}. Curves are separate
        measurements; no aggregate is inferred.
      </p>
      <div className="chart-tools">
        {[
          { name: 'Left', data: a.data, value: selectedA, set: setLeftPoint },
          { name: 'Right', data: b.data, value: selectedB, set: setRightPoint },
        ].map((p) => (
          <label key={p.name}>
            {p.name} profile
            <select
              aria-label={`${p.name} profile`}
              value={p.value ?? ''}
              onChange={(e) => p.set(e.target.value)}
            >
              {choices(p.data).map((c) => (
                <option key={c.id} value={c.id}>
                  {c.id} · ω={c.row.omega}
                </option>
              ))}
            </select>
          </label>
        ))}
        <button
          onClick={() =>
            saveDownload(
              'research-comparison.json',
              JSON.stringify(provenance, null, 2),
            )
          }
        >
          Export comparison
        </button>
      </div>
      <div className="visual-chart-grid">
        {a.data.views
          .filter((v) => v.dataset === 'branch' || v.id === 'f')
          .map((v) => {
            const other = b.data!.views.find((w) => w.id === v.id);
            if (!other) return null;
            const rows = [
              ...chartPoints(
                a.data!,
                v,
                v.id === 'f' ? selectedA : undefined,
              ).map((p) => ({
                ...p,
                id: `left:${p.id}`,
                parent: p.parent ? `left:${p.parent}` : undefined,
                group: `Left / ${p.group}`,
              })),
              ...chartPoints(
                b.data!,
                other,
                v.id === 'f' ? selectedB : undefined,
              ).map((p) => ({
                ...p,
                id: `right:${p.id}`,
                parent: p.parent ? `right:${p.parent}` : undefined,
                group: `Right / ${p.group}`,
              })),
            ];
            return (
              <ScientificChart
                key={v.id}
                title={`Compare ${v.title}`}
                xLabel={`${v.x_label} (${v.x_unit})`}
                yLabel={`${v.y_label} (${v.y_unit})`}
                points={rows}
                line={v.line}
                reference={v.reference}
                provenance={provenance}
              />
            );
          })}
      </div>
    </section>
  );
}
