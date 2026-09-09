import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { validateScenario, roundTripScenario } from '../packages/model/src/index.js';

const load = async name => JSON.parse(await readFile(new URL(`../fixtures/scenarios/${name}.json`, import.meta.url)));
const clone = x => JSON.parse(JSON.stringify(x));

test('isolated and reciprocal pair fixtures are valid', async () => {
  for (const name of ['isolated','pair']) assert.deepEqual(validateScenario(await load(name)), { ok:true, errors:[] });
});

test('A-B-C and chain topologies are accepted', async () => {
  const pair=await load('pair');
  const abc=clone(pair); abc.id='abc'; abc.nodes.push({...abc.nodes[1],id:'C',position:2,phi:0});
  abc.links.push({id:'B-C',source:'B',target:'C',sourcePort:'right',targetPort:'left',delay:1},{id:'C-B',source:'C',target:'B',sourcePort:'left',targetPort:'right',delay:1});
  abc.initialHistory.nodes.C={phiAtZero:0,omega:2}; abc.initialHistory.filters.C={left:0,right:0};
  assert.equal(validateScenario(abc).ok,true);
  const chain=clone(abc); chain.id='chain'; chain.nodes.push({...abc.nodes[2],id:'D',position:3});
  chain.links.push({id:'C-D',source:'C',target:'D',sourcePort:'right',targetPort:'left',delay:1},{id:'D-C',source:'D',target:'C',sourcePort:'left',targetPort:'right',delay:1});
  chain.initialHistory.nodes.D={phiAtZero:0,omega:2}; chain.initialHistory.filters.D={left:0,right:0};
  assert.equal(validateScenario(chain).ok,true);
});

test('explicit positive-delay ring and mirror boundaries are accepted', async () => {
  const ring=await load('pair'); ring.boundaries={left:{kind:'periodic',closureDelay:2},right:{kind:'periodic',closureDelay:2}};
  const mirror=await load('pair'); mirror.boundaries.left={kind:'mirror',exteriorDistance:0.5};
  assert.equal(validateScenario(ring).ok,true); assert.equal(validateScenario(mirror).ok,true);
});

test('invalid bounds, zero delay, and inconsistent ports return field errors', async () => {
  const bad=await load('pair'); bad.nodes[0].amplitude=2; bad.nodes[0].gain=bad.nodes[0].omega0; bad.links[0].delay=0; bad.links[1].sourcePort='right';
  const result=validateScenario(bad); assert.equal(result.ok,false);
  for (const path of ['nodes[0].amplitude','nodes[0].gain','links[0].delay','links[1].sourcePort']) assert.ok(result.errors.some(e=>e.path===path),path);
});

test('round trip preserves predictive state and observer protocol has no private fields', async () => {
  const scenario=await load('pair'); scenario.initialHistory.pendingPackets=[{id:'private-1',source:'A',target:'B',emissionTime:-0.25,arrivalTime:0.75,port:'left'}];
  scenario.initialHistory.pendingResponses=[{nodeId:'B',dueTime:0.8,payload:{kind:'filter'}}];
  const copy=roundTripScenario(scenario); assert.deepEqual(copy,scenario);
  assert.equal('packets' in scenario.observation,false); assert.equal('remotePhase' in scenario.observation,false);
});

test('dimensionless scaling can round trip without changing physical inputs', async () => {
  const scenario=await load('pair'), scales={time:2,length:3};
  const dimensionless={c0:scenario.c0*scales.time/scales.length,positions:scenario.nodes.map(n=>n.position/scales.length),omega:scenario.nodes.map(n=>n.omega*scales.time)};
  const restored={c0:dimensionless.c0*scales.length/scales.time,positions:dimensionless.positions.map(x=>x*scales.length),omega:dimensionless.omega.map(x=>x/scales.time)};
  assert.deepEqual(restored,{c0:scenario.c0,positions:scenario.nodes.map(n=>n.position),omega:scenario.nodes.map(n=>n.omega)});
});
