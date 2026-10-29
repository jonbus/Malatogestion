import type { DomainEvent } from '../../contracts/src/domain-event.ts';
import type {
  Clock,
  FactResolver,
  IdGenerator,
  Logger,
} from '../../contracts/src/ports.ts';
import type { RoleCode } from '../../contracts/src/rbac.ts';
import { roleLevel } from '../../contracts/src/rbac.ts';
import { createEventFactory } from '../../core/src/events/event-factory.ts';
import type { EventFactory } from '../../core/src/events/event-factory.ts';
import { canTransition, isOpenStatus, priorityWeight } from './domain/task.ts';
import type {
  AssignmentStrategy,
  TaskEventRecord,
  TaskEventType,
  TaskPriority,
  TaskRecord,
  TaskStatus,
} from './domain/task.ts';

export interface TeamMember {
  readonly userId: string;
  readonly displayName: string;
  readonly role: RoleCode;
  readonly storeId: string;
  /** Nivel del rol (contracts ROLE_LEVELS). Es lo que permite comparar roles. */
  readonly level: number;
  /**
   * Si esta persona entra en el reparto de tareas de sala. Gerencia no: no opera
   * en la tienda. Sin este filtro, como el nivel de Gerencia (30) supera al de
   * cualquier tarea, el motor le asignaria reposiciones.
   */
  readonly assignable: boolean;
}

/** Directorio del equipo: el modulo de tareas no sabe de usuarios, se lo inyectan. */
export interface TeamDirectory {
  membersByRole(storeId: string, role: RoleCode): readonly TeamMember[];
  /**
   * Candidatos para una tarea: nivel MAYOR O IGUAL al requerido y asignables.
   * Es la traduccion del rol jerarquico: una COORDINADORA (20) entra en una tarea
   * requerida OPERADORA (10).
   */
  membersAtLeast(storeId: string, minLevel: number): readonly TeamMember[];
}

export class InMemoryTeamDirectory implements TeamDirectory {
  private readonly members: TeamMember[] = [];

  add(member: TeamMember): void {
    this.members.push(member);
  }

  addAll(members: readonly TeamMember[]): void {
    for (const member of members) this.add(member);
  }

  membersByRole(storeId: string, role: RoleCode): readonly TeamMember[] {
    return this.members.filter((member) => member.storeId === storeId && member.role === role);
  }

  membersAtLeast(storeId: string, minLevel: number): readonly TeamMember[] {
    return this.members.filter(
      (member) => member.storeId === storeId && member.assignable && member.level >= minLevel,
    );
  }

  all(): readonly TeamMember[] {
    return this.members;
  }
}

export class TaskNotFoundError extends Error {
  constructor(taskId: string) {
    super(`Tarea no encontrada: '${taskId}'`);
    this.name = 'TaskNotFoundError';
  }
}

export class TaskTransitionError extends Error {
  constructor(from: TaskStatus, to: TaskStatus) {
    super(`Transicion de tarea no permitida: ${from} -> ${to}`);
    this.name = 'TaskTransitionError';
  }
}

/**
 * Otra persona modifico la tarea entre la lectura y la escritura. NO es un fallo
 * del sistema: es una condicion de carrera real entre coordinadoras trabajando el
 * mismo Kanban, y el usuario tiene que enterarse en lugar de perder su cambio.
 */
export class TaskVersionConflictError extends Error {
  readonly taskId: string;
  readonly expectedVersion: number;
  readonly actualVersion: number;

  constructor(taskId: string, expectedVersion: number, actualVersion: number) {
    super(
      `La tarea ${taskId} cambio desde que la leiste (esperabas la version ${expectedVersion}, ` +
        `ahora es la ${actualVersion}). Otra persona la movio: recarga el tablero antes de reasignar.`,
    );
    this.name = 'TaskVersionConflictError';
    this.taskId = taskId;
    this.expectedVersion = expectedVersion;
    this.actualVersion = actualVersion;
  }
}

export interface CreateTaskInput {
  readonly title: string;
  readonly description?: string | null;
  readonly priority?: TaskPriority;
  readonly assigneeId?: string | null;
  readonly locationId?: string | null;
  readonly dueAt?: string | null;
  readonly templateCode?: string | null;
  readonly createdBy?: string | null;
  readonly createdByRuleId?: string | null;
  readonly payload?: Readonly<Record<string, unknown>>;
  readonly parentTaskId?: string | null;
}

export interface TasksServiceOptions {
  readonly clock: Clock;
  readonly ids: IdGenerator;
  readonly storeId: string;
  readonly team: TeamDirectory;
  readonly logger?: Logger;
}

function asString(value: unknown): string | null {
  return typeof value === 'string' && value !== '' ? value : null;
}

/**
 * Motor de tareas: casos de uso en memoria.
 * Cada mutacion deja un task_event (historial) y emite un evento de dominio.
 */
export class TasksService {
  private readonly tasks = new Map<string, TaskRecord>();
  private readonly history: TaskEventRecord[] = [];
  private readonly pending: DomainEvent[] = [];
  private readonly clock: Clock;
  private readonly ids: IdGenerator;
  private readonly storeId: string;
  private readonly team: TeamDirectory;
  private readonly events: EventFactory;
  private readonly logger: Logger | null;
  private readonly roundRobin = new Map<string, number>();

  constructor(options: TasksServiceOptions) {
    this.clock = options.clock;
    this.ids = options.ids;
    this.storeId = options.storeId;
    this.team = options.team;
    this.events = createEventFactory({ clock: options.clock, ids: options.ids, storeId: options.storeId });
    this.logger = options.logger ?? null;
  }

  drainEvents(): readonly DomainEvent[] {
    const drained = [...this.pending];
    this.pending.length = 0;
    return drained;
  }

  private emit(eventType: string, payload: Record<string, unknown>, actorId: string | null): DomainEvent {
    const event = this.events.create(eventType, payload, { actorId });
    this.pending.push(event);
    return event;
  }

  private appendEvent(
    task: TaskRecord,
    type: TaskEventType,
    change: {
      fromUserId?: string | null;
      toUserId?: string | null;
      fromStatus?: TaskStatus | null;
      toStatus?: TaskStatus | null;
      comment?: string | null;
    },
  ): void {
    this.history.push(
      Object.freeze({
        id: this.ids.next(),
        taskId: task.id,
        storeId: task.storeId,
        type,
        fromUserId: change.fromUserId ?? null,
        toUserId: change.toUserId ?? null,
        fromStatus: change.fromStatus ?? null,
        toStatus: change.toStatus ?? null,
        comment: change.comment ?? null,
        at: this.clock.nowIso(),
      }),
    );
  }

  private replace(taskId: string, patch: Partial<TaskRecord>): TaskRecord {
    const current = this.tasks.get(taskId);
    if (!current) throw new TaskNotFoundError(taskId);
    const updated: TaskRecord = Object.freeze({
      ...current,
      ...patch,
      // Todo cambio invalida cualquier lectura previa. Es la base del bloqueo
      // optimista: si la version no avanza, un cliente con datos viejos no se
      // entera de que los suyos ya no valen.
      version: current.version + 1,
      updatedAt: this.clock.nowIso(),
    });
    this.tasks.set(taskId, updated);
    return updated;
  }

  // ------------------------------------------------------------------
  // Casos de uso
  // ------------------------------------------------------------------

  createTask(input: CreateTaskInput): TaskRecord {
    const nowIso = this.clock.nowIso();
    const assigneeId = input.assigneeId ?? null;

    const task: TaskRecord = Object.freeze({
      id: this.ids.next(),
      storeId: this.storeId,
      templateCode: input.templateCode ?? null,
      title: input.title,
      description: input.description ?? null,
      priority: input.priority ?? 'MEDIA',
      status: assigneeId ? 'ASIGNADA' : 'PENDIENTE',
      assigneeId,
      locationId: input.locationId ?? null,
      dueAt: input.dueAt ?? null,
      startedAt: null,
      completedAt: null,
      cancelledAt: null,
      cancelReason: null,
      createdBy: input.createdBy ?? null,
      createdByRuleId: input.createdByRuleId ?? null,
      payload: input.payload ?? {},
      evidence: [],
      parentTaskId: input.parentTaskId ?? null,
      version: 1,
      createdAt: nowIso,
      updatedAt: nowIso,
    });

    this.tasks.set(task.id, task);
    this.appendEvent(task, 'CREADA', { toUserId: assigneeId, toStatus: task.status });
    this.emit(
      'task.created',
      {
        taskId: task.id,
        title: task.title,
        priority: task.priority,
        status: task.status,
        assigneeId,
        templateCode: task.templateCode,
        createdByRuleId: task.createdByRuleId,
        locationId: task.locationId,
        dueAt: task.dueAt,
      },
      input.createdBy ?? null,
    );

    if (assigneeId) {
      this.emit(
        'task.assigned',
        { taskId: task.id, assigneeId, assignedBy: input.createdBy ?? null, reason: 'CREACION' },
        input.createdBy ?? null,
      );
    }

    return task;
  }

  assign(taskId: string, toUserId: string, byUserId: string | null, reason = 'ASIGNACION'): TaskRecord {
    const task = this.require(taskId);
    this.assertTransition(task.status, 'ASIGNADA');

    const updated = this.replace(taskId, { status: 'ASIGNADA', assigneeId: toUserId });
    this.appendEvent(updated, 'ASIGNADA', {
      fromUserId: task.assigneeId,
      toUserId,
      fromStatus: task.status,
      toStatus: 'ASIGNADA',
      comment: reason,
    });
    this.emit('task.assigned', { taskId, assigneeId: toUserId, assignedBy: byUserId, reason }, byUserId);
    return updated;
  }

  /**
   * Reasigna una tarea. Si `expectedVersion` viene informada —y en el Kanban de las
   * coordinadoras SIEMPRE viene—, se contrasta con la version actual: una version
   * obsoleta lanza TaskVersionConflictError en lugar de pisar el cambio de otra
   * persona. Pasar null la omite, y solo es aceptable en flujos sin interfaz humana
   * (por ejemplo, una accion automatica del motor sobre una tarea que acaba de leer).
   */
  reassign(
    taskId: string,
    toUserId: string,
    byUserId: string | null,
    reason: string,
    expectedVersion: number | null = null,
  ): TaskRecord {
    const task = this.require(taskId);
    if (expectedVersion !== null && expectedVersion !== task.version) {
      throw new TaskVersionConflictError(taskId, expectedVersion, task.version);
    }

    const updated = this.replace(taskId, { status: 'ASIGNADA', assigneeId: toUserId });
    this.appendEvent(updated, 'REASIGNADA', {
      fromUserId: task.assigneeId,
      toUserId,
      fromStatus: task.status,
      toStatus: 'ASIGNADA',
      comment: reason,
    });
    this.emit(
      'task.reassigned',
      { taskId, fromUserId: task.assigneeId, toUserId, byUserId, reason },
      byUserId,
    );
    return updated;
  }

  start(taskId: string, userId: string | null): TaskRecord {
    const task = this.require(taskId);
    this.assertTransition(task.status, 'EN_CURSO');
    const updated = this.replace(taskId, { status: 'EN_CURSO', startedAt: this.clock.nowIso() });
    this.appendEvent(updated, 'INICIADA', {
      fromUserId: task.assigneeId,
      fromStatus: task.status,
      toStatus: 'EN_CURSO',
    });
    this.emit('task.started', { taskId, assigneeId: task.assigneeId }, userId);
    return updated;
  }

  block(taskId: string, userId: string | null, comment: string): TaskRecord {
    const task = this.require(taskId);
    this.assertTransition(task.status, 'BLOQUEADA');
    const updated = this.replace(taskId, { status: 'BLOQUEADA' });
    this.appendEvent(updated, 'BLOQUEADA', {
      fromStatus: task.status,
      toStatus: 'BLOQUEADA',
      comment,
    });
    this.emit('task.blocked', { taskId, comment }, userId);
    return updated;
  }

  complete(taskId: string, userId: string | null, evidence: readonly unknown[] = []): TaskRecord {
    const task = this.require(taskId);
    this.assertTransition(task.status, 'HECHA');

    const completedAt = this.clock.nowIso();
    const updated = this.replace(taskId, {
      status: 'HECHA',
      completedAt,
      evidence: [...evidence],
    });

    const durationMin = task.startedAt
      ? Math.max(0, Math.round((Date.parse(completedAt) - Date.parse(task.startedAt)) / 60_000))
      : null;

    this.appendEvent(updated, 'COMPLETADA', {
      fromUserId: task.assigneeId,
      fromStatus: task.status,
      toStatus: 'HECHA',
    });
    this.emit(
      'task.completed',
      { taskId, assigneeId: task.assigneeId, durationMin, templateCode: task.templateCode },
      userId,
    );
    return updated;
  }

  cancel(taskId: string, userId: string | null, reason: string): TaskRecord {
    const task = this.require(taskId);
    this.assertTransition(task.status, 'CANCELADA');
    const updated = this.replace(taskId, {
      status: 'CANCELADA',
      cancelledAt: this.clock.nowIso(),
      cancelReason: reason,
    });
    this.appendEvent(updated, 'CANCELADA', {
      fromStatus: task.status,
      toStatus: 'CANCELADA',
      comment: reason,
    });
    this.emit('task.cancelled', { taskId, reason, assigneeId: task.assigneeId }, userId);
    return updated;
  }

  /** Barrido de vencimientos: emite task.overdue por cada tarea pasada de fecha. */
  sweepOverdue(actorId: string | null = null): readonly DomainEvent[] {
    const emitted: DomainEvent[] = [];
    for (const task of this.overdue()) {
      emitted.push(
        this.emit(
          'task.overdue',
          {
            taskId: task.id,
            assigneeId: task.assigneeId,
            status: task.status,
            priority: task.priority,
            dueAt: task.dueAt,
            minutesOverdue: this.minutesOverdue(task),
          },
          actorId,
        ),
      );
      this.appendEvent(task, 'VENCIDA', { fromStatus: task.status, toStatus: task.status });
    }
    return emitted;
  }

  // ------------------------------------------------------------------
  // Consultas
  // ------------------------------------------------------------------

  require(taskId: string): TaskRecord {
    const task = this.tasks.get(taskId);
    if (!task) throw new TaskNotFoundError(taskId);
    return task;
  }

  task(taskId: string): TaskRecord | undefined {
    return this.tasks.get(taskId);
  }

  all(): readonly TaskRecord[] {
    return [...this.tasks.values()];
  }

  tasksOf(userId: string): readonly TaskRecord[] {
    return this.all()
      .filter((task) => task.assigneeId === userId && isOpenStatus(task.status))
      .sort((a, b) => priorityWeight(a.priority) - priorityWeight(b.priority));
  }

  openTaskCount(userId: string): number {
    return this.all().filter((task) => task.assigneeId === userId && isOpenStatus(task.status)).length;
  }

  /** Tablero: tareas abiertas ordenadas por urgencia (lo que ve coordinacion). */
  board(storeId = this.storeId): readonly TaskRecord[] {
    return this.all()
      .filter((task) => task.storeId === storeId && isOpenStatus(task.status))
      .sort((a, b) => {
        const byPriority = priorityWeight(a.priority) - priorityWeight(b.priority);
        if (byPriority !== 0) return byPriority;
        return (a.dueAt ?? '9999').localeCompare(b.dueAt ?? '9999');
      });
  }

  overdue(now: Date = this.clock.now()): readonly TaskRecord[] {
    return this.all().filter((task) => {
      if (!isOpenStatus(task.status)) return false;
      if (!task.dueAt) return false;
      return Date.parse(task.dueAt) < now.getTime();
    });
  }

  minutesOverdue(task: TaskRecord, now: Date = this.clock.now()): number {
    if (!task.dueAt) return 0;
    return Math.max(0, Math.round((now.getTime() - Date.parse(task.dueAt)) / 60_000));
  }

  historyOf(taskId: string): readonly TaskEventRecord[] {
    return this.history.filter((entry) => entry.taskId === taskId);
  }

  allHistory(): readonly TaskEventRecord[] {
    return this.history;
  }

  /**
   * Reparto por estrategia. `role` es el rol MINIMO de la tarea, no el exclusivo:
   * los candidatos son quienes tienen nivel >= ese rol y entran en el reparto de
   * sala (Gerencia queda fuera, no opera en tienda).
   * LEAST_LOADED = quien menos tareas abiertas tenga.
   */
  pickAssignee(
    role: RoleCode,
    strategy: AssignmentStrategy,
    excludeUserId: string | null = null,
  ): string | null {
    const minLevel = roleLevel(role);
    const candidates = this.team
      .membersAtLeast(this.storeId, minLevel)
      .filter((member) => member.userId !== excludeUserId);

    if (candidates.length === 0) return null;

    if (strategy === 'ROUND_ROBIN') {
      // Clave por NIVEL, no por rol: el turno rota entre las 5 personas de sala en
      // lugar de girar en dos circulos separados (operadoras por un lado,
      // coordinadoras por otro), que es justo lo que se quiere evitar.
      const key = `${this.storeId}:${minLevel}`;
      const index = this.roundRobin.get(key) ?? 0;
      this.roundRobin.set(key, index + 1);
      return candidates[index % candidates.length]?.userId ?? null;
    }

    const ranked = [...candidates].sort((a, b) => {
      const loadA = this.openTaskCount(a.userId);
      const loadB = this.openTaskCount(b.userId);
      if (loadA !== loadB) return loadA - loadB;
      return a.displayName.localeCompare(b.displayName);
    });

    return ranked[0]?.userId ?? null;
  }

  private assertTransition(from: TaskStatus, to: TaskStatus): void {
    if (!canTransition(from, to)) {
      this.logger?.warn('Transicion rechazada', { from, to });
      throw new TaskTransitionError(from, to);
    }
  }
}

/** Facts que el modulo aporta al motor de reglas. */
export function tasksFacts(service: TasksService): Record<string, FactResolver> {
  // Devuelven el VALOR CRUDO: FactRegistry es quien lo envuelve en { found, value }.
  return {
    'tasks.open_by_user': (params, ctx) => {
      const userId = asString(params['userId']) ?? asString(ctx.event.payload['assigneeId']);
      return userId ? service.openTaskCount(userId) : null;
    },

    'tasks.minutes_overdue': (params, ctx) => {
      const fromPayload = ctx.event.payload['minutesOverdue'];
      if (typeof fromPayload === 'number') return fromPayload;

      const taskId = asString(params['taskId']) ?? asString(ctx.event.payload['taskId']);
      const task = taskId ? service.task(taskId) : undefined;
      return task ? service.minutesOverdue(task, ctx.now) : null;
    },

    'tasks.status': (params, ctx) => {
      const fromPayload = asString(ctx.event.payload['status']);
      if (fromPayload) return fromPayload;

      const taskId = asString(params['taskId']) ?? asString(ctx.event.payload['taskId']);
      const task = taskId ? service.task(taskId) : undefined;
      return task ? task.status : null;
    },
  };
}
