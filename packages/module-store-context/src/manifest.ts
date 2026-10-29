import type { ModuleManifest } from '../../contracts/src/manifest.ts';

/**
 * Contexto de tienda: calendario y afluencia.
 *
 * Estas variables NO son del host ni del nucleo: son datos de negocio que el
 * motor de reglas necesita. Por eso viven en un modulo con su manifiesto, y no
 * en apps/api. Anadir una variable nueva (por ejemplo, "es víspera de festivo")
 * es anadir un fact aqui, sin tocar packages/core ni el host.
 */
export const storeContextManifest: ModuleManifest = {
  id: 'store-context',
  name: 'Contexto de tienda',
  version: '0.1.0',

  // No expone permisos propios: sus variables las consume el motor de reglas,
  // no una pantalla. Un modulo puede aportar facts sin aportar permisos.
  permissions: [],

  publishes: [],
  consumes: [],

  facts: [
    {
      key: 'calendar.weekday',
      description: 'Dia de la semana en UTC: MONDAY..SUNDAY.',
      params: [],
    },
    {
      key: 'calendar.time_window',
      description:
        'Etiqueta de la franja horaria activa (08:00, 12:00, 17:00, 21:00). Es una etiqueta, no una hora: por eso las reglas la comparan con el operador "in".',
      params: [],
    },
    {
      key: 'store.affluence',
      description: 'Afluencia actual en tienda: LOW, MEDIUM o HIGH.',
      params: [],
    },
    {
      key: 'store.affluence_forecast',
      description: 'Afluencia prevista para la franja en curso.',
      params: [],
    },
  ],

  actions: [],

  uiRoutes: [],

  featureFlags: ['store.context.affluence.enabled'],

  // Modulo sin persistencia en el Bloque 0: no tiene tablas propias, asi que no
  // declara migrationsPath. Cuando necesite tablas, se anade la ruta Y el
  // directorio a la vez.
};
