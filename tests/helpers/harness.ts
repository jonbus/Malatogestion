/**
 * Utilidades compartidas por los tests. Este fichero NO acaba en .test.ts a
 * proposito: el runner lo ignora y solo ejecuta las suites reales.
 */
import { createSystem } from '../../apps/api/src/composition-root.ts';
import type { SystemOptions, SystemRuntime } from '../../apps/api/src/composition-root.ts';
import type { Clock, Logger } from '../../packages/contracts/src/ports.ts';

/** Reloj controlable: evita esperas reales al probar backoff y cooldowns. */
export class MutableClock implements Clock {
  private current: Date;

  constructor(iso: string) {
    this.current = new Date(iso);
  }

  now(): Date {
    return new Date(this.current);
  }

  nowIso(): string {
    return this.current.toISOString();
  }

  advanceMs(ms: number): void {
    this.current = new Date(this.current.getTime() + ms);
  }

  set(iso: string): void {
    this.current = new Date(iso);
  }
}

export const silentLogger: Logger = {
  debug: () => undefined,
  info: () => undefined,
  warn: () => undefined,
  error: () => undefined,
};

/** Sistema completo con logger silencioso. */
export function buildSystem(options: SystemOptions = {}): SystemRuntime {
  return createSystem({ logger: silentLogger, ...options });
}

/** Devuelve la fecha (UTC) del proximo dia de la semana indicado, a esa hora. */
export function nextWeekdayAt(weekday: number, hour: number, from = '2026-01-01T00:00:00.000Z'): Date {
  const date = new Date(from);
  while (date.getUTCDay() !== weekday) date.setUTCDate(date.getUTCDate() + 1);
  date.setUTCHours(hour, 0, 0, 0);
  return date;
}

export const MONDAY = 1;
export const WEDNESDAY = 3;
export const FRIDAY = 5;

/** Escenario de inventario calcado de db/seed/001_demo_store.sql. */
export interface SeedInventoryRow {
  readonly sku: string;
  readonly categoryPath: string;
  readonly locationCode: string;
  readonly qty: number;
  readonly minStock: number;
  readonly targetStock: number;
}

export const SEED_STOCK: readonly SeedInventoryRow[] = [
  // LAC-001: 12 unidades en sala frente a un minimo de 48 => ratio 0,25 (ROTURA).
  { sku: 'LAC-001', categoryPath: 'lacteos.leche', locationCode: 'SALA', qty: 12, minStock: 48, targetStock: 120 },
  { sku: 'LAC-002', categoryPath: 'lacteos.leche', locationCode: 'SALA', qty: 60, minStock: 48, targetStock: 120 },
  { sku: 'LAC-005', categoryPath: 'lacteos.yogures', locationCode: 'SALA', qty: 18, minStock: 16, targetStock: 40 },
  { sku: 'FRE-001', categoryPath: 'frescos.frutas_verduras', locationCode: 'SALA', qty: 8, minStock: 15, targetStock: 40 },
  { sku: 'BEB-001', categoryPath: 'bebidas.refrescos', locationCode: 'SALA', qty: 20, minStock: 36, targetStock: 96 },
];

export function seedInventory(system: SystemRuntime): void {
  for (const row of SEED_STOCK) {
    system.inventory.setStock({
      productId: `prod-${row.sku}`,
      sku: row.sku,
      categoryPath: row.categoryPath,
      locationCode: row.locationCode,
      qty: row.qty,
      minStock: row.minStock,
      targetStock: row.targetStock,
    });
  }
}
