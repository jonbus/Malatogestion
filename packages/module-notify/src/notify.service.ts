import type { DomainEvent } from '../../contracts/src/domain-event.ts';
import type { ActionContext, ActionHandler, ActionResult, Clock, IdGenerator } from '../../contracts/src/ports.ts';
import { createEventFactory } from '../../core/src/events/event-factory.ts';
import type { EventFactory } from '../../core/src/events/event-factory.ts';

export type NotificationChannel = 'IN_APP' | 'PUSH' | 'EMAIL';
export type NotificationSeverity = 'INFO' | 'AVISO' | 'GRAVE';

export interface NotificationRecord {
  readonly id: string;
  readonly at: string;
  readonly type: string;
  readonly severity: NotificationSeverity;
  readonly title: string;
  readonly body: string | null;
  readonly targetRole: string | null;
  readonly targetUserId: string | null;
  readonly channels: readonly NotificationChannel[];
  readonly refType: string | null;
  readonly refId: string | null;
  readonly payload: Readonly<Record<string, unknown>>;
}

export interface SendNotificationInput {
  readonly title: string;
  readonly body?: string | null;
  readonly severity?: NotificationSeverity;
  readonly type?: string;
  readonly targetRole?: string | null;
  readonly targetUserId?: string | null;
  readonly channels?: readonly NotificationChannel[];
  readonly refType?: string | null;
  readonly refId?: string | null;
  readonly payload?: Readonly<Record<string, unknown>>;
}

const CHANNELS: readonly string[] = ['IN_APP', 'PUSH', 'EMAIL'];
const SEVERITIES: readonly string[] = ['INFO', 'AVISO', 'GRAVE'];

function asChannels(value: unknown): readonly NotificationChannel[] {
  if (!Array.isArray(value)) return ['IN_APP'];
  const parsed = value
    .map((item) => String(item))
    .filter((item) => CHANNELS.includes(item));
  return parsed.length > 0 ? (parsed as readonly NotificationChannel[]) : ['IN_APP'];
}

function asSeverity(value: unknown): NotificationSeverity {
  const text = String(value ?? 'AVISO');
  return (SEVERITIES.includes(text) ? text : 'AVISO') as NotificationSeverity;
}

function asString(value: unknown): string | null {
  return typeof value === 'string' && value !== '' ? value : null;
}

/**
 * Modulo de notificaciones.
 * En el Bloque 0 persiste en memoria; en produccion escribe en
 * notify.notifications y un worker reparte por push/email.
 */
export class NotifyService {
  private readonly records: NotificationRecord[] = [];
  private readonly pending: DomainEvent[] = [];
  private readonly clock: Clock;
  private readonly ids: IdGenerator;
  private readonly events: EventFactory;

  constructor(options: { clock: Clock; ids: IdGenerator; storeId: string }) {
    this.clock = options.clock;
    this.ids = options.ids;
    this.events = createEventFactory({ clock: options.clock, ids: options.ids, storeId: options.storeId });
  }

  drainEvents(): readonly DomainEvent[] {
    const drained = [...this.pending];
    this.pending.length = 0;
    return drained;
  }

  send(input: SendNotificationInput): NotificationRecord {
    const record: NotificationRecord = Object.freeze({
      id: this.ids.next(),
      at: this.clock.nowIso(),
      type: input.type ?? 'GENERICA',
      severity: input.severity ?? 'AVISO',
      title: input.title,
      body: input.body ?? null,
      targetRole: input.targetRole ?? null,
      targetUserId: input.targetUserId ?? null,
      channels: [...(input.channels ?? ['IN_APP'])],
      refType: input.refType ?? null,
      refId: input.refId ?? null,
      payload: input.payload ?? {},
    });

    this.records.push(record);

    this.pending.push(
      this.events.create(
        'notification.sent',
        {
          notificationId: record.id,
          type: record.type,
          severity: record.severity,
          title: record.title,
          targetRole: record.targetRole,
          targetUserId: record.targetUserId,
          channels: record.channels,
          refType: record.refType,
          refId: record.refId,
        },
        { actorId: null },
      ),
    );

    return record;
  }

  all(): readonly NotificationRecord[] {
    return this.records;
  }

  byRole(role: string): readonly NotificationRecord[] {
    return this.records.filter((record) => record.targetRole === role);
  }

  bySeverity(severity: NotificationSeverity): readonly NotificationRecord[] {
    return this.records.filter((record) => record.severity === severity);
  }

  count(): number {
    return this.records.length;
  }
}

/**
 * Accion NOTIFY que el motor de reglas ejecuta.
 * Traduce los parametros del JSONB de la regla al caso de uso del modulo.
 */
export function notifyAction(service: NotifyService): ActionHandler {
  return {
    type: 'NOTIFY',
    execute(params: Readonly<Record<string, unknown>>, ctx: ActionContext): ActionResult {
      const target = asString(params['target']) ?? 'ROLE';

      const record = service.send({
        title: asString(params['title']) ?? 'Aviso del motor de reglas',
        body: asString(params['body']),
        severity: asSeverity(params['severity']),
        type: asString(params['type']) ?? 'REGLA',
        targetRole: target === 'ROLE' ? asString(params['role']) : null,
        targetUserId: target === 'USER' ? asString(params['userId']) : null,
        channels: asChannels(params['channels']),
        refType: 'rule',
        refId: ctx.ruleCode,
        payload: { ruleCode: ctx.ruleCode, eventId: ctx.event.eventId, params },
      });

      return {
        ok: true,
        detail: { notificationId: record.id, severity: record.severity, targetRole: record.targetRole },
      };
    },
  };
}
