import type { DomainEvent } from '../../contracts/src/domain-event.ts';
import type { FactContext, FactResolver, Clock, IdGenerator, Logger } from '../../contracts/src/ports.ts';
import { createEventFactory } from '../../core/src/events/event-factory.ts';
import type { EventFactory } from '../../core/src/events/event-factory.ts';

export interface StockRow {
  readonly productId: string;
  readonly sku: string;
  readonly categoryPath: string;
  readonly locationCode: string;
  qty: number;
  readonly minStock: number;
  readonly targetStock: number;
}

export interface LotRow {
  readonly lotId: string;
  readonly productId: string;
  readonly sku: string;
  readonly batchCode: string;
  readonly locationCode: string;
  /** Fecha de caducidad en ISO corto: YYYY-MM-DD. */
  readonly expiryDate: string;
  qty: number;
}

export interface WastageInput {
  readonly productId: string;
  readonly lotId: string | null;
  readonly qty: number;
  readonly reasonCode: 'CADUCADO' | 'ROTO' | 'MERMA_DESCONOCIDA' | 'DEVOLUCION';
  readonly note?: string;
  readonly actorId?: string | null;
}

export interface InventoryServiceOptions {
  readonly clock: Clock;
  readonly ids: IdGenerator;
  readonly storeId: string;
  readonly logger?: Logger;
}

const MS_PER_DAY = 86_400_000;

function asString(value: unknown): string | null {
  return typeof value === 'string' && value !== '' ? value : null;
}

/**
 * Inventario en memoria: stock por ubicacion y lotes con caducidad.
 * Produce eventos de dominio; el host los vuelca al outbox con drainEvents().
 */
export class InventoryService {
  private readonly stock = new Map<string, StockRow>();
  private readonly lots = new Map<string, LotRow>();
  private readonly pending: DomainEvent[] = [];
  private readonly clock: Clock;
  private readonly events: EventFactory;
  private readonly logger: Logger | null;

  constructor(options: InventoryServiceOptions) {
    this.clock = options.clock;
    this.events = createEventFactory({ clock: options.clock, ids: options.ids, storeId: options.storeId });
    this.logger = options.logger ?? null;
  }

  private static key(productId: string, locationCode: string): string {
    return `${productId}@${locationCode}`;
  }

  setStock(row: StockRow): void {
    this.stock.set(InventoryService.key(row.productId, row.locationCode), { ...row });
  }

  stockOf(productId: string, locationCode: string): StockRow | undefined {
    return this.stock.get(InventoryService.key(productId, locationCode));
  }

  stockRows(): readonly StockRow[] {
    return [...this.stock.values()];
  }

  addLot(lot: LotRow): void {
    this.lots.set(lot.lotId, { ...lot });
  }

  lot(lotId: string): LotRow | undefined {
    return this.lots.get(lotId);
  }

  lotRows(): readonly LotRow[] {
    return [...this.lots.values()];
  }

  /** Eventos producidos y aun no publicados. */
  drainEvents(): readonly DomainEvent[] {
    const drained = [...this.pending];
    this.pending.length = 0;
    return drained;
  }

  private emit(eventType: string, payload: Record<string, unknown>, actorId: string | null): DomainEvent {
    const event = this.events.create(eventType, payload, { actorId });
    this.pending.push(event);
    return event;
  }

  /**
   * Aplica una venta: descuenta de sala y emite stock.below_minimum por cada
   * producto que quede por debajo de su minimo.
   */
  applySale(
    lines: readonly { readonly productId: string; readonly qty: number }[],
    actorId: string | null = null,
    locationCode = 'SALA',
  ): readonly DomainEvent[] {
    const emitted: DomainEvent[] = [];

    for (const line of lines) {
      const row = this.stock.get(InventoryService.key(line.productId, locationCode));
      if (!row) continue;
      row.qty = Math.max(0, Number((row.qty - line.qty).toFixed(3)));

      const breach = this.checkMinimum(line.productId, locationCode, actorId);
      if (breach) emitted.push(breach);
    }

    return emitted;
  }

  /** Emite stock.below_minimum si el stock quedo por debajo del minimo. */
  checkMinimum(
    productId: string,
    locationCode = 'SALA',
    actorId: string | null = null,
  ): DomainEvent | null {
    const row = this.stock.get(InventoryService.key(productId, locationCode));
    if (!row) return null;
    if (row.qty >= row.minStock) return null;

    this.logger?.warn('Stock bajo minimo', { sku: row.sku, qty: row.qty, minStock: row.minStock });

    return this.emit(
      'stock.below_minimum',
      {
        productId: row.productId,
        sku: row.sku,
        categoryPath: row.categoryPath,
        locationCode: row.locationCode,
        qty: row.qty,
        minStock: row.minStock,
        targetStock: row.targetStock,
        deficit: Number((row.minStock - row.qty).toFixed(3)),
      },
      actorId,
    );
  }

  /** Dias (enteros) que faltan hasta la caducidad. Negativo si ya caduco. */
  daysToExpiry(expiryDate: string, now: Date = this.clock.now()): number {
    const expiry = Date.parse(`${expiryDate}T00:00:00.000Z`);
    const today = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate());
    return Math.round((expiry - today) / MS_PER_DAY);
  }

  findExpiringLots(withinDays: number, now: Date = this.clock.now()): readonly LotRow[] {
    return this.lotRows()
      .filter((lot) => lot.qty > 0)
      .filter((lot) => {
        const days = this.daysToExpiry(lot.expiryDate, now);
        return days <= withinDays;
      })
      .sort((a, b) => a.expiryDate.localeCompare(b.expiryDate));
  }

  /** Barrido de caducidades: emite lot.expiring_soon por cada lote proximo. */
  sweepExpiringLots(withinDays = 3, actorId: string | null = null): readonly DomainEvent[] {
    const now = this.clock.now();
    const emitted: DomainEvent[] = [];

    for (const lot of this.findExpiringLots(withinDays, now)) {
      emitted.push(
        this.emit(
          'lot.expiring_soon',
          {
            lotId: lot.lotId,
            productId: lot.productId,
            sku: lot.sku,
            batchCode: lot.batchCode,
            locationCode: lot.locationCode,
            expiryDate: lot.expiryDate,
            daysToExpiry: this.daysToExpiry(lot.expiryDate, now),
            qty: lot.qty,
          },
          actorId,
        ),
      );
    }

    return emitted;
  }

  registerWastage(input: WastageInput): DomainEvent {
    if (input.lotId) {
      const lot = this.lots.get(input.lotId);
      if (lot) lot.qty = Math.max(0, Number((lot.qty - input.qty).toFixed(3)));
    }

    const lot = input.lotId ? this.lots.get(input.lotId) : undefined;
    if (lot) {
      const row = this.stock.get(InventoryService.key(lot.productId, lot.locationCode));
      if (row) row.qty = Math.max(0, Number((row.qty - input.qty).toFixed(3)));
    }

    return this.emit(
      'wastage.registered',
      {
        productId: input.productId,
        lotId: input.lotId,
        qty: input.qty,
        reasonCode: input.reasonCode,
        note: input.note ?? null,
      },
      input.actorId ?? null,
    );
  }

  /**
   * Peor ratio stock/minimo de un conjunto de productos, acotado a 1.
   * Definicion acordada: "hay algun producto de la categoria por debajo del X%
   * de su minimo". Es la lectura que hace util la regla del seed.
   */
  stockRatio(params: Readonly<Record<string, unknown>>, locationCode = 'SALA'): number | null {
    const categoryPath = asString(params['categoryPath']);
    const productId = asString(params['productId']);
    const location = asString(params['locationCode']) ?? locationCode;

    const candidates = this.stockRows().filter((row) => {
      if (row.locationCode !== location) return false;
      if (productId) return row.productId === productId;
      if (categoryPath) {
        return row.categoryPath === categoryPath || row.categoryPath.startsWith(`${categoryPath}.`);
      }
      return true;
    });

    if (candidates.length === 0) return null;

    return candidates.reduce((worst, row) => {
      const ratio = row.minStock > 0 ? Math.min(1, row.qty / row.minStock) : 1;
      return Math.min(worst, ratio);
    }, 1);
  }
}

/** Facts que el modulo aporta al motor de reglas. */
export function inventoryFacts(service: InventoryService): Record<string, FactResolver> {
  const resolveLotId = (
    params: Readonly<Record<string, unknown>>,
    ctx: FactContext,
  ): string | null => asString(params['lotId']) ?? asString(ctx.event.payload['lotId']);

  // Devuelven el VALOR CRUDO: FactRegistry es quien lo envuelve en { found, value }.
  // Un dato ausente se expresa con null, no con un sobre.
  return {
    'inventory.stock_ratio': (params) => service.stockRatio(params),

    'inventory.days_to_expiry': (params, ctx) => {
      const lotId = resolveLotId(params, ctx);
      const lot = lotId ? service.lot(lotId) : undefined;
      return lot ? service.daysToExpiry(lot.expiryDate, ctx.now) : null;
    },

    'inventory.lot_qty': (params, ctx) => {
      const lotId = resolveLotId(params, ctx);
      const lot = lotId ? service.lot(lotId) : undefined;
      return lot ? lot.qty : null;
    },
  };
}
