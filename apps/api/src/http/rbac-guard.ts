import { can } from '../../../../packages/core/src/index.ts';
import type { ModuleRegistry } from '../../../../packages/core/src/index.ts';
import type { SessionUser } from '../../../../packages/contracts/src/rbac.ts';
import type { RouteDefinition } from './router.ts';

export interface GuardOutcome {
  readonly allowed: boolean;
  readonly status: number;
  readonly body: unknown;
}

const ALLOWED: GuardOutcome = { allowed: true, status: 200, body: null };

/**
 * Guard de permisos por ruta.
 *
 * Hace TRES comprobaciones, no dos:
 *  1. hay sesion,
 *  2. el permiso que exige la ruta existe de verdad en algun manifiesto
 *     (si no, es un fallo de programacion y devuelve 500),
 *  3. el rol del usuario lo tiene.
 *
 * La comprobacion 2 es la que impide que una ruta pida un permiso inventado.
 */
export function authorize(
  route: RouteDefinition,
  user: SessionUser | null,
  registry: ModuleRegistry,
): GuardOutcome {
  if (route.permission === null) return ALLOWED;

  if (!user) {
    return { allowed: false, status: 401, body: { error: 'NO_AUTENTICADO' } };
  }

  if (!registry.hasPermission(route.permission)) {
    return {
      allowed: false,
      status: 500,
      body: {
        error: 'PERMISO_NO_DECLARADO',
        permission: route.permission,
        detail: 'Ningun manifiesto declara este permiso: revisa el modulo que expone la ruta',
      },
    };
  }

  if (!can(user, route.permission)) {
    return {
      allowed: false,
      status: 403,
      body: {
        error: 'PERMISO_DENEGADO',
        permission: route.permission,
        role: user.role,
      },
    };
  }

  return ALLOWED;
}
