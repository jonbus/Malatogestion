/**
 * Dominio de tareas: tipos y reglas puras.
 * Este fichero NO importa infraestructura, ni HTTP, ni framework alguno:
 * es TypeScript puro y por tanto testeable al 100%.
 */

export const TASK_PRIORITY = {
  BAJA: 'BAJA',
  MEDIA: 'MEDIA',
  ALTA: 'ALTA',
  URGENTE: 'URGENTE',
} as const;

export type TaskPriority = (typeof TASK_PRIORITY)[keyof typeof TASK_PRIORITY];

export const TASK_STATUS = {
  PENDIENTE: 'PENDIENTE',
  ASIGNADA: 'ASIGNADA',
  EN_CURSO: 'EN_CURSO',
  BLOQUEADA: 'BLOQUEADA',
  HECHA: 'HECHA',
  CANCELADA: 'CANCELADA',
} as const;

export type TaskStatus = (typeof TASK_STATUS)[keyof typeof TASK_STATUS];

export const TASK_EVENT_TYPE = {
  CREADA: 'CREADA',
  ASIGNADA: 'ASIGNADA',
  REASIGNADA: 'REASIGNADA',
  INICIADA: 'INICIADA',
  BLOQUEADA: 'BLOQUEADA',
  DESBLOQUEADA: 'DESBLOQUEADA',
  COMPLETADA: 'COMPLETADA',
  CANCELADA: 'CANCELADA',
  VENCIDA: 'VENCIDA',
} as const;

export type TaskEventType = (typeof TASK_EVENT_TYPE)[keyof typeof TASK_EVENT_TYPE];

/** Estrategias de asignacion automatica que usan las acciones del motor. */
export const ASSIGNMENT_STRATEGY = {
  LEAST_LOADED: 'LEAST_LOADED',
  ROUND_ROBIN: 'ROUND_ROBIN',
} as const;

export type AssignmentStrategy = (typeof ASSIGNMENT_STRATEGY)[keyof typeof ASSIGNMENT_STRATEGY];

export interface TaskRecord {
  readonly id: string;
  readonly storeId: string;
  readonly templateCode: string | null;
  readonly title: string;
  readonly description: string | null;
  readonly priority: TaskPriority;
  readonly status: TaskStatus;
  readonly assigneeId: string | null;
  readonly locationId: string | null;
  readonly dueAt: string | null;
  readonly startedAt: string | null;
  readonly completedAt: string | null;
  readonly cancelledAt: string | null;
  readonly cancelReason: string | null;
  readonly createdBy: string | null;
  readonly createdByRuleId: string | null;
  readonly payload: Readonly<Record<string, unknown>>;
  readonly evidence: readonly unknown[];
  readonly parentTaskId: string | null;
  /**
   * Version para el bloqueo optimista del Kanban. Avanza de uno en uno con cada
   * cambio (lo garantiza el trigger tasks.bump_version en la base de datos).
   * Quien reasigna envia la version que leyo: si otra coordinadora se le adelanto,
   * el valor no coincide y el cambio se rechaza en lugar de pisarse en silencio.
   */
  readonly version: number;
  readonly createdAt: string;
  readonly updatedAt: string;
}

export interface TaskEventRecord {
  readonly id: string;
  readonly taskId: string;
  readonly storeId: string;
  readonly type: TaskEventType;
  readonly fromUserId: string | null;
  readonly toUserId: string | null;
  readonly fromStatus: TaskStatus | null;
  readonly toStatus: TaskStatus | null;
  readonly comment: string | null;
  readonly at: string;
}

const TRANSITIONS: Readonly<Record<TaskStatus, readonly TaskStatus[]>> = {
  PENDIENTE: ['ASIGNADA', 'EN_CURSO', 'HECHA', 'CANCELADA'],
  ASIGNADA: ['EN_CURSO', 'BLOQUEADA', 'HECHA', 'CANCELADA', 'PENDIENTE'],
  EN_CURSO: ['BLOQUEADA', 'HECHA', 'CANCELADA'],
  BLOQUEADA: ['EN_CURSO', 'HECHA', 'CANCELADA'],
  HECHA: [],
  CANCELADA: [],
};

export const OPEN_STATUSES: readonly TaskStatus[] = ['PENDIENTE', 'ASIGNADA', 'EN_CURSO', 'BLOQUEADA'];

export function isOpenStatus(status: TaskStatus): boolean {
  return OPEN_STATUSES.includes(status);
}

export function canTransition(from: TaskStatus, to: TaskStatus): boolean {
  return (TRANSITIONS[from] ?? []).includes(to);
}

/** Peso para ordenar el tablero: menor = mas urgente. */
export function priorityWeight(priority: TaskPriority): number {
  switch (priority) {
    case 'URGENTE':
      return 0;
    case 'ALTA':
      return 1;
    case 'MEDIA':
      return 2;
    default:
      return 3;
  }
}
