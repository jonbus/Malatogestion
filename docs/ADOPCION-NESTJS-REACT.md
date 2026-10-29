# Adopción del host NestJS y de la shell React

El Bloque 0 entrega el **núcleo** ejecutándose con Node puro y sin dependencias. Este
documento explica cómo se monta encima el host NestJS y la shell React **sin tocar el
núcleo**.

## Por qué el núcleo es independiente del framework

NestJS necesita **decoradores con `emitDecoratorMetadata`**, y el TypeScript nativo de Node
solo admite sintaxis *erasable* (los decoradores con metadatos no lo son). Por tanto NestJS
requiere un paso de compilación, mientras que `packages/core` y los módulos se ejecutan
directamente.

Eso no es un inconveniente: es exactamente lo que exige la arquitectura hexagonal. El host
es un **adaptador**, no el sistema. Si mañana se cambia NestJS por Fastify, el núcleo y los
módulos no se tocan.

## Estado de la verificación en este entorno

Comprobado en esta máquina:

| Comprobación | Resultado |
|---|---|
| `npm install` de `@nestjs/core`, `@nestjs/common`, `platform-express`, `reflect-metadata` | OK (22 + 78 paquetes) |
| `tsc` compilando un host NestJS con decoradores y `emitDecoratorMetadata` | exit 0 |
| Arranque real: inyección de dependencias + `GET /health` | `200 {"status":"ok"}` |
| `vite build` con React y `@vitejs/plugin-react` | 14 módulos, built en 400 ms |

Lo que **no** está hecho todavía: montar el host real en `apps/api` y la shell en `apps/web`.

## Cómo se enchufa NestJS

`apps/api` pasa de host `node:http` a host NestJS. El núcleo no cambia.

1. **Dependencias** (solo en `apps/api`): `@nestjs/core`, `@nestjs/common`,
   `@nestjs/platform-express`, `reflect-metadata`.

2. **Un módulo NestJS por manifiesto.** El registro del núcleo ya sabe qué hay; NestJS solo
   necesita construir los proveedores:

   ```
   packages/core/src/registry/registrar.ts  →  ModuleRegistry
                                               ├─ permissions()
                                               ├─ factKeys() / ownerOfFact()
                                               ├─ actionTypes()
                                               ├─ uiRoutes(role)
                                               └─ migrationsPaths()
   ```

3. **El composition root sigue siendo el único sitio que enumera módulos.** Hoy es
   `apps/api/src/composition-root.ts` con `createSystem()`. En NestJS se convierte en un
   `AppModule` que importa un módulo por cada entrada. La lista de módulos **no se dispersa**
   por decoradores: se mantiene en un array, porque es lo que hace verificable que añadir un
   módulo no toca el núcleo.

4. **Los controladores se reutilizan tal cual.** `apps/api/src/controllers/*` ya son clases
   con métodos que reciben una petición y devuelven una respuesta; solo hay que anotarlas con
   `@Controller` y `@Get`/`@Post`, y sustituir el guard propio por un `CanActivate` que llame
   a la misma función `authorize()` de `http/rbac-guard.ts`.

5. **La regla R6 se mantiene.** `apps/api/src` sigue sin poder tener `domain/`, `services/`
   ni `actions/`. Añadir un proveedor NestJS no autoriza a meter negocio en el host.

## Cómo se enchufa la shell React

La shell **no cablea rutas a mano**: las descubre en los manifiestos.

- `registry.uiRoutes(role)` devuelve las entradas de navegación de ese rol, con su `path`,
  su `label` y el permiso exigido. Añadir un módulo con `uiRoutes` hace aparecer su pantalla
  sin tocar la shell.
- `registry.featureFlags()` permite ocultar funcionalidad sin desplegar.
- El login por PIN llama a `POST /auth/login` y guarda el token de sesión; el rol determina
  el layout.

Ver [`apps/web/ROADMAP-SHELL.md`](../apps/web/ROADMAP-SHELL.md).

## Orden de trabajo recomendado

1. Persistencia real: implementar los puertos (`OutboxRepository`, repositorios) contra
   PostgreSQL. **Antes** que la UI: sin datos reales, la UI se valida contra humo.
2. Host NestJS reutilizando controladores y guard.
3. Shell React PWA consumiendo `uiRoutes`.
4. Modo offline de caja (cola local + `offline_sync_id`, ya previsto en el esquema SQL).

## Advertencia

Al montar NestJS, **`npm run typecheck` deja de ser opcional**: los decoradores y los
metadatos se generan en compilación, y el type stripping de Node ignora los tipos. Un error
de tipos que hoy pasa desapercibido en un test puede impedir que el host arranque.
