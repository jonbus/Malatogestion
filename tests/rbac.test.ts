import assert from 'node:assert/strict';
import { test } from 'node:test';
import { PERMISSIONS, ROLES } from '../packages/contracts/src/rbac.ts';
import type { SessionUser } from '../packages/contracts/src/rbac.ts';
import { can, canAny, isSuperRole, permissionsOf } from '../packages/core/src/index.ts';
import { authorize } from '../apps/api/src/http/rbac-guard.ts';
import { DEMO_STORE_ID } from '../apps/api/src/composition-root.ts';
import { buildSystem } from './helpers/harness.ts';
import type { RouteDefinition } from '../apps/api/src/http/router.ts';

const gerencia: SessionUser = {
  id: 'u-gerencia',
  storeId: DEMO_STORE_ID,
  role: ROLES.GERENCIA,
  displayName: 'Marta Ferrer',
};
const coordinadora: SessionUser = {
  id: 'u-coord-1',
  storeId: DEMO_STORE_ID,
  role: ROLES.COORDINADORA,
  displayName: 'Lucia Sanchis',
};
const operadora: SessionUser = {
  id: 'u-sala-1',
  storeId: DEMO_STORE_ID,
  role: ROLES.OPERADORA,
  displayName: 'Ana Torres',
};

function reassignRoute(): RouteDefinition {
  const system = buildSystem();
  const route = system.router.routes().find((candidate) => candidate.pattern === '/tasks/:id/reassign');
  assert.ok(route, 'el host debe exponer POST /tasks/:id/reassign');
  return route as RouteDefinition;
}

test('OPERADORA no puede reasignar tareas', () => {
  assert.equal(can(operadora, PERMISSIONS.TASKS_REASSIGN), false);
  assert.equal(can(operadora, PERMISSIONS.TASKS_ASSIGN), false);
  assert.equal(can(operadora, PERMISSIONS.RULES_MANAGE), false);
  assert.equal(can(operadora, PERMISSIONS.ANALYTICS_MARGIN_READ), false);
});

test('COORDINADORA si puede reasignar tareas', () => {
  assert.equal(can(coordinadora, PERMISSIONS.TASKS_REASSIGN), true);
  assert.equal(can(coordinadora, PERMISSIONS.TASKS_ASSIGN), true);
  assert.equal(can(coordinadora, PERMISSIONS.RULES_SIMULATE), true);
  // Pero no puede tocar la regla ni aprobar pedidos ni ver margenes.
  assert.equal(can(coordinadora, PERMISSIONS.RULES_MANAGE), false);
  assert.equal(can(coordinadora, PERMISSIONS.ORDERS_APPROVE), false);
  assert.equal(can(coordinadora, PERMISSIONS.ANALYTICS_MARGIN_READ), false);
});

test('GERENCIA accede a todo, incluso a permisos que aun no existen', () => {
  assert.equal(isSuperRole(ROLES.GERENCIA), true);
  assert.equal(can(gerencia, PERMISSIONS.TASKS_REASSIGN), true);
  assert.equal(can(gerencia, PERMISSIONS.ORDERS_APPROVE), true);
  assert.equal(can(gerencia, PERMISSIONS.ANALYTICS_MARGIN_READ), true);
  assert.equal(can(gerencia, 'modulo.futuro.permiso'), true, 'el comodin cubre modulos futuros');
  assert.equal(can(null, PERMISSIONS.TASKS_READ), false, 'sin sesion no hay permiso');
});

test('los permisos puntuales amplian la politica del rol sin cambiarla', () => {
  const operadoraConExtra: SessionUser = {
    ...operadora,
    extraPermissions: [PERMISSIONS.TASKS_REASSIGN],
  };

  assert.equal(can(operadora, PERMISSIONS.TASKS_REASSIGN), false);
  assert.equal(can(operadoraConExtra, PERMISSIONS.TASKS_REASSIGN), true);
  assert.equal(canAny(operadoraConExtra, [PERMISSIONS.ORDERS_APPROVE, PERMISSIONS.TASKS_REASSIGN]), true);
  assert.equal(permissionsOf(ROLES.OPERADORA).includes(PERMISSIONS.POS_SELL), true);
});

test('el guard de ruta devuelve 401, 403 y 200 segun quien llame', () => {
  const system = buildSystem();
  const route = reassignRoute();

  const anonimo = authorize(route, null, system.registry);
  assert.equal(anonimo.allowed, false);
  assert.equal(anonimo.status, 401);

  const denegado = authorize(route, operadora, system.registry);
  assert.equal(denegado.allowed, false);
  assert.equal(denegado.status, 403);
  assert.equal((denegado.body as Record<string, unknown>)['error'], 'PERMISO_DENEGADO');
  assert.equal((denegado.body as Record<string, unknown>)['role'], ROLES.OPERADORA);

  assert.equal(authorize(route, coordinadora, system.registry).allowed, true);
  assert.equal(authorize(route, gerencia, system.registry).allowed, true);
});

test('el guard detecta una ruta que exige un permiso que ningun manifiesto declara', () => {
  const system = buildSystem();
  const route: RouteDefinition = { ...reassignRoute(), permission: 'permiso.inventado' };

  const outcome = authorize(route, gerencia, system.registry);
  assert.equal(outcome.allowed, false);
  assert.equal(outcome.status, 500, 'es un fallo de programacion, no un 403');
  assert.equal((outcome.body as Record<string, unknown>)['error'], 'PERMISO_NO_DECLARADO');
});

test('las rutas publicas no exigen sesion y las privadas si', () => {
  const system = buildSystem();

  const health = system.router.routes().find((route) => route.pattern === '/health');
  assert.ok(health);
  assert.equal(health?.permission, null);
  assert.equal(authorize(health as RouteDefinition, null, system.registry).allowed, true);

  const board = system.router.routes().find((route) => route.pattern === '/tasks/board');
  assert.ok(board);
  assert.equal(board?.permission, PERMISSIONS.TASKS_ASSIGN);
  assert.equal(authorize(board as RouteDefinition, operadora, system.registry).status, 403);
});
