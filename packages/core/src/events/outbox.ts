import { EVENT_STATUS } from '../../../contracts/src/domain-event.ts';
import type { DomainEvent, EventEnvelope, EventStatus } from '../../../contracts/src/domain-event.ts';
import type { Clock, EventBusPort, IdGenerator, Logger, OutboxRepository } from '../../../contracts/src/ports.ts';

export interface OutboxOptions {
  readonly clock: Clock;
  readonly ids: IdGenerator;
}

/**
 * Outbox en memoria. En produccion es la tabla core.outbox_events: el evento se
 * escribe en la MISMA transaccion que el cambio de estado, y un relay lo publica.
 */
export class InMemoryOutbox implements OutboxRepository {
  private readonly rows = new Map<string, EventEnvelope>();
  private readonly insertionOrder: string[] = [];
  private readonly clock: Clock;
  private readonly ids: IdGenerator;

  constructor(options: OutboxOptions) {
    this.clock = options.clock;
    this.ids = options.ids;
  }

  add(event: DomainEvent): EventEnvelope {
    const envelope: EventEnvelope = Object.freeze({
      id: this.ids.next(),
      event,
      status: EVENT_STATUS.PENDIENTE,
      attempts: 0,
      availableAt: this.clock.nowIso(),
      lastError: null,
      createdAt: this.clock.nowIso(),
      processedAt: null,
    });
    this.rows.set(envelope.id, envelope);
    this.insertionOrder.push(envelope.id);
    return envelope;
  }

  private replace(id: string, patch: Partial<EventEnvelope>): void {
    const current = this.rows.get(id);
    if (!current) return;
    this.rows.set(id, Object.freeze({ ...current, ...patch }));
  }

  pending(nowIso: string): readonly EventEnvelope[] {
    return this.insertionOrder
      .map((id) => this.rows.get(id))
      .filter((row): row is EventEnvelope => row !== undefined)
      .filter(
        (row) =>
          (row.status === EVENT_STATUS.PENDIENTE || row.status === EVENT_STATUS.FALLIDO) &&
          row.availableAt <= nowIso,
      );
  }

  markProcessed(id: string, atIso: string): void {
    this.replace(id, {
      status: EVENT_STATUS.PROCESADO,
      processedAt: atIso,
      availableAt: atIso,
    });
  }

  markFailed(id: string, error: string, attempts: number, availableAtIso: string): void {
    this.replace(id, {
      status: EVENT_STATUS.FALLIDO,
      attempts,
      lastError: error,
      availableAt: availableAtIso,
    });
  }

  markDeadLetter(id: string, error: string, attempts: number): void {
    this.replace(id, {
      status: EVENT_STATUS.DLQ,
      attempts,
      lastError: error,
      processedAt: this.clock.nowIso(),
    });
  }

  byStatus(status: EventStatus): readonly EventEnvelope[] {
    return this.insertionOrder
      .map((id) => this.rows.get(id))
      .filter((row): row is EventEnvelope => row !== undefined && row.status === status);
  }

  all(): readonly EventEnvelope[] {
    return this.insertionOrder
      .map((id) => this.rows.get(id))
      .filter((row): row is EventEnvelope => row !== undefined);
  }

  get(id: string): EventEnvelope | undefined {
    return this.rows.get(id);
  }

  deadLetters(): readonly EventEnvelope[] {
    return this.byStatus(EVENT_STATUS.DLQ);
  }
}

export interface RelayOptions extends OutboxOptions {
  readonly bus: EventBusPort;
  readonly logger?: Logger;
  /** Intentos antes de mandar el evento a la DLQ. */
  readonly maxAttempts?: number;
  readonly baseBackoffMs?: number;
  readonly maxBackoffMs?: number;
}

export interface RelayResult {
  readonly due: number;
  readonly processed: number;
  readonly retried: number;
  readonly deadLettered: number;
}

/** Relay del outbox: lee pendientes, entrega por el bus y aplica reintentos. */
export class OutboxRelay {
  private readonly outbox: InMemoryOutbox;
  private readonly bus: EventBusPort;
  private readonly clock: Clock;
  private readonly logger: Logger | null;
  private readonly maxAttempts: number;
  private readonly baseBackoffMs: number;
  private readonly maxBackoffMs: number;

  constructor(options: RelayOptions) {
    this.outbox = new InMemoryOutbox(options);
    this.bus = options.bus;
    this.clock = options.clock;
    this.logger = options.logger ?? null;
    this.maxAttempts = options.maxAttempts ?? 3;
    this.baseBackoffMs = options.baseBackoffMs ?? 1_000;
    this.maxBackoffMs = options.maxBackoffMs ?? 30_000;
  }

  repository(): InMemoryOutbox {
    return this.outbox;
  }

  /** Backoff exponencial con techo: base * 2^(intento-1). */
  backoffMsFor(attempt: number): number {
    const factor = 2 ** Math.max(0, attempt - 1);
    return Math.min(this.baseBackoffMs * factor, this.maxBackoffMs);
  }

  async drain(): Promise<RelayResult> {
    const due = this.outbox.pending(this.clock.nowIso());
    let processed = 0;
    let retried = 0;
    let deadLettered = 0;

    for (const envelope of due) {
      const reports = await this.bus.deliver(envelope.event);
      const failures = reports.filter((report) => !report.ok);
      const nowIso = this.clock.nowIso();

      if (failures.length === 0) {
        this.outbox.markProcessed(envelope.id, nowIso);
        processed += 1;
        continue;
      }

      const attempts = envelope.attempts + 1;
      const message = failures
        .map((failure) => `${failure.subscriptionId}: ${failure.error ?? 'error desconocido'}`)
        .join(' | ');

      if (attempts >= this.maxAttempts) {
        this.outbox.markDeadLetter(envelope.id, message, attempts);
        deadLettered += 1;
        this.logger?.error('Evento enviado a la DLQ', {
          eventId: envelope.event.eventId,
          eventType: envelope.event.eventType,
          attempts,
        });
        continue;
      }

      const availableAt = new Date(this.clock.now().getTime() + this.backoffMsFor(attempts)).toISOString();
      this.outbox.markFailed(envelope.id, message, attempts, availableAt);
      retried += 1;
    }

    return { due: due.length, processed, retried, deadLettered };
  }

  /** Publica un evento nuevo y lo entrega de inmediato (atajo para el host). */
  async publish(event: DomainEvent): Promise<RelayResult> {
    this.outbox.add(event);
    return this.drain();
  }
}
