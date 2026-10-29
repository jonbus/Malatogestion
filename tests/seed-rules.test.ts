import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { test } from 'node:test';
import type { DomainEvent, FactContext, RuleDefinition } from '../packages/contracts/src/ports.ts';
import { ConditionEvaluator } from '../packages/core/src/index.ts';
import { DEMO_STORE_ID } from '../apps/api/src/composition-root.ts';
import { loadSeedRules, parseSeedRules } from '../apps/api/src/adapters/seed-rules.adapter.ts';
import {
  FRIDAY,
  MONDAY,
  MutableClock,
  WEDNESDAY,
  buildSystem,
  nextWeekdayAt,
  seedInventory,
} from './helpers/harness.ts';

const SEED_PATH = join(process.cwd(), 'db', 'seed', '001_demo_store.sql');
const RULES = loadSeedRules({ storeId: DEMO_STORE_ID });
const BY_CODE = new Map(RULES.map((rule) => [rule.code, rule]));

function rule(code: string): RuleDefinition {
  const found = BY_CODE.get(code);
  assert.ok(found, `la regla '${code}' deberia existir en el seed`);
  return found as RuleDefinition;
}

function makeEvent(eventType: string, payload: Record<string, unknown>, at: Date): DomainEvent {
  return {
    eventId: `evt-${eventType}-${at.getTime()}`,
    eventType,
    occurredAt: at.toISOString(),
    storeId: DEMO_STORE_ID,
    actorId: null,
    version: 1,
    payload,
  };
}

async function evaluate(
  system: ReturnType<typeof buildSystem>,
  target: RuleDefinition,
  now: Date,
  event: DomainEvent,
): Promise<{ matched: boolean; labels: string[] }> {
  const ctx: FactContext = { storeId: event.storeId, actorId: null, event, now };
  const evaluator = new ConditionEvaluator((key, params) => system.facts.resolve(key, params, ctx));
  const result = await evaluator.evaluate(target.condition);
  return { matched: result.matched, labels: result.trace.map((node) => node.label) };
}

/** Recorre el arbol JSONB y devuelve las claves de fact referenciadas. */
function referencedFacts(condition: unknown, out = new Set<string>()): Set<string> {
  if (typeof condition !== 'object' || condition === null) return out;
  const node = condition as Record<string, unknown>;

  if (Array.isArray(node['all'])) for (const child of node['all'] as unknown[]) referencedFacts(child, out);
  if (Array.isArray(node['any'])) for (const child of node['any'] as unknown[]) referencedFacts(child, out);
  if (node['not'] !== undefined) referencedFacts(node['not'], out);

  const fact = node['fact'];
  if (typeof fact === 'string') out.add(fact);
  return out;
}

function buildScenario() {
  const monday = nextWeekdayAt(MONDAY, 9);
  const clock = new MutableClock(monday.toISOString());

  // store.affluence_forecast = HIGH (viernes tarde) y store.affluence = LOW (el
  // resto), porque son dos variables distintas y el seed usa ambas.
  const system = buildSystem({ clock, affluenceForecast: 'HIGH' });
  seedInventory(system);
  system.pos.setAffluence('LOW');

  const expiry = new Date(monday.getTime() + 2 * 86_400_000).toISOString().slice(0, 10);
  system.inventory.addLot({
    lotId: 'LOT-YOG-2601',
    productId: 'prod-LAC-005',
    sku: 'LAC-005',
    batchCode: 'YOG-2601',
    locationCode: 'CAMARA',
    expiryDate: expiry,
    qty: 8,
  });

  return { system, monday, expiry };
}

test('el seed contiene exactamente las 5 reglas esperadas', () => {
  // Se relee el fichero real a traves del adaptador: nada de mocks.
  const parsed = parseSeedRules(readFileSync(SEED_PATH, 'utf8'));

  assert.equal(parsed.length, 5);
  assert.deepEqual(
    parsed.map((entry) => entry.code),
    [
      'LUNES_LACTEOS_STOCK_BAJO',
      'VIERNES_TARDE_REFUERZO_BEBIDAS',
      'LOTE_PROXIMO_CADUCIDAD',
      'DESCUADRE_CAJA',
      'TAREA_VENCIDA_REASIGNAR',
    ],
  );
  assert.deepEqual(
    parsed.map((entry) => entry.priority),
    [10, 20, 30, 5, 40],
    'la prioridad define el orden de evaluacion (menor numero = antes)',
  );
  assert.ok(parsed.every((entry) => entry.isActive));
  assert.deepEqual(
    parsed.map((entry) => entry.maxPerDay),
    [3, 1, 10, 5, 20],
  );
});

test('el motor carga las 5 reglas reales del seed', () => {
  const system = buildSystem();
  assert.equal(system.ruleRepository.size(), 5);

  // Orden de evaluacion por prioridad: DESCUADRE_CAJA (5) va primero.
  const forDiscrepancy = system.ruleRepository.activeRulesFor('cash_session.discrepancy', DEMO_STORE_ID);
  assert.deepEqual(
    forDiscrepancy.map((entry) => entry.code),
    ['DESCUADRE_CAJA'],
  );

  const forStock = system.ruleRepository.activeRulesFor('stock.below_minimum', DEMO_STORE_ID);
  assert.deepEqual(
    forStock.map((entry) => entry.code),
    ['LUNES_LACTEOS_STOCK_BAJO'],
  );
});

test('el evaluador entiende las 5 condiciones reales y las hace coincidir', async () => {
  const { system, monday, expiry } = buildScenario();

  // 1 · Lunes + afluencia baja + lacteos al 25 % de su minimo.
  const lunes = await evaluate(
    system,
    rule('LUNES_LACTEOS_STOCK_BAJO'),
    monday,
    makeEvent('stock.below_minimum', { productId: 'prod-LAC-001', sku: 'LAC-001' }, monday),
  );
  assert.equal(lunes.matched, true, 'lunes + LOW + stock_ratio 0.25 debe coincidir');
  assert.deepEqual(lunes.labels, ['calendar.weekday eq', 'store.affluence eq', 'inventory.stock_ratio lt', 'all[3]']);

  // 2 · Viernes por la tarde con prevision alta.
  const friday = nextWeekdayAt(FRIDAY, 18);
  const viernes = await evaluate(
    system,
    rule('VIERNES_TARDE_REFUERZO_BEBIDAS'),
    friday,
    makeEvent('schedule.weekday_window', {}, friday),
  );
  assert.equal(viernes.matched, true, 'viernes 18:00 + previsión HIGH debe coincidir');

  // 3 · Lote que caduca en 2 dias y con existencias.
  const caducidad = await evaluate(
    system,
    rule('LOTE_PROXIMO_CADUCIDAD'),
    monday,
    makeEvent('lot.expiring_soon', { lotId: 'LOT-YOG-2601', productId: 'prod-LAC-005' }, monday),
  );
  assert.equal(caducidad.matched, true, `el lote caduca el ${expiry} (2 dias) y tiene 8 unidades`);

  // 4 · Descuadre de caja de 12,50 EUR (umbral de la regla: 5).
  const descuadre = await evaluate(
    system,
    rule('DESCUADRE_CAJA'),
    monday,
    makeEvent('cash_session.discrepancy', { difference: -12.5, registerId: 'CAJA-1' }, monday),
  );
  assert.equal(descuadre.matched, true, 'un descuadre de 12,50 supera el umbral de 5 EUR');

  // 5 · Tarea vencida 45 minutos y todavia asignada.
  const vencida = await evaluate(
    system,
    rule('TAREA_VENCIDA_REASIGNAR'),
    monday,
    makeEvent('task.overdue', { taskId: 't-1', minutesOverdue: 45, status: 'ASIGNADA' }, monday),
  );
  assert.equal(vencida.matched, true, 'una tarea con 45 minutos de retraso supera el umbral de 30');
});

test('ninguna condicion del seed coincide por accidente en un contexto neutro', async () => {
  const { system } = buildScenario();
  const neutral = nextWeekdayAt(WEDNESDAY, 10);
  const emptyEvent = makeEvent('evento.neutro', {}, neutral);

  for (const target of RULES) {
    const result = await evaluate(system, target, neutral, emptyEvent);
    assert.equal(
      result.matched,
      false,
      `la regla '${target.code}' no debe coincidir en un miercoles a las 10:00 sin datos de evento`,
    );
  }
});

test('todas las claves de fact que usan las reglas del seed estan registradas por algun modulo', () => {
  const system = buildSystem();
  const referenciadas = new Set<string>();
  for (const target of RULES) for (const key of referencedFacts(target.condition)) referenciadas.add(key);

  assert.ok(referenciadas.size >= 10, `se esperaban al menos 10 facts distintos, hay ${referenciadas.size}`);

  const sinRegistrar = [...referenciadas].filter((key) => !system.facts.has(key)).sort();
  assert.deepEqual(sinRegistrar, [], 'hay facts usados por reglas que ningun modulo registra');

  // Y cada uno tiene un dueno identificable.
  for (const key of referenciadas) {
    assert.ok(system.facts.ownerOf(key), `el fact '${key}' no tiene modulo responsable`);
  }
});

test('todas las acciones que usan las reglas del seed estan registradas y declaradas', () => {
  const system = buildSystem();
  const usadas = new Set<string>();
  for (const target of RULES) for (const action of target.actions) usadas.add(action.type);

  const sinRegistrar = [...usadas].filter((type) => !system.actions.has(type)).sort();
  assert.deepEqual(sinRegistrar, [], 'hay acciones usadas por reglas que ningun modulo implementa');

  for (const type of usadas) {
    assert.ok(system.registry.ownerOfAction(type), `la accion '${type}' no la declara ningun manifiesto`);
  }

  assert.deepEqual([...usadas].sort(), ['CREATE_TASK', 'NOTIFY', 'REASSIGN_TASK']);
});

test('las reglas del seed encajan con los parametros que leen las acciones reales', async () => {
  const { system, monday } = buildScenario();
  const target = rule('LUNES_LACTEOS_STOCK_BAJO');

  const created = target.actions.find((action) => action.type === 'CREATE_TASK');
  assert.ok(created, 'la regla del lunes debe crear una tarea');
  const params = created.params ?? {};

  assert.equal(params['template_code'], 'REPOSICION_PRIORITARIA');
  assert.equal(params['assignee_strategy'], 'LEAST_LOADED');
  assert.equal(params['role'], 'OPERADORA');
  assert.equal(params['priority'], 'ALTA');
  assert.equal(params['due_in_minutes'], 30);

  // Y el motor lo ejecuta de verdad contra el sistema real.
  const event = system.inventory.checkMinimum('prod-LAC-001', 'SALA');
  assert.ok(event);
  await system.publish(event as DomainEvent);

  const task = system.tasks.all().find((candidate) => candidate.createdByRuleId === target.id);
  assert.ok(task, 'el motor debe haber creado la tarea a partir del JSONB del seed');
  assert.equal(task.priority, 'ALTA');
  assert.equal(task.assigneeId, 'u-sala-1');
  assert.equal(Date.parse(task.dueAt as string) - monday.getTime(), 30 * 60_000);
});

test('la regla de caducidad resuelve los facts desde el payload del evento', async () => {
  const { system, monday } = buildScenario();

  const event = makeEvent(
    'lot.expiring_soon',
    { lotId: 'LOT-YOG-2601', productId: 'prod-LAC-005', daysToExpiry: 2, qty: 8 },
    monday,
  );

  const ctx: FactContext = { storeId: event.storeId, actorId: null, event, now: monday };
  const dias = await system.facts.resolve('inventory.days_to_expiry', {}, ctx);
  const cantidad = await system.facts.resolve('inventory.lot_qty', {}, ctx);

  assert.equal(dias.found, true);
  assert.equal(dias.value, 2);
  assert.equal(cantidad.found, true);
  assert.equal(cantidad.value, 8);

  // Un lote inexistente NO aporta valor: la regla no debe coincidir por accidente.
  // 'found' significa "ese fact lo registra algun modulo" (aqui si: inventory lo
  // registra). La ausencia de DATO se expresa con value === null, y el evaluador
  // trata null como no coincidente en cualquier comparacion.
  const desconocido = await system.facts.resolve(
    'inventory.days_to_expiry',
    { lotId: 'NO-EXISTE' },
    ctx,
  );
  assert.equal(desconocido.found, true, 'el fact esta registrado aunque no haya dato');
  assert.equal(desconocido.value, null, 'sin lote no hay valor, y eso no coincide');

  // Un fact que NADIE registra si devuelve found: false. Esta distincion es la
  // que permite avisar en el editor de reglas de un error de configuracion
  // (variable inexistente) sin confundirlo con una ausencia temporal de dato.
  const noRegistrado = await system.facts.resolve('no.existe_este_fact', {}, ctx);
  assert.equal(noRegistrado.found, false);
  assert.equal(noRegistrado.value, undefined);
});
