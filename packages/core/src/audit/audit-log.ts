import type { Clock, IdGenerator } from '../../../contracts/src/ports.ts';

export interface AuditEntry {
  readonly id: string;
  readonly at: string;
  readonly actorId: string | null;
  readonly moduleId: string;
  readonly action: string;
  readonly refType: string | null;
  readonly refId: string | null;
  readonly before: unknown;
  readonly after: unknown;
}

export type AuditInput = Omit<AuditEntry, 'id' | 'at'>;

/**
 * Registro de auditoria append-only en memoria.
 * No expone update ni delete: es la traza inmutable de todo lo que pasa.
 */
export class AuditLog {
  private readonly entries: AuditEntry[] = [];
  private readonly clock: Clock;
  private readonly ids: IdGenerator;

  constructor(clock: Clock, ids: IdGenerator) {
    this.clock = clock;
    this.ids = ids;
  }

  append(input: AuditInput): AuditEntry {
    const entry: AuditEntry = Object.freeze({
      id: this.ids.next(),
      at: this.clock.nowIso(),
      actorId: input.actorId,
      moduleId: input.moduleId,
      action: input.action,
      refType: input.refType,
      refId: input.refId,
      before: input.before,
      after: input.after,
    });
    this.entries.push(entry);
    return entry;
  }

  all(): readonly AuditEntry[] {
    return this.entries;
  }

  count(): number {
    return this.entries.length;
  }

  byRef(refType: string, refId: string): readonly AuditEntry[] {
    return this.entries.filter((entry) => entry.refType === refType && entry.refId === refId);
  }

  byActor(actorId: string): readonly AuditEntry[] {
    return this.entries.filter((entry) => entry.actorId === actorId);
  }

  byModule(moduleId: string): readonly AuditEntry[] {
    return this.entries.filter((entry) => entry.moduleId === moduleId);
  }
}
