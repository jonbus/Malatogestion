import type { Clock, FactResolver } from '../../contracts/src/ports.ts';

export interface HealthReport {
  readonly status: 'OK' | 'DEGRADADO';
  readonly uptimeSeconds: number;
  readonly startedAt: string;
}

/**
 * Servicio minimo del modulo de prueba. Se registra bajo la clave generica
 * 'health' para que el host pueda descubrirlo por convencion de clave, sin
 * conocer el identificador del modulo.
 */
export class HealthcheckService {
  private readonly clock: Clock;
  private readonly startedAtMs: number;

  constructor(clock: Clock) {
    this.clock = clock;
    this.startedAtMs = clock.now().getTime();
  }

  status(): HealthReport {
    return {
      status: 'OK',
      uptimeSeconds: this.uptimeSeconds(),
      startedAt: new Date(this.startedAtMs).toISOString(),
    };
  }

  uptimeSeconds(): number {
    return Math.max(0, Math.round((this.clock.now().getTime() - this.startedAtMs) / 1000));
  }
}

export function healthcheckFacts(service: HealthcheckService): Record<string, FactResolver> {
  return {
    // El resolver devuelve el VALOR CRUDO: es FactRegistry quien lo envuelve en
    // { found, value }. Devolver aqui el sobre lo envolveria dos veces y ninguna
    // comparacion coincidiria nunca.
    'healthcheck.uptime_seconds': () => service.uptimeSeconds(),
  };
}
