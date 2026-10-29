import type { ActionContext, ActionHandler, ActionResult } from '../../../contracts/src/ports.ts';
import type { TasksService } from '../tasks.service.ts';

function asString(value: unknown): string | null {
  return typeof value === 'string' && value !== '' ? value : null;
}

/** Accion CANCEL_TASK: cancela la tarea del evento dejando motivo en el historial. */
export function cancelTaskAction(service: TasksService): ActionHandler {
  return {
    type: 'CANCEL_TASK',
    execute(params: Readonly<Record<string, unknown>>, ctx: ActionContext): ActionResult {
      const taskId = asString(params['taskId']) ?? asString(ctx.event.payload['taskId']);
      if (!taskId) {
        return { ok: false, detail: { reason: 'El evento no identifica ninguna tarea' } };
      }

      const task = service.task(taskId);
      if (!task) return { ok: false, detail: { reason: `Tarea inexistente: ${taskId}` } };

      const reason = asString(params['reason']) ?? 'Cancelada por regla';

      try {
        service.cancel(taskId, null, reason);
      } catch (cause) {
        return {
          ok: false,
          detail: { reason: cause instanceof Error ? cause.message : String(cause) },
        };
      }

      return { ok: true, detail: { taskId, reason, ruleCode: ctx.ruleCode } };
    },
  };
}
