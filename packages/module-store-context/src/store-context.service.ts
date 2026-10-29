import type { Clock, FactResolver } from '../../contracts/src/ports.ts';

/**
 * Tipo propio del modulo. NO se importa de module-pos: eso seria una dependencia
 * entre modulos (violacion R1). La compatibilidad estructural basta, y el
 * composition root inyecta quien realmente mide la afluencia.
 */
export type AffluenceLevel = 'LOW' | 'MEDIUM' | 'HIGH';

/** Franjas horarias que usa el editor de reglas de Gerencia. */
export const TIME_WINDOWS: readonly string[] = ['08:00', '12:00', '17:00', '21:00'];

const WEEKDAYS = [
  'SUNDAY',
  'MONDAY',
  'TUESDAY',
  'WEDNESDAY',
  'THURSDAY',
  'FRIDAY',
  'SATURDAY',
] as const;

export interface StoreContextOptions {
  readonly clock: Clock;
  /**
   * Puerto inyectado por el composition root. El modulo NO sabe quien mide la
   * afluencia: solo pide el valor. Asi no hay import entre modulos.
   */
  readonly affluenceProvider?: () => AffluenceLevel;
  readonly forecast?: AffluenceLevel;
  readonly defaultAffluence?: AffluenceLevel;
}

export class StoreContextService {
  private readonly clock: Clock;
  private readonly affluenceProvider: (() => AffluenceLevel) | null;
  private readonly defaultAffluence: AffluenceLevel;
  private forecast: AffluenceLevel;

  constructor(options: StoreContextOptions) {
    this.clock = options.clock;
    this.affluenceProvider = options.affluenceProvider ?? null;
    this.defaultAffluence = options.defaultAffluence ?? 'MEDIUM';
    this.forecast = options.forecast ?? 'MEDIUM';
  }

  /** Dia de la semana en UTC. */
  weekday(now: Date = this.clock.now()): string {
    return WEEKDAYS[now.getUTCDay()] ?? 'MONDAY';
  }

  /**
   * Etiqueta de la franja ACTIVA.
   * Devuelve la hora de inicio de la franja en curso, de modo que la regla del
   * seed `{"op":"in","value":["17:00","21:00"]}` signifique "estamos en la
   * franja de tarde o de noche". Es una etiqueta, no una hora exacta.
   */
  timeWindow(now: Date = this.clock.now()): string {
    const minutes = now.getUTCHours() * 60 + now.getUTCMinutes();
    let active = TIME_WINDOWS[0] ?? '08:00';

    for (const window of TIME_WINDOWS) {
      const [hours = '0', mins = '0'] = window.split(':');
      const windowMinutes = Number(hours) * 60 + Number(mins);
      if (minutes >= windowMinutes) active = window;
    }

    return active;
  }

  affluence(): AffluenceLevel {
    return this.affluenceProvider?.() ?? this.defaultAffluence;
  }

  affluenceForecast(): AffluenceLevel {
    return this.forecast;
  }

  setAffluenceForecast(level: AffluenceLevel): void {
    this.forecast = level;
  }
}

/** Facts que el modulo aporta al motor de reglas. */
export function storeContextFacts(service: StoreContextService): Record<string, FactResolver> {
  // Devuelven el VALOR CRUDO: FactRegistry es quien lo envuelve en { found, value }.
  return {
    'calendar.weekday': (_params, ctx) => service.weekday(ctx.now),
    'calendar.time_window': (_params, ctx) => service.timeWindow(ctx.now),
    'store.affluence': () => service.affluence(),
    'store.affluence_forecast': () => service.affluenceForecast(),
  };
}
