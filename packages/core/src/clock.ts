import type { Clock } from '../../contracts/src/ports.ts';

/** Reloj real. En tests se inyecta un reloj mutable para no esperar nunca. */
export class SystemClock implements Clock {
  now(): Date {
    return new Date();
  }

  nowIso(): string {
    return this.now().toISOString();
  }
}

export function createClock(): Clock {
  return new SystemClock();
}
