import assert from 'node:assert/strict';
import { test } from 'node:test';
import type { DomainEvent, RuleDefinition } from '../packages/contracts/src/ports.ts';
import { DEMO_STORE_ID } from '../apps/api/src/composition-root.ts';
import { MONDAY, MutableClock, buildSystem, nextWeekdayAt, seedInventory } from './helpers/harness.ts';

const RULE_LUNES = 'seed-LUNES_LACTEOS_STOCK_BAJO';

function mondayClock(): MutableClock {
  return new MutableClock(nextWeekdayAt(MONDAY, 9).toISOString());
}

function executionsOf(system: ReturnType<typeof buildSystem>, code: string) {
  return system.ruleRepository.executions().filter((execution) => execution.ruleCode === code);
}

test('una regla real del seed dispara y crea la tarea prioritaria por LEAST_LOADED', async () => {
  const clock = mondayClock();
  const system = buildSystem({ clock });
  seedInventory(system);
  system.pos.setAffluence('LOW');

  const event = system.inventory.checkMinimum('prod-LAC-001', 'SALA', 'u-sala-2');
  assert.ok(event, 'el inventario debe emitir stock.below_minimum al bajar del minimo');
  await system.publish(event as DomainEvent);

  const executions = executionsOf(system, 'LUNES_LACTEOS_STOCK_BAJO');
  assert.equal(executions.length, 1, 'la regla LUNES_LACTEOS_STOCK_BAJO debe evaluarse una vez');
  assert.equal(executions[0]?.result, 'DISPARADA');
  assert.equal(executions[0]?.matched, true);

  // Las acciones se ejecutan en el orden declarado en el JSONB del seed.
  assert.deepEqual(
    executions[0]?.actionsExecuted.map((action) => action.type),
    ['CREATE_TASK', 'NOTIFY'],
  );
  assert.ok(executions[0]?.actionsExecuted.every((action) => action.ok));

  // La tarea la crea la REGLA (no el suscriptor del modulo de tareas).
  const ruleTasks = system.tasks.all().filter((task) => task.createdByRuleId === RULE_LUNES);
  assert.equal(ruleTasks.length, 1);

  const task = ruleTasks[0];
  assert.ok(task);
  assert.equal(task.priority, 'ALTA');
  assert.equal(task.templateCode, 'REPOSICION_PRIORITARIA');
  // LEAST_LOADED con las tres operadoras a cero: desempata por nombre -> Ana Torres.
  assert.equal(task.assigneeId, 'u-sala-1');
  assert.equal(task.payload['categoryPath'], 'lacteos');
  assert.equal(task.payload['origin'], 'RULE');

  // due_in_minutes: 30
  assert.ok(task.dueAt);
  assert.equal(Date.parse(task.dueAt as string) - clock.now().getTime(), 30 * 60_000);

  // El historial de la tarea queda registrado.
  assert.ok(system.tasks.historyOf(task.id).some((entry) => entry.type === 'CREADA'));

  // La accion NOTIFY llego a coordinacion.
  const avisos = system.notify.byRole('COORDINADORA');
  assert.equal(avisos.length, 1);
  assert.equal(avisos[0]?.title, 'Reposición prioritaria de lácteos generada');
  assert.equal(avisos[0]?.severity, 'AVISO');
});

test('una regla que no coincide devuelve SIN_COINCIDENCIA y no crea nada', async () => {
  const clock = mondayClock();
  const system = buildSystem({ clock });
  seedInventory(system);
  // La regla exige afluencia LOW; ponemos HIGH para que no coincida.
  system.pos.setAffluence('HIGH');

  const event = system.inventory.checkMinimum('prod-LAC-001', 'SALA');
  assert.ok(event);
  await system.publish(event as DomainEvent);

  const executions = executionsOf(system, 'LUNES_LACTEOS_STOCK_BAJO');
  assert.equal(executions.length, 1);
  assert.equal(executions[0]?.result, 'SIN_COINCIDENCIA');
  assert.equal(executions[0]?.matched, false);
  assert.equal(executions[0]?.actionsExecuted.length, 0);

  assert.equal(system.tasks.all().filter((task) => task.createdByRuleId === RULE_LUNES).length, 0);
  assert.equal(system.notify.count(), 0);
});

test('el cooldown de la regla impide un segundo disparo dentro de la ventana', async () => {
  const clock = mondayClock();
  const system = buildSystem({ clock });
  seedInventory(system);
  system.pos.setAffluence('LOW');

  const first = system.inventory.checkMinimum('prod-LAC-001', 'SALA');
  assert.ok(first);
  await system.publish(first as DomainEvent);

  // Diez minutos despues vuelve a haber rotura: la regla tiene 120 min de cooldown.
  clock.advanceMs(10 * 60_000);
  const second = system.inventory.checkMinimum('prod-LAC-001', 'SALA');
  assert.ok(second, 'el stock sigue bajo minimo, debe emitirse otro evento');
  await system.publish(second as DomainEvent);

  assert.deepEqual(
    executionsOf(system, 'LUNES_LACTEOS_STOCK_BAJO').map((execution) => execution.result),
    ['DISPARADA', 'OMITIDA_COOLDOWN'],
  );

  // Solo la primera genero tarea por regla.
  assert.equal(system.tasks.all().filter((task) => task.createdByRuleId === RULE_LUNES).length, 1);

  // Pasado el cooldown, vuelve a dispararse.
  clock.advanceMs(120 * 60_000);
  const third = system.inventory.checkMinimum('prod-LAC-001', 'SALA');
  assert.ok(third);
  await system.publish(third as DomainEvent);

  assert.deepEqual(
    executionsOf(system, 'LUNES_LACTEOS_STOCK_BAJO').map((execution) => execution.result),
    ['DISPARADA', 'OMITIDA_COOLDOWN', 'DISPARADA'],
  );
});

test('max_per_day corta la regla al alcanzar el limite diario', async () => {
  const clock = mondayClock();

  const rule: RuleDefinition = {
    id: 'rule-limite-diario',
    code: 'LIMITE_DIARIO_PRUEBA',
    name: 'Prueba de limite diario',
    storeId: DEMO_STORE_ID,
    eventType: 'test.ping',
    condition: { all: [{ fact: 'pos.affluence', op: 'eq', value: 'LOW' }] },
    actions: [
      {
        type: 'CREATE_TASK',
        params: { title: 'Ping de prueba', priority: 'BAJA', role: 'OPERADORA', assignee_strategy: 'ROUND_ROBIN' },
      },
    ],
    priority: 1,
    version: 1,
    isActive: true,
    cooldownMinutes: 0,
    maxPerDay: 2,
  };

  const system = buildSystem({ clock, rules: [rule] });
  system.pos.setAffluence('LOW');

  for (let index = 0; index < 3; index += 1) {
    await system.publish({
      eventId: `evt-limite-${index}`,
      eventType: 'test.ping',
      occurredAt: clock.nowIso(),
      storeId: DEMO_STORE_ID,
      actorId: null,
      version: 1,
      payload: { index },
    });
  }

  assert.deepEqual(
    executionsOf(system, 'LIMITE_DIARIO_PRUEBA').map((execution) => execution.result),
    ['DISPARADA', 'DISPARADA', 'OMITIDA_LIMITE'],
  );

  // Solo dos tareas: la tercera no se creo.
  assert.equal(system.tasks.all().length, 2);
});

test('la traza de la condicion explica por que coincidio cada variable', async () => {
  const clock = mondayClock();
  const system = buildSystem({ clock });
  seedInventory(system);
  system.pos.setAffluence('LOW');

  const event = system.inventory.checkMinimum('prod-LAC-001', 'SALA');
  assert.ok(event);
  await system.publish(event as DomainEvent);

  const execution = executionsOf(system, 'LUNES_LACTEOS_STOCK_BAJO')[0];
  assert.ok(execution);

  const hojas = execution.trace.filter((node) => node.kind === 'leaf');
  assert.equal(hojas.length, 3, 'la regla tiene tres condiciones hoja');
  assert.deepEqual(
    hojas.map((node) => node.label),
    ['calendar.weekday eq', 'store.affluence eq', 'inventory.stock_ratio lt'],
  );
  assert.ok(hojas.every((node) => node.matched));
  assert.ok(hojas[2]?.detail?.includes('0.25'), `la traza debe mostrar el ratio real: ${hojas[2]?.detail}`);
});
