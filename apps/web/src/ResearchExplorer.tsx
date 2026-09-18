import { useMemo, useState } from 'react';
import catalog from '../../../research/catalog.json';

type CatalogEntry = (typeof catalog.entries)[number] & { related?: string[] };

const rawDocuments = {
  ...import.meta.glob('../../../research/papers/*.md', {
    eager: true,
    query: '?raw',
    import: 'default',
  }),
  ...import.meta.glob('../../../research/milestones/*.md', {
    eager: true,
    query: '?raw',
    import: 'default',
  }),
  ...import.meta.glob('../../../research/source/*/README.md', {
    eager: true,
    query: '?raw',
    import: 'default',
  }),
  ...import.meta.glob('../../../research/research-coach-persona.md', {
    eager: true,
    query: '?raw',
    import: 'default',
  }),
  ...import.meta.glob('../../../docs/research/*.md', {
    eager: true,
    query: '?raw',
    import: 'default',
  }),
} as Record<string, string>;

const assetUrls = {
  ...import.meta.glob('../../../research/papers/*.md', {
    eager: true,
    query: '?url',
    import: 'default',
  }),
  ...import.meta.glob('../../../research/milestones/*.md', {
    eager: true,
    query: '?url',
    import: 'default',
  }),
  ...import.meta.glob('../../../research/source/*/README.md', {
    eager: true,
    query: '?url',
    import: 'default',
  }),
  ...import.meta.glob('../../../research/research-coach-persona.md', {
    eager: true,
    query: '?url',
    import: 'default',
  }),
  ...import.meta.glob('../../../research/figures/*.png', {
    eager: true,
    query: '?url',
    import: 'default',
  }),
  ...import.meta.glob('../../../docs/research/*.md', {
    eager: true,
    query: '?url',
    import: 'default',
  }),
} as Record<string, string>;

function assetKey(path: string) {
  return `../../../${path}`;
}

function searchable(entry: CatalogEntry) {
  return [
    entry.title,
    entry.kind,
    entry.status,
    entry.summary,
    entry.tags.join(' '),
  ]
    .join(' ')
    .toLocaleLowerCase();
}

export function ResearchExplorer() {
  const [query, setQuery] = useState('');
  const [kind, setKind] = useState('all');
  const [selectedId, setSelectedId] = useState('knot-grid');
  const kinds = useMemo(
    () => [...new Set(catalog.entries.map((entry) => entry.kind))].sort(),
    [],
  );
  const results = useMemo(() => {
    const normalized = query.trim().toLocaleLowerCase();
    return catalog.entries.filter(
      (entry) =>
        (kind === 'all' || entry.kind === kind) &&
        (!normalized || searchable(entry).includes(normalized)),
    );
  }, [kind, query]);
  const selected =
    catalog.entries.find((entry) => entry.id === selectedId) ?? results[0];
  const selectedKey = selected ? assetKey(selected.path) : '';
  const document = selected ? rawDocuments[selectedKey] : undefined;
  const assetUrl = selected ? assetUrls[selectedKey] : undefined;
  const isImage = selected?.path.endsWith('.png');
  const related = (selected?.related ?? [])
    .map((id) => catalog.entries.find((entry) => entry.id === id))
    .filter((entry): entry is CatalogEntry => Boolean(entry));

  return (
    <section className="research-shell" aria-labelledby="research-heading">
      <div className="section-heading">
        <div>
          <p className="eyebrow">RESEARCH COLLECTION / {catalog.updated}</p>
          <h2 id="research-heading">Trace theory to evidence</h2>
        </div>
        <span className="record-count">{catalog.entries.length} records</span>
      </div>
      <p className="section-intro">
        Search active plans, theory papers, executed milestones, figures, and
        curated source bundles. Status labels distinguish proposals from
        numerical results.
      </p>
      <div className="library-controls" role="search">
        <div className="search-field">
          <label htmlFor="research-search">Search collection</label>
          <input
            id="research-search"
            type="search"
            placeholder="Try winding, radiation, or provenance"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </div>
        <div>
          <label htmlFor="research-kind">Material type</label>
          <select
            id="research-kind"
            value={kind}
            onChange={(event) => setKind(event.target.value)}
          >
            <option value="all">All types</option>
            {kinds.map((value) => (
              <option key={value} value={value}>
                {value[0]?.toLocaleUpperCase()}
                {value.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="library-layout">
        <div className="catalog-list" aria-label="Research materials">
          <p className="result-count" aria-live="polite">
            {results.length} result{results.length === 1 ? '' : 's'}
          </p>
          {results.map((entry) => (
            <button
              className={`catalog-card${selected?.id === entry.id ? ' selected' : ''}`}
              key={entry.id}
              id={`catalog-${entry.id}`}
              onClick={() => setSelectedId(entry.id)}
              aria-pressed={selected?.id === entry.id}
            >
              <span className="catalog-meta">
                {entry.kind} · {entry.date}
              </span>
              <strong>{entry.title}</strong>
              <span>{entry.summary}</span>
            </button>
          ))}
          {results.length === 0 && (
            <p className="empty compact">No research materials match.</p>
          )}
        </div>
        <article className="catalog-detail" aria-live="polite">
          {selected ? (
            <>
              <div className="detail-meta">
                <span className="status-chip">{selected.status}</span>
                <span>{selected.date}</span>
              </div>
              <h3>{selected.title}</h3>
              <p>{selected.summary}</p>
              <div className="tag-list" aria-label="Tags">
                {selected.tags.map((tag) => (
                  <span key={tag}>{tag}</span>
                ))}
              </div>
              {related.length > 0 && (
                <div className="related-materials">
                  <strong>Related evidence</strong>
                  {related.map((entry) => (
                    <button
                      key={entry.id}
                      className="relation-link"
                      onClick={() => setSelectedId(entry.id)}
                    >
                      {entry.kind} · {entry.title}
                    </button>
                  ))}
                </div>
              )}
              {assetUrl && (
                <a
                  className="open-file"
                  href={assetUrl}
                  target="_blank"
                  rel="noreferrer"
                >
                  Open source file
                </a>
              )}
              {isImage && assetUrl ? (
                <img
                  className="figure-preview"
                  src={assetUrl}
                  alt={`${selected.title} preview`}
                />
              ) : document ? (
                <DocumentPreview source={document} />
              ) : (
                <p className="preview-unavailable">
                  Preview unavailable. Open the source file to inspect it.
                </p>
              )}
            </>
          ) : (
            <p className="empty">Select a research material.</p>
          )}
        </article>
      </div>
    </section>
  );
}

function DocumentPreview({ source }: { source: string }) {
  const blocks = source.split(/\n{2,}/).slice(0, 80);
  return (
    <div className="document-preview rendered-document">
      {blocks.map((block, index) => {
        const text = block.trim();
        if (!text) return null;
        const heading = /^(#{1,4})\s+(.+)$/s.exec(text);
        if (heading) {
          const value = heading[2] ?? '';
          if (heading[1]?.length === 1) return <h3 key={index}>{value}</h3>;
          return <h4 key={index}>{value}</h4>;
        }
        if (text.startsWith('$$') && text.endsWith('$$'))
          return (
            <pre className="equation-block" key={index}>
              {text.slice(2, -2).trim()}
            </pre>
          );
        if (text.split('\n').every((line) => /^[-*]\s/.test(line)))
          return (
            <ul key={index}>
              {text.split('\n').map((line) => (
                <li key={line}>{line.replace(/^[-*]\s/, '')}</li>
              ))}
            </ul>
          );
        return <p key={index}>{text.replaceAll(/\*\*|__/g, '')}</p>;
      })}
      {blocks.length >= 80 && (
        <p>
          Preview truncated. Open the source file for the complete document.
        </p>
      )}
    </div>
  );
}
