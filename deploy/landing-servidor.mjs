#!/usr/bin/env node
/*
  Página "en construcción" para la raíz de supermalato.es.

  Solo sirve dos ficheros: la portada y el logo. Todo lo demás es un 404.
  El asador NO pasa por aquí: sus rutas (/asador y /erretegia) van directas
  al 8082 desde el túnel.
*/
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const PUERTO = Number(process.env.PORT || 3003);
const HOST = process.env.HOST || '127.0.0.1';
const AQUI = path.dirname(fileURLToPath(import.meta.url));
const PUBLICO = process.env.LANDING_DIR || path.join(AQUI, 'landing');

const TIPOS = {
  '.html': 'text/html; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon'
};

const PERMITIDOS = new Set(['index.html', 'logo-o-verde.png']);

function cabecerasSeguridad(res) {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('Referrer-Policy', 'no-referrer');
}

const servidor = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://localhost');

  if (url.pathname === '/salud') {
    cabecerasSeguridad(res);
    res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8',
                         'Cache-Control': 'no-store' });
    return res.end(JSON.stringify({ ok: true, servicio: 'malato-landing' }));
  }

  const rel = url.pathname === '/' ? 'index.html' : url.pathname.replace(/^\/+/, '');
  if (!PERMITIDOS.has(rel)) {
    cabecerasSeguridad(res);
    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8',
                         'Cache-Control': 'no-store' });
    return res.end('no encontrado');
  }

  const fichero = path.join(PUBLICO, rel);
  if (!fichero.startsWith(PUBLICO + path.sep)) {
    cabecerasSeguridad(res);
    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
    return res.end('no encontrado');
  }

  let contenido;
  try {
    contenido = fs.readFileSync(fichero);
  } catch (e) {
    cabecerasSeguridad(res);
    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
    return res.end('no encontrado');
  }

  cabecerasSeguridad(res);
  res.writeHead(200, {
    'Content-Type': TIPOS[path.extname(fichero)] || 'application/octet-stream',
    'Content-Length': contenido.length,
    'Cache-Control': rel === 'index.html' ? 'no-store' : 'public, max-age=86400'
  });
  if (req.method === 'HEAD') return res.end();
  res.end(contenido);
});

servidor.listen(PUERTO, HOST, () => {
  console.log(`  página en construcción en marcha`);
  console.log(`    escucha en:   http://${HOST}:${PUERTO}`);
  console.log(`    ficheros:     ${PUBLICO}`);
});

for (const senal of ['SIGTERM', 'SIGINT']) {
  process.on(senal, () => {
    servidor.close(() => process.exit(0));
    setTimeout(() => process.exit(0), 3000).unref();
  });
}
