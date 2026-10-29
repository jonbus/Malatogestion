import { PERMISSIONS } from '../../../../packages/contracts/src/rbac.ts';
import { json } from '../http/router.ts';
import type { Router } from '../http/router.ts';
import type { InventoryService } from '../../../../packages/module-inventory/src/inventory.service.ts';

/** Rutas de stock. La logica vive en el modulo; aqui solo se expone. */
export class InventoryController {
  private readonly inventory: InventoryService;

  constructor(inventory: InventoryService) {
    this.inventory = inventory;
  }

  register(router: Router): void {
    router.add({
      method: 'GET',
      pattern: '/stock/alerts',
      permission: PERMISSIONS.INVENTORY_READ,
      summary: 'Productos por debajo del minimo',
      handler: () => {
        const alerts = this.inventory
          .stockRows()
          .filter((row) => row.qty < row.minStock)
          .map((row) => ({
            productId: row.productId,
            sku: row.sku,
            categoryPath: row.categoryPath,
            locationCode: row.locationCode,
            qty: row.qty,
            minStock: row.minStock,
            targetStock: row.targetStock,
            deficit: Number((row.minStock - row.qty).toFixed(3)),
          }))
          .sort((a, b) => b.deficit - a.deficit);

        return json(200, { count: alerts.length, alerts });
      },
    });

    router.add({
      method: 'GET',
      pattern: '/stock/expiring',
      permission: PERMISSIONS.INVENTORY_READ,
      summary: 'Lotes proximos a caducar',
      handler: (request) => {
        const raw = request.query.get('days');
        const days = raw === null ? 3 : Number(raw);
        const safeDays = Number.isFinite(days) ? days : 3;

        const lots = this.inventory.findExpiringLots(safeDays).map((lot) => ({
          lotId: lot.lotId,
          sku: lot.sku,
          batchCode: lot.batchCode,
          expiryDate: lot.expiryDate,
          daysToExpiry: this.inventory.daysToExpiry(lot.expiryDate),
          qty: lot.qty,
        }));

        return json(200, { withinDays: safeDays, count: lots.length, lots });
      },
    });
  }
}
