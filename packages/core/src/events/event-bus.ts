import type { DeliveryLogEntry, DeliveryReport, DomainEvent } from '../../../contracts/src/domain-event.ts';
import type {
  Clock,
  EventBusPort,
  EventHandler,
  Logger,
  Subscription,
  Unsubscribe,
} from '../../../contracts/src/ports.ts';
import { IdempotencyStore } from './idempotency.ts';

interface SubscriptionEntry extends Subscription {
  readonly handler: EventHandler;
  readonly order: number;
}

export interface EventBusOptions {
  readonly clock: Clock;
  readonly logger?: Logger;
  /** Si se pasa, cada (suscripcion, evento) se entrega como maximo una vez con exito. */
  readonly idempotency?: IdempotencyStore;
}

/**
 * Bus de eventos en memoria.
 * `deliver` informa POR SUSCRIPTOR: el outbox necesita saber cual fallo para
 * reintentar sin volver a ejecutar los que ya fueron bien.
 * El tipo '*' es comodin y recibe todos los eventos (lo usa el motor de reglas).
 */
export class InMemoryEventBus implements EventBusPort {
  private readonly entries: SubscriptionEntry[] = [];
  private readonly deliveries: DeliveryLogEntry[] = [];
  private readonly clock: Clock;
  private readonly logger: Logger | null;
  private readonly idempotency: IdempotencyStore | null;
  private sequence = 0;

  constructor(options: EventBusOptions) {
    this.clock = options.clock;
    this.logger = options.logger ?? null;
    this.idempotency = options.idempotency ?? null;
  }

  subscribe(
    eventType: string,
    handler: EventHandler,
    options: { id?: string; moduleId?: string } = {},
  ): Unsubscribe {
    this.sequence += 1;
    const entry: SubscriptionEntry = {
      id: options.id ?? `sub-${this.sequence}`,
      eventType,
      moduleId: options.moduleId ?? 'desconocido',
      handler,
      order: this.sequence,
    };
    this.entries.push(entry);

    return () => {
      const index = this.entries.indexOf(entry);
      if (index >= 0) this.entries.splice(index, 1);
    };
  }

  subscriptions(): readonly Subscription[] {
    return this.entries.map(({ id, eventType, moduleId }) => ({ id, eventType, moduleId }));
  }

  /** Suscripciones que deben recibir un evento, en orden de registro. */
  private matching(eventType: string): readonly SubscriptionEntry[] {
    return this.entries
      .filter((entry) => entry.eventType === eventType || entry.eventType === '*')
      .sort((a, b) => a.order - b.order);
  }

  async deliver(event: DomainEvent): Promise<DeliveryReport[]> {
    const reports: DeliveryReport[] = [];

    for (const entry of this.matching(event.eventType)) {
      const at = this.clock.nowIso();

      if (this.idempotency?.has(entry.id, event.eventId)) {
        reports.push(this.record({
          subscriptionId: entry.id,
          eventId: event.eventId,
          eventType: event.eventType,
          ok: true,
          skipped: true,
          error: null,
          at,
          attempt: this.attemptOf(event.eventId, entry.id) + 1,
        }));
        continue;
      }

      try {
        await entry.handler(event);
        this.idempotency?.mark(entry.id, event.eventId);
        reports.push(this.record({
          subscriptionId: entry.id,
          eventId: event.eventId,
          eventType: event.eventType,
          ok: true,
          skipped: false,
          error: null,
          at,
          attempt: this.attemptOf(event.eventId, entry.id) + 1,
        }));
      } catch (cause) {
        const message = cause instanceof Error ? cause.message : String(cause);
        this.logger?.error('Fallo al entregar evento', {
          subscriptionId: entry.id,
          eventId: event.eventId,
          eventType: event.eventType,
          error: message,
        });
        reports.push(this.record({
          subscriptionId: entry.id,
          eventId: event.eventId,
          eventType: event.eventType,
          ok: false,
          skipped: false,
          error: message,
          at,
          attempt: this.attemptOf(event.eventId, entry.id) + 1,
        }));
      }
    }

    return reports;
  }

  private attemptOf(eventId: string, subscriptionId: string): number {
    return this.deliveries.filter(
      (entry) => entry.eventId === eventId && entry.subscriptionId === subscriptionId,
    ).length;
  }

  private record(entry: DeliveryLogEntry): DeliveryLogEntry {
    const frozen = Object.freeze(entry);
    this.deliveries.push(frozen);
    return frozen;
  }

  /** Traza de todas las entregas: base de la observabilidad del Bloque 0. */
  deliveryLog(): readonly DeliveryLogEntry[] {
    return this.deliveries;
  }
}
