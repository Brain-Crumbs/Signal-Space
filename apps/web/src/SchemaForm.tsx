import type { JsonSchema, ResearchConfig } from './researchApi.js';

interface SchemaFormProps {
  schema: JsonSchema;
  value: ResearchConfig;
  disabled: boolean;
  onChange: (value: ResearchConfig) => void;
}

function title(value: string) {
  return value
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function inputType(schema: JsonSchema) {
  const types = Array.isArray(schema.type) ? schema.type : [schema.type];
  if (types.includes('integer') || types.includes('number')) return 'number';
  return 'text';
}

function unitFor(path: string, config: ResearchConfig) {
  const name = path.split('.').at(-1) ?? '';
  if (name === 'steps' || name === 'checkpoint_interval')
    return config.units.step;
  if (['initial_value', 'gain', 'forcing', 'max_abs_error'].includes(name))
    return config.units.value;
  if (name.endsWith('_seconds')) return 's';
  if (name.endsWith('_mb')) return 'MB';
  if (name === 'step_delay_ms') return 'ms';
  return '';
}

function setAtPath(
  source: ResearchConfig,
  path: string[],
  value: unknown,
): ResearchConfig {
  const copy = structuredClone(source) as unknown as Record<string, unknown>;
  let target = copy;
  path.slice(0, -1).forEach((part) => {
    target = target[part] as Record<string, unknown>;
  });
  const final = path.at(-1);
  if (final) target[final] = value;
  return copy as unknown as ResearchConfig;
}

function fieldValue(source: ResearchConfig, path: string[]) {
  let value: unknown = source;
  path.forEach((part) => {
    value = (value as Record<string, unknown>)[part];
  });
  return value;
}

function Field({
  name,
  path,
  schema,
  value,
  disabled,
  config,
  onChange,
}: {
  name: string;
  path: string[];
  schema: JsonSchema;
  value: unknown;
  disabled: boolean;
  config: ResearchConfig;
  onChange: (value: ResearchConfig) => void;
}) {
  const id = `config-${path.join('-')}`;
  const types = Array.isArray(schema.type) ? schema.type : [schema.type];
  const unit = unitFor(path.join('.'), config);
  const constraint = [
    schema.minimum === undefined ? '' : `min ${schema.minimum}`,
    schema.maximum === undefined ? '' : `max ${schema.maximum}`,
  ]
    .filter(Boolean)
    .join(' · ');

  if (types.includes('boolean')) {
    return (
      <label className="checkbox-field" htmlFor={id}>
        <input
          id={id}
          type="checkbox"
          checked={Boolean(value)}
          disabled={disabled}
          onChange={(event) =>
            onChange(setAtPath(config, path, event.target.checked))
          }
        />
        <span>{title(name)}</span>
      </label>
    );
  }

  return (
    <div className="schema-field">
      <label htmlFor={id}>
        {title(name)} {unit && <span className="unit">({unit})</span>}
      </label>
      <input
        id={id}
        type={inputType(schema)}
        value={value === null || value === undefined ? '' : String(value)}
        disabled={disabled || schema.const !== undefined}
        min={schema.minimum}
        max={schema.maximum}
        step={types.includes('integer') ? 1 : 'any'}
        required={!types.includes('null')}
        onChange={(event) => {
          let next: unknown = event.target.value;
          if (event.target.value === '' && types.includes('null')) next = null;
          else if (inputType(schema) === 'number')
            next = Number(event.target.value);
          onChange(setAtPath(config, path, next));
        }}
      />
      {constraint && <small>{constraint}</small>}
    </div>
  );
}

export function SchemaForm({
  schema,
  value,
  disabled,
  onChange,
}: SchemaFormProps) {
  const top = schema.properties ?? {};
  const sections = Object.entries(top).filter(
    ([name, child]) => child.properties && !['units'].includes(name),
  );
  return (
    <div className="schema-form">
      <div className="contract-banner">
        <div>
          <span>Active experiment</span>
          <strong>{value.experiment_id}</strong>
        </div>
        <div>
          <span>Model / action</span>
          <strong>{value.model_id}</strong>
        </div>
        <div>
          <span>Schema</span>
          <strong>{value.schema_version}</strong>
        </div>
      </div>
      {sections.map(([sectionName, section]) => (
        <fieldset key={sectionName}>
          <legend>{title(sectionName)}</legend>
          <div className="field-grid">
            {Object.entries(section.properties ?? {}).map(
              ([name, fieldSchema]) => (
                <Field
                  key={name}
                  name={name}
                  path={[sectionName, name]}
                  schema={fieldSchema}
                  value={fieldValue(value, [sectionName, name])}
                  disabled={disabled}
                  config={value}
                  onChange={onChange}
                />
              ),
            )}
          </div>
        </fieldset>
      ))}
      <fieldset>
        <legend>Declared units</legend>
        <dl className="compact-definition-list">
          {Object.entries(value.units).map(([name, unit]) => (
            <div key={name}>
              <dt>{title(name)}</dt>
              <dd>{unit}</dd>
            </div>
          ))}
        </dl>
      </fieldset>
    </div>
  );
}
