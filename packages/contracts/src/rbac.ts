/**
 * Vocabulario de roles y permisos.
 * Los codigos son EXACTAMENTE los que siembra db/seed/001_demo_store.sql.
 * El nucleo (packages/core) no conoce estos nombres: los recibe inyectados.
 */

export const ROLES = {
  GERENCIA: 'GERENCIA',
  COORDINADORA: 'COORDINADORA',
  OPERADORA: 'OPERADORA',
} as const;

export type RoleCode = (typeof ROLES)[keyof typeof ROLES];

/**
 * Nivel jerarquico de cada rol. Es lo que permite COMPARAR roles en lugar de
 * tratarlos como conjuntos disjuntos: `required_role` en una tarea es el rol
 * MINIMO, no el exclusivo, asi que una persona puede tomarla si su nivel es
 * mayor o igual.
 *
 * En una tienda de alimentacion esto no es un matiz teorico: con 2 operadoras y
 * 91 h semanales de apertura, quien coordina tambien repone y cobra. Si los roles
 * fueran excluyentes, el motor apilaria trabajo en dos personas mientras tres
 * coordinadoras miran.
 *
 * Debe coincidir con core.roles.level en db/seed/001_demo_store.sql.
 */
export const ROLE_LEVELS: Readonly<Record<RoleCode, number>> = {
  GERENCIA: 30,
  COORDINADORA: 20,
  OPERADORA: 10,
};

export function roleLevel(role: RoleCode): number {
  return ROLE_LEVELS[role];
}

/** Comodin de acceso total. */
export const WILDCARD = '*';

export const PERMISSIONS = {
  CORE_USERS_READ: 'core.users.read',
  CORE_USERS_MANAGE: 'core.users.manage',
  CORE_ROLES_MANAGE: 'core.roles.manage',
  CORE_SETTINGS_MANAGE: 'core.settings.manage',
  CORE_AUDIT_READ: 'core.audit.read',

  CATALOG_PRODUCTS_READ: 'catalog.products.read',
  CATALOG_PRODUCTS_MANAGE: 'catalog.products.manage',
  CATALOG_SUPPLIERS_MANAGE: 'catalog.suppliers.manage',
  CATALOG_PRICES_MANAGE: 'catalog.prices.manage',

  INVENTORY_READ: 'inventory.read',
  INVENTORY_ADJUST: 'inventory.adjust',
  INVENTORY_WASTAGE_REGISTER: 'inventory.wastage.register',
  INVENTORY_LOTS_MANAGE: 'inventory.lots.manage',

  ORDERS_READ: 'orders.read',
  ORDERS_CREATE: 'orders.create',
  ORDERS_APPROVE: 'orders.approve',
  ORDERS_SEND: 'orders.send',
  ORDERS_RECEIVE: 'orders.receive',

  TASKS_READ: 'tasks.read',
  TASKS_CREATE: 'tasks.create',
  TASKS_ASSIGN: 'tasks.assign',
  TASKS_REASSIGN: 'tasks.reassign',
  TASKS_COMPLETE: 'tasks.complete',
  TASKS_TEMPLATES_MANAGE: 'tasks.templates.manage',

  RULES_READ: 'rules.read',
  RULES_MANAGE: 'rules.manage',
  RULES_SIMULATE: 'rules.simulate',
  RULES_OVERRIDE: 'rules.override',

  POS_OPEN_SESSION: 'pos.open_session',
  POS_CLOSE_SESSION: 'pos.close_session',
  POS_SELL: 'pos.sell',
  POS_REFUND: 'pos.refund',
  POS_SESSIONS_READ: 'pos.sessions.read',

  NOTIFY_READ: 'notify.read',
  NOTIFY_MANAGE: 'notify.manage',

  ANALYTICS_DASHBOARD_GERENCIA: 'analytics.dashboard.gerencia',
  ANALYTICS_DASHBOARD_OPERACIONES: 'analytics.dashboard.operaciones',
  ANALYTICS_KPI_READ: 'analytics.kpi.read',
  ANALYTICS_MARGIN_READ: 'analytics.margin.read',
  ANALYTICS_EXPORT: 'analytics.export',
} as const;

export type PermissionCode = (typeof PERMISSIONS)[keyof typeof PERMISSIONS];

/** Todos los permisos conocidos, en orden estable. */
export const ALL_PERMISSIONS: readonly string[] = Object.values(PERMISSIONS);

/**
 * Politica por defecto rol -> permisos. Es configuracion de negocio, no codigo
 * del nucleo: por eso vive en contracts y no en packages/core.
 */
export const ROLE_POLICY: Readonly<Record<RoleCode, readonly string[]>> = {
  GERENCIA: [WILDCARD],
  // Coordinacion = ENCARGADAS. El rol es JERARQUICO: contiene TODO lo de OPERADORA
  // (reponen y cobran, no solo supervisan) mas sus propias facultades. Son las
  // duenas del catalogo, de ahi CATALOG_PRODUCTS_MANAGE.
  COORDINADORA: [
    // --- todo lo de OPERADORA (ver mas abajo) ---
    PERMISSIONS.CATALOG_PRODUCTS_READ,
    PERMISSIONS.INVENTORY_READ,
    PERMISSIONS.INVENTORY_WASTAGE_REGISTER,
    PERMISSIONS.TASKS_READ,
    PERMISSIONS.TASKS_COMPLETE,
    PERMISSIONS.POS_OPEN_SESSION,
    PERMISSIONS.POS_CLOSE_SESSION,
    PERMISSIONS.POS_SELL,
    PERMISSIONS.NOTIFY_READ,
    // --- facultades propias de coordinacion ---
    PERMISSIONS.CATALOG_PRODUCTS_MANAGE,
    PERMISSIONS.INVENTORY_ADJUST,
    PERMISSIONS.INVENTORY_LOTS_MANAGE,
    PERMISSIONS.ORDERS_READ,
    PERMISSIONS.ORDERS_CREATE,
    PERMISSIONS.ORDERS_SEND,
    PERMISSIONS.ORDERS_RECEIVE,
    PERMISSIONS.TASKS_CREATE,
    PERMISSIONS.TASKS_ASSIGN,
    PERMISSIONS.TASKS_REASSIGN,
    PERMISSIONS.RULES_READ,
    PERMISSIONS.RULES_SIMULATE,
    PERMISSIONS.RULES_OVERRIDE,
    PERMISSIONS.POS_SESSIONS_READ,
    PERMISSIONS.NOTIFY_MANAGE,
    PERMISSIONS.ANALYTICS_DASHBOARD_OPERACIONES,
    PERMISSIONS.ANALYTICS_KPI_READ,
  ],
  OPERADORA: [
    PERMISSIONS.CATALOG_PRODUCTS_READ,
    PERMISSIONS.INVENTORY_READ,
    PERMISSIONS.INVENTORY_WASTAGE_REGISTER,
    PERMISSIONS.TASKS_READ,
    PERMISSIONS.TASKS_COMPLETE,
    PERMISSIONS.POS_OPEN_SESSION,
    PERMISSIONS.POS_CLOSE_SESSION,
    PERMISSIONS.POS_SELL,
    PERMISSIONS.NOTIFY_READ,
  ],
};

/** Usuario autenticado tal y como lo ve el guard de permisos. */
export interface SessionUser {
  readonly id: string;
  readonly storeId: string;
  readonly role: RoleCode;
  readonly displayName: string;
  /** Concesiones puntuales que amplian la politica del rol (core.user_permissions). */
  readonly extraPermissions?: readonly string[];
}
