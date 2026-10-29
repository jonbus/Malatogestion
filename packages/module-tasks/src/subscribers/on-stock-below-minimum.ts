import type { DomainEvent } from '../../../contracts/src/domain-event.ts';
import type { EventSubscriber } from '../../../core/src/registry/registrar.ts';
import type { TasksService } from '../tasks.service.ts';

function asNumber(value: unknown): number {
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  return 0;
}

/**
 * Reaccion del modulo de tareas a una rotura de stock:
 * crea una tarea de reposicion prioritaria y la asigna a quien menos carga tenga.
 * Si el evento se reintenta, la idempotencia del bus evita duplicar la tarea.
 */
export function onStockBelowMinimum(service: TasksService): EventSubscriber {
  return {
    id: 'on-stock-below-minimum',
    eventType: 'stock.below_minimum',
    handler: (event: DomainEvent) => {
      const payload = event.payload;
      const sku = typeof payload['sku'] === 'string' ? payload['sku'] : 'producto';
      const deficit = asNumber(payload['deficit']);
      const assigneeId = service.pickAssignee('OPERADORA', 'LEAST_LOADED');
      const dueAt = new Date(Date.parse(event.occurredAt) + 30 * 60_000).toISOString();

      service.createTask({
        title: `Reponer ${sku} en sala`,
        description: `Stock por debajo del minimo: faltan ${deficit} unidades.`,
        priority: deficit > 0 ? 'ALTA' : 'MEDIA',
        assigneeId,
        dueAt,
        templateCode: 'REPOSICION_PRIORITARIA',
        createdBy: null,
        payload: {
          origin: 'EVENT',
          sku,
          productId: payload['productId'] ?? null,
          deficit,
          sourceEventId: event.eventId,
        },
      });
    },
  };
}
