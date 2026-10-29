import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { test } from 'node:test';
import { ALL_PERMISSIONS, ROLE_LEVELS, ROLE_POLICY, ROLES } from '../packages/contracts/src/rbac.ts';
import type { RoleCode } from '../packages/contracts/src/rbac.ts';
import type { ModuleManifest } from '../packages/contracts/src/manifest.ts';
import { ActionRegistry, FactRegistry, InMemoryEventBus, registerModules } from '../packages/core/src/index.ts';
import { createClock } from '../packages/core/src/index.ts';
import { silentLogger } from './helpers/harness.ts';

import { tasksManifest } from '../packages/module-tasks/src/manifest.ts';
import { inventoryManifest } from '../packages/module-inventory/src/manifest.ts';
import { posManifest } from '../packages/module-pos/src/manifest.ts';
import { notifyManifest } from '../packages/module-notify/src/manifest.ts';
import { storeContextManifest } from '../packages/module-store-context/src/manifest.ts';
import { healthcheckManifest } from '../packages/module-healthcheck/src/manifest.ts';

const SEED_PATH = join(process.cwd(), 'db', 'seed', '001_demo_store.sql');
const SEED_SQL = readFileSync(SEED_PATH, 'utf8');

const MANIFESTS: readonly ModuleManifest[] = [
  tasksManifest,
  inventoryManifest,
  posManifest,
  notifyManifest,
  storeContextManifest,
  healthcheckManifest,
];

/**
 * Permisos que los manifiestos declaran y que AUN NO existen en core.permissions.
 * La lista es explicita y cerrada a proposito: si aparece cualquier otra
 * divergencia, el test falla. Estos dos exigen una migracion pendiente.
 */
const PERMISOS_PENDIENTES_DE_MIGRACION = new Map<string, string>([
  ['healthcheck.read', 'modulo de demostracion de extensibilidad (Bloque 0)'],
  ['notify.send', 'accion NOTIFY del modulo de notificaciones (Bloque 5)'],
]);

function seedBlock(startMarker: string): string {
  const start = SEED_SQL.indexOf(startMarker);
  assert.ok(start >= 0, `no se encontro '${startMarker}' en el seed`);
  const end = SEED_SQL.indexOf('ON CONFLICT DO NOTHING;', start);
  return SEED_SQL.slice(start, end < 0 ? undefined : end);
}

/** Permisos que siembra la base de datos. */
function seedPermissions(): readonly string[] {
  const block = seedBlock('INSERT INTO core.permissions');
  return [...block.matchAll(/\('([a-z][a-z0-9_.]*)',\s*'([a-z][a-z0-9-]*)',/g)].map(
    (match) => match[1] as string,
  );
}

function seedRoles(): readonly string[] {
  const block = seedBlock('INSERT INTO core.roles');
  return [...block.matchAll(/\('([A-Z_]+)',/g)].map((match) => match[1] as string);
}

test('el seed siembra exactamente los mismos permisos que declara contracts', () => {
  const seeded = seedPermissions();
  assert.equal(seeded.length, 40, 'el seed debe sembrar 40 permisos');

  const fromSeed = new Set(seeded);
  const fromContracts = new Set<string>(ALL_PERMISSIONS);

  const soloEnContracts = [...fromContracts].filter((code) => !fromSeed.has(code));
  const soloEnSeed = [...fromSeed].filter((code) => !fromContracts.has(code));

  assert.deepEqual(soloEnContracts, [], 'permisos en contracts que no estan en el seed');
  assert.deepEqual(soloEnSeed, [], 'permisos en el seed que no estan en contracts');

  assert.equal(new Set(seeded).size, seeded.length, 'no debe haber permisos duplicados en el seed');
});

test('el seed siembra los tres roles y contracts define su politica', () => {
  const roles = seedRoles();
  assert.deepEqual(roles, [ROLES.GERENCIA, ROLES.COORDINADORA, ROLES.OPERADORA]);

  for (const role of Object.keys(ROLE_POLICY) as RoleCode[]) {
    assert.ok(roles.includes(role), `la politica define '${role}', que no esta en el seed`);
  }
});

/** Permisos concedidos a un rol en el seed, leidos SOLO del bloque ARRAY[...]. */
function seedRolePermissions(role: string): readonly string[] {
  const end = SEED_SQL.indexOf(`WHERE r.code = '${role}'`);
  assert.ok(end >= 0, `no se encontro el bloque de permisos de '${role}' en el seed`);
  const start = SEED_SQL.lastIndexOf('INSERT INTO core.role_permissions', end);
  assert.ok(start >= 0, `no se encontro el INSERT de permisos de '${role}'`);

  const block = SEED_SQL.slice(start, end);
  const arrayStart = block.indexOf('ARRAY[');
  if (arrayStart < 0) return []; // Gerencia no enumera: concede todo con CROSS JOIN.
  const arrayEnd = block.indexOf(']', arrayStart);
  return [...block.slice(arrayStart, arrayEnd).matchAll(/'([a-z][a-z0-9_.]*)'/g)].map(
    (match) => match[1] as string,
  );
}

test('los permisos por rol del seed coinciden EXACTAMENTE con ROLE_POLICY', () => {
  // Gerencia no enumera permisos: los recibe todos por CROSS JOIN.
  const bloqueGerencia = SEED_SQL.slice(
    SEED_SQL.lastIndexOf('INSERT INTO core.role_permissions', SEED_SQL.indexOf("WHERE r.code = 'GERENCIA'")),
    SEED_SQL.indexOf("WHERE r.code = 'GERENCIA'"),
  );
  assert.match(bloqueGerencia, /CROSS JOIN/, 'Gerencia debe recibir todos los permisos');

  for (const role of [ROLES.COORDINADORA, ROLES.OPERADORA] as const) {
    const delSeed = [...new Set(seedRolePermissions(role))].sort();
    const deContracts = [...new Set(ROLE_POLICY[role])].sort();
    assert.deepEqual(
      delSeed,
      deContracts,
      `los permisos de '${role}' divergen entre db/seed/001_demo_store.sql y contracts ROLE_POLICY`,
    );
  }
});

test('los roles son JERARQUICOS: coordinacion puede todo lo que puede una operadora', () => {
  // No es una preferencia de estilo: con 2 operadoras y 91 h semanales de apertura,
  // quien coordina tambien repone y cobra. Si los conjuntos fueran disjuntos, el
  // motor apilaria el trabajo en dos personas mientras las otras tres miran.
  const deOperadora = new Set(ROLE_POLICY[ROLES.OPERADORA]);
  const faltanEnCoordinacion = [...deOperadora].filter(
    (permission) => !ROLE_POLICY[ROLES.COORDINADORA].includes(permission),
  );
  assert.deepEqual(
    faltanEnCoordinacion,
    [],
    'una coordinadora debe poder hacer todo lo que hace una operadora',
  );

  // Y el nivel declarado tiene que respetar ese orden.
  assert.ok(
    ROLE_LEVELS[ROLES.GERENCIA] > ROLE_LEVELS[ROLES.COORDINADORA],
    'Gerencia debe estar por encima de coordinacion',
  );
  assert.ok(
    ROLE_LEVELS[ROLES.COORDINADORA] > ROLE_LEVELS[ROLES.OPERADORA],
    'coordinacion debe estar por encima de sala',
  );
});

test('cada permiso de un manifiesto existe en la base de datos (o esta en la lista de pendientes)', () => {
  const seeded = new Set(seedPermissions());
  const declared = MANIFESTS.flatMap((manifest) =>
    manifest.permissions.map((permission) => ({ permission, moduleId: manifest.id })),
  );

  const sinMigrar = declared.filter((entry) => !seeded.has(entry.permission));
  const inesperados = sinMigrar.filter((entry) => !PERMISOS_PENDIENTES_DE_MIGRACION.has(entry.permission));

  assert.deepEqual(
    inesperados,
    [],
    'hay permisos de manifiesto que no existen en core.permissions y no estan declarados como pendientes',
  );

  // Y la lista de pendientes no puede quedarse obsoleta: si ya existe en la BD, sobra.
  for (const [permission, motivo] of PERMISOS_PENDIENTES_DE_MIGRACION) {
    assert.ok(motivo.length > 10, `el permiso pendiente '${permission}' debe justificar su motivo`);
    assert.equal(
      seeded.has(permission),
      false,
      `'${permission}' ya existe en el seed: quitalo de PERMISOS_PENDIENTES_DE_MIGRACION`,
    );
  }
});

test('el registro de todos los modulos es coherente: sin colisiones ni duplicados', () => {
  const clock = createClock();
  const result = registerModules({
    modules: MANIFESTS.map((manifest) => ({ manifest })),
    bus: new InMemoryEventBus({ clock }),
    facts: new FactRegistry(),
    actions: new ActionRegistry(),
    logger: silentLogger,
  });

  const { registry } = result;
  assert.equal(registry.count(), MANIFESTS.length);
  assert.equal(new Set(registry.ids()).size, MANIFESTS.length);

  // El propio registro ya lanza si hay colisiones; comprobamos ademas que cada
  // permiso tiene un unico dueno.
  for (const permission of registry.permissions()) {
    assert.ok(registry.ownerOfPermission(permission), `'${permission}' sin dueno`);
  }
  assert.equal(new Set(registry.permissions()).size, registry.permissions().length);
  assert.equal(new Set(registry.factKeys()).size, registry.factKeys().length);
  assert.equal(new Set(registry.actionTypes()).size, registry.actionTypes().length);
  assert.equal(new Set(registry.publishedEvents()).size, registry.publishedEvents().length);
});

test('migrationsPath y el directorio en disco coinciden en los dos sentidos', () => {
  const declaradoSinDirectorio: string[] = [];
  const directorioSinDeclarar: string[] = [];

  // Convencion del monorepo: el modulo 'X' vive en packages/module-X y sus
  // migraciones en packages/module-X/migrations. Las rutas del manifiesto van en
  // estilo POSIX ('/'), que es lo que se escribe en el repo, no lo que devuelve
  // path.join en Windows.
  for (const manifest of MANIFESTS) {
    const esperado = `packages/module-${manifest.id}/migrations`;
    const declarado = manifest.migrationsPath;

    if (declarado !== undefined && !existsSync(join(process.cwd(), declarado))) {
      declaradoSinDirectorio.push(`${manifest.id} declara '${declarado}', que no existe`);
    }

    if (existsSync(join(process.cwd(), esperado)) && declarado !== esperado) {
      directorioSinDeclarar.push(
        `${manifest.id} tiene '${esperado}' en disco pero declara '${declarado ?? '(nada)'}'`,
      );
    }
  }

  assert.deepEqual(declaradoSinDirectorio, [], 'un manifiesto no puede declarar migraciones inexistentes');
  assert.deepEqual(directorioSinDeclarar, [], 'un modulo con migraciones en disco debe declararlas');

  // Guarda contra el paso en vacio: si alguien borrase migrationsPath de todos
  // los manifiestos, las dos listas quedarian vacias y el test no comprobaria
  // nada. Los modulos con tablas propias son exactamente estos.
  assert.deepEqual(
    MANIFESTS.filter((manifest) => manifest.migrationsPath !== undefined)
      .map((manifest) => manifest.id)
      .sort(),
    ['inventory', 'notify', 'pos', 'tasks'],
  );
});

test('los eventos publicados y consumidos son nombres cualificados y en pasado', () => {
  for (const manifest of MANIFESTS) {
    for (const eventType of [...manifest.publishes, ...manifest.consumes]) {
      assert.match(
        eventType,
        /^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$/,
        `'${eventType}' no tiene forma modulo.entidad_accion`,
      );
    }
  }

  // Todo evento consumido por alguien debe publicarlo alguien: si no, hay un
  // modulo esperando algo que nunca llegara.
  const published = new Set<string>();
  for (const manifest of MANIFESTS) for (const eventType of manifest.publishes) published.add(eventType);

  const huerfanos = [...new Set(MANIFESTS.flatMap((manifest) => [...manifest.consumes]))]
    .filter((eventType) => !published.has(eventType))
    .sort();

  // inventory declara interes en eventos de venta y recepcion: los publicara pos
  // (sale.completed ya se publica) y el futuro modulo de pedidos (reception.completed).
  assert.deepEqual(huerfanos, ['reception.completed']);
});
