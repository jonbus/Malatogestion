/* =========================================================================
   Tienda Malato · adaptador de Cloudflare Workers
   Los ficheros estáticos los sirve Cloudflare; la lógica está en nucleo.js
   y los datos en KV. El mismo núcleo que usa Netlify y el servidor local.
   ========================================================================= */
/* el MISMO nucleo que usan Netlify y el servidor local:
   una sola copia, para que no se queden despistadas */
import nucleo from '../netlify/functions/nucleo.js';

function json(codigo, objeto) {
  return new Response(JSON.stringify(objeto), {
    status: codigo,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'no-store'
    }
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    /* todo lo que no es /api/ son ficheros: los sirve Cloudflare */
    if (!url.pathname.startsWith('/api/')) {
      return env.ASSETS.fetch(request);
    }

    /* el almacén, con la misma forma que el de Netlify y el local */
    const store = {
      async get(clave, opciones) {
        const txt = await env.ESTADO.get(clave);
        if (!txt) return null;
        if (opciones && opciones.type === 'json') {
          try { return JSON.parse(txt); } catch (e) { return null; }
        }
        return txt;
      },
      async setJSON(clave, valor) {
        await env.ESTADO.put(clave, JSON.stringify(valor));
      }
    };

    const manejar = nucleo.crearManejador({
      store: store,
      pinGerencia: env.GERENCIA_PIN
    });

    let cuerpo = null;
    const m = String(request.method).toUpperCase();
    if (m === 'POST' || m === 'PUT') {
      try { cuerpo = await request.text(); } catch (e) { cuerpo = null; }
    }

    let salida;
    try {
      salida = await manejar({ metodo: m, ruta: url.pathname, cuerpo: cuerpo });
    } catch (e) {
      return json(500, { ok: false, error: 'Fallo interno: ' + e.message });
    }

    return json(salida.status, Object.assign({ version_funcion: 'cf-1' }, salida.body));
  }
};
