import type { DomainEvent } from '../../contracts/src/domain-event.ts';
import type { Clock, FactResolver, IdGenerator, Logger } from '../../contracts/src/ports.ts';
import { createEventFactory } from '../../core/src/events/event-factory.ts';
import type { EventFactory } from '../../core/src/events/event-factory.ts';

export type PaymentMethod = 'EFECTIVO' | 'TARJETA' | 'MIXTO' | 'VALE';
export type AffluenceLevel = 'LOW' | 'MEDIUM' | 'HIGH';

export interface SaleLineInput {
  readonly productId: string;
  readonly sku: string;
  readonly description?: string;
  readonly qty: number;
  readonly unitPrice: number;
  readonly discount?: number;
  readonly taxRate?: number;
}

export interface PaymentInput {
  readonly method: PaymentMethod;
  readonly amount: number;
}

export interface SaleLine extends SaleLineInput {
  readonly lineNo: number;
  readonly lineTotal: number;
}

export interface Sale {
  readonly id: string;
  readonly sessionId: string;
  readonly registerId: string;
  readonly storeId: string;
  readonly operatorId: string;
  readonly lines: readonly SaleLine[];
  readonly total: number;
  readonly payments: readonly PaymentInput[];
  readonly at: string;
}

export type CashSessionStatus = 'ABIERTA' | 'CERRADA';

export interface CashSession {
  readonly id: string;
  readonly storeId: string;
  readonly registerId: string;
  readonly status: CashSessionStatus;
  readonly openedBy: string;
  readonly openedAt: string;
  readonly closedBy: string | null;
  readonly closedAt: string | null;
  readonly openingFloat: number;
  readonly expectedCash: number;
  readonly countedCash: number | null;
  readonly difference: number | null;
}

export interface SellInput {
  readonly registerId: string;
  readonly operatorId: string;
  readonly lines: readonly SaleLineInput[];
  readonly payments: readonly PaymentInput[];
}

export interface PosServiceOptions {
  readonly clock: Clock;
  readonly ids: IdGenerator;
  readonly storeId: string;
  /** Umbral de descuadre en euros (settings: pos.discrepancy_threshold_eur). */
  readonly discrepancyThresholdEur?: number;
  readonly logger?: Logger;
}

function round2(value: number): number {
  return Math.round(value * 100) / 100;
}

function asString(value: unknown): string | null {
  return typeof value === 'string' && value !== '' ? value : null;
}

/**
 * Punto de venta en memoria: sesiones de caja y ventas.
 * La venta NO descuenta stock directamente: emite sale.completed y es inventario
 * quien reacciona. Asi el cobro nunca depende del modulo de inventario.
 */
export class PosService {
  private readonly sessions = new Map<string, CashSession>();
  private readonly sales = new Map<string, Sale>();
  private readonly pending: DomainEvent[] = [];
  private readonly clock: Clock;
  private readonly ids: IdGenerator;
  private readonly storeId: string;
  private readonly events: EventFactory;
  private readonly discrepancyThresholdEur: number;
  private readonly logger: Logger | null;
  private affluence: AffluenceLevel = 'MEDIUM';

  constructor(options: PosServiceOptions) {
    this.clock = options.clock;
    this.ids = options.ids;
    this.storeId = options.storeId;
    this.events = createEventFactory({ clock: options.clock, ids: options.ids, storeId: options.storeId });
    this.discrepancyThresholdEur = options.discrepancyThresholdEur ?? 5;
    this.logger = options.logger ?? null;
  }

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

  setAffluence(level: AffluenceLevel): void {
    this.affluence = level;
  }

  openSession(registerId: string, operatorId: string, openingFloat: number): CashSession {
    const open = [...this.sessions.values()].find(
      (session) => session.registerId === registerId && session.status === 'ABIERTA',
    );
    if (open) {
      throw new Error(`La caja '${registerId}' ya tiene una sesion abierta (${open.id})`);
    }

    const session: CashSession = Object.freeze({
      id: this.ids.next(),
      storeId: this.storeId,
      registerId,
      status: 'ABIERTA',
      openedBy: operatorId,
      openedAt: this.clock.nowIso(),
      closedBy: null,
      closedAt: null,
      openingFloat: round2(openingFloat),
      expectedCash: round2(openingFloat),
      countedCash: null,
      difference: null,
    });

    this.sessions.set(session.id, session);
    this.emit(
      'cash_session.opened',
      { sessionId: session.id, registerId, operatorId, openingFloat: session.openingFloat },
      operatorId,
    );

    return session;
  }

  requireOpenSession(registerId: string): CashSession {
    const session = [...this.sessions.values()].find(
      (candidate) => candidate.registerId === registerId && candidate.status === 'ABIERTA',
    );
    if (!session) throw new Error(`La caja '${registerId}' no tiene sesion abierta`);
    return session;
  }

  sell(input: SellInput): Sale {
    const session = this.requireOpenSession(input.registerId);

    const lines: SaleLine[] = input.lines.map((line, index) => ({
      ...line,
      lineNo: index + 1,
      lineTotal: round2(line.qty * line.unitPrice - (line.discount ?? 0)),
    }));

    const total = round2(lines.reduce((sum, line) => sum + line.lineTotal, 0));
    const cashIn = round2(
      input.payments
        .filter((payment) => payment.method === 'EFECTIVO')
        .reduce((sum, payment) => sum + payment.amount, 0),
    );

    const sale: Sale = Object.freeze({
      id: this.ids.next(),
      sessionId: session.id,
      registerId: input.registerId,
      storeId: this.storeId,
      operatorId: input.operatorId,
      lines,
      total,
      payments: [...input.payments],
      at: this.clock.nowIso(),
    });

    this.sales.set(sale.id, sale);
    this.replaceSession(session.id, { expectedCash: round2(session.expectedCash + cashIn) });

    this.emit(
      'sale.completed',
      {
        saleId: sale.id,
        sessionId: session.id,
        registerId: sale.registerId,
        operatorId: sale.operatorId,
        total,
        payments: sale.payments,
        lines: lines.map((line) => ({
          productId: line.productId,
          sku: line.sku,
          qty: line.qty,
          unitPrice: line.unitPrice,
          lineTotal: line.lineTotal,
        })),
      },
      input.operatorId,
    );

    return sale;
  }

  /**
   * Cierra la sesion y calcula el descuadre.
   * Si supera el umbral, emite ademas cash_session.discrepancy (lo que dispara
   * la regla DESCUADRE_CAJA del seed).
   */
  closeSession(sessionId: string, countedCash: number, byUserId: string): CashSession {
    const session = this.sessions.get(sessionId);
    if (!session) throw new Error(`Sesion de caja inexistente: ${sessionId}`);
    if (session.status === 'CERRADA') throw new Error(`La sesion ${sessionId} ya esta cerrada`);

    const counted = round2(countedCash);
    const difference = round2(counted - session.expectedCash);

    const closed = this.replaceSession(sessionId, {
      status: 'CERRADA',
      closedBy: byUserId,
      closedAt: this.clock.nowIso(),
      countedCash: counted,
      difference,
    });

    this.emit(
      'cash_session.closed',
      {
        sessionId,
        registerId: closed.registerId,
        expectedCash: closed.expectedCash,
        countedCash: counted,
        difference,
      },
      byUserId,
    );

    if (Math.abs(difference) > this.discrepancyThresholdEur) {
      this.logger?.warn('Descuadre de caja por encima del umbral', { sessionId, difference });
      this.emit(
        'cash_session.discrepancy',
        {
          sessionId,
          registerId: closed.registerId,
          expectedCash: closed.expectedCash,
          countedCash: counted,
          difference,
          threshold: this.discrepancyThresholdEur,
          closedBy: byUserId,
        },
        byUserId,
      );
    }

    return closed;
  }

  private replaceSession(sessionId: string, patch: Partial<CashSession>): CashSession {
    const current = this.sessions.get(sessionId);
    if (!current) throw new Error(`Sesion de caja inexistente: ${sessionId}`);
    const updated: CashSession = Object.freeze({ ...current, ...patch });
    this.sessions.set(sessionId, updated);
    return updated;
  }

  session(sessionId: string): CashSession | undefined {
    return this.sessions.get(sessionId);
  }

  allSessions(): readonly CashSession[] {
    return [...this.sessions.values()];
  }

  sale(saleId: string): Sale | undefined {
    return this.sales.get(saleId);
  }

  allSales(): readonly Sale[] {
    return [...this.sales.values()];
  }

  affluenceLevel(): AffluenceLevel {
    return this.affluence;
  }
}

/** Facts que el modulo aporta al motor de reglas. */
export function posFacts(service: PosService): Record<string, FactResolver> {
  // Devuelven el VALOR CRUDO: FactRegistry es quien lo envuelve en { found, value }.
  return {
    'pos.cash_difference_abs': (params, ctx) => {
      const fromPayload = ctx.event.payload['difference'];
      if (typeof fromPayload === 'number') return Math.abs(fromPayload);

      const sessionId = asString(params['sessionId']) ?? asString(ctx.event.payload['sessionId']);
      const session = sessionId ? service.session(sessionId) : undefined;
      if (!session || session.difference === null) return null;
      return Math.abs(session.difference);
    },

    'pos.affluence': () => service.affluenceLevel(),
  };
}
