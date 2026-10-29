import type { ActionContext, ActionHandler, ActionResult } from '../../../contracts/src/ports.ts';
import type { RoleCode } from '../../../contracts/src/rbac.ts';
import type { AssignmentStrategy } from '../domain/task.ts';
import { TaskVersionConflictError } from '../tasks.service.ts';
import type { TasksService } from '../tasks.service.ts';

function asString(value: unknown): string | null {
  return typeof value === 'string' && value !== '' ? value : null;
}

function asNumber(value: unknown): number | null {
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (typeof value === 'string' && value.trim() !== '') {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
}

/**
 * Accion REASSIGN_TASK: reasigna la tarea del evento a quien menos carga tenga.
 * Es la respuesta automatica a una tarea vencida.
 *
 * Acepta `expected_version` opcional. Cuando la regla lo informa, la reasignacion
 * es segura ante dos coordinadoras actuando a la vez: si la tarea cambio desde que
 * se leyo, la accion NO pisa el cambio y devuelve el motivo.
 */
export function reassignTaskAction(service: TasksService): ActionHandler {
  return {
    type: 'REASSIGN_TASK',
    execute(params: Readonly<Record<string, unknown>>, ctx: ActionContext): ActionResult {
      const taskId = asString(params['taskId']) ?? asString(ctx.event.payload['taskId']);
      if (!taskId) {
        return { ok: false, detail: { reason: 'El evento no identifica ninguna tarea' } };
      }

      const task = service.task(taskId);
      if (!task) return { ok: false, detail: { reason: `Tarea inexistente: ${taskId}` } };

      const excludeCurrent = params['exclude_current_assignee'] === true;
      const role = (asString(params['role']) ?? 'OPERADORA') as RoleCode;
      const strategy = (asString(params['strategy']) ?? 'LEAST_LOADED') as AssignmentStrategy;
      const expectedVersion = asNumber(params['expected_version']);

      const target = service.pickAssignee(role, strategy, excludeCurrent ? task.assigneeId : null);
      if (!target) {
        return { ok: false, detail: { reason: 'No hay candidatas disponibles para reasignar' } };
      }

      const reason = asString(params['reason']) ?? 'Reasignacion automatica';

      try {
        const updated = service.reassign(taskId, target, null, reason, expectedVersion);
        return {
          ok: true,
          detail: {
            taskId,
            fromUserId: task.assigneeId,
            toUserId: target,
            version: updated.version,
            ruleCode: ctx.ruleCode,
          },
        };
      } catch (cause) {
        if (cause instanceof TaskVersionConflictError) {
          return {
            ok: false,
            detail: {
              reason: cause.message,
              taskId,
              expectedVersion: cause.expectedVersion,
              actualVersion: cause.actualVersion,
            },
          };
        }
        throw cause;
      }
    },
  };
}
