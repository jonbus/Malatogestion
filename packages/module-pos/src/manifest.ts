import type { ModuleManifest } from '../../contracts/src/manifest.ts';
import { PERMISSIONS, ROLES } from '../../contracts/src/rbac.ts';

export const posManifest: ModuleManifest = {
  id: 'pos',
  name: 'Punto de venta',
  version: '0.1.0',

  permissions: [
    PERMISSIONS.POS_OPEN_SESSION,
    PERMISSIONS.POS_CLOSE_SESSION,
    PERMISSIONS.POS_SELL,
    PERMISSIONS.POS_REFUND,
    PERMISSIONS.POS_SESSIONS_READ,
  ],

  publishes: [
    'cash_session.opened',
    'cash_session.closed',
    'cash_session.discrepancy',
    'sale.completed',
  ],

  consumes: [],

  facts: [
    {
      key: 'pos.cash_difference_abs',
      description: 'Descuadre absoluto de una sesion de caja, en euros.',
      params: ['sessionId'],
    },
    {
      key: 'pos.affluence',
      description: 'Afluencia actual en tienda: LOW, MEDIUM o HIGH.',
      params: [],
    },
  ],

  actions: [],

  uiRoutes: [
    {
      path: '/caja',
      label: 'Caja',
      roles: [ROLES.OPERADORA, ROLES.COORDINADORA, ROLES.GERENCIA],
      permission: PERMISSIONS.POS_SELL,
    },
    {
      path: '/caja/sesiones',
      label: 'Sesiones y descuadres',
      roles: [ROLES.GERENCIA, ROLES.COORDINADORA],
      permission: PERMISSIONS.POS_SESSIONS_READ,
    },
  ],

  featureFlags: ['pos.offline_queue.enabled'],

  migrationsPath: 'packages/module-pos/migrations',
};
