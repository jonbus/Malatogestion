import assert from 'node:assert/strict';
import { test } from 'node:test';
import type { DomainEvent } from '../packages/contracts/src/domain-event.ts';
import { IdempotencyStore, InMemoryEventBus, OutboxRelay, createIdGenerator } from '../packages/core/src/index.ts';
import { MutableClock } from './helpers/harness.ts';

const STORE_ID = '11111111-1111-4111-8111-111111111111';

function makeEvent(eventId: string, eventType = 'stock.below_minimum'): DomainEvent {
  return {
    eventId,
    eventType,
    occurredAt: '2026-03-02T09:00:00.000Z',
    storeId: STORE_ID,
    actorId: null,
    version: 1,
    payload: { sku: 'LAC-001' },
  };
}

test('un evento atraviesa el bus y llega a todos sus suscriptores', async () => {
  const clock = new MutableClock('2026-03-02T09:00:00.000Z');
  const bus = new InMemoryEventBus({ clock });

  const seen: string[] = [];
  bus.subscribe('stock.below_minimum', () => void seen.push('a'), { id: 'a' });
  bus.subscribe('stock.below_minimum', async () => void seen.push('b'), { id: 'b' });
  bus.subscribe('otro.evento', () => void seen.push('c'), { id: 'c' });

  const reports = await bus.deliver(makeEvent('evt-1'));

  assert.deepEqual(seen, ['a', 'b'], 'solo deben recibirlo los suscriptores de ese tipo');
  assert.equal(reports.length, 2);
  assert.ok(reports.every((report) => report.ok));
  assert.ok(reports.every((report) => report.skipped === false));
  assert.equal(bus.deliveryLog().length, 2, 'el log de entregas registra cada entrega');

  // El comodin '*' recibe todo (asi se suscribe el motor de reglas).
  const wildcard: string[] = [];
  bus.subscribe('*', (event) => void wildcard.push(event.eventType), { id: 'comodin' });
  await bus.deliver(makeEvent('evt-2', 'cualquier.cosa'));
  assert.deepEqual(wildcard, ['cualquier.cosa']);
});

test('un manejador idempotente NO se reejecuta con el mismo eventId', async () => {
  const clock = new MutableClock('2026-03-02T09:00:00.000Z');
  const idempotency = new IdempotencyStore();
  const bus = new InMemoryEventBus({ clock, idempotency });

  let calls = 0;
  bus.subscribe('stock.below_minimum', () => void (calls += 1), { id: 'handler' });

  await bus.deliver(makeEvent('evt-repetido'));
  assert.equal(calls, 1);

  const second = await bus.deliver(makeEvent('evt-repetido'));
  assert.equal(calls, 1, 'el mismo eventId no debe reejecutar el manejador');
  assert.equal(second[0]?.skipped, true);
  assert.equal(second[0]?.ok, true);

  await bus.deliver(makeEvent('evt-distinto'));
  assert.equal(calls, 2, 'un eventId distinto si debe ejecutarse');
});

test('un manejador que falla se reintenta con backoff y acaba en la DLQ', async () => {
  const clock = new MutableClock('2026-03-02T09:00:00.000Z');
  const bus = new InMemoryEventBus({ clock, idempotency: new IdempotencyStore() });

  let calls = 0;
  bus.subscribe(
    'stock.below_minimum',
    () => {
      calls += 1;
      throw new Error('fallo simulado de entrega');
    },
    { id: 'roto' },
  );

  const relay = new OutboxRelay({
    clock,
    ids: createIdGenerator(),
    bus,
    maxAttempts: 3,
    baseBackoffMs: 1_000,
  });
  relay.repository().add(makeEvent('evt-dlq'));

  const first = await relay.drain();
  assert.equal(first.retried, 1);
  assert.equal(first.processed, 0);
  assert.equal(calls, 1);
  assert.equal(relay.repository().byStatus('FALLIDO').length, 1);

  // El backoff impide reintentar antes de tiempo.
  const tooEarly = await relay.drain();
  assert.equal(tooEarly.due, 0);
  assert.equal(calls, 1, 'no debe reintentarse antes de que venza el backoff');

  clock.advanceMs(1_000);
  const second = await relay.drain();
  assert.equal(second.retried, 1);
  assert.equal(calls, 2);

  clock.advanceMs(2_000);
  const third = await relay.drain();
  assert.equal(third.deadLettered, 1);
  assert.equal(third.retried, 0);
  assert.equal(calls, 3, 'tres intentos antes de la DLQ');

  const dead = relay.repository().byStatus('DLQ');
  assert.equal(dead.length, 1);
  assert.equal(dead[0]?.attempts, 3);
  assert.match(dead[0]?.lastError ?? '', /fallo simulado de entrega/);
});

test('el backoff es exponencial y tiene techo', () => {
  const clock = new MutableClock('2026-03-02T09:00:00.000Z');
  const relay = new OutboxRelay({
    clock,
    ids: createIdGenerator(),
    bus: new InMemoryEventBus({ clock }),
    baseBackoffMs: 1_000,
    maxBackoffMs: 5_000,
  });

  assert.equal(relay.backoffMsFor(1), 1_000);
  assert.equal(relay.backoffMsFor(2), 2_000);
  assert.equal(relay.backoffMsFor(3), 4_000);
  assert.equal(relay.backoffMsFor(4), 5_000, 'el techo recorta el crecimiento');
});

test('un evento sin fallos queda PROCESADO y no se reentrega', async () => {
  const clock = new MutableClock('2026-03-02T09:00:00.000Z');
  const bus = new InMemoryEventBus({ clock, idempotency: new IdempotencyStore() });
  let calls = 0;
  bus.subscribe('stock.below_minimum', () => void (calls += 1), { id: 'ok' });

  const relay = new OutboxRelay({ clock, ids: createIdGenerator(), bus });
  await relay.publish(makeEvent('evt-ok'));

  assert.equal(calls, 1);
  assert.equal(relay.repository().byStatus('PROCESADO').length, 1);
  assert.equal((await relay.drain()).due, 0);
  assert.equal(calls, 1);
});
