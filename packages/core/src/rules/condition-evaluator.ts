import type { FactResolution } from '../../../contracts/src/ports.ts';

/** El evaluador no conoce modulos: solo pide el valor de una clave. */
export type FactLookup = (
  key: string,
  params: Readonly<Record<string, unknown>>,
) => FactResolution | Promise<FactResolution>;

export const OPERATORS = [
  'eq',
  'neq',
  'gt',
  'gte',
  'lt',
  'lte',
  'in',
  'nin',
  'contains',
  'exists',
  'is_null',
] as const;

export type Operator = (typeof OPERATORS)[number];

export interface ConditionTraceNode {
  readonly kind: 'group' | 'leaf';
  readonly label: string;
  readonly matched: boolean;
  readonly detail: string | null;
}

export interface ConditionEvaluation {
  readonly matched: boolean;
  readonly trace: readonly ConditionTraceNode[];
}

export class ConditionError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ConditionError';
  }
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function toNumber(value: unknown): number | null {
  if (typeof value === 'number') return Number.isFinite(value) ? value : null;
  if (typeof value === 'string' && value.trim() !== '') {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  if (typeof value === 'boolean') return value ? 1 : 0;
  return null;
}

function equals(actual: unknown, expected: unknown): boolean {
  if (actual === expected) return true;
  const a = toNumber(actual);
  const b = toNumber(expected);
  if (a !== null && b !== null) return a === b;
  if (isPlainObject(actual) || isPlainObject(expected) || Array.isArray(actual) || Array.isArray(expected)) {
    try {
      return JSON.stringify(actual) === JSON.stringify(expected);
    } catch {
      return false;
    }
  }
  return false;
}

/** Comparacion ordenada: numerica si ambos son numeros; si no, alfabetica. */
function compareOrdered(actual: unknown, expected: unknown): number | null {
  const a = toNumber(actual);
  const b = toNumber(expected);
  if (a !== null && b !== null) return a === b ? 0 : a < b ? -1 : 1;
  if (typeof actual === 'string' && typeof expected === 'string') {
    return actual.localeCompare(expected);
  }
  return null;
}

function render(value: unknown): string {
  if (value === undefined) return 'undefined';
  try {
    return JSON.stringify(value) ?? String(value);
  } catch {
    return String(value);
  }
}

/**
 * Evaluador del arbol JSONB de condiciones de la Fase 5.2:
 *   { "all": [ { "fact": "...", "op": "...", "value": ..., "params": {...} } ] }
 * Soporta anidamiento con all / any / not y 11 operadores.
 */
export class ConditionEvaluator {
  private readonly lookup: FactLookup;

  constructor(lookup: FactLookup) {
    this.lookup = lookup;
  }

  async evaluate(condition: unknown): Promise<ConditionEvaluation> {
    const trace: ConditionTraceNode[] = [];
    const matched = await this.evaluateNode(condition, trace);
    return { matched, trace };
  }

  private async evaluateNode(node: unknown, trace: ConditionTraceNode[]): Promise<boolean> {
    if (!isPlainObject(node)) {
      throw new ConditionError(`Nodo de condicion invalido: ${render(node)}`);
    }

    if ('all' in node) return this.evaluateGroup('all', node['all'], trace);
    if ('any' in node) return this.evaluateGroup('any', node['any'], trace);
    if ('not' in node) return this.evaluateGroup('not', node['not'], trace);

    return this.evaluateLeaf(node, trace);
  }

  private async evaluateGroup(
    kind: 'all' | 'any' | 'not',
    children: unknown,
    trace: ConditionTraceNode[],
  ): Promise<boolean> {
    if (kind === 'not') {
      const matched = !(await this.evaluateNode(children, trace));
      trace.push({ kind: 'group', label: 'not', matched, detail: null });
      return matched;
    }

    if (!Array.isArray(children)) {
      throw new ConditionError(`El grupo '${kind}' debe ser un array`);
    }

    const results: boolean[] = [];
    for (const child of children) {
      results.push(await this.evaluateNode(child, trace));
    }

    // 'all' vacio = true (verdad vacua); 'any' vacio = false.
    const matched = kind === 'all' ? results.every(Boolean) : results.some(Boolean);
    trace.push({ kind: 'group', label: `${kind}[${results.length}]`, matched, detail: null });
    return matched;
  }

  private async evaluateLeaf(
    node: Record<string, unknown>,
    trace: ConditionTraceNode[],
  ): Promise<boolean> {
    const fact = node['fact'];
    if (typeof fact !== 'string' || fact === '') {
      throw new ConditionError(`Hoja de condicion sin 'fact': ${render(node)}`);
    }

    const op = (node['op'] ?? 'eq') as string;
    if (!(OPERATORS as readonly string[]).includes(op)) {
      throw new ConditionError(`Operador no soportado: '${op}'`);
    }

    const rawParams = node['params'];
    const params = isPlainObject(rawParams) ? rawParams : {};
    const expected = node['value'];

    const resolution = await this.lookup(fact, params);
    const actual = resolution.value;
    const isNil = !resolution.found || actual === null || actual === undefined;

    let matched: boolean;
    let detail: string;

    if (op === 'exists') {
      const want = expected === undefined ? true : Boolean(expected);
      matched = !isNil === want;
      detail = resolution.found
        ? `${fact} existe=${!isNil}`
        : `${fact} NO registrado`;
    } else if (op === 'is_null') {
      const want = expected === undefined ? true : Boolean(expected);
      matched = isNil === want;
      detail = resolution.found ? `${fact} es_nulo=${isNil}` : `${fact} NO registrado`;
    } else if (isNil) {
      // Una variable inexistente o nula NUNCA hace coincidir una comparacion:
      // asi una regla mal escrita no dispara por accidente.
      matched = false;
      detail = `${fact} = ${resolution.found ? 'null' : 'NO registrado'}`;
    } else {
      matched = this.compare(op, actual, expected);
      detail = `${fact} ${op} ${render(expected)} -> ${render(actual)}`;
    }

    trace.push({ kind: 'leaf', label: `${fact} ${op}`, matched, detail });
    return matched;
  }

  private compare(op: string, actual: unknown, expected: unknown): boolean {
    switch (op) {
      case 'eq':
        return equals(actual, expected);
      case 'neq':
        return !equals(actual, expected);
      case 'gt':
      case 'gte':
      case 'lt':
      case 'lte': {
        const order = compareOrdered(actual, expected);
        if (order === null) return false;
        if (op === 'gt') return order > 0;
        if (op === 'gte') return order >= 0;
        if (op === 'lt') return order < 0;
        return order <= 0;
      }
      case 'in':
        return Array.isArray(expected) && expected.some((candidate) => equals(actual, candidate));
      case 'nin':
        return Array.isArray(expected) && !expected.some((candidate) => equals(actual, candidate));
      case 'contains': {
        if (Array.isArray(actual)) return actual.some((candidate) => equals(candidate, expected));
        if (typeof actual === 'string') return actual.includes(String(expected));
        return false;
      }
      default:
        return false;
    }
  }
}
