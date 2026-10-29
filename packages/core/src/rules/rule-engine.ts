import type { DomainEvent } from '../../../contracts/src/domain-event.ts';
import type {
  ActionContext,
  Clock,
  FactContext,
  Logger,
  RuleDefinition,
} from '../../../contracts/src/ports.ts';
import { ConditionEvaluator } from './condition-evaluator.ts';
import type { ConditionTraceNode } from './condition-evaluator.ts';
import type { ActionRegistry } from './action-registry.ts';
import type { FactRegistry } from './fact-registry.ts';
import type { AuditLog } from '../audit/audit-log.ts';
import type { EventSubscriber } from '../registry/registrar.ts';

export type RuleResult =
  | 'DISPARADA'
  | 'SIN_COINCIDENCIA'
  | 'ERROR'
  | 'OMITIDA_COOLDOWN'
  | 'OMITIDA_LIMITE';

export interface ExecutedAction {
  readonly type: string;
  readonly ok: boolean;
  readonly detail: Readonly<Record<string, unknown>> | null;
  readonly error: string | null;
}

/** Auditoria de cada decision del motor (equivale a rules.rule_executions). */
export interface RuleExecution {
  readonly ruleId: string;
  readonly ruleCode: string;
  readonly ruleVersion: number;
  readonly storeId: string;
  readonly eventId: string;
  readonly eventType: string;
  readonly matched: boolean;
  readonly result: RuleResult;
  readonly actionsExecuted: readonly ExecutedAction[];
  readonly trace: readonly ConditionTraceNode[];
  readonly durationMs: number;
  readonly at: string;
  readonly error: string | null;
}

export interface RuleRepository {
  activeRulesFor(eventType: string, storeId: string): readonly RuleDefinition[];
  record(execution: RuleExecution): void;
  executions(): readonly RuleExecution[];
  /** Fecha ISO del ultimo disparo efectivo de la regla, o null si nunca disparo. */
  lastDispatchAt(ruleId: string): string | null;
  /** Numero de disparos efectivos de la regla en un dia (YYYY-MM-DD). */
  dispatchCountOn(ruleId: string, dayIso: string): number;
}

/** Repositorio en memoria. En produccion lee rules.rules y escribe rule_executions. */
export class InMemoryRuleRepository implements RuleRepository {
  private readonly rules: RuleDefinition[] = [];
  private readonly history: RuleExecution[] = [];

  add(rule: RuleDefinition): void {
    this.rules.push(rule);
  }

  addAll(rules: readonly RuleDefinition[]): void {
    for (const rule of rules) this.add(rule);
  }

  /** Reglas activas del evento, ordenadas por prioridad (menor numero = antes). */
  activeRulesFor(eventType: string, storeId: string): readonly RuleDefinition[] {
    return this.rules
      .filter(
        (rule) => rule.isActive && rule.eventType === eventType && rule.storeId === storeId,
      )
      .sort((a, b) => (a.priority === b.priority ? a.code.localeCompare(b.code) : a.priority - b.priority));
  }

  record(execution: RuleExecution): void {
    this.history.push(execution);
  }

  executions(): readonly RuleExecution[] {
    return this.history;
  }

  /** Momento del ultimo disparo efectivo de una regla (para el cooldown). */
  lastDispatchAt(ruleId: string): string | null {
    const dispatches = this.history
      .filter((execution) => execution.ruleId === ruleId && execution.result === 'DISPARADA')
      .map((execution) => execution.at)
      .sort();
    return dispatches.length > 0 ? (dispatches[dispatches.length - 1] ?? null) : null;
  }

  /** Disparos de una regla en un dia UTC (para max_per_day). */
  dispatchCountOn(ruleId: string, dayIso: string): number {
    return this.history.filter(
      (execution) =>
        execution.ruleId === ruleId &&
        execution.result === 'DISPARADA' &&
        execution.at.slice(0, 10) === dayIso,
    ).length;
  }

  size(): number {
    return this.rules.length;
  }
}

export interface RuleEngineOptions {
  readonly rules: RuleRepository;
  readonly facts: FactRegistry;
  readonly actions: ActionRegistry;
  readonly clock: Clock;
  readonly logger?: Logger;
  readonly audit?: AuditLog;
  /**
   * Si es true, un fallo al ejecutar acciones propaga la excepcion para que el
   * outbox reintente el evento. En el host de produccion se activa.
   */
  readonly throwOnError?: boolean;
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

/**
 * Sustituye referencias `"$event.lotId"` por el valor real del evento.
 * Busca primero en payload y, si no existe, en la raiz del evento.
 */
export function resolveEventRefs(value: unknown, event: DomainEvent): unknown {
  if (typeof value === 'string') {
    if (!value.startsWith('$event.')) return value;
    const path = value.slice('$event.'.length).split('.');
    const fromPayload = path.reduce<unknown>(
      (acc, key) => (isPlainObject(acc) ? acc[key] : undefined),
      event.payload,
    );
    if (fromPayload !== undefined) return fromPayload;
    return path.reduce<unknown>(
      (acc, key) => (isPlainObject(acc) ? acc[key] : undefined),
      event as unknown,
    );
  }
  if (Array.isArray(value)) return value.map((item) => resolveEventRefs(item, event));
  if (isPlainObject(value)) {
    const out: Record<string, unknown> = {};
    for (const [key, item] of Object.entries(value)) out[key] = resolveEventRefs(item, event);
    return out;
  }
  return value;
}

/**
 * Motor ECA (Evento-Condicion-Accion).
 * No conoce ningun modulo: pide facts y ejecuta acciones por clave/tipo.
 */
export class RuleEngine {
  private readonly rules: RuleRepository;
  private readonly facts: FactRegistry;
  private readonly actions: ActionRegistry;
  private readonly clock: Clock;
  private readonly logger: Logger | null;
  private readonly audit: AuditLog | null;
  private readonly throwOnError: boolean;

  constructor(options: RuleEngineOptions) {
    this.rules = options.rules;
    this.facts = options.facts;
    this.actions = options.actions;
    this.clock = options.clock;
    this.logger = options.logger ?? null;
    this.audit = options.audit ?? null;
    this.throwOnError = options.throwOnError ?? false;
  }

  /** Suscripcion comodin: el motor ve todos los eventos del sistema. */
  subscriber(): EventSubscriber {
    return {
      id: 'rule-engine',
      eventType: '*',
      handler: async (event: DomainEvent) => {
        await this.handle(event);
      },
    };
  }

  async handle(event: DomainEvent): Promise<readonly RuleExecution[]> {
    const candidates = this.rules.activeRulesFor(event.eventType, event.storeId);
    const executions: RuleExecution[] = [];

    for (const rule of candidates) {
      const execution = await this.evaluateRule(rule, event);
      if (execution === null) continue;
      executions.push(execution);
      this.rules.record(execution);
    }

    return executions;
  }

  /** Devuelve null si la regla no aplica hoy (fuera de valid_from / valid_to). */
  private async evaluateRule(rule: RuleDefinition, event: DomainEvent): Promise<RuleExecution | null> {
    const now = this.clock.now();

    if (rule.validFrom && now.getTime() < new Date(rule.validFrom).getTime()) return null;
    if (rule.validTo && now.getTime() > new Date(rule.validTo).getTime()) return null;

    const startedAt = now.getTime();
    const factContext: FactContext = {
      storeId: event.storeId,
      actorId: event.actorId,
      event,
      now,
    };

    const evaluator = new ConditionEvaluator((key, params) =>
      this.facts.resolve(key, params, factContext),
    );

    let matched = false;
    let trace: readonly ConditionTraceNode[] = [];
    let error: string | null = null;

    try {
      const evaluation = await evaluator.evaluate(rule.condition);
      matched = evaluation.matched;
      trace = evaluation.trace;
    } catch (cause) {
      error = cause instanceof Error ? cause.message : String(cause);
      return this.finish(rule, event, false, 'ERROR', [], trace, startedAt, error);
    }

    if (!matched) {
      return this.finish(rule, event, false, 'SIN_COINCIDENCIA', [], trace, startedAt, null);
    }

    // Solo se comprueban los limites cuando la regla HABRIA disparado.
    if (rule.cooldownMinutes > 0) {
      const lastDispatch = this.rules.lastDispatchAt(rule.id);
      if (lastDispatch) {
        const elapsedMs = now.getTime() - new Date(lastDispatch).getTime();
        if (elapsedMs < rule.cooldownMinutes * 60_000) {
          return this.finish(rule, event, true, 'OMITIDA_COOLDOWN', [], trace, startedAt, null);
        }
      }
    }

    if (rule.maxPerDay !== null && rule.maxPerDay >= 0) {
      const dayIso = this.clock.nowIso().slice(0, 10);
      if (this.rules.dispatchCountOn(rule.id, dayIso) >= rule.maxPerDay) {
        return this.finish(rule, event, true, 'OMITIDA_LIMITE', [], trace, startedAt, null);
      }
    }

    const actionContext: ActionContext = {
      ...factContext,
      ruleId: rule.id,
      ruleCode: rule.code,
    };

    const executed: ExecutedAction[] = [];
    let failed = false;

    for (const action of rule.actions) {
      const params = resolveEventRefs(action.params ?? {}, event) as Record<string, unknown>;
      try {
        const result = await this.actions.execute(action.type, params, actionContext);
        executed.push({
          type: action.type,
          ok: result.ok,
          detail: result.detail ?? null,
          error: null,
        });
        if (!result.ok) failed = true;
      } catch (cause) {
        const message = cause instanceof Error ? cause.message : String(cause);
        executed.push({ type: action.type, ok: false, detail: null, error: message });
        failed = true;
        error = message;
        if (this.throwOnError) {
          this.rules.record(
            this.finish(rule, event, true, 'ERROR', executed, trace, startedAt, message),
          );
          throw cause;
        }
        break;
      }
    }

    return this.finish(
      rule,
      event,
      true,
      failed ? 'ERROR' : 'DISPARADA',
      executed,
      trace,
      startedAt,
      error,
    );
  }

  private finish(
    rule: RuleDefinition,
    event: DomainEvent,
    matched: boolean,
    result: RuleResult,
    actionsExecuted: readonly ExecutedAction[],
    trace: readonly ConditionTraceNode[],
    startedAt: number,
    error: string | null,
  ): RuleExecution {
    const execution: RuleExecution = Object.freeze({
      ruleId: rule.id,
      ruleCode: rule.code,
      ruleVersion: rule.version,
      storeId: rule.storeId,
      eventId: event.eventId,
      eventType: event.eventType,
      matched,
      result,
      actionsExecuted,
      trace,
      durationMs: Math.max(0, this.clock.now().getTime() - startedAt),
      at: this.clock.nowIso(),
      error,
    });

    this.logger?.debug('Regla evaluada', {
      rule: rule.code,
      event: event.eventType,
      result,
    });

    if (result === 'DISPARADA' || result === 'ERROR') {
      this.audit?.append({
        actorId: event.actorId,
        moduleId: 'core',
        action: `rule.${result.toLowerCase()}`,
        refType: 'rule',
        refId: rule.code,
        before: null,
        after: { eventId: event.eventId, actions: actionsExecuted.map((action) => action.type) },
      });
    }

    return execution;
  }
}
