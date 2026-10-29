import type { ModuleManifest } from '../../contracts/src/manifest.ts';
import { PERMISSIONS, ROLES } from '../../contracts/src/rbac.ts';

export const inventoryManifest: ModuleManifest = {
  id: 'inventory',
  name: 'Inventario',
  version: '0.1.0',

  permissions: [
    PERMISSIONS.INVENTORY_READ,
    PERMISSIONS.INVENTORY_ADJUST,
    PERMISSIONS.INVENTORY_WASTAGE_REGISTER,
    PERMISSIONS.INVENTORY_LOTS_MANAGE,
  ],

  publishes: ['stock.below_minimum', 'lot.expiring_soon', 'wastage.registered'],

  // Declarado para el Bloque 1; las suscripciones se implementaran entonces.
  consumes: ['sale.completed', 'reception.completed'],

  facts: [
    {
      key: 'inventory.stock_ratio',
      description:
        'Peor ratio stock/minimo de la categoria o producto (0-1). Sin params usa el evento.',
      params: ['categoryPath', 'productId', 'locationCode'],
    },
    {
      key: 'inventory.days_to_expiry',
      description: 'Dias que faltan para que caduque un lote. Sin params toma lotId del evento.',
      params: ['lotId'],
    },
    {
      key: 'inventory.lot_qty',
      description: 'Unidades disponibles de un lote. Sin params toma lotId del evento.',
      params: ['lotId'],
    },
  ],

  actions: [],

  uiRoutes: [
    { path: '/stock', label: 'Stock', roles: [ROLES.GERENCIA, ROLES.COORDINADORA] },
    {
      path: '/stock/alertas',
      label: 'Alertas de stock',
      roles: [ROLES.GERENCIA, ROLES.COORDINADORA],
      permission: PERMISSIONS.INVENTORY_READ,
    },
  ],

  featureFlags: ['inventory.lots.enabled'],

  migrationsPath: 'packages/module-inventory/migrations',
};
