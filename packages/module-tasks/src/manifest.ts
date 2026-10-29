import type { ModuleManifest } from '../../contracts/src/manifest.ts';
import { PERMISSIONS, ROLES } from '../../contracts/src/rbac.ts';

export const tasksManifest: ModuleManifest = {
  id: 'tasks',
  name: 'Tareas',
  version: '0.1.0',

  permissions: [
    PERMISSIONS.TASKS_READ,
    PERMISSIONS.TASKS_CREATE,
    PERMISSIONS.TASKS_ASSIGN,
    PERMISSIONS.TASKS_REASSIGN,
    PERMISSIONS.TASKS_COMPLETE,
    PERMISSIONS.TASKS_TEMPLATES_MANAGE,
    PERMISSIONS.RULES_READ,
    PERMISSIONS.RULES_MANAGE,
    PERMISSIONS.RULES_SIMULATE,
    PERMISSIONS.RULES_OVERRIDE,
  ],

  publishes: [
    'task.created',
    'task.assigned',
    'task.reassigned',
    'task.started',
    'task.blocked',
    'task.completed',
    'task.cancelled',
    'task.overdue',
  ],

  consumes: ['stock.below_minimum', 'lot.expiring_soon'],

  facts: [
    {
      key: 'tasks.open_by_user',
      description: 'Numero de tareas abiertas de una persona. Sin params toma assigneeId del evento.',
      params: ['userId'],
    },
    {
      key: 'tasks.minutes_overdue',
      description: 'Minutos de retraso de una tarea. Sin params toma taskId del evento.',
      params: ['taskId'],
    },
    {
      key: 'tasks.status',
      description: 'Estado actual de una tarea. Sin params toma taskId del evento.',
      params: ['taskId'],
    },
  ],

  actions: [
    { type: 'CREATE_TASK', description: 'Crea una o varias tareas y las asigna por estrategia.' },
    { type: 'REASSIGN_TASK', description: 'Reasigna la tarea del evento a quien menos carga tenga.' },
    { type: 'CANCEL_TASK', description: 'Cancela la tarea del evento con un motivo.' },
  ],

  uiRoutes: [
    { path: '/mis-tareas', label: 'Mis tareas', roles: [ROLES.OPERADORA, ROLES.COORDINADORA] },
    {
      path: '/tareas/tablero',
      label: 'Tablero de tareas',
      roles: [ROLES.GERENCIA, ROLES.COORDINADORA],
      permission: PERMISSIONS.TASKS_READ,
    },
    {
      path: '/reglas',
      label: 'Motor de reglas',
      roles: [ROLES.GERENCIA],
      permission: PERMISSIONS.RULES_MANAGE,
    },
  ],

  featureFlags: ['tasks.engine.enabled', 'tasks.kanban.realtime'],

  migrationsPath: 'packages/module-tasks/migrations',
};
