import { useId, useRef, useState } from 'react';
import { saveDownload, type ChartPoint } from './researchVisuals.js';

const colors = [
  '#38bdf8',
  '#fbbf24',
  '#c084fc',
  '#34d399',
  '#fb7185',
  '#a3e635',
];
export function ScientificChart({
  title,
  xLabel,
  yLabel,
  points,
  line = false,
  selected,
  onSelect,
  threshold,
  provenance,
  reference,
}: {
  title: string;
  xLabel: string;
  yLabel: string;
  points: ChartPoint[];
  line?: boolean | undefined;
  selected?: string;
  onSelect?: (id: string) => void;
  threshold?: number | undefined;
  provenance?: unknown;
  reference?: 'identity' | undefined;
}) {
  const id = useId();
  const svg = useRef<SVGSVGElement>(null);
  const [range, setRange] = useState<[string, string]>(['', '']);
  const [page, setPage] = useState(0);
  const visible = points.filter(
    (p) =>
      (range[0] === '' || p.x >= Number(range[0])) &&
      (range[1] === '' || p.x <= Number(range[1])),
  );
  let xmin = Infinity,
    xmax = -Infinity,
    ymin = Infinity,
    ymax = -Infinity;
  for (const p of visible) {
    xmin = Math.min(xmin, p.x);
    xmax = Math.max(xmax, p.x);
    ymin = Math.min(ymin, p.y - (p.error ?? 0));
    ymax = Math.max(ymax, p.y + (p.error ?? 0));
  }
  if (!visible.length) {
    xmin = 0;
    xmax = 1;
    ymin = 0;
    ymax = 1;
  }
  if (threshold !== undefined) {
    ymin = Math.min(ymin, threshold);
    ymax = Math.max(ymax, threshold);
  }
  if (xmin === xmax) {
    xmin -= 0.5;
    xmax += 0.5;
  }
  if (ymin === ymax) {
    ymin -= 0.5;
    ymax += 0.5;
  }
  if (reference === 'identity') {
    ymin = Math.min(ymin, xmin);
    ymax = Math.max(ymax, xmax);
  }
  const pad = (ymax - ymin) * 0.08;
  ymin -= pad;
  ymax += pad;
  const x = (v: number) => 85 + ((v - xmin) / (xmax - xmin)) * 620;
  const y = (v: number) => 285 - ((v - ymin) / (ymax - ymin)) * 250;
  const groups = [...new Set(points.map((p) => p.group))];
  const color = (p: ChartPoint) =>
    colors[groups.indexOf(p.group) % colors.length];
  // Exact data remains in exports; large scatter views use a declared display cap.
  const stride = Math.max(1, Math.ceil(visible.length / 4000));
  const display = visible.filter(
    (p, i) => i % stride === 0 || p.id === selected,
  );
  const byId = new Map(visible.map((p) => [p.id, p]));
  const ticks = Array.from({ length: 5 }, (_, i) => i / 4);
  const fmt = (n: number) => Number(n.toPrecision(4)).toString();
  const safePage = Math.min(
    page,
    Math.max(0, Math.ceil(visible.length / 25) - 1),
  );
  return (
    <figure className="scientific-chart">
      <h4>{title}</h4>
      <div className="chart-tools">
        <label>
          X minimum
          <input
            aria-label={`${title} X minimum`}
            type="number"
            value={range[0]}
            onChange={(e) => setRange([e.target.value, range[1]])}
          />
        </label>
        <label>
          X maximum
          <input
            aria-label={`${title} X maximum`}
            type="number"
            value={range[1]}
            onChange={(e) => setRange([range[0], e.target.value])}
          />
        </label>
        <button type="button" onClick={() => setRange(['', ''])}>
          Reset zoom
        </button>
        <button
          type="button"
          onClick={() => {
            if (!svg.current) return;
            const copy = svg.current.cloneNode(true) as SVGSVGElement;
            const metadata = document.createElementNS(
              'http://www.w3.org/2000/svg',
              'metadata',
            );
            metadata.textContent = JSON.stringify({
              renderer: 'signal-space-svg-v1',
              title,
              xLabel,
              yLabel,
              range,
              display_stride: stride,
              provenance,
              points,
            });
            copy.prepend(metadata);
            saveDownload(
              `${title.replace(/[^a-z0-9]/gi, '-')}.svg`,
              new XMLSerializer().serializeToString(copy),
              'image/svg+xml',
            );
          }}
        >
          Export SVG
        </button>
      </div>
      <svg
        ref={svg}
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 760 350"
        role="img"
        aria-labelledby={id}
      >
        <title id={id}>{title}</title>
        <rect width="760" height="350" fill="#101d30" />
        {ticks.map((t) => (
          <g key={t} fill="#dbeafe" fontSize="11">
            <line
              x1="85"
              x2="705"
              y1={y(ymin + t * (ymax - ymin))}
              y2={y(ymin + t * (ymax - ymin))}
              stroke="#334155"
            />
            <text x="78" y={y(ymin + t * (ymax - ymin)) + 4} textAnchor="end">
              {fmt(ymin + t * (ymax - ymin))}
            </text>
            <text x={x(xmin + t * (xmax - xmin))} y="305" textAnchor="middle">
              {fmt(xmin + t * (xmax - xmin))}
            </text>
          </g>
        ))}
        {threshold !== undefined && (
          <line
            x1="85"
            x2="705"
            y1={y(threshold)}
            y2={y(threshold)}
            stroke="#f8fafc"
            strokeDasharray="5 4"
          />
        )}
        {reference === 'identity' && (
          <g>
            <line
              x1={x(xmin)}
              x2={x(xmax)}
              y1={y(xmin)}
              y2={y(xmax)}
              stroke="#f8fafc"
              strokeDasharray="5 4"
            />
            <text x="90" y="27" fill="#f8fafc" fontSize="11">
              Free charge E = m|Q| (m=1, Q&gt;0)
            </text>
          </g>
        )}
        {/* Parent connections stay exact; a display cap never creates new edges. */}
        {stride === 1 &&
          display.map((p, i) => {
            const previous = p.parent
              ? byId.get(p.parent)
              : line && i > 0 && display[i - 1]?.group === p.group
                ? display[i - 1]
                : undefined;
            return (
              previous && (
                <line
                  key={`edge-${i}`}
                  x1={x(previous.x)}
                  y1={y(previous.y)}
                  x2={x(p.x)}
                  y2={y(p.y)}
                  stroke={color(p)}
                  opacity=".6"
                />
              )
            );
          })}
        {display.map((p, i) => (
          <g key={i}>
            {p.error !== undefined && (
              <path
                d={`M ${x(p.x)} ${y(p.y - p.error)} V ${y(p.y + p.error)} M ${x(p.x) - 4} ${y(p.y - p.error)} h 8 M ${x(p.x) - 4} ${y(p.y + p.error)} h 8`}
                stroke={color(p)}
                fill="none"
              />
            )}
            <circle
              cx={x(p.x)}
              cy={y(p.y)}
              r={p.id === selected ? 5 : 3}
              fill={color(p)}
              stroke={p.id === selected ? 'white' : 'none'}
              onClick={() => onSelect?.(p.id)}
              style={{ cursor: onSelect ? 'pointer' : 'default' }}
            >
              <title>{p.label}</title>
            </circle>
          </g>
        ))}
        <text x="395" y="334" fill="#dbeafe" textAnchor="middle" fontSize="12">
          {xLabel}
        </text>
        <text
          transform="translate(17 160) rotate(-90)"
          fill="#dbeafe"
          textAnchor="middle"
          fontSize="12"
        >
          {yLabel}
        </text>
      </svg>
      {!visible.length && (
        <p>No data in this range. Missing evidence remains unresolved.</p>
      )}
      <figcaption>
        {groups.map((g, i) => (
          <span key={g} style={{ color: colors[i % colors.length] }}>
            ● {g}{' '}
          </span>
        ))}
        <p>
          {visible.length} points in range.{' '}
          {stride > 1
            ? `Display stride ${stride}; connecting lines omitted; exact rows retained below and in exports.`
            : 'All points displayed.'}
        </p>
      </figcaption>
      <details>
        <summary>Inspect exact chart data</summary>
        <div className="chart-table">
          <table>
            <thead>
              <tr>
                <th>Selection</th>
                <th>{xLabel}</th>
                <th>{yLabel}</th>
                <th>Evidence</th>
              </tr>
            </thead>
            <tbody>
              {visible.slice(safePage * 25, safePage * 25 + 25).map((p, i) => (
                <tr key={i}>
                  <td>
                    {onSelect ? (
                      <button type="button" onClick={() => onSelect(p.id)}>
                        {p.id}
                      </button>
                    ) : (
                      p.id
                    )}
                  </td>
                  <td>{p.x}</td>
                  <td>
                    {p.y}
                    {p.error !== undefined ? ` ± ${p.error}` : ''}
                  </td>
                  <td>{p.label}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <button
          type="button"
          disabled={safePage === 0}
          onClick={() => setPage(safePage - 1)}
        >
          Previous rows
        </button>{' '}
        <span>Page {safePage + 1}</span>{' '}
        <button
          type="button"
          disabled={(safePage + 1) * 25 >= visible.length}
          onClick={() => setPage(safePage + 1)}
        >
          Next rows
        </button>
      </details>
    </figure>
  );
}
