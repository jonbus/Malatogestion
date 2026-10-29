import assert from 'node:assert/strict';
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { test } from 'node:test';
import { ROLES } from '../packages/contracts/src/rbac.ts';
import type { ModuleManifest } from '../packages/contracts/src/manifest.ts';
import {
  ActionRegistry,
  FactRegistry,
  InMemoryEventBus,
  ModuleRegistrationError,
  registerModules,
} from '../packages/core/src/index.ts';
import { createClock } from '../packages/core/src/index.ts';
import { silentLogger } from './helpers/harness.ts';

import { tasksManifest } from '../packages/module-tasks/src/manifest.ts';
import { inventoryManifest } from '../packages/module-inventory/src/manifest.ts';
import { posManifest } from '../packages/module-pos/src/manifest.ts';
import { notifyManifest } from '../packages/module-notify/src/manifest.ts';
import { storeContextManifest } from '../packages/module-store-context/src/manifest.ts';
import { healthcheckManifest } from '../packages/module-healthcheck/src/manifest.ts';

const BASE_MODULES: readonly ModuleManifest[] = [
  tasksManifest,
  inventoryManifest,
  posManifest,
  notifyManifest,
  storeContextManifest,
];

/** Monta un registro nuevo desde cero con los manifiestos que se le pasen. */
function freshRegistry(manifests: readonly ModuleManifest[]) {
  const clock = createClock();
  return registerModules({
    modules: manifests.map((manifest) => ({ manifest })),
    bus: new InMemoryEventBus({ clock }),
    facts: new FactRegistry(),
    actions: new ActionRegistry(),
    logger: silentLogger,
  });
}

function coreSources(): readonly { path: string; source: string }[] {
  const out: { path: string; source: string }[] = [];

  const walk = (dir: string): void => {
    for (const entry of readdirSync(dir)) {
      const full = join(dir, entry);
      if (statSync(full).isDirectory()) walk(full);
      else if (entry.endsWith('.ts')) out.push({ path: full, source: readFileSync(full, 'utf8') });
    }
  };

  walk(join(process.cwd(), 'packages', 'core', 'src'));
  return out;
}

test('anadir module-healthcheck expone su permiso, su fact y su ruta SIN tocar core', () => {
  const before = freshRegistry(BASE_MODULES);
  const after = freshRegistry([...BASE_MODULES, healthcheckManifest]);

  // El nucleo no cambio: solo se le entrego un manifiesto mas.
  assert.equal(before.registry.hasPermission('healthcheck.read'), false);
  assert.equal(after.registry.hasPermission('healthcheck.read'), true);

  assert.equal(before.registry.factKeys().includes('healthcheck.uptime_seconds'), false);
  assert.equal(after.registry.factKeys().includes('healthcheck.uptime_seconds'), true);

  assert.equal(
    before.registry.uiRoutes(ROLES.GERENCIA).some((route) => route.path === '/salud'),
    false,
  );
  assert.equal(
    after.registry.uiRoutes(ROLES.GERENCIA).some((route) => route.path === '/salud'),
    true,
  );

  assert.equal(after.registry.count(), before.registry.count() + 1);
  assert.equal(after.registry.featureFlags().includes('healthcheck.expose.public'), true);

  // El permiso y el fact tienen dueno identificable: trazabilidad del plugin.
  assert.equal(after.registry.ownerOfPermission('healthcheck.read'), 'healthcheck');
  assert.equal(after.registry.ownerOfFact('healthcheck.uptime_seconds'), 'healthcheck');
});

test('el registro rechaza colisiones entre modulos: los manifiestos no pueden pisarse', () => {
  const intruso: ModuleManifest = {
    ...healthcheckManifest,
    id: 'intruso',
    permissions: ['healthcheck.read'],
  };

  assert.throws(
    () => freshRegistry([...BASE_MODULES, healthcheckManifest, intruso]),
    (error: unknown) => error instanceof ModuleRegistrationError,
    'dos modulos no pueden declarar el mismo permiso',
  );

  const intrusoFact: ModuleManifest = {
    ...healthcheckManifest,
    id: 'intruso-fact',
    permissions: [],
    facts: [{ key: 'tasks.open_by_user', description: 'choque de fact' }],
  };

  assert.throws(() => freshRegistry([...BASE_MODULES, intrusoFact]), ModuleRegistrationError);

  const intrusoRuta: ModuleManifest = {
    ...healthcheckManifest,
    id: 'intruso-ruta',
    permissions: [],
    facts: [],
    uiRoutes: [{ path: '/mis-tareas', label: 'Choque', roles: [ROLES.GERENCIA] }],
  };

  assert.throws(() => freshRegistry([...BASE_MODULES, intrusoRuta]), ModuleRegistrationError);

  const duplicado: ModuleManifest = { ...healthcheckManifest, permissions: [], facts: [], uiRoutes: [] };
  assert.throws(() => freshRegistry([healthcheckManifest, duplicado]), ModuleRegistrationError);
});

test('packages/core NO contiene ningun nombre de modulo de negocio ni "healthcheck"', () => {
  const sources = coreSources();
  assert.ok(sources.length >= 15, `deberia haber ficheros en packages/core, hay ${sources.length}`);

  const moduleIds = [
    'healthcheck',
    'tasks',
    'inventory',
    'inventory.lots',
    'pos',
    'notify',
    'store-context',
    'catalog',
    'orders',
    'analytics',
  ];

  for (const { path, source } of sources) {
    // Busqueda cruda del nombre del modulo de prueba.
    assert.equal(
      source.includes('healthcheck'),
      false,
      `${path} menciona 'healthcheck': el nucleo no debe conocer modulos de negocio`,
    );

    for (const id of moduleIds) {
      // Se buscan TOKENS citados, no subcadenas: en castellano 'pos' aparece en
      // 'composicion' o 'posible', y eso seria un falso positivo.
      for (const token of [`'${id}'`, `"${id}"`, `module-${id}`, `/module-${id}/`]) {
        assert.equal(
          source.includes(token),
          false,
          `${path} contiene el token '${token}': el nucleo conoce un modulo de negocio`,
        );
      }
    }
  }
});

/**
 * Extrae los especificadores de import/export de un fichero.
 * OJO: no basta con buscar 'module-' en el texto. El nucleo tiene ficheros que
 * se llaman 'module-registry.ts' y se importan entre si con rutas LOCALES
 * ('./registry/module-registry.ts'). Eso NO es acoplamiento a un modulo de
 * negocio: es un fichero del propio core. Solo es violacion un especificador
 * que realmente SALGA del paquete hacia un paquete de modulo.
 */
function moduleSpecifiers(source: string): readonly string[] {
  const specifiers: string[] = [];
  const pattern = /(?:from|import)\s*\(?\s*['"]([^'"]+)['"]/g;
  for (const match of source.matchAll(pattern)) {
    const specifier = match[1];
    if (specifier !== undefined) specifiers.push(specifier);
  }
  return specifiers;
}

/** Un especificador es violacion si sale del paquete hacia packages/module-*. */
function escapesToBusinessModule(specifier: string): boolean {
  // Ruta explicita al paquete de un modulo.
  if (specifier.includes('packages/module-')) return true;
  // Ruta relativa que escapa del paquete ('..') y ademas nombra un modulo.
  return specifier.startsWith('..') && specifier.includes('module-');
}

test('el nucleo se sostiene sin conocer los modulos: cero imports que salgan a packages/module-*', () => {
  const infractores: string[] = [];

  for (const { path, source } of coreSources()) {
    for (const specifier of moduleSpecifiers(source)) {
      if (escapesToBusinessModule(specifier)) infractores.push(`${path} -> ${specifier}`);
    }
  }

  assert.deepEqual(
    infractores,
    [],
    'packages/core no puede importar de un modulo de negocio: la lista de arriba son las violaciones',
  );
});
