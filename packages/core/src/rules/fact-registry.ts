import type { FactContext, FactResolution, FactResolver } from '../../../contracts/src/ports.ts';
import type { FactDeclaration } from '../../../contracts/src/manifest.ts';

interface RegisteredFact {
  readonly key: string;
  readonly resolver: FactResolver;
  readonly moduleId: string;
}

export class UnknownFactError extends Error {
  constructor(key: string) {
    super(`Fact no registrado: '${key}'`);
    this.name = 'UnknownFactError';
  }
}

export class DuplicateFactError extends Error {
  constructor(key: string, moduleId: string, owner: string) {
    super(`El fact '${key}' de '${moduleId}' ya lo aporta '${owner}'`);
    this.name = 'DuplicateFactError';
  }
}

/**
 * Un resolver devolvio el sobre { found, value } en lugar del valor crudo.
 * Sin esta comprobacion el motor evaluaria siempre en falso y las reglas
 * quedarian muertas sin que nada avise.
 */
export class MiswrappedFactError extends Error {
  constructor(key: string, moduleId: string) {
    super(
      `El resolver del fact '${key}' (modulo '${moduleId}') devolvio un objeto ` +
        `{ found, value } en lugar del valor crudo: el registro ya lo envuelve, ` +
        `asi que se envolveria dos veces. Devuelve el valor directamente y usa ` +
        `null cuando no haya dato.`,
    );
    this.name = 'MiswrappedFactError';
  }
}

/** Detecta un FactResolution devuelto por error como si fuese un valor. */
function looksLikeResolution(value: unknown): boolean {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) return false;
  const keys = Object.keys(value);
  if (keys.length === 0 || keys.length > 2) return false;
  const candidate = value as { found?: unknown; value?: unknown };
  return typeof candidate.found === 'boolean' && 'value' in candidate;
}

/**
 * Catalogo de variables del motor de reglas.
 * Los modulos se dan de alta aqui a traves de sus manifiestos: el motor NUNCA
 * conoce nombres de modulo, solo claves que alguien registro.
 */
export class FactRegistry {
  private readonly entries = new Map<string, RegisteredFact>();

  register(key: string, resolver: FactResolver, moduleId: string): void {
    const existing = this.entries.get(key);
    if (existing) throw new DuplicateFactError(key, moduleId, existing.moduleId);
    this.entries.set(key, { key, resolver, moduleId });
  }

  has(key: string): boolean {
    return this.entries.has(key);
  }

  keys(): readonly string[] {
    return [...this.entries.keys()].sort();
  }

  ownerOf(key: string): string | null {
    return this.entries.get(key)?.moduleId ?? null;
  }

  size(): number {
    return this.entries.size;
  }

  /**
   * Resuelve un fact. Devuelve `found: false` en vez de lanzar: una regla que
   * referencia una variable inexistente debe NO coincidir, no tumbar el motor.
   *
   * El resolver devuelve el VALOR CRUDO; el sobre { found, value } lo pone aqui
   * el registro, en un unico sitio. Un resolver que devuelva el sobre ya formado
   * lo envolveria dos veces y ninguna comparacion coincidiria, asi que se
   * detecta y se rechaza en vez de fallar en silencio.
   */
  async resolve(
    key: string,
    params: Readonly<Record<string, unknown>>,
    ctx: FactContext,
  ): Promise<FactResolution> {
    const entry = this.entries.get(key);
    if (!entry) return { found: false, value: undefined };
    const value = await entry.resolver(params, ctx);

    if (looksLikeResolution(value)) {
      throw new MiswrappedFactError(key, entry.moduleId);
    }

    return { found: true, value };
  }
}

/** Manifiesto de facts agregados, util para el editor de reglas de Gerencia. */
export function describeFacts(declarations: readonly FactDeclaration[]): readonly string[] {
  return declarations.map((fact) => fact.key).sort();
}
