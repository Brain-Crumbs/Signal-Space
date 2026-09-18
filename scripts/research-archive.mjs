import { createHash } from 'node:crypto';
import { readdir, readFile, stat, writeFile } from 'node:fs/promises';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const researchRoot = resolve(root, 'research');
const manifestPath = resolve(researchRoot, 'archive-manifest.json');
const catalogPath = resolve(researchRoot, 'catalog.json');
const write = process.argv.includes('--write');

async function walk(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = [];
  for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
    const path = resolve(directory, entry.name);
    if (entry.isDirectory()) files.push(...(await walk(path)));
    else if (path !== manifestPath) files.push(path);
  }
  return files;
}

async function describe(path) {
  const bytes = await readFile(path);
  return {
    path: relative(root, path).replaceAll('\\', '/'),
    size: bytes.byteLength,
    sha256: createHash('sha256').update(bytes).digest('hex'),
  };
}

function stableJson(value) {
  return `${JSON.stringify(value, null, 2)}\n`;
}

const files = await walk(researchRoot);
const descriptions = await Promise.all(files.map(describe));
const nextManifest = {
  schema_version: 1,
  generated_by: 'scripts/research-archive.mjs',
  file_count: descriptions.length,
  files: descriptions,
};

if (write) {
  await writeFile(manifestPath, stableJson(nextManifest));
  console.log(
    `Wrote ${relative(root, manifestPath)} (${descriptions.length} files)`,
  );
  process.exit(0);
}

const expected = JSON.parse(await readFile(manifestPath, 'utf8'));
if (stableJson(expected) !== stableJson(nextManifest))
  throw new Error(
    'Research archive manifest is stale. Run npm run research:manifest and inspect the diff.',
  );

const catalog = JSON.parse(await readFile(catalogPath, 'utf8'));
const ids = new Set();
for (const entry of catalog.entries) {
  if (ids.has(entry.id)) throw new Error(`Duplicate catalog id: ${entry.id}`);
  ids.add(entry.id);
  const path = resolve(root, entry.path);
  const metadata = await stat(path).catch(() => undefined);
  if (!metadata?.isFile())
    throw new Error(`Catalog path is missing or not a file: ${entry.path}`);
}

const checkedText = [
  resolve(root, 'README.md'),
  resolve(root, 'docs/research'),
];
const supersededShortName = ['V', 'T', 'O', 'S'].join('');
const researchTextExtensions = /\.(?:md|txt|json|ya?ml|py|cpp|csv)$/i;
const textFiles = [
  checkedText[0],
  ...(await walk(checkedText[1])),
  ...files.filter((path) => researchTextExtensions.test(path)),
];
for (const { path } of descriptions)
  if (path.includes(supersededShortName))
    throw new Error(`Superseded project name found in path: ${path}`);
for (const path of textFiles) {
  const content = await readFile(path, 'utf8');
  if (
    content.includes(supersededShortName) ||
    /Velocity.?Time Optical Substrate/i.test(content)
  )
    throw new Error(`Superseded project name found in ${relative(root, path)}`);
}

console.log(
  `Verified ${descriptions.length} research files and ${catalog.entries.length} catalog entries.`,
);
