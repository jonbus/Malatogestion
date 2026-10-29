#!/usr/bin/env node
/*
  Portero de /workers para la app de gestión.

  Qué hace:
    - Publica la app en  https://supermalato.es/workers/
    - Pide una clave antes de dejar ver nada.
    - Traduce /workers/api/...  ->  http://127.0.0.1:3001/api/...
    - Reescribe la página para que sus llamadas vayan por /workers/api/...

  No toca la app ni sus datos. Si este portero se para, la app sigue viva
  en 127.0.0.1:3001 y en la red local; solo deja de responder /workers.

  Arranque:
    PORT=3002 APP_ORIGIN=http://127.0.0.1:3001 \
    PIN_FILE=/opt/malato-gestion/.workers-pin \
    SECRET_FILE=/opt/malato-gestion/.workers-secret \
    node workers-gateway.mjs
*/
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const PUERTO = Number(process.env.PORT || 3002);
const HOST = process.env.HOST || '127.0.0.1';
const APP_ORIGEN = process.env.APP_ORIGIN || 'http://127.0.0.1:3001';
const PREFIJO = (process.env.PUBLIC_PREFIX || '/workers').replace(/\/+$/, '');
const PUBLICO = process.env.APP_PUBLIC || '/opt/malato-gestion/public';
const FICHERO_PIN = process.env.PIN_FILE || '/opt/malato-gestion/.workers-pin';
const FICHERO_SECRETO = process.env.SECRET_FILE || '/opt/malato-gestion/.workers-secret';
const DIAS_SESION = Number(process.env.SESSION_DAYS || 30);
const NOMBRE_COOKIE = process.env.COOKIE_NAME || 'malato_workers';
const MAX_INTENTOS = Number(process.env.MAX_ATTEMPTS || 8);
const VENTANA_INTENTOS = Number(process.env.ATTEMPT_WINDOW_MS || 10 * 60 * 1000);
const MAX_CUERPO = 64 * 1024;

/* ------------------------------------------------------------------ */
/*  La clave y el secreto de las sesiones                              */
/* ------------------------------------------------------------------ */

function leerPin() {
  let pin;
  try {
    pin = fs.readFileSync(FICHERO_PIN, 'utf8').trim();
  } catch (e) {
    console.error(`No puedo leer la clave de acceso: ${FICHERO_PIN}`);
    process.exit(1);
  }
  if (!/^[A-Za-z0-9_-]{6,32}$/.test(pin)) {
    console.error(`La clave de ${FICHERO_PIN} debe tener entre 6 y 32 caracteres ` +
                  `(letras, números, guion o guion bajo).`);
    process.exit(1);
  }
  return pin;
}

function leerSecreto() {
  try {
    const s = fs.readFileSync(FICHERO_SECRETO);
    if (s.length >= 32) return s;
  } catch (e) {
    /* se crea abajo */
  }
  const s = crypto.randomBytes(32);
  fs.writeFileSync(FICHERO_SECRETO, s, { mode: 0o600 });
  try { fs.chmodSync(FICHERO_SECRETO, 0o600); } catch (e) {}
  return s;
}

const PIN = leerPin();
const SECRETO = leerSecreto();

/* ------------------------------------------------------------------ */
/*  Sesión: cookie firmada, sin estado en el servidor                  */
/* ------------------------------------------------------------------ */

function firma(expira) {
  return crypto.createHmac('sha256', SECRETO)
    .update(`malato-workers-v1.${expira}`)
    .digest('base64url');
}

function crearToken() {
  const expira = Date.now() + DIAS_SESION * 24 * 60 * 60 * 1000;
  return `v1.${expira}.${firma(expira)}`;
}

function tokenValido(token) {
  if (typeof token !== 'string') return false;
  const m = /^v1\.(\d{10,16})\.([A-Za-z0-9_-]{20,64})$/.exec(token);
  if (!m) return false;
  const expira = Number(m[1]);
  if (!Number.isFinite(expira) || expira < Date.now()) return false;
  const esperada = Buffer.from(firma(expira));
  const dada = Buffer.from(m[2]);
  return esperada.length === dada.length && crypto.timingSafeEqual(esperada, dada);
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

function esHttps(req) {
  const proto = String(req.headers['x-forwarded-proto'] || '').split(',')[0].trim();
  return proto === 'https' || Boolean(req.socket.encrypted);
}

function cookieSesion(req, token) {
  const seguro = esHttps(req) ? '; Secure' : '';
  return `${NOMBRE_COOKIE}=${encodeURIComponent(token)}; Path=${PREFIJO}; ` +
         `HttpOnly; SameSite=Lax; Max-Age=${DIAS_SESION * 24 * 60 * 60}${seguro}`;
}

function cookieBorrada(req) {
  const seguro = esHttps(req) ? '; Secure' : '';
  return `${NOMBRE_COOKIE}=; Path=${PREFIJO}; HttpOnly; SameSite=Lax; Max-Age=0${seguro}`;
}

/* ------------------------------------------------------------------ */
/*  Límite de intentos por IP (en memoria)                             */
/* ------------------------------------------------------------------ */

const intentos = new Map();

function ipDe(req) {
  return String(req.headers['cf-connecting-ip'] ||
                (req.headers['x-forwarded-for'] || '').split(',')[0].trim() ||
                req.socket.remoteAddress || 'desconocida');
}

function bloqueado(ip) {
  const ahora = Date.now();
  const f = intentos.get(ip);
  if (!f) return false;
  if (f.hasta < ahora) { intentos.delete(ip); return false; }
  return f.n >= MAX_INTENTOS;
}

function anotarFallo(ip) {
  const ahora = Date.now();
  const f = intentos.get(ip);
  if (!f || f.hasta < ahora) {
    intentos.set(ip, { n: 1, hasta: ahora + VENTANA_INTENTOS });
  } else {
    f.n += 1;
  }
  if (intentos.size > 2000) {
    for (const [k, v] of intentos) if (v.hasta < ahora) intentos.delete(k);
  }
}

/* ------------------------------------------------------------------ */
/*  Página de entrada y página de la app                               */
/* ------------------------------------------------------------------ */

function escapeHtml(t) {
  return String(t).replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
}

function paginaEntrada(error = '', estado = 200) {
  const aviso = error
    ? `<p class="error" role="alert">${escapeHtml(error)}</p>`
    : `<p class="pista">Escribe la clave de la tienda para entrar.</p>`;
  return {
    estado,
    html: `<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Malato · acceso</title>
<style>
  :root { --verde:#1f6f43; --tinta:#1d2b24; --papel:#f6f3ea; --borde:#d8d2c2; }
  * { box-sizing:border-box; }
  body { margin:0; min-height:100dvh; display:grid; place-items:center; padding:24px;
         background:var(--papel); color:var(--tinta);
         font:16px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; }
  main { width:100%; max-width:360px; background:#fff; border:1px solid var(--borde);
         border-radius:18px; padding:28px 22px; box-shadow:0 12px 30px rgba(29,43,36,.08); }
  .marca { display:flex; align-items:center; gap:10px; margin-bottom:18px; }
  .logo { width:42px; height:42px; border-radius:12px; background:var(--verde);
          display:grid; place-items:center; color:#fff; font-weight:800; font-size:20px; }
  h1 { font-size:20px; margin:0; letter-spacing:-.01em; }
  .sub { margin:2px 0 0; color:#5d6b63; font-size:13px; }
  label { display:block; font-weight:650; font-size:14px; margin:0 0 6px; }
  input { width:100%; padding:14px 16px; font-size:22px; letter-spacing:.35em;
          text-align:center; border:1.5px solid var(--borde); border-radius:12px;
          background:#fff; color:var(--tinta); }
  input:focus { outline:none; border-color:var(--verde); box-shadow:0 0 0 3px rgba(31,111,67,.15); }
  button { width:100%; margin-top:14px; padding:14px 16px; border:0; border-radius:12px;
           background:var(--verde); color:#fff; font-size:16px; font-weight:700; cursor:pointer; }
  button:active { transform:translateY(1px); }
  .pista { color:#5d6b63; font-size:14px; margin:0 0 16px; }
  .error { color:#9b2c2c; background:#fdf0f0; border:1px solid #f2c9c9;
           padding:10px 12px; border-radius:10px; font-size:14px; margin:0 0 16px; }
  .pie { margin:18px 0 0; color:#7a857e; font-size:12px; text-align:center; }
</style>
</head>
<body>
<main>
  <div class="marca">
    <div class="logo" aria-hidden="true">M</div>
    <div>
      <h1>Malato · gestión</h1>
      <p class="sub">Acceso reservado al equipo</p>
    </div>
  </div>
  ${aviso}
  <form method="post" action="${PREFIJO}/login" autocomplete="off">
    <label for="pin">Clave de acceso</label>
    <input id="pin" name="pin" type="password"
           maxlength="32" required autofocus
           autocomplete="current-password" aria-describedby="pin-ayuda">
    <button type="submit">Entrar</button>
  </form>
  <p class="pie" id="pin-ayuda">Si no la sabes, pídesela a la propiedad.</p>
</main>
</body>
</html>`
  };
}

let cacheHtml = { mtime: 0, html: '' };

function htmlApp() {
  const fichero = path.join(PUBLICO, 'index.html');
  const st = fs.statSync(fichero);
  if (st.mtimeMs !== cacheHtml.mtime) {
    let html = fs.readFileSync(fichero, 'utf8');
    /* Las llamadas de la app son absolutas: /api/...  ->  /workers/api/... */
    html = html.replace(/(["'])\/api\//g, `$1${PREFIJO}/api/`);
    html = html.replace(/<head([^>]*)>/i,
      `<head$1><meta name="robots" content="noindex,nofollow">`);
    cacheHtml = { mtime: st.mtimeMs, html };
  }
  return cacheHtml.html;
}

function enviarHtml(res, estado, html) {
  res.writeHead(estado, {
    'Content-Type': 'text/html; charset=utf-8',
    'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'Referrer-Policy': 'no-referrer'
  });
  res.end(html);
}

function enviarJson(res, estado, objeto) {
  res.writeHead(estado, {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff'
  });
  res.end(JSON.stringify(objeto));
}

function leerCuerpo(req, limite = MAX_CUERPO) {
  return new Promise((ok, mal) => {
    let t = '';
    let n = 0;
    req.setEncoding('utf8');
    req.on('data', c => {
      n += Buffer.byteLength(c);
      if (n > limite) { mal(new Error('cuerpo demasiado grande')); req.destroy(); return; }
      t += c;
    });
    req.on('end', () => ok(t));
    req.on('error', mal);
  });
}

/* ------------------------------------------------------------------ */
/*  Pasar las llamadas de la API a la app de verdad                    */
/* ------------------------------------------------------------------ */

function proxyApi(req, res, url) {
  let destino;
  try { destino = new URL(APP_ORIGEN); }
  catch (e) { return enviarJson(res, 502, { ok: false, error: 'origen mal configurado' }); }

  const rutaDestino = url.pathname.slice(PREFIJO.length) + url.search;
  const cabeceras = { ...req.headers };
  delete cabeceras.host;
  delete cabeceras.connection;
  /* La cookie de la puerta NO se pasa a la app. La de gerencia SÍ, porque
     la app la necesita para firmar el acceso a las copias de seguridad. */
  const galletas = String(req.headers.cookie || '').split(';').map(s => s.trim()).filter(Boolean);
  const deGerencia = galletas.filter(c => c.startsWith('malato_gerencia='));
  if (deGerencia.length) cabeceras.cookie = deGerencia.join('; ');
  else delete cabeceras.cookie;
  cabeceras['x-forwarded-host'] = req.headers.host || '';
  cabeceras['x-forwarded-proto'] = req.headers['x-forwarded-proto'] || 'https';
  cabeceras['x-forwarded-prefix'] = PREFIJO;

  const peticion = http.request({
    hostname: destino.hostname,
    port: destino.port || 80,
    method: req.method,
    path: rutaDestino,
    headers: cabeceras,
    timeout: 30000
  }, respuesta => {
    const salida = { ...respuesta.headers };
    delete salida.connection;
    delete salida['transfer-encoding'];
    salida['cache-control'] = 'no-store';
    res.writeHead(respuesta.statusCode || 502, salida);
    respuesta.pipe(res);
  });

  peticion.on('timeout', () => { peticion.destroy(new Error('tiempo agotado')); });
  peticion.on('error', e => {
    if (!res.headersSent) enviarJson(res, 502, { ok: false, error: 'la app no responde' });
    else res.destroy();
    console.error(`  API ${req.method} ${rutaDestino}: ${e.message}`);
  });

  req.pipe(peticion);
}

/* ------------------------------------------------------------------ */
/*  El servidor                                                        */
/* ------------------------------------------------------------------ */

const servidor = http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://localhost');

  /* Si llega por HTTP a un nombre público, se manda a HTTPS.
     Así la cookie de sesión siempre viaja segura. */
  const proto = String(req.headers['x-forwarded-proto'] || '').split(',')[0].trim();
  const anfitrion = String(req.headers.host || '');
  if (proto === 'http' && !/^(localhost|127\.0\.0\.1)(:|$)/.test(anfitrion)) {
    res.writeHead(301, { Location: `https://${anfitrion}${req.url}` });
    return res.end();
  }

  if (!url.pathname.startsWith(PREFIJO)) {
    return enviarJson(res, 404, { ok: false, error: 'no encontrado' });
  }

  const resto = url.pathname.slice(PREFIJO.length) || '/';

  /* Para saber si está vivo, sin revelar nada */
  if (resto === '/health') {
    return enviarJson(res, 200, { ok: true, servicio: 'malato-workers' });
  }

  /* Salir: borra la cookie y vuelve a la puerta */
  if (resto === '/salir') {
    res.writeHead(303, { 'Set-Cookie': cookieBorrada(req), Location: `${PREFIJO}/` });
    return res.end();
  }

  /* Entrar con la clave */
  if (resto === '/login' && (req.method === 'POST' || req.method === 'PUT')) {
    const ip = ipDe(req);
    if (bloqueado(ip)) {
      const p = paginaEntrada('Demasiados intentos. Espera unos minutos.', 429);
      return enviarHtml(res, p.estado, p.html);
    }
    let cuerpo;
    try { cuerpo = await leerCuerpo(req, 2048); }
    catch (e) { return enviarJson(res, 413, { ok: false, error: 'petición demasiado grande' }); }
    const dado = (new URLSearchParams(cuerpo).get('pin') || '').trim();
    const a = Buffer.from(dado);
    const b = Buffer.from(PIN);
    const bien = a.length === b.length && crypto.timingSafeEqual(a, b);
    if (!bien) {
      anotarFallo(ip);
      console.error(`  clave incorrecta desde ${ip}`);
      const p = paginaEntrada('La clave no es correcta.', 401);
      return enviarHtml(res, p.estado, p.html);
    }
    intentos.delete(ip);
    res.writeHead(303, {
      'Set-Cookie': cookieSesion(req, crearToken()),
      Location: `${PREFIJO}/`
    });
    return res.end();
  }

  const autenticado = tokenValido(leerCookie(req, NOMBRE_COOKIE));

  /* /workers  ->  /workers/  (para que la página tenga su base) */
  if (resto === '' || resto === '/') {
    if (url.pathname === PREFIJO) {
      res.writeHead(302, { Location: `${PREFIJO}/${url.search}` });
      return res.end();
    }
    if (!autenticado) {
      const p = paginaEntrada();
      return enviarHtml(res, p.estado, p.html);
    }
    try {
      return enviarHtml(res, 200, htmlApp());
    } catch (e) {
      console.error(`  no puedo leer ${PUBLICO}/index.html: ${e.message}`);
      return enviarHtml(res, 500, '<h1>La aplicación no está disponible</h1>');
    }
  }

  /* Las llamadas de la app */
  if (resto.startsWith('/api/')) {
    if (!autenticado) return enviarJson(res, 401, { ok: false, error: 'no autorizado' });
    return proxyApi(req, res, url);
  }

  /* Cualquier otra ruta: si no ha entrado, la puerta; si ha entrado, 404 */
  if (!autenticado) {
    const p = paginaEntrada();
    return enviarHtml(res, p.estado, p.html);
  }
  return enviarJson(res, 404, { ok: false, error: 'no encontrado' });
});

servidor.listen(PUERTO, HOST, () => {
  console.log(`  portero de ${PREFIJO} en marcha`);
  console.log(`    escucha en:   http://${HOST}:${PUERTO}`);
  console.log(`    app detrás:   ${APP_ORIGEN}`);
  console.log(`    página:       ${PUBLICO}/index.html`);
  console.log(`    sesión:       ${DIAS_SESION} días`);
});

for (const senal of ['SIGTERM', 'SIGINT']) {
  process.on(senal, () => {
    console.log(`  cerrando por ${senal}`);
    servidor.close(() => process.exit(0));
    setTimeout(() => process.exit(0), 3000).unref();
  });
}
