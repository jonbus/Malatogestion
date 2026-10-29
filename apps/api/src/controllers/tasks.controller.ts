import { PERMISSIONS } from '../../../../packages/contracts/src/rbac.ts';
import type { Router } from '../http/router.ts';
import { json } from '../http/router.ts';
import type { TaskRecord } from '../../../../packages/module-tasks/src/domain/task.ts';
import { TaskNotFoundError, TaskTransitionError, TaskVersionConflictError } from '../../../../packages/module-tasks/src/tasks.service.ts';
import type { TasksService } from '../../../../packages/module-tasks/src/tasks.service.ts';

function toDto(task: TaskRecord): Record<string, unknown> {
  return {
    id: task.id,
    title: task.title,
    description: task.description,
    priority: task.priority,
    status: task.status,
    assigneeId: task.assigneeId,
    locationId: task.locationId,
    dueAt: task.dueAt,
    templateCode: task.templateCode,
    createdByRuleId: task.createdByRuleId,
    startedAt: task.startedAt,
    completedAt: task.completedAt,
    payload: task.payload,
    // El Kanban necesita la version para devolverla al reasignar (bloqueo optimista).
    version: task.version,
  };
}

/** Rutas de tareas. Los permisos son los que declara el manifiesto del modulo. */
export class TasksController {
  private readonly tasks: TasksService;

  constructor(tasks: TasksService) {
    this.tasks = tasks;
  }

  register(router: Router): void {
    router.add({
      method: 'GET',
      pattern: '/me/tasks',
      permission: PERMISSIONS.TASKS_READ,
      summary: 'Tareas abiertas de la persona autenticada',
      handler: (request) => {
        if (!request.user) return json(401, { error: 'NO_AUTENTICADO' });
        const tasks = this.tasks.tasksOf(request.user.id).map(toDto);
        return json(200, { count: tasks.length, tasks });
      },
    });

    router.add({
      method: 'GET',
      pattern: '/tasks/board',
      // Ver el tablero de TODO el equipo es supervision: el permiso mas proximo
      // del modelo es tasks.assign, que solo tienen coordinacion y gerencia.
      permission: PERMISSIONS.TASKS_ASSIGN,
      summary: 'Tablero de tareas del equipo (Kanban)',
      handler: (request) => {
        if (!request.user) return json(401, { error: 'NO_AUTENTICADO' });
        const tasks = this.tasks.board(request.user.storeId).map(toDto);
        return json(200, { count: tasks.length, tasks });
      },
    });

    router.add({
      method: 'POST',
      pattern: '/tasks/:id/reassign',
      permission: PERMISSIONS.TASKS_REASSIGN,
      summary: 'Reasignar una tarea en tiempo real',
      handler: (request) => {
        if (!request.user) return json(401, { error: 'NO_AUTENTICADO' });

        const taskId = request.params['id'] ?? '';
        const body = (request.body ?? {}) as Record<string, unknown>;
        const toUserId = typeof body['toUserId'] === 'string' ? body['toUserId'] : '';
        const reason = typeof body['reason'] === 'string' ? body['reason'] : 'Reasignada por coordinacion';

        if (toUserId === '') {
          return json(400, { error: 'FALTA_DESTINATARIO', detail: 'Se espera { toUserId, reason }' });
        }

        // La version es OBLIGATORIA en la via humana: si fuese opcional, un cliente
        // podria omitirla y volveriamos al "el ultimo gana" en silencio, que es
        // justo lo que este bloqueo existe para evitar.
        const rawVersion = body['version'];
        const version =
          typeof rawVersion === 'number' && Number.isInteger(rawVersion) ? rawVersion : null;
        if (version === null) {
          return json(400, {
            error: 'FALTA_VERSION',
            detail:
              'Se espera { toUserId, version, reason }. Envia la version que devolvio GET /tasks/board; ' +
              'es lo que impide pisar el cambio de otra coordinadora.',
          });
        }

        try {
          const updated = this.tasks.reassign(taskId, toUserId, request.user.id, reason, version);
          return json(200, { task: toDto(updated) });
        } catch (cause) {
          if (cause instanceof TaskNotFoundError) return json(404, { error: 'TAREA_NO_ENCONTRADA', taskId });
          if (cause instanceof TaskTransitionError) return json(409, { error: 'TRANSICION_INVALIDA' });
          if (cause instanceof TaskVersionConflictError) {
            return json(409, {
              error: 'VERSION_OBSOLETA',
              detail: cause.message,
              expectedVersion: cause.expectedVersion,
              actualVersion: cause.actualVersion,
            });
          }
          throw cause;
        }
      },
    });
  }
}
