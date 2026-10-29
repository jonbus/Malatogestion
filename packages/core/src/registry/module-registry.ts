import type {
  ActionDeclaration,
  FactDeclaration,
  ModuleManifest,
  UiRouteDeclaration,
} from '../../../contracts/src/manifest.ts';
import type { RoleCode } from '../../../contracts/src/rbac.ts';

/** Manifiesto normalizado que el registro guarda junto a su modulo. */
export interface RegisteredModule {
  readonly manifest: ModuleManifest;
  readonly permissions: readonly string[];
  readonly facts: readonly FactDeclaration[];
  readonly actions: readonly ActionDeclaration[];
  readonly uiRoutes: readonly UiRouteDeclaration[];
}

export class ModuleRegistrationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ModuleRegistrationError';
  }
}

/**
 * Registro de modulos. Agrega permisos, eventos, facts, acciones, rutas UI y
 * feature flags de todos los manifiestos. NO conoce ningun modulo concreto:
 * trabaja con lo que le entregan.
 */
export class ModuleRegistry {
  private readonly modules = new Map<string, RegisteredModule>();

  register(manifest: ModuleManifest): RegisteredModule {
    if (this.modules.has(manifest.id)) {
      throw new ModuleRegistrationError(`Modulo duplicado: '${manifest.id}'`);
    }
    if (!/^[a-z][a-z0-9-]*$/.test(manifest.id)) {
      throw new ModuleRegistrationError(
        `Identificador de modulo invalido: '${manifest.id}' (minusculas, digitos y guiones)`,
      );
    }

    this.assertNoCollisions(manifest);

    const registered: RegisteredModule = {
      manifest,
      permissions: [...manifest.permissions],
      facts: [...manifest.facts],
      actions: [...manifest.actions],
      uiRoutes: [...manifest.uiRoutes],
    };
    this.modules.set(manifest.id, registered);
    return registered;
  }

  private assertNoCollisions(manifest: ModuleManifest): void {
    for (const permission of manifest.permissions) {
      const owner = this.ownerOfPermission(permission);
      if (owner) {
        throw new ModuleRegistrationError(
          `Permiso '${permission}' declarado por '${manifest.id}' ya pertenece a '${owner}'`,
        );
      }
    }
    for (const fact of manifest.facts) {
      const owner = this.ownerOfFact(fact.key);
      if (owner) {
        throw new ModuleRegistrationError(
          `Fact '${fact.key}' declarado por '${manifest.id}' ya pertenece a '${owner}'`,
        );
      }
    }
    for (const action of manifest.actions) {
      const owner = this.ownerOfAction(action.type);
      if (owner) {
        throw new ModuleRegistrationError(
          `Accion '${action.type}' declarada por '${manifest.id}' ya pertenece a '${owner}'`,
        );
      }
    }
    for (const route of manifest.uiRoutes) {
      const owner = this.ownerOfRoute(route.path);
      if (owner) {
        throw new ModuleRegistrationError(
          `Ruta UI '${route.path}' declarada por '${manifest.id}' ya pertenece a '${owner}'`,
        );
      }
    }
  }

  ownerOfPermission(permission: string): string | null {
    for (const mod of this.modules.values()) {
      if (mod.permissions.includes(permission)) return mod.manifest.id;
    }
    return null;
  }

  ownerOfFact(key: string): string | null {
    for (const mod of this.modules.values()) {
      if (mod.facts.some((fact) => fact.key === key)) return mod.manifest.id;
    }
    return null;
  }

  ownerOfAction(type: string): string | null {
    for (const mod of this.modules.values()) {
      if (mod.actions.some((action) => action.type === type)) return mod.manifest.id;
    }
    return null;
  }

  ownerOfRoute(path: string): string | null {
    for (const mod of this.modules.values()) {
      if (mod.uiRoutes.some((route) => route.path === path)) return mod.manifest.id;
    }
    return null;
  }

  has(id: string): boolean {
    return this.modules.has(id);
  }

  get(id: string): RegisteredModule {
    const mod = this.modules.get(id);
    if (!mod) throw new ModuleRegistrationError(`Modulo no registrado: '${id}'`);
    return mod;
  }

  all(): readonly RegisteredModule[] {
    return [...this.modules.values()];
  }

  ids(): readonly string[] {
    return [...this.modules.keys()].sort();
  }

  count(): number {
    return this.modules.size;
  }

  permissions(): readonly string[] {
    return this.all()
      .flatMap((mod) => mod.permissions)
      .sort();
  }

  hasPermission(permission: string): boolean {
    return this.ownerOfPermission(permission) !== null;
  }

  publishedEvents(): readonly string[] {
    return [...new Set(this.all().flatMap((mod) => mod.manifest.publishes))].sort();
  }

  consumedEvents(): readonly string[] {
    return [...new Set(this.all().flatMap((mod) => mod.manifest.consumes))].sort();
  }

  facts(): readonly FactDeclaration[] {
    return this.all().flatMap((mod) => mod.facts);
  }

  factKeys(): readonly string[] {
    return this.facts()
      .map((fact) => fact.key)
      .sort();
  }

  actions(): readonly ActionDeclaration[] {
    return this.all().flatMap((mod) => mod.actions);
  }

  actionTypes(): readonly string[] {
    return this.actions()
      .map((action) => action.type)
      .sort();
  }

  /** Rutas UI agregadas; sin rol devuelve todas. */
  uiRoutes(role?: RoleCode): readonly UiRouteDeclaration[] {
    const routes = this.all().flatMap((mod) => mod.uiRoutes);
    if (!role) return routes;
    return routes.filter((route) => route.roles.includes(role));
  }

  featureFlags(): readonly string[] {
    return [...new Set(this.all().flatMap((mod) => mod.manifest.featureFlags))].sort();
  }

  /** Solo los modulos que declaran migraciones (los que tienen tablas propias). */
  migrationsPaths(): readonly string[] {
    return this.all()
      .map((mod) => mod.manifest.migrationsPath)
      .filter((path): path is string => path !== undefined)
      .sort();
  }
}
