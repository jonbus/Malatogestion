/**
 * Registro de idempotencia: (suscripcion, eventId) ya procesado.
 * El outbox garantiza entrega AL MENOS UNA VEZ; esto evita el efecto duplicado.
 */
export class IdempotencyStore {
  private readonly processed = new Set<string>();

  private static key(subscriptionId: string, eventId: string): string {
    return `${subscriptionId}::${eventId}`;
  }

  has(subscriptionId: string, eventId: string): boolean {
    return this.processed.has(IdempotencyStore.key(subscriptionId, eventId));
  }

  mark(subscriptionId: string, eventId: string): void {
    this.processed.add(IdempotencyStore.key(subscriptionId, eventId));
  }

  size(): number {
    return this.processed.size;
  }

  clear(): void {
    this.processed.clear();
  }

  /**
   * Ejecuta `fn` solo si (suscripcion, evento) no se proceso CON EXITO antes.
   * Se marca DESPUES de que `fn` termine bien: si falla, el reintento del outbox
   * debe volver a ejecutarla (entrega al menos una vez + deduplicacion en exito).
   * Por eso los manejadores deben ser idempotentes por diseno.
   */
  async run<T>(
    subscriptionId: string,
    eventId: string,
    fn: () => Promise<T>,
  ): Promise<{ executed: boolean; value?: T }> {
    if (this.has(subscriptionId, eventId)) return { executed: false };
    const value = await fn();
    this.mark(subscriptionId, eventId);
    return { executed: true, value };
  }
}
