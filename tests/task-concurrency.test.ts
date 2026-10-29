/**
 * Concurrencia en el Kanban: dos coordinadoras moviendo la MISMA tarjeta.
 *
 * Con tres coordinadoras y traspaso de turno, esto no es un caso raro: es el momento
 * de máxima concurrencia de la tienda. Sin bloqueo optimista la segunda reasignación
 * pisa a la primera y nadie se entera — una coordinadora cree haber dejado la tarea
 * en Ana cuando en realidad se fue a Paula.
 *
 * El blindaje real está en la base de datos (columna version + trigger
 * tasks.bump_version); aquí se comprueba que la capa de aplicación lo expone y lo
 * convierte en un aviso al usuario en lugar de en una pérdida silenciosa.
 */
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { ROLES } from '../packages/contracts/src/rbac.ts';
import type { SessionUser } from '../packages/contracts/src/rbac.ts';
import { TaskVersionConflictError } from '../packages/module-tasks/src/tasks.service.ts';
import { DEMO_STORE_ID } from '../apps/api/src/composition-root.ts';
import type { SystemRuntime } from '../apps/api/src/composition-root.ts';
import { buildSystem } from './helpers/harness.ts';
import type { HttpRequest, RouteHandler } from '../apps/api/src/http/router.ts';

const coordinadoraA: SessionUser = {
  id: 'u-coord-1',
  storeId: DEMO_STORE_ID,
  role: ROLES.COORDINADORA,
  displayName: 'Lucia Sanchis',
};
const coordinadoraB: SessionUser = {
  id: 'u-coord-2',
  storeId: DEMO_STORE_ID,
  role: ROLES.COORDINADORA,
  displayName: 'Nuria Blasco',
};

function handlerOf(system: SystemRuntime, pattern: string, method = 'POST'): RouteHandler {
  const route = system.router.routes().find((c) => c.pattern === pattern && c.method === method);
  assert.ok(route, `el host debe exponer ${method} ${pattern}`);
  return route.handler;
}

function peticion(taskId: string, user: SessionUser, body: unknown): HttpRequest {
  return {
    method: 'POST',
    path: `/tasks/${taskId}/reassign`,
    params: { id: taskId },
    query: new URLSearchParams(),
    body,
    token: 'token-de-prueba',
    user,
  };
}

function cuerpo(response: { body: unknown }): Record<string, unknown> {
  return response.body as Record<string, unknown>;
}

test('dos reasignaciones desde la MISMA version: gana la primera, la segunda recibe 409', async () => {
  const system = buildSystem();
  const tarea = system.tasks.createTask({ title: 'Reponer leche', priority: 'ALTA' });
  const reasignar = handlerOf(system, '/tasks/:id/reassign');

  // Las dos coordinadoras cargan el tablero y ven la MISMA version.
  const versionLeida = tarea.version;

  const primera = await reasignar(peticion(tarea.id, coordinadoraA, {
    toUserId: 'u-sala-1',
    version: versionLeida,
    reason: 'Reparto de Lucía',
  }));
  assert.equal(primera.status, 200, 'la primera reasignación debe aceptarse');
  const versionNueva = cuerpo(primera)['task'] as Record<string, unknown>;
  assert.equal(versionNueva['version'], versionLeida + 1, 'la version avanza de uno en uno');

  const segunda = await reasignar(peticion(tarea.id, coordinadoraB, {
    toUserId: 'u-sala-2',
    version: versionLeida, // Nuria sigue con la copia vieja
    reason: 'Reparto de Nuria',
  }));
  assert.equal(segunda.status, 409, 'la segunda debe rechazarse, no pisar');
  assert.equal(cuerpo(segunda)['error'], 'VERSION_OBSOLETA');
  assert.equal(cuerpo(segunda)['expectedVersion'], versionLeida);
  assert.equal(cuerpo(segunda)['actualVersion'], versionLeida + 1);

  // El cambio de Lucía SIGUE EN PIE: es lo importante.
  assert.equal(system.tasks.task(tarea.id)?.assigneeId, 'u-sala-1');
});

test('recargar la version permite reintentar: el rechazo no deja la tarea bloqueada', async () => {
  const system = buildSystem();
  const tarea = system.tasks.createTask({ title: 'Reponer yogur' });
  const reasignar = handlerOf(system, '/tasks/:id/reassign');

  const primera = await reasignar(peticion(tarea.id, coordinadoraA, {
    toUserId: 'u-sala-1',
    version: tarea.version,
    reason: 'Primera',
  }));
  assert.equal(primera.status, 200);
  const alDia = (cuerpo(primera)['task'] as Record<string, unknown>)['version'] as number;

  // Nuria recarga el tablero, ve la version nueva y su reasignación pasa.
  const reintento = await reasignar(peticion(tarea.id, coordinadoraB, {
    toUserId: 'u-sala-2',
    version: alDia,
    reason: 'Segunda, ya con la version al día',
  }));
  assert.equal(reintento.status, 200);
  assert.equal(system.tasks.task(tarea.id)?.assigneeId, 'u-sala-2');
});

test('la version es OBLIGATORIA en la via humana: sin ella no hay proteccion posible', async () => {
  const system = buildSystem();
  const tarea = system.tasks.createTask({ title: 'Limpiar lineal' });
  const reasignar = handlerOf(system, '/tasks/:id/reassign');

  const sinVersion = await reasignar(peticion(tarea.id, coordinadoraA, { toUserId: 'u-sala-1' }));
  assert.equal(sinVersion.status, 400);
  assert.equal(cuerpo(sinVersion)['error'], 'FALTA_VERSION');

  // Y no ha cambiado nada: la petición inválida no reasigna.
  assert.equal(system.tasks.task(tarea.id)?.assigneeId, null);
});

test('el servicio tambien rechaza una version obsoleta y no toca la tarea', () => {
  const system = buildSystem();
  const tarea = system.tasks.createTask({ title: 'Recuento de lácteos', assigneeId: 'u-sala-1' });

  system.tasks.reassign(tarea.id, 'u-sala-2', 'u-coord-1', 'Primera', tarea.version);
  assert.equal(system.tasks.task(tarea.id)?.assigneeId, 'u-sala-2');

  assert.throws(
    () => system.tasks.reassign(tarea.id, 'u-sala-1', 'u-coord-2', 'Obsoleta', tarea.version),
    (error: unknown) => {
      assert.ok(error instanceof TaskVersionConflictError);
      assert.equal(error.expectedVersion, tarea.version);
      return true;
    },
  );
  assert.equal(system.tasks.task(tarea.id)?.assigneeId, 'u-sala-2', 'el cambio previo no se pisa');
});

test('el tablero expone la version: sin ella el Kanban no puede reasignar', async () => {
  const system = buildSystem();
  system.tasks.createTask({ title: 'Tarea de ejemplo' });

  const tablero = handlerOf(system, '/tasks/board', 'GET');
  const respuesta = await tablero({
    method: 'GET',
    path: '/tasks/board',
    params: {},
    query: new URLSearchParams(),
    body: null,
    token: 'token-de-prueba',
    user: coordinadoraA,
  });

  assert.equal(respuesta.status, 200);
  const tareas = cuerpo(respuesta)['tasks'] as Record<string, unknown>[];
  assert.ok(tareas.length > 0);
  assert.equal(typeof tareas[0]?.['version'], 'number', 'cada tarjeta lleva su version');
});
