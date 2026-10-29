import type { DomainEvent } from '../../../contracts/src/domain-event.ts';
import type { Clock, IdGenerator } from '../../../contracts/src/ports.ts';

export interface EventFactory {
  /** Crea un evento de dominio listo para el outbox. */
  create(
    eventType: string,
    payload: Record<string, unknown>,
    options?: { actorId?: string | null; version?: number },
  ): DomainEvent;
  readonly storeId: string;
}

/**
 * Fabrica de eventos. Evita que cada modulo repita la construccion del sobre
 * (eventId, occurredAt, storeId, version) y garantiza un formato homogeneo.
 */
export function createEventFactory(input: {
  clock: Clock;
  ids: IdGenerator;
  storeId: string;
}): EventFactory {
  return {
    storeId: input.storeId,
    create(eventType, payload, options = {}) {
      return Object.freeze({
        eventId: input.ids.next(),
        eventType,
        occurredAt: input.clock.nowIso(),
        storeId: input.storeId,
        actorId: options.actorId ?? null,
        version: options.version ?? 1,
        payload,
      });
    },
  };
}
