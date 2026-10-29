import type { ActionContext, ActionHandler, ActionResult } from '../../../contracts/src/ports.ts';

interface RegisteredAction {
  readonly handler: ActionHandler;
  readonly moduleId: string;
}

export class UnknownActionError extends Error {
  constructor(type: string) {
    super(`Accion no registrada: '${type}'`);
    this.name = 'UnknownActionError';
  }
}

export class DuplicateActionError extends Error {
  constructor(type: string, moduleId: string, owner: string) {
    super(`La accion '${type}' de '${moduleId}' ya la aporta '${owner}'`);
    this.name = 'DuplicateActionError';
  }
}

/**
 * Catalogo de acciones que el motor de reglas sabe ejecutar.
 * Igual que los facts: el motor solo conoce tipos, nunca modulos.
 */
export class ActionRegistry {
  private readonly entries = new Map<string, RegisteredAction>();

  register(handler: ActionHandler, moduleId: string): void {
    const existing = this.entries.get(handler.type);
    if (existing) throw new DuplicateActionError(handler.type, moduleId, existing.moduleId);
    this.entries.set(handler.type, { handler, moduleId });
  }

  has(type: string): boolean {
    return this.entries.has(type);
  }

  types(): readonly string[] {
    return [...this.entries.keys()].sort();
  }

  ownerOf(type: string): string | null {
    return this.entries.get(type)?.moduleId ?? null;
  }

  size(): number {
    return this.entries.size;
  }

  async execute(
    type: string,
    params: Readonly<Record<string, unknown>>,
    ctx: ActionContext,
  ): Promise<ActionResult> {
    const entry = this.entries.get(type);
    if (!entry) throw new UnknownActionError(type);
    return entry.handler.execute(params, ctx);
  }
}
