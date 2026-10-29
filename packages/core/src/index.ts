export { UuidGenerator, createIdGenerator } from './ids.ts';
export { SystemClock, createClock } from './clock.ts';
export { ok, err, unwrap } from './result.ts';
export type { Result } from './result.ts';

export {
  can,
  canAny,
  assertCan,
  permissionsOf,
  isSuperRole,
  PermissionDeniedError,
} from './rbac/permissions.ts';
export type { RolePolicy } from './rbac/permissions.ts';

export { ModuleRegistry, ModuleRegistrationError } from './registry/module-registry.ts';
export type { RegisteredModule } from './registry/module-registry.ts';
export { registerModules, ServiceLocator } from './registry/registrar.ts';
export type {
  ModuleImplementation,
  EventSubscriber,
  RegistrarInput,
  RegisteredSystem,
} from './registry/registrar.ts';

export { InMemoryEventBus } from './events/event-bus.ts';
export type { EventBusOptions } from './events/event-bus.ts';
export { IdempotencyStore } from './events/idempotency.ts';
export { InMemoryOutbox, OutboxRelay } from './events/outbox.ts';
export type { OutboxOptions, RelayOptions, RelayResult } from './events/outbox.ts';
export { createEventFactory } from './events/event-factory.ts';
export type { EventFactory } from './events/event-factory.ts';

export { ConditionEvaluator, ConditionError, OPERATORS } from './rules/condition-evaluator.ts';
export type {
  ConditionEvaluation,
  ConditionTraceNode,
  FactLookup,
  Operator,
} from './rules/condition-evaluator.ts';
export {
  FactRegistry,
  UnknownFactError,
  DuplicateFactError,
  describeFacts,
} from './rules/fact-registry.ts';
export {
  ActionRegistry,
  UnknownActionError,
  DuplicateActionError,
} from './rules/action-registry.ts';
export {
  RuleEngine,
  InMemoryRuleRepository,
  resolveEventRefs,
} from './rules/rule-engine.ts';
export type {
  RuleResult,
  RuleExecution,
  ExecutedAction,
  RuleRepository,
  RuleEngineOptions,
} from './rules/rule-engine.ts';

export { AuditLog } from './audit/audit-log.ts';
export type { AuditEntry, AuditInput } from './audit/audit-log.ts';
