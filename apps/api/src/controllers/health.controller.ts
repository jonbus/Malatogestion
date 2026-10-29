import { json } from '../http/router.ts';
import type { Router } from '../http/router.ts';
import type { ModuleRegistry, ServiceLocator } from '../../../../packages/core/src/index.ts';
import type { InMemoryOutbox } from '../../../../packages/core/src/index.ts';

export interface HealthControllerDeps {
  readonly registry: ModuleRegistry;
  readonly services: ServiceLocator;
  readonly outbox: InMemoryOutbox;
  readonly describeRoutes: () => readonly unknown[];
}

/**
 * Estado del sistema.
 *
 * NO conoce el modulo healthcheck: descubre por convencion de clave cualquier
 * servicio registrado como '<modulo>:health'. Asi el host sigue siendo agnostico
 * a los modulos y el modulo de prueba demuestra la extensibilidad de verdad.
 */
export class HealthController {
  private readonly deps: HealthControllerDeps;

  constructor(deps: HealthControllerDeps) {
    this.deps = deps;
  }

  private moduleReports(): readonly Record<string, unknown>[] {
    const reports: Record<string, unknown>[] = [];

    for (const key of this.deps.services.keys()) {
      if (!key.endsWith(':health')) continue;
      const moduleId = key.slice(0, key.length - ':health'.length);
      const service = this.deps.services.tryGet<{ status?: () => unknown }>(moduleId, 'health');
      if (service && typeof service.status === 'function') {
        reports.push({ moduleId, ...(service.status() as Record<string, unknown>) });
      }
    }

    return reports;
  }

  register(router: Router): void {
    router.add({
      method: 'GET',
      pattern: '/health',
      permission: null,
      summary: 'Estado del nucleo, de los modulos y del outbox',
      handler: () => {
        const { registry, outbox } = this.deps;
        const modules = this.moduleReports();

        return json(200, {
          status: modules.some((report) => report['status'] === 'DEGRADADO') ? 'DEGRADADO' : 'OK',
          modules,
          registry: {
            count: registry.count(),
            ids: registry.ids(),
            permissions: registry.permissions().length,
            facts: registry.factKeys(),
            actions: registry.actionTypes(),
            events: { published: registry.publishedEvents(), consumed: registry.consumedEvents() },
            featureFlags: registry.featureFlags(),
            migrations: registry.migrationsPaths(),
          },
          outbox: {
            total: outbox.all().length,
            pendiente: outbox.byStatus('PENDIENTE').length,
            procesado: outbox.byStatus('PROCESADO').length,
            fallido: outbox.byStatus('FALLIDO').length,
            dlq: outbox.byStatus('DLQ').length,
          },
          routes: this.deps.describeRoutes(),
        });
      },
    });
  }
}
