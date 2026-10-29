#!/usr/bin/env node
/**
 * Verificador de las 5 reglas de frontera del monolito modular.
 * Sin dependencias: recorre el arbol, extrae los imports por regex y resuelve
 * las rutas relativas para saber a que paquete apunta cada import.
 *
 * Uso: node tools/check-boundaries.mjs
 * Salida: 0 si no hay violaciones; 1 si hay alguna.
 */
import { readdirSync, readFileSync, statSync, existsSync } from 'node:fs';
import { dirname, join, relative, resolve, sep } from 'node:path';

const ROOT = process.cwd();
const SCAN_DIRS = ['packages', 'apps'];
const SKIP_DIRS = new Set(['node_modules', 'dist', 'build', 'migrations', '.tools', '.npmcache']);

const NODE_BUILTIN_RE = /^node:/;
const FRAMEWORKS = [
  '@nestjs',
  'nestjs',
  'express',
  'fastify',
  'react',
  'react-dom',
  'vite',
  'pg',
  'prisma',
  'ioredis',
  'bullmq',
];

function walk(dir, out = []) {
  if (!existsSync(dir)) return out;
  for (const entry of readdirSync(dir)) {
    if (SKIP_DIRS.has(entry)) continue;
    const full = join(dir, entry);
    const stats = statSync(full);
    if (stats.isDirectory()) walk(full, out);
    else if (entry.endsWith('.ts') || entry.endsWith('.tsx')) out.push(full);
  }
  return out;
}

/** Extrae los especificadores de import/export con su numero de linea. */
function extractImports(source) {
  const found = [];
  const patterns = [/from\s+['"]([^'"]+)['"]/g, /^\s*import\s+['"]([^'"]+)['"]/gm];
  const seen = new Set();

  for (const pattern of patterns) {
    for (const match of source.matchAll(pattern)) {
      const specifier = match[1];
      const index = match.index ?? 0;
      const line = source.slice(0, index).split('\n').length;
      const key = `${line}:${specifier}`;
      if (seen.has(key)) continue;
      seen.add(key);
      found.push({ specifier, line });
    }
  }
  return found.sort((a, b) => a.line - b.line);
}

/** Resuelve un import relativo a una ruta absoluta existente, o null. */
function resolveRelative(file, specifier) {
  if (!specifier.startsWith('.')) return null;
  const base = resolve(dirname(file), specifier);
  const candidates = [base, `${base}.ts`, `${base}.tsx`, `${base}.js`, join(base, 'index.ts')];
  for (const candidate of candidates) {
    if (existsSync(candidate) && statSync(candidate).isFile()) return candidate;
  }
  return null;
}

/** Identifica el paquete al que pertenece una ruta absoluta. */
function packageOf(absPath) {
  const rel = relative(ROOT, absPath).split(sep).join('/');
  const parts = rel.split('/');
  if (parts.length >= 2 && (parts[0] === 'packages' || parts[0] === 'apps')) {
    return { kind: parts[0], name: parts[1], path: `${parts[0]}/${parts[1]}` };
  }
  return { kind: 'raiz', name: parts[0] ?? '', path: rel };
}

const files = SCAN_DIRS.flatMap((dir) => walk(join(ROOT, dir))).sort();
const violations = [];

/**
 * R6 · FORMA DEL HOST.
 * apps/<host>/src solo puede contener la composicion, la fontaneria HTTP y los
 * adaptadores de infraestructura DECLARADOS UNO A UNO aqui.
 *
 * Esta es la regla que impide mecanicamente que el host se convierta en el nuevo
 * monolito: si alguien crea apps/api/src/services/ con logica de negocio, el
 * build falla. Anadir un adaptador exige editar esta lista a proposito.
 */
const HOST_ALLOWED_FILES = new Set(['main.ts', 'composition-root.ts']);

const HOST_ALLOWED_DIRS = new Map([
  ['http', 'enrutado y guard: fontaneria HTTP'],
  ['controllers', 'adaptadores de entrada: traducen HTTP a casos de uso'],
  ['adapters', 'adaptadores de infraestructura de demo, declarados uno a uno'],
]);

const HOST_ALLOWED_ADAPTERS = new Map([
  ['seed-rules.adapter.ts', 'lee db/seed/*.sql y devuelve datos: fontaneria pura, sin reglas de decision'],
]);

function checkHostLayout() {
  const appsDir = join(ROOT, 'apps');
  if (!existsSync(appsDir)) return;

  for (const host of readdirSync(appsDir)) {
    const src = join(appsDir, host, 'src');
    if (!existsSync(src) || !statSync(src).isDirectory()) continue;

    for (const entry of readdirSync(src)) {
      const full = join(src, entry);
      const rel = relative(ROOT, full).split(sep).join('/');
      const isDir = statSync(full).isDirectory();

      if (!isDir) {
        if (entry.endsWith('.ts') && !HOST_ALLOWED_FILES.has(entry)) {
          report(full, 1, 'R6', `fichero no permitido en el host: '${rel}'`);
        }
        continue;
      }

      if (!HOST_ALLOWED_DIRS.has(entry)) {
        report(
          full,
          1,
          'R6',
          `directorio no permitido en el host: '${rel}'. Solo se admiten ${[...HOST_ALLOWED_DIRS.keys()].join(', ')} y los ficheros ${[...HOST_ALLOWED_FILES].join(', ')}. La logica de negocio va en packages/module-*`,
        );
        continue;
      }

      if (entry === 'adapters') {
        for (const adapter of readdirSync(full)) {
          if (!HOST_ALLOWED_ADAPTERS.has(adapter)) {
            report(
              join(full, adapter),
              1,
              'R6',
              `adaptador no declarado: '${relative(ROOT, join(full, adapter)).split(sep).join('/')}'. Declaralo en HOST_ALLOWED_ADAPTERS justificando por que es fontaneria pura`,
            );
          }
        }
      }
    }
  }
}

checkHostLayout();

function report(file, line, rule, message) {
  violations.push({
    file: relative(ROOT, file).split(sep).join('/'),
    line,
    rule,
    message,
  });
}

for (const file of files) {
  const source = readFileSync(file, 'utf8');
  const self = packageOf(file);
  const relPath = relative(ROOT, file).split(sep).join('/');
  const inDomain = relPath.includes('/domain/') || relPath.includes('/domain.');
  const isCore = self.path === 'packages/core';
  const isModule = self.kind === 'packages' && self.name.startsWith('module-');

  for (const { specifier, line } of extractImports(source)) {
    if (NODE_BUILTIN_RE.test(specifier)) {
      if (inDomain) {
        report(file, line, 'R3', `domain/ no puede depender de modulos nativos ('${specifier}')`);
      }
      continue;
    }

    const absolute = resolveRelative(file, specifier);

    // Ruta relativa que no existe: error de import (rompe en runtime).
    if (specifier.startsWith('.') && absolute === null) {
      report(file, line, 'R0', `el import '${specifier}' no resuelve a ningun fichero`);
      continue;
    }

    // Paquete externo (sin node_modules en el Bloque 0: no deberia haber ninguno).
    if (absolute === null) {
      if (inDomain && FRAMEWORKS.some((fw) => specifier.startsWith(fw))) {
        report(file, line, 'R3', `domain/ no puede depender del framework '${specifier}'`);
      }
      if (!inDomain && FRAMEWORKS.some((fw) => specifier.startsWith(fw))) {
        report(file, line, 'R0', `dependencia externa de runtime no permitida: '${specifier}'`);
      }
      continue;
    }

    const target = packageOf(absolute);

    // R4: el codigo reutilizable (packages/) nunca depende del host (apps/).
    // Los ficheros que YA viven en apps/ pueden importarse entre si.
    if (self.kind === 'packages' && target.kind === 'apps') {
      report(file, line, 'R4', `'${relPath}' importa del host '${target.path}'`);
      continue;
    }

    // R5: el nucleo no depende de ningun modulo de negocio.
    if (isCore && target.kind === 'packages' && target.name.startsWith('module-')) {
      report(file, line, 'R5', `packages/core importa del modulo '${target.path}'`);
      continue;
    }

    // R1: un modulo no importa de otro modulo.
    if (isModule && target.kind === 'packages' && target.name.startsWith('module-') && target.name !== self.name) {
      report(file, line, 'R1', `'${self.path}' importa de '${target.path}'`);
      continue;
    }

    // R2: un modulo solo puede depender de contracts, core, ui y de si mismo.
    if (isModule) {
      const allowed =
        target.name === self.name ||
        target.path === 'packages/contracts' ||
        target.path === 'packages/core' ||
        target.path === 'packages/ui';
      if (!allowed) {
        report(file, line, 'R2', `'${self.path}' importa de '${target.path}', que no esta permitido`);
      }
    }

    // R3: domain/ es TypeScript puro.
    if (inDomain) {
      const forbidden =
        target.path === 'packages/core' && relPath.includes('/infrastructure/')
          ? false
          : /(^|\/)(infrastructure|api)(\/|$)/.test(relative(ROOT, absolute).split(sep).join('/'));
      if (forbidden) {
        report(file, line, 'R3', `domain/ no puede importar de '${target.path}'`);
      }
    }
  }

  // R3 por ruta: un fichero bajo domain/ no puede vivir bajo infrastructure/ ni api/.
  if (inDomain && /(^|\/)(infrastructure|api)(\/|$)/.test(relPath)) {
    report(file, 1, 'R3', 'un fichero de domain/ no puede estar bajo infrastructure/ ni api/');
  }
}

const RULE_TITLES = {
  R0: 'import no resoluble / dependencia externa',
  R1: 'un modulo no importa de otro modulo',
  R2: 'un modulo solo importa de contracts, core, ui o si mismo',
  R3: 'domain/ no importa infrastructure/, api/ ni frameworks',
  R4: 'packages/ no importa del host apps/',
  R5: 'packages/core no importa modulos de negocio',
  R6: 'apps/<host>/src solo contiene composicion, HTTP y adaptadores declarados',
};

if (violations.length === 0) {
  console.log(`OK  ${files.length} ficheros analizados en ${SCAN_DIRS.join(', ')}`);
  console.log('OK  Reglas de frontera R1-R6 y resolucion de imports: 0 violaciones');
  process.exit(0);
}

console.error(`FALLO  ${violations.length} violacion(es) de frontera en ${files.length} ficheros:\n`);
for (const violation of violations) {
  console.error(`  [${violation.rule}] ${violation.file}:${violation.line}`);
  console.error(`        ${RULE_TITLES[violation.rule] ?? violation.rule}`);
  console.error(`        ${violation.message}\n`);
}
process.exit(1);
