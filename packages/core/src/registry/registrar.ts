import type {
  ActionHandler,
  EventBusPort,
  EventHandler,
  FactResolver,
  Logger,
} from '../../../contracts/src/ports.ts';
import type { ModuleManifest } from '../../../contracts/src/manifest.ts';
import { ModuleRegistry, ModuleRegistrationError } from './module-registry.ts';
import type { ActionRegistry } from '../rules/action-registry.ts';
import type { FactRegistry } from '../rules/fact-registry.ts';

/** Suscripcion declarada por un modulo en su implementacion. */
export interface EventSubscriber {
  readonly id: string;
  readonly eventType: string;
  readonly handler: EventHandler;
}

/** Implementacion de un modulo: manifiesto + lo que aporta al sistema. */
export interface ModuleImplementation {
  readonly manifest: ModuleManifest;
  readonly facts?: Readonly<Record<string, FactResolver>>;
  readonly actions?: readonly ActionHandler[];
  readonly subscribers?: readonly EventSubscriber[];
  readonly services?: Readonly<Record<string, unknown>>;
}

/** Localizador de servicios: los controladores resuelven aqui sus dependencias. */
export class ServiceLocator {
  private readonly services = new Map<string, unknown>();

  provide(moduleId: string, key: string, service: unknown): void {
    const id = `${moduleId}:${key}`;
    if (this.services.has(id)) throw new ModuleRegistrationError(`Servicio duplicado: '${id}'`);
    this.services.set(id, service);
  }

  get<T>(moduleId: string, key: string): T {
    const id = `${moduleId}:${key}`;
    const service = this.services.get(id);
    if (service === undefined) throw new ModuleRegistrationError(`Servicio no registrado: '${id}'`);
    return service as T;
  }

  tryGet<T>(moduleId: string, key: string): T | undefined {
    return this.services.get(`${moduleId}:${key}`) as T | undefined;
  }

  keys(): readonly string[] {
    return [...this.services.keys()].sort();
  }
}

export interface RegistrarInput {
  readonly modules: readonly ModuleImplementation[];
  readonly bus: EventBusPort;
  readonly facts: FactRegistry;
  readonly actions: ActionRegistry;
  readonly logger: Logger;
}

export interface RegisteredSystem {
  readonly registry: ModuleRegistry;
  readonly services: ServiceLocator;
  /** Suscripciones conectadas al bus, en orden de registro. */
  readonly wiredSubscriptions: readonly string[];
}

/**
 * Punto de composicion PURO: valida manifiestos, los registra, publica facts y
 * acciones y conecta las suscripciones al bus. No abre conexiones ni lee disco.
 */
export function registerModules(input: RegistrarInput): RegisteredSystem {
  const registry = new ModuleRegistry();
  const services = new ServiceLocator();
  const wired: string[] = [];

  for (const implementation of input.modules) {
    const { manifest } = implementation;
    registry.register(manifest);

    for (const [key, resolver] of Object.entries(implementation.facts ?? {})) {
      if (!manifest.facts.some((fact) => fact.key === key)) {
        throw new ModuleRegistrationError(
          `El modulo '${manifest.id}' registra el fact '${key}' sin declararlo en su manifiesto`,
        );
      }
      input.facts.register(key, resolver, manifest.id);
    }

    for (const handler of implementation.actions ?? []) {
      if (!manifest.actions.some((action) => action.type === handler.type)) {
        throw new ModuleRegistrationError(
          `El modulo '${manifest.id}' registra la accion '${handler.type}' sin declararla en su manifiesto`,
        );
      }
      input.actions.register(handler, manifest.id);
    }

    for (const subscriber of implementation.subscribers ?? []) {
      if (!manifest.consumes.includes(subscriber.eventType) && subscriber.eventType !== '*') {
        throw new ModuleRegistrationError(
          `El modulo '${manifest.id}' se suscribe a '${subscriber.eventType}' sin declararlo en consumes`,
        );
      }
      input.bus.subscribe(subscriber.eventType, subscriber.handler, {
        id: `${manifest.id}:${subscriber.id}`,
        moduleId: manifest.id,
      });
      wired.push(`${manifest.id}:${subscriber.id} -> ${subscriber.eventType}`);
    }

    for (const [key, service] of Object.entries(implementation.services ?? {})) {
      services.provide(manifest.id, key, service);
    }

    input.logger.debug('Modulo registrado', {
      moduleId: manifest.id,
      version: manifest.version,
      facts: manifest.facts.length,
      actions: manifest.actions.length,
    });
  }

  return { registry, services, wiredSubscriptions: wired };
}
