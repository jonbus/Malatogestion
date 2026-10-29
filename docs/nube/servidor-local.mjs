/* Servidor local para probar la app antes de subirla.
   Sirve public/ y atiende /api/... con el mismo nucleo que usará Netlify.

   Uso:  node docs/nube/servidor-local.mjs [puerto]
*/
import http from 'node:http';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const nucleo = require('./netlify/functions/nucleo.js');

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const PUBLICO = path.join(AQUI, 'public');
const DATOS = path.join(AQUI, '.datos');
const FICHERO = path.join(DATOS, 'estado.json');
const PUERTO = Number(process.argv[2] || 8099);

/* Copias diarias de los datos de gestión. */
const COPIAS = path.resolve(process.env.COPIAS_DIR || path.join(os.homedir(), 'copias-gestion'));
const COOKIE_GERENCIA = 'malato_gerencia';
const HORAS_GERENCIA = 12;
const ID_COPIA = /^\d{4}-\d{2}-\d{2}_\d{6}$/;

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

/* ------------------------------------------------------------------ */
/*  La sesión de la Jefa: cookie firmada, para las copias              */
/* ------------------------------------------------------------------ */

function esHttps(req) {
  const proto = String(req.headers['x-forwarded-proto'] || '').split(',')[0].trim();
  return proto === 'https' || Boolean(req.socket.encrypted);
}

function firmaGerencia(expira) {
  return crypto.createHmac('sha256', pinGerencia)
    .update('malato-gerencia-v1.' + expira)
    .digest('base64url');
}

function crearTokenGerencia() {
  const expira = Date.now() + HORAS_GERENCIA * 60 * 60 * 1000;
  return `v1.${expira}.${firmaGerencia(expira)}`;
}

function leerCookie(req, nombre) {
  const crudo = req.headers.cookie || '';
  for (const trozo of crudo.split(';')) {
    const i = trozo.indexOf('=');
    if (i < 0) continue;
    if (trozo.slice(0, i).trim() !== nombre) continue;
    try { return decodeURIComponent(trozo.slice(i + 1).trim()); } catch (e) { return null; }
  }
  return null;
}

function gerenciaValida(req) {
  if (!pinGerencia) return false;
  const token = leerCookie(req, COOKIE_GERENCIA);
  if (!token) return false;
  const m = /^v1\.(\d{10,16})\.([A-Za-z0-9_-]{20,64})$/.exec(token);
  if (!m) return false;
  const expira = Number(m[1]);
  if (!Number.isFinite(expira) || expira < Date.now()) return false;
  const esperada = Buffer.from(firmaGerencia(expira));
  const dada = Buffer.from(m[2]);
  return esperada.length === dada.length && crypto.timingSafeEqual(esperada, dada);
}

function cookieGerencia(req, borrar = false) {
  const seguro = esHttps(req) ? '; Secure' : '';
  const valor = borrar ? '' : encodeURIComponent(crearTokenGerencia());
  const edad = borrar ? 0 : HORAS_GERENCIA * 60 * 60;
  return `${COOKIE_GERENCIA}=${valor}; Path=/; HttpOnly; SameSite=Lax; ` +
         `Max-Age=${edad}${seguro}`;
}

function responderJson(res, estado, cuerpo) {
  res.writeHead(estado, { 'Content-Type': 'application/json; charset=utf-8',
                          'Cache-Control': 'no-store' });
  res.end(JSON.stringify(cuerpo));
}

/* ------------------------------------------------------------------ */
/*  Las copias de seguridad                                            */
/* ------------------------------------------------------------------ */

function listarCopias() {
  if (!fs.existsSync(COPIAS)) return [];
  const salida = [];
  for (const e of fs.readdirSync(COPIAS, { withFileTypes: true })) {
    if (!e.isDirectory() || !ID_COPIA.test(e.name)) continue;
    const dir = path.join(COPIAS, e.name);
    const f = path.join(dir, 'estado.json');
    if (!fs.existsSync(f)) continue;
    let marcas = null, encargos = null;
    try {
      const info = fs.readFileSync(path.join(dir, 'INFO.txt'), 'utf8');
      for (const linea of info.split('\n')) {
        const i = linea.indexOf(':');
        if (i < 0) continue;
        const k = linea.slice(0, i).trim();
        const v = linea.slice(i + 1).trim();
        if (k === 'Marcas' && /^\d+$/.test(v)) marcas = Number(v);
        if (k === 'Encargos' && /^\d+$/.test(v)) encargos = Number(v);
      }
    } catch (e) { /* sin INFO: se enseña igual, sin contadores */ }
    const [fecha, hora] = e.name.split('_');
    const [a, m, d] = fecha.split('-');
    salida.push({
      id: e.name,
      fecha: `${d}/${m}/${a} ${hora.slice(0, 2)}:${hora.slice(2, 4)}`,
      tamano: fs.statSync(f).size,
      marcas: marcas,
      encargos: encargos
    });
  }
  return salida.sort((a, b) => b.id.localeCompare(a.id));
}

/* ------------------------------------------------------------------ */
/*  El servidor                                                        */
/* ------------------------------------------------------------------ */

const TIPOS = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8',
  '.png': 'image/png', '.svg': 'image/svg+xml', '.ico': 'image/x-icon',
  '.webmanifest': 'application/manifest+json'
};

const servidor = http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://localhost');

  /* Salir de la sesión de la Jefa: borra su cookie. */
  if (url.pathname === '/api/salir' && req.method === 'POST') {
    res.setHeader('Set-Cookie', cookieGerencia(req, true));
    return responderJson(res, 200, { ok: true });
  }

  /* Lista de copias: solo con la sesión de la Jefa. */
  if (url.pathname === '/api/copias' && req.method === 'GET') {
    if (!gerenciaValida(req)) {
      return responderJson(res, 401, { ok: false, error: 'no autorizado' });
    }
    try {
      return responderJson(res, 200, { ok: true, copias: listarCopias() });
    } catch (e) {
      return responderJson(res, 500, { ok: false, error: 'no se pudieron leer las copias' });
    }
  }

  /* Descargar una copia concreta. */
  if (url.pathname.startsWith('/api/copia/') && req.method === 'GET') {
    if (!gerenciaValida(req)) {
      return responderJson(res, 401, { ok: false, error: 'no autorizado' });
    }
    let id;
    try { id = decodeURIComponent(url.pathname.slice('/api/copia/'.length)); }
    catch (e) { return responderJson(res, 400, { ok: false, error: 'copia no válida' }); }
    if (!ID_COPIA.test(id)) {
      return responderJson(res, 400, { ok: false, error: 'copia no válida' });
    }
    const f = path.join(COPIAS, id, 'estado.json');
    if (!f.startsWith(COPIAS + path.sep) || !fs.existsSync(f)) {
      return responderJson(res, 404, { ok: false, error: 'copia no encontrada' });
    }
    res.writeHead(200, {
      'Content-Type': 'application/json; charset=utf-8',
      'Content-Disposition': `attachment; filename="malato-gestion-${id}.json"`,
      'Cache-Control': 'no-store'
    });
    return fs.createReadStream(f).pipe(res);
  }

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
    const cabeceras = { 'Content-Type': 'application/json; charset=utf-8',
                        'Cache-Control': 'no-store' };
    /* Al entrar en gerencia, se firma una cookie para poder pedir las copias. */
    if (url.pathname === '/api/entrar' && salida.status === 200 && pinGerencia) {
      cabeceras['Set-Cookie'] = cookieGerencia(req);
    }
    res.writeHead(salida.status, cabeceras);
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
  console.log(`    copias:              ${COPIAS}`);
  console.log(`\n  (sin túnel: solo funciona dentro de la misma wifi)`);
});
