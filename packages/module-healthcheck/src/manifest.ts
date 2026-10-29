import type { ModuleManifest } from '../../contracts/src/manifest.ts';
import { ROLES } from '../../contracts/src/rbac.ts';

/**
 * MODULO DE PRUEBA DE EXTENSIBILIDAD.
 * Registra su propio permiso, su propio fact y su propia ruta UI, y no se toca
 * ni un fichero de packages/core para que funcione: eso demuestra que el
 * nucleo esta desacoplado de verdad.
 */
export const healthcheckManifest: ModuleManifest = {
  id: 'healthcheck',
  name: 'Estado del sistema',
  version: '0.1.0',

  permissions: ['healthcheck.read'],

  publishes: [],
  consumes: [],

  facts: [
    {
      key: 'healthcheck.uptime_seconds',
      description: 'Segundos que lleva vivo el proceso.',
      params: [],
    },
  ],

  actions: [],

  uiRoutes: [
    {
      path: '/salud',
      label: 'Estado del sistema',
      roles: [ROLES.GERENCIA],
      permission: 'healthcheck.read',
    },
  ],

  featureFlags: ['healthcheck.expose.public'],

  // Sin migraciones: este modulo no persiste nada, todo vive en memoria.
  // Declarar una ruta inexistente seria mentir en el manifiesto.
};
