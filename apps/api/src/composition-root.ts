import {
  ActionRegistry,
  AuditLog,
  FactRegistry,
  IdempotencyStore,
  InMemoryEventBus,
  InMemoryRuleRepository,
  OutboxRelay,
  RuleEngine,
  createClock,
  createIdGenerator,
  registerModules,
} from '../../../packages/core/src/index.ts';
import type { ModuleRegistry, ServiceLocator } from '../../../packages/core/src/index.ts';
import type { Clock, DomainEvent, IdGenerator, Logger, LogMeta, RuleDefinition } from '../../../packages/contracts/src/ports.ts';
import type { RoleCode } from '../../../packages/contracts/src/rbac.ts';
import { ROLES, roleLevel } from '../../../packages/contracts/src/rbac.ts';

import { tasksManifest } from '../../../packages/module-tasks/src/manifest.ts';
import {
  InMemoryTeamDirectory,
  TasksService,
  tasksFacts,
} from '../../../packages/module-tasks/src/tasks.service.ts';
import { createTaskAction } from '../../../packages/module-tasks/src/actions/create-task.action.ts';
import { reassignTaskAction } from '../../../packages/module-tasks/src/actions/reassign-task.action.ts';
import { cancelTaskAction } from '../../../packages/module-tasks/src/actions/cancel-task.action.ts';
import { onStockBelowMinimum } from '../../../packages/module-tasks/src/subscribers/on-stock-below-minimum.ts';

import { inventoryManifest } from '../../../packages/module-inventory/src/manifest.ts';
import { InventoryService, inventoryFacts } from '../../../packages/module-inventory/src/inventory.service.ts';

import { posManifest } from '../../../packages/module-pos/src/manifest.ts';
import { PosService, posFacts } from '../../../packages/module-pos/src/pos.service.ts';

import { notifyManifest } from '../../../packages/module-notify/src/manifest.ts';
import { NotifyService, notifyAction } from '../../../packages/module-notify/src/notify.service.ts';

import { storeContextManifest } from '../../../packages/module-store-context/src/manifest.ts';
import {
  StoreContextService,
  storeContextFacts,
} from '../../../packages/module-store-context/src/store-context.service.ts';
import type { AffluenceLevel } from '../../../packages/module-store-context/src/store-context.service.ts';

import { healthcheckManifest } from '../../../packages/module-healthcheck/src/manifest.ts';
import {
  HealthcheckService,
  healthcheckFacts,
} from '../../../packages/module-healthcheck/src/healthcheck.service.ts';

import { loadSeedRules } from './adapters/seed-rules.adapter.ts';
import { Router } from './http/router.ts';
import { AuthController } from './controllers/auth.controller.ts';
import type { AuthUser } from './controllers/auth.controller.ts';
import { TasksController } from './controllers/tasks.controller.ts';
import { InventoryController } from './controllers/inventory.controller.ts';
import { HealthController } from './controllers/health.controller.ts';

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

const LEVEL_ORDER: Record<LogLevel, number> = { debug: 10, info: 20, warn: 30, error: 40 };

/** Logger minimo en JSON por linea. En produccion se sustituye por pino/OTel. */
export function createConsoleLogger(level: LogLevel = 'info'): Logger {
  const threshold = LEVEL_ORDER[level];

  const write = (severity: LogLevel, message: string, meta?: LogMeta): void => {
    if (LEVEL_ORDER[severity] < threshold) return;
    const line = JSON.stringify({ severity, message, ...(meta ?? {}), at: new Date().toISOString() });
    if (severity === 'error' || severity === 'warn') process.stderr.write(`${line}\n`);
    else process.stdout.write(`${line}\n`);
  };

  return {
    debug: (message, meta) => write('debug', message, meta),
    info: (message, meta) => write('info', message, meta),
    warn: (message, meta) => write('warn', message, meta),
    error: (message, meta) => write('error', message, meta),
  };
}

/** Id de tienda del entorno de demostracion (en produccion viene de core.stores). */
export const DEMO_STORE_ID = '11111111-1111-4111-8111-111111111111';

interface DemoUser extends AuthUser {
  readonly userId: string;
  readonly displayName: string;
  readonly role: RoleCode;
}

/**
 * Usuarios de demostracion. Los PIN coinciden con el sufijo de los hashes
 * PLACEHOLDER de db/seed/001_demo_store.sql (gerencia-1234 -> 1234), que son
 * simbolicos: en produccion se guardan hasheados con argon2id.
 */
export const DEMO_USERS: readonly DemoUser[] = [
  {
    userId: 'u-gerencia',
    displayName: 'Marta Ferrer',
    role: ROLES.GERENCIA,
    email: 'gerencia@malato.es',
    pin: '1234',
    session: { id: 'u-gerencia', storeId: DEMO_STORE_ID, role: ROLES.GERENCIA, displayName: 'Marta Ferrer' },
  },
  {
    userId: 'u-coord-1',
    displayName: 'Lucia Sanchis',
    role: ROLES.COORDINADORA,
    email: 'coordinacion1@malato.es',
    pin: '2345',
    session: { id: 'u-coord-1', storeId: DEMO_STORE_ID, role: ROLES.COORDINADORA, displayName: 'Lucia Sanchis' },
  },
  {
    userId: 'u-coord-2',
    displayName: 'Nuria Blasco',
    role: ROLES.COORDINADORA,
    email: 'coordinacion2@malato.es',
    pin: '3456',
    session: { id: 'u-coord-2', storeId: DEMO_STORE_ID, role: ROLES.COORDINADORA, displayName: 'Nuria Blasco' },
  },
  {
    userId: 'u-coord-3',
    displayName: 'Rocio Beltran',
    role: ROLES.COORDINADORA,
    email: 'coordinacion3@malato.es',
    pin: '6789',
    session: { id: 'u-coord-3', storeId: DEMO_STORE_ID, role: ROLES.COORDINADORA, displayName: 'Rocio Beltran' },
  },
  {
    userId: 'u-sala-1',
    displayName: 'Ana Torres',
    role: ROLES.OPERADORA,
    email: 'sala1@malato.es',
    pin: '4567',
    session: { id: 'u-sala-1', storeId: DEMO_STORE_ID, role: ROLES.OPERADORA, displayName: 'Ana Torres' },
  },
  {
    userId: 'u-sala-2',
    displayName: 'Paula Giner',
    role: ROLES.OPERADORA,
    email: 'sala2@malato.es',
    pin: '5678',
    session: { id: 'u-sala-2', storeId: DEMO_STORE_ID, role: ROLES.OPERADORA, displayName: 'Paula Giner' },
  },
];

export interface SystemOptions {
  readonly storeId?: string;
  /** Carga las 5 reglas reales de db/seed/001_demo_store.sql (adaptador de demo). */
  readonly loadRulesFromSeed?: boolean;
  readonly rules?: readonly RuleDefinition[];
  readonly discrepancyThresholdEur?: number;
  readonly affluenceForecast?: AffluenceLevel;
  readonly logLevel?: LogLevel;
  readonly maxAttempts?: number;
  /** Inyectables: los tests pasan un reloj mutable y un logger silencioso. */
  readonly clock?: Clock;
  readonly ids?: IdGenerator;
  readonly logger?: Logger;
}

export interface DispatchSummary {
  readonly rounds: number;
  readonly delivered: number;
}

export interface SystemRuntime {
  readonly storeId: string;
  readonly logger: Logger;
  readonly bus: InMemoryEventBus;
  readonly relay: OutboxRelay;
  readonly registry: ModuleRegistry;
  readonly services: ServiceLocator;
  readonly facts: FactRegistry;
  readonly actions: ActionRegistry;
  readonly audit: AuditLog;
  readonly ruleEngine: RuleEngine;
  readonly ruleRepository: InMemoryRuleRepository;
  readonly tasks: TasksService;
  readonly inventory: InventoryService;
  readonly pos: PosService;
  readonly notify: NotifyService;
  readonly storeContext: StoreContextService;
  readonly healthcheck: HealthcheckService;
  readonly auth: AuthController;
  readonly router: Router;
  /** Vuelca al outbox los eventos generados por los servicios. */
  flushPendingEvents(): number;
  /** Bucle completo: volcar, entregar y repetir mientras haya eventos. */
  dispatch(maxRounds?: number): Promise<DispatchSummary>;
  /** Publica un evento ya construido por un servicio. */
  publish(event: DomainEvent): Promise<DispatchSummary>;
}

/**
 * COMPOSITION ROOT: el UNICO sitio del sistema donde se enumeran los modulos.
 * Anadir un modulo es anadir una entrada aqui; packages/core no cambia nunca y
 * apps/api no gana ni una linea de logica de negocio.
 */
export function createSystem(options: SystemOptions = {}): SystemRuntime {
  const storeId = options.storeId ?? DEMO_STORE_ID;
  const logger = options.logger ?? createConsoleLogger(options.logLevel ?? 'info');

  const clock = options.clock ?? createClock();
  const ids = options.ids ?? createIdGenerator();
  const idempotency = new IdempotencyStore();
  const bus = new InMemoryEventBus({ clock, logger, idempotency });
  const relay = new OutboxRelay({
    clock,
    ids,
    bus,
    logger,
    maxAttempts: options.maxAttempts ?? 3,
    baseBackoffMs: 1_000,
  });
  const outbox = relay.repository();

  const facts = new FactRegistry();
  const actions = new ActionRegistry();
  const audit = new AuditLog(clock, ids);

  const ruleRepository = new InMemoryRuleRepository();
  const ruleEngine = new RuleEngine({ rules: ruleRepository, facts, actions, clock, logger, audit });

  // El motor de reglas ve TODOS los eventos (comodin '*') y se suscribe primero.
  const engineSubscriber = ruleEngine.subscriber();
  bus.subscribe(engineSubscriber.eventType, engineSubscriber.handler, {
    id: 'core:rule-engine',
    moduleId: 'core',
  });

  // --- Servicios de los modulos (se construyen aqui, no dentro del nucleo) ---
  const team = new InMemoryTeamDirectory();
  team.addAll(
    DEMO_USERS.map((user) => ({
      userId: user.userId,
      displayName: user.displayName,
      role: user.role,
      storeId,
      // El nivel es lo que hace jerarquico el reparto: una tarea requerida
      // OPERADORA la puede tomar tambien una COORDINADORA.
      level: roleLevel(user.role),
      // Gerencia NO opera en tienda. Sin este filtro, y al ser el rol de mayor
      // nivel, el motor le asignaria reposiciones de sala.
      assignable: user.role !== ROLES.GERENCIA,
    })),
  );

  const tasks = new TasksService({ clock, ids, storeId, team, logger });
  const inventory = new InventoryService({ clock, ids, storeId, logger });
  const pos = new PosService({
    clock,
    ids,
    storeId,
    logger,
    discrepancyThresholdEur: options.discrepancyThresholdEur ?? 5,
  });
  const notify = new NotifyService({ clock, ids, storeId });
  // El contexto de tienda NO importa al modulo de caja: recibe un puerto.
  const storeContext = new StoreContextService({
    clock,
    affluenceProvider: () => pos.affluenceLevel(),
    forecast: options.affluenceForecast ?? 'MEDIUM',
  });
  const healthcheck = new HealthcheckService(clock);

  // --- Registro: cada modulo aporta manifiesto, facts, acciones y suscriptores ---
  const registered = registerModules({
    modules: [
      {
        manifest: tasksManifest,
        facts: tasksFacts(tasks),
        actions: [createTaskAction(tasks), reassignTaskAction(tasks), cancelTaskAction(tasks)],
        subscribers: [onStockBelowMinimum(tasks)],
        services: { tasks },
      },
      {
        manifest: inventoryManifest,
        facts: inventoryFacts(inventory),
        services: { inventory },
      },
      {
        manifest: posManifest,
        facts: posFacts(pos),
        services: { pos },
      },
      {
        manifest: notifyManifest,
        actions: [notifyAction(notify)],
        services: { notify },
      },
      {
        manifest: storeContextManifest,
        facts: storeContextFacts(storeContext),
        services: { storeContext },
      },
      {
        manifest: healthcheckManifest,
        facts: healthcheckFacts(healthcheck),
        // Clave generica 'health': el host lo descubre por convencion, no por nombre.
        services: { health: healthcheck },
      },
    ],
    bus,
    facts,
    actions,
    logger,
  });

  // --- Reglas ------------------------------------------------------------------
  // En produccion un repositorio PostgreSQL lee de la tabla rules.rules.
  // El adaptador de demo existe solo para el Bloque 0 y para los tests.
  if (options.rules) ruleRepository.addAll(options.rules);
  if (!options.rules && options.loadRulesFromSeed !== false) {
    ruleRepository.addAll(loadSeedRules({ storeId }));
  }

  // --- Entrada HTTP ------------------------------------------------------------
  const auth = new AuthController(DEMO_USERS);
  const router = new Router();

  const flushPendingEvents = (): number => {
    let flushed = 0;
    for (const service of [tasks, inventory, pos, notify]) {
      for (const event of service.drainEvents()) {
        outbox.add(event);
        flushed += 1;
      }
    }
    return flushed;
  };

  const dispatch = async (maxRounds = 10): Promise<DispatchSummary> => {
    let rounds = 0;
    let delivered = 0;

    for (let round = 0; round < maxRounds; round += 1) {
      flushPendingEvents();
      const result = await relay.drain();
      delivered += result.processed;
      rounds += 1;
      if (result.due === 0) break;
    }

    // Los manejadores pueden haber generado eventos de cola.
    flushPendingEvents();
    return { rounds, delivered };
  };

  new TasksController(tasks).register(router);
  new InventoryController(inventory).register(router);
  new HealthController({
    registry: registered.registry,
    services: registered.services,
    outbox,
    describeRoutes: () => router.describe(),
  }).register(router);
  auth.register(router);

  logger.info('Sistema compuesto', {
    storeId,
    modules: registered.registry.ids(),
    facts: facts.size(),
    actions: actions.size(),
    rules: ruleRepository.size(),
    subscriptions: registered.wiredSubscriptions.length + 1,
  });

  return {
    storeId,
    logger,
    bus,
    relay,
    registry: registered.registry,
    services: registered.services,
    facts,
    actions,
    audit,
    ruleEngine,
    ruleRepository,
    tasks,
    inventory,
    pos,
    notify,
    storeContext,
    healthcheck,
    auth,
    router,
    flushPendingEvents,
    dispatch,
    publish: async (event: DomainEvent) => {
      outbox.add(event);
      return dispatch();
    },
  };
}
