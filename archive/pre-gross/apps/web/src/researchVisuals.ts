import type { ResearchApi, RunManifest } from './researchApi.js';

export type Datum = Record<string, string | number | boolean | null>;
export interface ViewSpec {
  id: string;
  title: string;
  dataset: string;
  x: string;
  y: string;
  x_label: string;
  y_label: string;
  x_unit: string;
  y_unit: string;
  point_key?: string;
  group?: string;
  parent_key?: string;
  line?: boolean;
  filters?: Record<string, string | string[]>;
  error?: string;
  error_multiplier?: number;
  threshold?: number;
  reference?: 'identity';
}
export interface Exploration {
  schema_version: 'research-exploration-v1';
  tables: Record<string, Datum[]>;
  views: ViewSpec[];
  selection: {
    outcome: string;
    coverage: boolean;
    points: Array<{
      point: string;
      status: string;
      criteria: Record<string, { status: string; evidence: string }>;
    }>;
    limitations: string[];
  };
  spectral_budgets: unknown;
  failures: unknown;
  sources: string[];
  normalization: string;
  downsampling: string;
  renderer: string;
}
export interface ChartPoint {
  id: string;
  x: number;
  y: number;
  group: string;
  label: string;
  error?: number;
  parent?: string | undefined;
  row: Datum;
}
export function numeric(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value);
}
export function parseExploration(value: unknown): Exploration {
  if (!value || typeof value !== 'object')
    throw new Error('Invalid exploration data.');
  const data = value as Exploration;
  if (
    data.schema_version !== 'research-exploration-v1' ||
    !data.tables ||
    !Array.isArray(data.views) ||
    !data.selection ||
    !Array.isArray(data.selection.points) ||
    !Array.isArray(data.sources) ||
    !Array.isArray(data.selection.limitations) ||
    data.selection.limitations.some((s) => typeof s !== 'string') ||
    typeof data.selection.outcome !== 'string' ||
    typeof data.selection.coverage !== 'boolean' ||
    ['normalization', 'downsampling', 'renderer'].some(
      (key) =>
        typeof (data as unknown as Record<string, unknown>)[key] !== 'string',
    )
  )
    throw new Error('Unsupported exploration contract. Regenerate the report.');
  for (const rows of Object.values(data.tables)) {
    if (
      !Array.isArray(rows) ||
      rows.some(
        (row) =>
          !row ||
          typeof row !== 'object' ||
          Object.values(row).some(
            (v) =>
              (v !== null &&
                !['string', 'number', 'boolean'].includes(typeof v)) ||
              (typeof v === 'number' && !Number.isFinite(v)),
          ),
      )
    )
      throw new Error('Invalid or non-finite exploration row.');
  }
  for (const point of data.selection.points) {
    if (
      !point ||
      typeof point.point !== 'string' ||
      typeof point.status !== 'string' ||
      !point.criteria ||
      Object.values(point.criteria).some(
        (c) =>
          !c || typeof c.status !== 'string' || typeof c.evidence !== 'string',
      )
    )
      throw new Error('Invalid criterion evidence.');
  }
  if (!data.views.some((v) => v?.id === 'energy' && v.dataset === 'branch'))
    throw new Error('Missing E01 energy view mapping.');
  for (const view of data.views) {
    if (
      !view ||
      !data.tables[view.dataset] ||
      (view.error_multiplier !== undefined &&
        (!numeric(view.error_multiplier) || view.error_multiplier < 0)) ||
      (view.threshold !== undefined && !numeric(view.threshold)) ||
      (view.filters !== undefined &&
        (!view.filters ||
          typeof view.filters !== 'object' ||
          Object.values(view.filters).some(
            (f) =>
              typeof f !== 'string' &&
              !(Array.isArray(f) && f.every((v) => typeof v === 'string')),
          ))) ||
      ['id', 'title', 'x', 'y', 'x_label', 'y_label', 'x_unit', 'y_unit'].some(
        (key) =>
          typeof (view as unknown as Record<string, unknown>)[key] !== 'string',
      )
    )
      throw new Error('Invalid view mapping.');
  }
  return data;
}
export function chartPoints(
  data: Exploration,
  view: ViewSpec,
  selected?: string,
  sector = 'all',
): ChartPoint[] {
  return (data.tables[view.dataset] ?? []).flatMap((row, index) => {
    if (
      Object.entries(view.filters ?? {}).some(
        ([key, value]) =>
          !(Array.isArray(value)
            ? value.includes(String(row[key]))
            : row[key] === value),
      )
    )
      return [];
    if (selected && view.point_key && String(row[view.point_key]) !== selected)
      return [];
    if (
      view.dataset === 'spectra' &&
      sector !== 'all' &&
      String(row.ell) !== sector
    )
      return [];
    const x = view.x === '$index' ? index : row[view.x];
    const y = row[view.y];
    if (!numeric(x) || !numeric(y)) return [];
    const id = String(row[view.point_key ?? 'id'] ?? index);
    const error = view.error ? row[view.error] : undefined;
    return [
      {
        id,
        x,
        y,
        group: String(row[view.group ?? ''] ?? view.title),
        label: Object.entries(row)
          .map(([k, v]) => `${k}: ${v ?? 'unavailable'}`)
          .join('; '),
        row,
        ...(numeric(error)
          ? { error: Math.abs(error) * (view.error_multiplier ?? 1) }
          : {}),
        ...(view.parent_key && row[view.parent_key]
          ? { parent: String(row[view.parent_key]) }
          : {}),
      },
    ];
  });
}
export async function loadExploration(
  api: ResearchApi,
  run: RunManifest,
): Promise<Exploration | undefined> {
  const report = run.reports.at(-1);
  const artifact = run.artifacts.find(
    (a) => a.path === `${report?.path}/plot-data/exploration.json`,
  );
  if (!artifact) return undefined;
  return parseExploration(
    await (await api.artifact(run.run_id, artifact.id)).json(),
  );
}
export function saveDownload(
  name: string,
  value: string,
  type = 'application/json',
) {
  const url = URL.createObjectURL(new Blob([value], { type }));
  const link = document.createElement('a');
  link.href = url;
  link.download = name;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
export function viewExport(
  run: RunManifest,
  data: Exploration,
  selection: unknown,
) {
  const report = run.reports.at(-1);
  return {
    schema_version: 'research-view-export-v1',
    run_id: run.run_id,
    config_hash: run.config_hash,
    code_identity: run.code_identity,
    report_id: report?.report_id,
    analysis_id: report?.analysis_id,
    selection,
    artifacts: run.artifacts.filter((a) =>
      a.path.startsWith(`${report?.path}/`),
    ),
    data,
  };
}
