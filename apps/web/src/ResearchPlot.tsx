interface PlotRow {
  step: number;
  observed: number;
  expected: number;
  absolute_error: number;
}

export const MAX_DISPLAY_POINTS = 2000;

export interface FigureSpec {
  id: string;
  source_datasets: string[];
  transformations: unknown[];
  axes: {
    x: { label: string; unit: string };
    y: { label: string; unit: string };
  };
  normalization: string;
  downsampling: string;
  fit_window: unknown;
  renderer: string;
}

export function parsePlotCsv(source: string): PlotRow[] {
  const lines = source.trim().split(/\r?\n/);
  const header = lines.shift()?.split(',') ?? [];
  const column = (name: string) => header.indexOf(name);
  return lines
    .map((line) => line.split(','))
    .map((values) => ({
      step: Number(values[column('step')]),
      observed: Number(values[column('observed')]),
      expected: Number(values[column('expected')]),
      absolute_error: Number(values[column('absolute_error')]),
    }))
    .filter((row) => Object.values(row).every(Number.isFinite));
}

export function samplePlotRows(
  rows: PlotRow[],
  limit = MAX_DISPLAY_POINTS,
): PlotRow[] {
  if (rows.length <= limit) return rows;
  if (limit < 2) return [rows[0]!];
  const last = rows.length - 1;
  return Array.from({ length: limit }, (_, index) => {
    const sourceIndex = Math.round((index * last) / (limit - 1));
    return rows[sourceIndex]!;
  });
}

export function plotBounds(rows: PlotRow[]) {
  let xMin = Number.POSITIVE_INFINITY;
  let xMax = Number.NEGATIVE_INFINITY;
  let yMin = Number.POSITIVE_INFINITY;
  let yMax = Number.NEGATIVE_INFINITY;
  for (const row of rows) {
    xMin = Math.min(xMin, row.step);
    xMax = Math.max(xMax, row.step);
    yMin = Math.min(yMin, row.observed, row.expected);
    yMax = Math.max(yMax, row.observed, row.expected);
  }
  return { xMin, xMax, yMin, yMax };
}

function points(
  rows: PlotRow[],
  field: 'observed' | 'expected',
  width: number,
  height: number,
  bounds: ReturnType<typeof plotBounds>,
) {
  const { xMin, xMax, yMin, yMax } = bounds;
  return rows
    .map((row) => {
      const x = 48 + ((row.step - xMin) / Math.max(1, xMax - xMin)) * width;
      const y =
        18 +
        (1 - (row[field] - yMin) / Math.max(Number.EPSILON, yMax - yMin)) *
          height;
      return `${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(' ');
}

export function ResearchPlot({
  rows,
  spec,
}: {
  rows: PlotRow[];
  spec: FigureSpec;
}) {
  if (rows.length === 0) return <p className="empty compact">No plot rows.</p>;
  const plotWidth = 690;
  const plotHeight = 250;
  const displayRows = samplePlotRows(rows);
  const bounds = plotBounds(rows);
  return (
    <figure className="research-plot">
      <svg
        viewBox="0 0 780 330"
        role="img"
        aria-labelledby="run-plot-title run-plot-description"
      >
        <title id="run-plot-title">Saved recurrence output</title>
        <desc id="run-plot-description">
          Observed saved output compared with the independently regenerated
          recurrence.
        </desc>
        <line x1="48" y1="268" x2="738" y2="268" className="plot-axis" />
        <line x1="48" y1="18" x2="48" y2="268" className="plot-axis" />
        <polyline
          points={points(
            displayRows,
            'observed',
            plotWidth,
            plotHeight,
            bounds,
          )}
          className="plot-observed"
        />
        <polyline
          points={points(
            displayRows,
            'expected',
            plotWidth,
            plotHeight,
            bounds,
          )}
          className="plot-expected"
        />
        <text x="393" y="310" textAnchor="middle">
          {spec.axes.x.label} ({spec.axes.x.unit})
        </text>
        <text x="15" y="145" textAnchor="middle" transform="rotate(-90 15 145)">
          {spec.axes.y.label} ({spec.axes.y.unit})
        </text>
      </svg>
      <figcaption>
        <span>
          <i className="legend-observed" /> Saved output
        </span>
        <span>
          <i className="legend-expected" /> Independent recurrence
        </span>
      </figcaption>
      <dl className="plot-provenance">
        <div>
          <dt>Saved-data downsampling</dt>
          <dd>{spec.downsampling}</dd>
        </div>
        <div>
          <dt>Browser display</dt>
          <dd>
            {displayRows.length === rows.length
              ? `all ${rows.length} rows`
              : `${displayRows.length} of ${rows.length} rows (deterministic stride; saved data unchanged)`}
          </dd>
        </div>
        <div>
          <dt>Normalization</dt>
          <dd>{spec.normalization}</dd>
        </div>
        <div>
          <dt>Fit window</dt>
          <dd>
            {spec.fit_window === null
              ? 'none'
              : JSON.stringify(spec.fit_window)}
          </dd>
        </div>
        <div>
          <dt>Renderer</dt>
          <dd>{spec.renderer}</dd>
        </div>
      </dl>
    </figure>
  );
}

export type { PlotRow };
