# Shell web (React PWA) — pendiente del Bloque 0

La shell **no se ha construido** en el Bloque 0 a propósito: sin persistencia real, validar
pantallas contra datos en memoria es validar contra humo. Este documento fija el diseño para
que se monte encima del núcleo sin tocarlo.

## Principio rector

Cada rol ve **solo lo que necesita para operar**. Una sola base de componentes, layouts por
rol: nunca tres aplicaciones distintas, porque eso triplica el mantenimiento.

| Rol | Dispositivo | Interfaz | Regla de oro |
|---|---|---|---|
| Gerencia | Escritorio + móvil | Densa en datos | Configurar sin miedo: **simular antes de activar** |
| Coordinadoras | Tablet | Kanban + alertas | **Sobreescribir siempre en ≤3 toques** |
| Operadoras | Tablet / móvil | Tarjetas grandes | **Nunca más de 2 toques para completar una tarea** |

## Rutas: se descubren, no se cablean

La shell lee `registry.uiRoutes(role)` y construye la navegación. Los manifiestos ya declaran
estas entradas reales, y añadir un módulo con `uiRoutes` hace aparecer su pantalla **sin
tocar la shell**:

| Ruta | Roles | Permiso |
|---|---|---|
| `/mis-tareas` | OPERADORA, COORDINADORA | — |
| `/tareas/tablero` | GERENCIA, COORDINADORA | `tasks.read` |
| `/reglas` | GERENCIA | `rules.manage` |
| `/stock` | GERENCIA, COORDINADORA | — |
| `/stock/alertas` | GERENCIA, COORDINADORA | `inventory.read` |
| `/caja` | OPERADORA, COORDINADORA, GERENCIA | `pos.sell` |
| `/caja/sesiones` | GERENCIA, COORDINADORA | `pos.sessions.read` |
| `/notificaciones` | OPERADORA, COORDINADORA, GERENCIA | `notify.read` |
| `/salud` | GERENCIA | `healthcheck.read` |

`/salud` la aporta `module-healthcheck` y es la prueba de extensibilidad: un módulo nuevo
añade una ruta sin que nadie edite la shell. `module-store-context` no aporta rutas porque no
tiene pantalla propia: solo alimenta variables al motor de reglas.

## Estructura prevista

```
apps/web/
├── index.html
├── vite.config.ts
└── src/
    ├── main.tsx              arranque
    ├── shell/
    │   ├── AppShell.tsx      layout + navegacion desde los manifiestos
    │   ├── LoginPin.tsx      POST /auth/login con PIN (teclado numerico grande)
    │   └── FeatureFlags.tsx  oculta funcionalidad sin desplegar
    ├── layouts/
    │   ├── GerenciaLayout.tsx
    │   ├── CoordinadoraLayout.tsx
    │   └── OperadoraLayout.tsx
    └── features/             una carpeta por modulo, cargada de forma diferida
```

## Decisiones ya cerradas

- **PWA instalable** (tablet y TPV), no app nativa en el Bloque 1.
- **Offline-first en caja desde el principio**, no como mejora posterior: el esquema ya
  soporta `sales.offline_sync_id` (UUID generado en cliente) para reconciliar sin duplicar
  tickets. Se implementa con cola local en IndexedDB.
- **Login con PIN**, no email y contraseña: las operadoras tienen las manos ocupadas.
- **El tablero de una operadora muestra sus tareas y su progreso, nunca comparativas entre
  compañeras.** Las comparativas viven solo en la vista de Gerencia. Es la mitigación del
  riesgo de adopción número uno: si la app se percibe como un jefe digital que vigila, el
  proyecto fracasa.

## Cómo se valida

`vite build` está verificado en este entorno (14 módulos, 400 ms). La shell se dará por hecha
cuando compile y sus rutas se generen leyendo los manifiestos, con un test que compruebe que
añadir un módulo añade su ruta sin editar `apps/web`.
