import { randomUUID } from 'node:crypto';
import type { IdGenerator } from '../../contracts/src/ports.ts';

/** Generador de identificadores basado en UUID v4 (criptograficamente seguro). */
export class UuidGenerator implements IdGenerator {
  next(): string {
    return randomUUID();
  }
}

export function createIdGenerator(): IdGenerator {
  return new UuidGenerator();
}
