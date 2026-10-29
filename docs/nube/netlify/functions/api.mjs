/* =========================================================================
   Tienda Malato · adaptador de Netlify
   Netlify Functions 2.0 + Netlify Blobs. Toda la lógica está en nucleo.js.
   ========================================================================= */
import { getStore } from '@netlify/blobs';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const nucleo = require('./nucleo.js');

const ALMACEN = 'tienda-malato';
const VERSION = 'v1';

function respuesta(codigo, objeto) {
  return new Response(JSON.stringify(objeto), {
    status: codigo,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'no-store'
    }
  });
}

export default async (req) => {
  let store;
  try {
    /* 'strong' fuerza leer del almacén principal y no de una réplica con
       retraso: sin esto se pisan datos al guardar desde dos móviles. */
    try {
      store = getStore({ name: ALMACEN, consistency: 'strong' });
    } catch (e) {
      store = getStore(ALMACEN);
    }
  } catch (e) {
    return respuesta(500, { ok: false, version: VERSION,
      error: 'Netlify Blobs no está disponible: ' + e.message });
  }

  const manejar = nucleo.crearManejador({
    store: store,
    pinGerencia: process.env.GERENCIA_PIN
  });

  let cuerpo = null;
  const m = String(req.method).toUpperCase();
  if (m === 'POST' || m === 'PUT') {
    try { cuerpo = await req.text(); } catch (e) { cuerpo = null; }
  }

  const url = new URL(req.url);
  let salida;
  try {
    salida = await manejar({
      metodo: req.method,
      ruta: url.pathname,
      cuerpo: cuerpo
    });
  } catch (e) {
    return respuesta(500, { ok: false, version: VERSION, error: 'Fallo interno: ' + e.message });
  }

  return respuesta(salida.status, Object.assign({ version_funcion: VERSION }, salida.body));
};

export const config = { path: '/api/*' };
