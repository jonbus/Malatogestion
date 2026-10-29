/**
 * Manifiesto de modulo: el contrato que hace que el producto siga siendo vivo.
 * Todo lo que un modulo aporta al sistema se declara aqui. Anadir un modulo
 * NUNCA requiere tocar packages/core.
 */
import type { RoleCode } from './rbac.ts';

/** Variable que el modulo aporta al motor de reglas. */
export interface FactDeclaration {
  /** Clave cualificada, p. ej. 'inventory.stock_ratio'. */
  readonly key: string;
  readonly description: string;
  /** Nombres de los parametros que acepta (informativo, para el editor de reglas). */
  readonly params?: readonly string[];
}

/** Accion que el modulo aporta al motor de reglas. */
export interface ActionDeclaration {
  /** Tipo de accion, p. ej. 'CREATE_TASK'. */
  readonly type: string;
  readonly description: string;
}

/** Entrada de navegacion que el modulo aporta a la shell web. */
export interface UiRouteDeclaration {
  readonly path: string;
  readonly label: string;
  /** Roles que ven la ruta. */
  readonly roles: readonly RoleCode[];
  /** Permiso exigido para entrar. */
  readonly permission?: string;
}

/** Manifiesto completo de un modulo. */
export interface ModuleManifest {
  /** Identificador unico en minusculas, p. ej. 'inventory'. */
  readonly id: string;
  readonly name: string;
  /** Versionado independiente del resto del sistema (semver). */
  readonly version: string;

  /** Permisos granulares por accion que el modulo siembra en el nucleo. */
  readonly permissions: readonly string[];
  /** Eventos de dominio que emite. */
  readonly publishes: readonly string[];
  /** Eventos de otros modulos que escucha. */
  readonly consumes: readonly string[];

  readonly facts: readonly FactDeclaration[];
  readonly actions: readonly ActionDeclaration[];
  readonly uiRoutes: readonly UiRouteDeclaration[];
  /** Interruptores para activar/desactivar funcionalidad sin desplegar. */
  readonly featureFlags: readonly string[];

  /**
   * Ruta a sus migraciones SQL. OPCIONAL a proposito: un modulo sin tablas
   * propias no debe declarar una ruta que no existe. Si se declara, la ruta
   * tiene que existir (lo verifica tests/migrations-consistency.test.ts).
   */
  readonly migrationsPath?: string;
}
