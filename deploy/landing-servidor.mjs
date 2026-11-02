#!/usr/bin/env node
/*
  Página "en construcción" para la raíz de supermalato.es.

  Sirve la portada, el logo y la sambada de bienvenida. Todo lo demás es un 404.
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
  '.ico': 'image/x-icon',
  '.mp3': 'audio/mpeg'
};

const PERMITIDOS = new Set(['index.html', 'logo-o-verde.png', 'SambadaMalato.mp3']);

function cabecerasSeguridad(res) {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('Referrer-Policy', 'no-referrer');
}

/* Envía un fichero, con soporte de Range para que el audio pueda buscar
   dentro del MP3 sin descargarlo entero otra vez. */
function enviarFichero(req, res, fichero, rel) {
  let st;
  try { st = fs.statSync(fichero); }
  catch (e) {
    cabecerasSeguridad(res);
    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
    return res.end('no encontrado');
  }

  const tipo = TIPOS[path.extname(fichero)] || 'application/octet-stream';
  const cache = rel === 'index.html' ? 'no-store' : 'public, max-age=86400';
  const rango = req.headers.range;
  cabecerasSeguridad(res);

  if (rango) {
    const m = /^bytes=(\d*)-(\d*)$/.exec(String(rango).trim());
    let inicio = 0;
    let fin = st.size - 1;
    if (m) {
      if (m[1] === '' && m[2] !== '') {
        inicio = Math.max(0, st.size - Number(m[2]));
      } else {
        inicio = m[1] ? Number(m[1]) : 0;
        fin = m[2] ? Number(m[2]) : st.size - 1;
      }
      if (Number.isFinite(inicio) && Number.isFinite(fin) &&
          inicio >= 0 && inicio <= fin && inicio < st.size) {
        fin = Math.min(fin, st.size - 1);
        res.writeHead(206, {
          'Content-Type': tipo,
          'Content-Length': fin - inicio + 1,
          'Content-Range': `bytes ${inicio}-${fin}/${st.size}`,
          'Accept-Ranges': 'bytes',
          'Cache-Control': cache
        });
        if (req.method === 'HEAD') return res.end();
        const flujo = fs.createReadStream(fichero, { start: inicio, end: fin });
        flujo.on('error', () => res.destroy());
        return flujo.pipe(res);
      }
    }
    res.writeHead(416, { 'Content-Range': `bytes */${st.size}`,
                         'Cache-Control': 'no-store' });
    return res.end();
  }

  res.writeHead(200, {
    'Content-Type': tipo,
    'Content-Length': st.size,
    'Accept-Ranges': 'bytes',
    'Cache-Control': cache
  });
  if (req.method === 'HEAD') return res.end();
  const flujo = fs.createReadStream(fichero);
  flujo.on('error', () => res.destroy());
  flujo.pipe(res);
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

  enviarFichero(req, res, fichero, rel);
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
