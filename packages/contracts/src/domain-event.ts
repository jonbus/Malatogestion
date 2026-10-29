/**
 * Vocabulario compartido de eventos de dominio.
 * Sin dependencias, sin logica: solo tipos y constantes.
 */

/** Evento de dominio: un hecho consumado, nombrado en pasado (modulo.entidad.accion). */
export interface DomainEvent<TPayload = Record<string, unknown>> {
  /** Identificador unico del evento. Es la clave de idempotencia. */
  readonly eventId: string;
  /** Tipo cualificado, p. ej. 'stock.below_minimum'. */
  readonly eventType: string;
  /** ISO-8601 del momento en que ocurrio. */
  readonly occurredAt: string;
  /** Tienda en la que ocurrio (referencia blanda a core.stores). */
  readonly storeId: string;
  /** Usuario que lo provoco, o null si lo genero el sistema. */
  readonly actorId: string | null;
  /** Version del esquema del payload, para poder evolucionarlo. */
  readonly version: number;
  readonly payload: TPayload;
}

export const EVENT_STATUS = {
  PENDIENTE: 'PENDIENTE',
  PROCESADO: 'PROCESADO',
  FALLIDO: 'FALLIDO',
  DLQ: 'DLQ',
} as const;

export type EventStatus = (typeof EVENT_STATUS)[keyof typeof EVENT_STATUS];

/** Fila del outbox: el evento mas su estado de entrega. */
export interface EventEnvelope<TPayload = Record<string, unknown>> {
  readonly id: string;
  readonly event: DomainEvent<TPayload>;
  readonly status: EventStatus;
  /** Intentos de entrega ya realizados. */
  readonly attempts: number;
  /** No se reintenta antes de esta marca temporal (backoff). */
  readonly availableAt: string;
  readonly lastError: string | null;
  readonly createdAt: string;
  readonly processedAt: string | null;
}

/** Resultado de entregar un evento a UNA suscripcion. */
export interface DeliveryReport {
  readonly subscriptionId: string;
  readonly eventId: string;
  readonly eventType: string;
  readonly ok: boolean;
  /** true si la idempotencia lo salto porque ya se habia procesado. */
  readonly skipped: boolean;
  readonly error: string | null;
  readonly at: string;
}

/** Registro del log de entregas del bus (observabilidad del Bloque 0). */
export interface DeliveryLogEntry extends DeliveryReport {
  readonly attempt: number;
}
