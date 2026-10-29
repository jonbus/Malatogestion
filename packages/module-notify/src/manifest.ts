import type { ModuleManifest } from '../../contracts/src/manifest.ts';
import { ROLES } from '../../contracts/src/rbac.ts';

export const notifyManifest: ModuleManifest = {
  id: 'notify',
  name: 'Notificaciones',
  version: '0.1.0',

  // notify.read y notify.manage ya existen en core.permissions (seed).
  // notify.send esta declarado aqui y AUN NO tiene migracion: es una de las dos
  // filas pendientes de sembrar (ver tests/migrations-consistency.test.ts).
  permissions: ['notify.read', 'notify.send', 'notify.manage'],

  publishes: ['notification.sent'],

  consumes: [],

  facts: [],

  actions: [
    {
      type: 'NOTIFY',
      description: 'Emite una notificacion dirigida a un rol o a una persona concreta.',
    },
  ],

  uiRoutes: [
    {
      path: '/notificaciones',
      label: 'Notificaciones',
      roles: [ROLES.GERENCIA, ROLES.COORDINADORA, ROLES.OPERADORA],
      permission: 'notify.read',
    },
  ],

  featureFlags: ['notify.push.enabled', 'notify.email.enabled'],

  migrationsPath: 'packages/module-notify/migrations',
};
