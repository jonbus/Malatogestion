/* Servidor local para probar la app antes de subirla.
   Sirve public/ y atiende /api/... con el mismo nucleo que usará Netlify.

   Uso:  node docs/nube/servidor-local.mjs [puerto]
*/
import http from 'node:http';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const nucleo = require('./netlify/functions/nucleo.js');

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const PUBLICO = path.join(AQUI, 'public');
const DATOS = path.join(AQUI, '.datos');
const FICHERO = path.join(DATOS, 'estado.json');
const PUERTO = Number(process.argv[2] || 8099);

if (!fs.existsSync(DATOS)) fs.mkdirSync(DATOS, { recursive: true });

/* almacén en un fichero, con la misma forma que Netlify Blobs */
const store = {
  async get(clave, opciones) {
    if (!fs.existsSync(FICHERO)) return null;
    const txt = fs.readFileSync(FICHERO, 'utf8');
    if (!txt) return null;
    const todo = JSON.parse(txt);
    const v = todo[clave];
    if (v === undefined) return null;
    return opciones && opciones.type === 'json' ? v : JSON.stringify(v);
  },
  async setJSON(clave, valor) {
    let todo = {};
    if (fs.existsSync(FICHERO)) {
      try { todo = JSON.parse(fs.readFileSync(FICHERO, 'utf8') || '{}'); } catch (e) { todo = {}; }
    }
    todo[clave] = valor;
    fs.writeFileSync(FICHERO, JSON.stringify(todo, null, 1), 'utf8');
  }
};

/* la clave de la jefa: del entorno, o de un fichero al lado */
let pinGerencia = process.env.GERENCIA_PIN || '';
const F_PIN = path.join(AQUI, '.pin');
if (!pinGerencia && fs.existsSync(F_PIN)) {
  pinGerencia = fs.readFileSync(F_PIN, 'utf8').trim();
}
const manejar = nucleo.crearManejador({ store, pinGerencia: pinGerencia });

const TIPOS = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8',
  '.png': 'image/png', '.svg': 'image/svg+xml', '.ico': 'image/x-icon',
  '.webmanifest': 'application/manifest+json'
};

const servidor = http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://localhost');

  if (url.pathname.startsWith('/api/')) {
    let cuerpo = null;
    if (req.method === 'POST' || req.method === 'PUT') {
      cuerpo = await new Promise((ok) => {
        let t = '';
        req.on('data', c => { t += c; });
        req.on('end', () => ok(t));
      });
    }
    const salida = await manejar({ metodo: req.method, ruta: url.pathname, cuerpo });
    res.writeHead(salida.status, { 'Content-Type': 'application/json; charset=utf-8',
                                   'Cache-Control': 'no-store' });
    res.end(JSON.stringify(salida.body));
    return;
  }

  let rel = url.pathname === '/' ? '/index.html' : url.pathname;
  const fich = path.join(PUBLICO, rel);
  if (!fich.startsWith(PUBLICO) || !fs.existsSync(fich) || fs.statSync(fich).isDirectory()) {
    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('no encontrado');
    return;
  }
  res.writeHead(200, { 'Content-Type': TIPOS[path.extname(fich)] || 'application/octet-stream',
                       'Cache-Control': 'no-store' });
  res.end(fs.readFileSync(fich));
});

/* Escucha en TODAS las direcciones, no solo en 127.0.0.1.
   Antes solo contestaba a este ordenador, así que los móviles y las
   tablets de la tienda no podían entrar sin pasar por el túnel. */
const HOST = process.env.HOST_LOCAL || '0.0.0.0';

servidor.listen(PUERTO, HOST, () => {
  console.log(`\n  servidor local en marcha`);
  console.log(`    en este ordenador:   http://127.0.0.1:${PUERTO}`);
  for (const dir of Object.values(os.networkInterfaces()).flat()) {
    if (dir && dir.family === 'IPv4' && !dir.internal) {
      console.log(`    desde la red wifi:   http://${dir.address}:${PUERTO}`);
    }
  }
  console.log(`\n  (sin túnel: solo funciona dentro de la misma wifi)`);
});
