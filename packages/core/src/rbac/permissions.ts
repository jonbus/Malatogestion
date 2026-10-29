import { ROLE_POLICY, WILDCARD } from '../../../contracts/src/rbac.ts';
import type { RoleCode, SessionUser } from '../../../contracts/src/rbac.ts';

export type RolePolicy = Readonly<Record<string, readonly string[]>>;

export class PermissionDeniedError extends Error {
  readonly permission: string;
  readonly role: string;

  constructor(permission: string, role: string) {
    super(`El rol ${role} no tiene el permiso ${permission}`);
    this.name = 'PermissionDeniedError';
    this.permission = permission;
    this.role = role;
  }
}

/** Permisos efectivos de un rol segun la politica (por defecto, la de negocio). */
export function permissionsOf(role: RoleCode | string, policy: RolePolicy = ROLE_POLICY): readonly string[] {
  return policy[role] ?? [];
}

/**
 * Comprobacion de permiso granular.
 * El nucleo NO conoce los codigos: los recibe por la politica inyectada.
 */
export function can(
  user: SessionUser | null | undefined,
  permission: string,
  policy: RolePolicy = ROLE_POLICY,
): boolean {
  if (!user) return false;

  const granted = [...permissionsOf(user.role, policy), ...(user.extraPermissions ?? [])];
  return granted.includes(WILDCARD) || granted.includes(permission);
}

export function canAny(user: SessionUser | null | undefined, permissions: readonly string[]): boolean {
  return permissions.some((permission) => can(user, permission));
}

export function assertCan(user: SessionUser | null | undefined, permission: string): void {
  if (!can(user, permission)) {
    throw new PermissionDeniedError(permission, user?.role ?? 'ANONIMO');
  }
}

/** true si el rol tiene acceso total (comodin). */
export function isSuperRole(role: RoleCode | string, policy: RolePolicy = ROLE_POLICY): boolean {
  return permissionsOf(role, policy).includes(WILDCARD);
}
