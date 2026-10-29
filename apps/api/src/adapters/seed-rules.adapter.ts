import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import type { RuleActionDefinition, RuleDefinition } from '../../../../packages/contracts/src/ports.ts';

/**
 * ADAPTADOR DE INFRAESTRUCTURA DE DEMOSTRACION.
 *
 * Este fichero es PURA FONTANERIA: lee un fichero del disco y devuelve datos
 * estructurados. No contiene ninguna regla de decision ni logica de negocio.
 *
 * EN PRODUCCION ESTE ADAPTADOR NO SE USA: las reglas viven en la tabla
 * `rules.rules` de PostgreSQL (ver packages/module-tasks/migrations/001_tasks_init.sql)
 * y se cargan con un repositorio que implementa la misma interfaz RuleRepository
 * del nucleo. Este adaptador solo existe para que el Bloque 0 arranque y para que
 * los tests comprueben el motor contra los datos REALES del seed.
 */

/** Ruta al seed real de la base de datos: la fuente de verdad de la demo. */
export const DEFAULT_SEED_PATH = fileURLToPath(
  new URL('../../../../db/seed/001_demo_store.sql', import.meta.url),
);

/** Regla tal y como esta escrita en el seed, antes de darle identidad. */
export interface SeedRule {
  readonly code: string;
  readonly name: string;
  readonly description: string;
  readonly eventType: string;
  readonly condition: unknown;
  readonly actions: readonly RuleActionDefinition[];
  readonly priority: number;
  readonly isActive: boolean;
  readonly cooldownMinutes: number;
  readonly maxPerDay: number | null;
}

/**
 * Extrae las reglas del bloque `INSERT INTO rules.rules ... FROM (VALUES ...)`.
 *
 * Se parsea el seed REAL a proposito: asi el motor y los datos de produccion no
 * pueden divergir. Si el formato del seed cambia, esto falla de forma ruidosa y
 * obliga a actualizar el parser.
 */
export function parseSeedRules(sql: string): readonly SeedRule[] {
  const start = sql.indexOf('INSERT INTO rules.rules');
  if (start < 0) throw new Error('No se encontro el bloque INSERT INTO rules.rules en el seed');

  const end = sql.indexOf('ON CONFLICT DO NOTHING;', start);
  const section = sql.slice(start, end < 0 ? undefined : end);

  const blocks = section.split(/\n {2}\(\n/).slice(1);
  if (blocks.length === 0) throw new Error('El bloque de reglas del seed no tiene tuplas');

  return blocks.map((block, index) => parseRuleBlock(block, index));
}

function parseRuleBlock(block: string, index: number): SeedRule {
  const quoted = [...block.matchAll(/'([^']*)'/g)].map((match) => match[1] ?? '');
  const [code = '', name = '', description = '', eventType = ''] = quoted;

  // Validacion explicita: si un texto del seed llevase un apostrofo, los campos
  // se desplazarian y este guard lo detecta en vez de producir reglas basura.
  if (!eventType.includes('.')) {
    throw new Error(
      `Regla #${index + 1} del seed: no se pudo leer 'event_type' (¿un apostrofo en los textos?)`,
    );
  }

  const conditionMatch = block.match(/\$cond\$([\s\S]*?)\$cond\$/);
  const actionsMatch = block.match(/\$act\$([\s\S]*?)\$act\$/);
  if (!conditionMatch || !actionsMatch) {
    throw new Error(`Regla '${code}' sin bloque $cond$ o $act$`);
  }

  const tail = block.split('$act$')[2] ?? '';
  const tailMatch = tail.match(/(\d+),\s*(true|false),\s*(\d+),\s*(\d+)/);
  if (!tailMatch) throw new Error(`Regla '${code}' sin priority/is_active/cooldown/max_per_day`);

  return {
    code,
    name,
    description,
    eventType,
    condition: JSON.parse(conditionMatch[1] ?? '{}') as unknown,
    actions: JSON.parse(actionsMatch[1] ?? '[]') as RuleActionDefinition[],
    priority: Number(tailMatch[1]),
    isActive: tailMatch[2] === 'true',
    cooldownMinutes: Number(tailMatch[3]),
    maxPerDay: Number(tailMatch[4]) > 0 ? Number(tailMatch[4]) : null,
  };
}

/** Reglas del seed listas para el motor (id determinista y storeId dado). */
export function loadSeedRules(options: {
  storeId: string;
  sqlPath?: string;
}): readonly RuleDefinition[] {
  const sql = readFileSync(options.sqlPath ?? DEFAULT_SEED_PATH, 'utf8');
  return parseSeedRules(sql).map((rule) => ({
    ...rule,
    id: `seed-${rule.code}`,
    storeId: options.storeId,
    version: 1,
  }));
}
