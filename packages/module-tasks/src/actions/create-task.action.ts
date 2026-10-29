import type { ActionContext, ActionHandler, ActionResult } from '../../../contracts/src/ports.ts';
import type { RoleCode } from '../../../contracts/src/rbac.ts';
import type { AssignmentStrategy, TaskPriority } from '../domain/task.ts';
import type { TasksService } from '../tasks.service.ts';

/** Parametros tal y como los escribe Gerencia en el JSONB de la regla. */
export interface CreateTaskParams {
  readonly template_code?: string;
  readonly title?: string;
  readonly description?: string;
  readonly priority?: TaskPriority;
  readonly assignee_strategy?: AssignmentStrategy;
  readonly assignee_id?: string;
  readonly role?: RoleCode;
  readonly due_in_minutes?: number;
  readonly slots?: number;
  readonly location_id?: string;
  readonly payload?: Readonly<Record<string, unknown>>;
  readonly parent_task_id?: string;
}

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

function humanize(code: string): string {
  const text = code.replaceAll('_', ' ').toLowerCase().trim();
  return text.charAt(0).toUpperCase() + text.slice(1);
}

/**
 * Accion CREATE_TASK: instancia una o varias tareas (slots) y las asigna por
 * estrategia. Es la accion que hace que una regla se convierta en trabajo real.
 */
export function createTaskAction(service: TasksService): ActionHandler {
  return {
    type: 'CREATE_TASK',
    execute(params: Readonly<Record<string, unknown>>, ctx: ActionContext): ActionResult {
      const typed = params as CreateTaskParams;
      const slots = Math.max(1, Math.trunc(asNumber(typed.slots) ?? 1));
      const role = (typed.role ?? 'OPERADORA') as RoleCode;
      const strategy = (typed.assignee_strategy ?? 'LEAST_LOADED') as AssignmentStrategy;
      const dueInMinutes = asNumber(typed.due_in_minutes);
      const templateCode = asString(typed.template_code);
      const basePriority = (typed.priority ?? 'MEDIA') as TaskPriority;

      const taskIds: string[] = [];
      const assignedTo: string[] = [];

      for (let slot = 0; slot < slots; slot += 1) {
        const explicitAssignee = asString(typed.assignee_id);
        const assigneeId = explicitAssignee ?? service.pickAssignee(role, strategy);

        const dueAt =
          dueInMinutes === null
            ? null
            : new Date(ctx.now.getTime() + dueInMinutes * 60_000).toISOString();

        const isExtraSlot = slot > 0;
        const title =
          asString(typed.title) ??
          (templateCode ? humanize(templateCode) : 'Tarea generada por regla');

        const task = service.createTask({
          title: isExtraSlot ? `${title} (${slot + 1}/${slots})` : title,
          description: asString(typed.description),
          priority: basePriority,
          assigneeId,
          locationId: asString(typed.location_id),
          dueAt,
          templateCode,
          createdBy: null,
          createdByRuleId: ctx.ruleId,
          payload: {
            ...(typed.payload ?? {}),
            ruleCode: ctx.ruleCode,
            slot,
          },
          parentTaskId: asString(typed.parent_task_id),
        });

        taskIds.push(task.id);
        if (assigneeId) assignedTo.push(assigneeId);
      }

      return {
        ok: true,
        detail: { taskIds, assignedTo, slots, strategy, ruleCode: ctx.ruleCode },
      };
    },
  };
}
