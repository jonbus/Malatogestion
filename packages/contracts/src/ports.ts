/**
 * Puertos del sistema. El nucleo depende SOLO de estas interfaces:
 * la infraestructura (Postgres, Redis, HTTP) se enchufa despues.
 */
import type { DeliveryReport, DomainEvent, EventEnvelope, EventStatus } from './domain-event.ts';

// Los consumidores importan estos tipos desde el barrel de puertos.
export type { DeliveryReport, DomainEvent, EventEnvelope, EventStatus } from './domain-event.ts';

export interface Clock {
  now(): Date;
  nowIso(): string;
}

export interface IdGenerator {
  next(): string;
}

export type LogMeta = Record<string, unknown>;

export interface Logger {
  debug(message: string, meta?: LogMeta): void;
  info(message: string, meta?: LogMeta): void;
  warn(message: string, meta?: LogMeta): void;
  error(message: string, meta?: LogMeta): void;
}

export type EventHandler<TPayload = Record<string, unknown>> = (
  event: DomainEvent<TPayload>,
) => void | Promise<void>;

export interface Subscription {
  readonly id: string;
  readonly eventType: string;
  readonly moduleId: string;
}

export type Unsubscribe = () => void;

/** Bus de eventos: suscripcion por tipo y entrega con informe por suscriptor. */
export interface EventBusPort {
  subscribe(
    eventType: string,
    handler: EventHandler,
    options?: { id?: string; moduleId?: string },
  ): Unsubscribe;
  /** Entrega el evento a TODAS las suscripciones y devuelve un informe por cada una. */
  deliver(event: DomainEvent): Promise<DeliveryReport[]>;
  subscriptions(): readonly Subscription[];
}

/** Outbox: persistencia del evento dentro de la transaccion de negocio. */
export interface OutboxRepository {
  add(event: DomainEvent): EventEnvelope;
  /** Envelopes pendientes y ya disponibles para reintento. */
  pending(nowIso: string): readonly EventEnvelope[];
  markProcessed(id: string, atIso: string): void;
  markFailed(id: string, error: string, attempts: number, availableAtIso: string): void;
  markDeadLetter(id: string, error: string, attempts: number): void;
  byStatus(status: EventStatus): readonly EventEnvelope[];
  all(): readonly EventEnvelope[];
}

/** Contexto que reciben los resolvedores de facts y los manejadores de acciones. */
export interface FactContext {
  readonly storeId: string;
  readonly actorId: string | null;
  readonly event: DomainEvent;
  readonly now: Date;
}

export interface FactResolution {
  readonly found: boolean;
  readonly value: unknown;
}

/**
 * Resuelve el valor de una variable del motor de reglas.
 * Convencion: si la regla no declara `params`, el fact se resuelve contra
 * `ctx.event.payload` (asi lo hacen las reglas del seed).
 */
export type FactResolver = (
  params: Readonly<Record<string, unknown>>,
  ctx: FactContext,
) => unknown | Promise<unknown>;

export interface ActionContext extends FactContext {
  readonly ruleId: string;
  readonly ruleCode: string;
}

export interface ActionResult {
  readonly ok: boolean;
  readonly detail?: Readonly<Record<string, unknown>>;
}

/** Manejador de una accion del motor de reglas. */
export interface ActionHandler {
  readonly type: string;
  execute(
    params: Readonly<Record<string, unknown>>,
    ctx: ActionContext,
  ): ActionResult | Promise<ActionResult>;
}

export interface RuleActionDefinition {
  readonly type: string;
  readonly params?: Readonly<Record<string, unknown>>;
}

/** Regla activa tal y como la consume el motor (proyeccion de rules.rules). */
export interface RuleDefinition {
  readonly id: string;
  readonly code: string;
  readonly name: string;
  readonly storeId: string;
  readonly eventType: string;
  readonly condition: unknown;
  readonly actions: readonly RuleActionDefinition[];
  /** Menor numero = se evalua antes. */
  readonly priority: number;
  readonly version: number;
  readonly isActive: boolean;
  readonly cooldownMinutes: number;
  readonly maxPerDay: number | null;
  readonly validFrom?: string | null;
  readonly validTo?: string | null;
}
