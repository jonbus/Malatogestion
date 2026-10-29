/* =========================================================================
   Tienda Malato · núcleo
   La lógica de guardar las marcas y los fichajes, SIN depender de Netlify.
   Se prueba en local y el adaptador (api.mjs) solo la enchufa.

   El almacén tiene que ofrecer:
     store.get(clave, { type: 'json' })  -> objeto o null
     store.setJSON(clave, objeto)        -> nada

   Forma de lo guardado:
     {
       version: 12,
       marcas:  { "2026-10-22|md0.1": { q: "op1", h: "17:03" } },
       fichajes: [ { q:"op1", p:"tienda", e:"16:58", s:null, dia:"2026-10-22" } ]
     }

   Las MARCAS son COMPARTIDAS por día: si una marca algo, las demás lo ven.
   El FICHAJE es de cada persona.
   ========================================================================= */
'use strict';

const CLAVE = 'estado';
const DIAS_QUE_SE_GUARDAN = 30;

/* ---------------------------------------------------------------- utilidades */
function hoyISO(zona) {
  /* La fecha del día en la zona de la tienda, no la del servidor. */
  const f = new Date().toLocaleDateString('en-CA', { timeZone: zona || 'Europe/Madrid' });
  return f; // en-CA da AAAA-MM-DD
}

function horaLocal(zona) {
  return new Date().toLocaleTimeString('es-ES', {
    timeZone: zona || 'Europe/Madrid', hour: '2-digit', minute: '2-digit'
  });
}

function estadoVacio() {
  return { version: 0, marcas: {}, fichajes: [], traslados: {}, notas: {},
             encargos: [], recuentos: {}, tahona: {}, encargosFecha: [], cascadas: {}, nombres: [], proveedores: [], plantilla: {} };
}

/* Se queda con los últimos N días y con los fichajes de esos días. */
function podar(estado, zona) {
  const limite = new Date();
  limite.setDate(limite.getDate() - DIAS_QUE_SE_GUARDAN);
  const desde = limite.toLocaleDateString('en-CA', { timeZone: zona || 'Europe/Madrid' });

  const marcas = {};
  for (const k of Object.keys(estado.marcas)) {
    const dia = k.split('|')[0];
    if (dia >= desde) marcas[k] = estado.marcas[k];
  }
  /* Los traslados se guardan por día de ORIGEN: cuando el origen es viejo,
     el traslado ya no sirve para nada. */
  const traslados = {};
  for (const k of Object.keys(estado.traslados || {})) {
    if (k.split('|')[0] >= desde) traslados[k] = estado.traslados[k];
  }
  /* Las notas son para días FUTUROS, así que no se pueden podar por antigüedad
     del mismo modo: se guardan las de los últimos 60 días en adelante. */
  const limiteNotas = new Date();
  limiteNotas.setDate(limiteNotas.getDate() - 60);
  const desdeNotas = limiteNotas.toLocaleDateString('en-CA',
    { timeZone: zona || 'Europe/Madrid' });
  const notas = {};
  for (const f of Object.keys(estado.notas || {})) {
    if (f >= desdeNotas) notas[f] = estado.notas[f];
  }
  /* Los encargos NO caducan mientras no se hagan: se quitan hasta que alguien
     los cierre. Solo se tiran los ya hechos, pasados 60 días. */
  const encargos = (estado.encargos || []).filter(e => {
    if (!e.hecho) return true;
    return String(e.diaHecho || e.dia || '') >= desdeNotas;
  });
  /* Los recuentos del lunes se guardan mucho más tiempo: son el histórico
     con el que se hacen los pedidos. */
  const limiteRec = new Date();
  limiteRec.setDate(limiteRec.getDate() - 400);
  const desdeRec = limiteRec.toLocaleDateString('en-CA',
    { timeZone: zona || 'Europe/Madrid' });
  const recuentos = {};
  for (const f of Object.keys(estado.recuentos || {})) {
    if (f >= desdeRec) recuentos[f] = estado.recuentos[f];
  }
  /* el pan de la tahona: se guarda dos años, para poder cotejar facturas */
  const tahona = {};
  for (const f of Object.keys(estado.tahona || {})) {
    if (f >= desdeRec) tahona[f] = estado.tahona[f];
  }
  return {
    version: estado.version,
    marcas: marcas,
    recuentos: recuentos,
    tahona: tahona,
    /* los encargos no caducan: se quedan hasta que se reciben */
    cascadas: estado.cascadas || {},
    /* los proveedores no caducan: son una agenda */
    proveedores: estado.proveedores || [],
    plantilla: estado.plantilla || {},
    nombres: estado.nombres || [],
    encargosFecha: (estado.encargosFecha || []).filter(x => {
      const fin = x.hasta || x.desde || '';
      return fin >= desdeNotas || !x.recibido;
    }),
    traslados: traslados,
    notas: notas,
    encargos: encargos,
    fichajes: (estado.fichajes || []).filter(f => String(f.dia || '') >= desde)
  };
}

/* ------------------------------------------------------------------ manejador */
function crearManejador(opciones) {
  const store = opciones.store;
  const zona = opciones.zona || 'Europe/Madrid';
  const quien = opciones.quien || '';        /* qué número ha entrado, si se sabe */

  async function leer() {
    const guardado = await store.get(CLAVE, { type: 'json' });
    if (!guardado || typeof guardado !== 'object') return estadoVacio();
    return {
      version: Number(guardado.version) || 0,
      marcas: guardado.marcas && typeof guardado.marcas === 'object' ? guardado.marcas : {},
      traslados: guardado.traslados && typeof guardado.traslados === 'object'
        ? guardado.traslados : {},
      notas: guardado.notas && typeof guardado.notas === 'object' ? guardado.notas : {},
      encargos: Array.isArray(guardado.encargos) ? guardado.encargos : [],
      fichajes: Array.isArray(guardado.fichajes) ? guardado.fichajes : [],
      /* se guardaba, pero aquí se olvidaba: se escribía y no se leía nunca */
      recuentos: guardado.recuentos && typeof guardado.recuentos === 'object'
        ? guardado.recuentos : {},
      tahona: guardado.tahona && typeof guardado.tahona === 'object'
        ? guardado.tahona : {},
      encargosFecha: Array.isArray(guardado.encargosFecha) ? guardado.encargosFecha : [],
      cascadas: guardado.cascadas && typeof guardado.cascadas === 'object'
        ? guardado.cascadas : {},
      /* la memoria de los nombres: no caduca nunca */
      nombres: Array.isArray(guardado.nombres) ? guardado.nombres : [],
      proveedores: Array.isArray(guardado.proveedores) ? guardado.proveedores : [],
      plantilla: guardado.plantilla && typeof guardado.plantilla === 'object'
        ? guardado.plantilla : {}
    };
  }

  async function escribir(estado) {
    estado.version = (Number(estado.version) || 0) + 1;
    await store.setJSON(CLAVE, estado);
    return estado;
  }

  /* Acepta una lista de cambios y los aplica sobre lo que haya guardado.
     Nunca escribe el estado entero que manda el cliente: eso pisaría lo que
     hayan hecho las demás mientras tanto. */
  function aplicar(estado, cambios, marca, hora) {
    let n = 0;
    for (const clave of Object.keys(cambios || {})) {
      if (!/^\d{4}-\d{2}-\d{2}\|/.test(clave)) continue;   /* tiene que llevar fecha */
      const valor = cambios[clave];
      if (valor) {
        estado.marcas[clave] = { q: marca, h: hora };
        n++;
      } else {
        if (estado.marcas[clave]) { delete estado.marcas[clave]; n++; }
      }
    }
    return n;
  }

  return async function manejar(peticion) {
    const metodo = String(peticion.metodo || 'GET').toUpperCase();
    const ruta = String(peticion.ruta || '/');
    let cuerpo = null;
    try { cuerpo = peticion.cuerpo ? JSON.parse(peticion.cuerpo) : null; } catch (e) { cuerpo = null; }

    const marca = (cuerpo && String(cuerpo.quien || '').slice(0, 20)) || quien;
    const hora = horaLocal(zona);
    const dia = hoyISO(zona);

    /* -------- estado */
    if (ruta.endsWith('/estado') && metodo === 'GET') {
      const estado = podar(await leer(), zona);
      return { status: 200, body: {
        ok: true, dia: dia, version: estado.version,
        marcas: estado.marcas, traslados: estado.traslados,
        notas: estado.notas, fichajes: estado.fichajes,
        encargos: estado.encargos, recuentos: estado.recuentos,
        tahona: estado.tahona, encargosFecha: estado.encargosFecha,
        cascadas: estado.cascadas, nombres: estado.nombres,
        proveedores: estado.proveedores, plantilla: estado.plantilla
      }};
    }

    /* -------- encargos: tareas que alguien manda a otro puesto */
    if (ruta.endsWith('/encargo') && metodo === 'POST') {
      const c = cuerpo || {};
      const texto = String(c.t || '').trim().slice(0, 300);
      const puesto = String(c.p || '').slice(0, 20);
      const clave = c.clave ? String(c.clave).slice(0, 60) : '';
      if (!texto || !puesto) {
        return { status: 400, body: { ok: false, error: 'falta el texto o el puesto' } };
      }
      const estado = await leer();
      /* si lleva clave y ya existe sin hacer, no se duplica */
      if (clave && estado.encargos.some(e => e.clave === clave && !e.hecho)) {
        return { status: 200, body: { ok: true, yaEstaba: true, encargos: estado.encargos } };
      }
      /* la memoria de los nombres: solo el texto, sin fechas ni cantidades, y no caduca */
      estado.nombres = estado.nombres || [];
      if (!estado.nombres.includes(texto)) {
        estado.nombres.push(texto);
        if (estado.nombres.length > 500) estado.nombres.shift();
      }
      estado.encargos.push({
        id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
        t: texto, p: puesto, q: marca,
        f: /^\d{4}-\d{2}-\d{2}$/.test(String(c.f || '')) ? String(c.f) : null,
        diario: c.diario === true,
        turno: ['manana','tarde'].includes(c.turno) ? c.turno : null,
        /* extra = cuando se pueda · urgente = hoy y ya */
        /* extra = cuando se pueda · urgente = hoy y ya ·
           arreglar = algo que hay que reparar (lo apunta cualquiera, no caduca) */
        tipo: ['urgente', 'arreglar', 'llamada'].includes(c.tipo) ? c.tipo : 'extra',
        /* una llamada puede ser urgente, sin dejar de ser llamada */
        urgente: c.urgente === true,
        /* si es una llamada: a qué número y por qué */
        tel: c.tel ? String(c.tel).replace(/[^0-9]/g, '').slice(0, 15) : null,
        motivo: c.motivo ? String(c.motivo).slice(0, 200) : null,
        antesDe: c.antesDe ? String(c.antesDe).slice(0, 5) : null,
        opciones: Array.isArray(c.opciones) ? c.opciones.slice(0, 40).map(String) : null,
        /* los sub-pasos: sin esto, un encargo con pasos los perdía */
        partes: Array.isArray(c.partes) ? c.partes.slice(0, 20).map(String) : null,
        que: c.que ? String(c.que).slice(0, 60) : null,
        clave: clave || null,
        /* lo que hay que crear cuando este se haga (la cascada) */
        cascada: Array.isArray(c.cascada) ? c.cascada.slice(0, 10) : null,
        h: hora, hecho: false
      });
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, version: podado.version,
                                    encargos: podado.encargos } };
    }

    /* -------- un encargo hecho (y por tanto desaparece de la lista) */
    if (ruta.endsWith('/encargo-hecho') && metodo === 'POST') {
      if (!cuerpo || !cuerpo.id) {
        return { status: 400, body: { ok: false, error: 'falta el id' } };
      }
      const estado = await leer();
      const e = estado.encargos.find(x => x.id === String(cuerpo.id));
      if (!e) return { status: 404, body: { ok: false, error: 'no existe ese encargo' } };
      /* se puede marcar y DESMARCAR: si alguien le dio sin querer, se deshace */
      if (cuerpo.deshacer) {
        e.hecho = false;
        delete e.qHecho; delete e.hHecho; delete e.diaHecho;
      } else {
        e.hecho = true; e.qHecho = marca; e.hHecho = hora; e.diaHecho = hoyISO(zona);
      }
      if (cuerpo.que) e.que = String(cuerpo.que).slice(0, 60);

      /* LA CASCADA, AQUÍ MISMO: la lanza el servidor, no la pantalla.
         Así da igual quién la tache y desde dónde. */
      if (e.hecho) {
        const claveCasc = String(e.t || '')
          .toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
          .replace(/\s+/g, ' ').trim().slice(0, 120);
        const hijos = (estado.cascadas && estado.cascadas[claveCasc]) || [];
        const hoyC = hoyISO(zona);
        for (const h of hijos) {
          const clave = 'cascada:' + claveCasc + ':' +
            String(h.que || '').toLowerCase().trim() + ':' + hoyC;
          if ((estado.encargos || []).some(x => x.clave === clave && !x.hecho)) continue;
          estado.encargos.push({
            id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
            t: String(h.que || '').slice(0, 300),
            p: ['tienda', 'coordinacion', 'gerencia'].includes(h.p) ? h.p : 'tienda',
            f: hoyC, turno: h.turno || null, diario: false, tipo: 'extra',
            clave: clave, deCascada: claveCasc, q: marca, h: hora, hecho: false
          });
        }
      }

      /* LA CASCADA: al terminar este, nacen los siguientes.
         Y no nacen antes: hasta que este no se hace, los otros NO EXISTEN. */
      let nacidos = 0;
      for (const hijo of (e.cascada || [])) {
        if (!hijo || !hijo.t || !hijo.p) continue;
        const k = hijo.clave ? String(hijo.clave).slice(0, 60) : '';
        if (k && estado.encargos.some(x => x.clave === k && !x.hecho)) continue;  // ya está
        estado.encargos.push({
          id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6) + nacidos,
          t: String(hijo.t).slice(0, 300),
          p: String(hijo.p).slice(0, 20),
          q: e.q,                       /* la pone quien la mandó */
          f: /^\d{4}-\d{2}-\d{2}$/.test(String(hijo.f || '')) ? String(hijo.f) : null,
          diario: hijo.diario === true,
          partes: Array.isArray(hijo.partes) ? hijo.partes.slice(0, 20).map(String) : null,
          clave: k || null,
          vieneDe: e.id,
          h: hora, hecho: false
        });
        nacidos++;
      }

      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, version: podado.version,
                                    nacidos: nacidos, encargos: podado.encargos } };
    }

    /* -------- borrar un encargo (solo lo hace la gerencia) */
    if (ruta.endsWith('/encargo-borrar') && metodo === 'POST') {
      if (!cuerpo || !cuerpo.id) {
        return { status: 400, body: { ok: false, error: 'falta el id' } };
      }
      const estado = await leer();
      const antes = estado.encargos.length;
      estado.encargos = estado.encargos.filter(x => x.id !== String(cuerpo.id));
      const n = antes - estado.encargos.length;
      if (n) await escribir(podar(estado, zona));
      return { status: 200, body: { ok: true, borrados: n,
                                    encargos: podar(estado, zona).encargos } };
    }

    /* -------- el recuento del lunes: lo que sobró del asador el fin de semana.
       Es el stock inicial antes de hacer los pedidos. */
    if (ruta.endsWith('/recuento') && metodo === 'POST') {
      if (!cuerpo) return { status: 400, body: { ok: false, error: 'faltan los datos' } };
      const fecha = String(cuerpo.fecha || '');
      if (!/^\d{4}-\d{2}-\d{2}$/.test(fecha)) {
        return { status: 400, body: { ok: false, error: 'fecha no válida' } };
      }
      if (!marca) return { status: 400, body: { ok: false, error: 'falta quién lo apunta' } };
      const v = cuerpo.valores || {};
      const num = (x) => {
        const n = Number(x);
        return Number.isFinite(n) && n >= 0 ? Math.round(n * 100) / 100 : 0;
      };
      const estado = await leer();
      if (!estado.recuentos) estado.recuentos = {};
      const antes = estado.recuentos[fecha] || {};
      estado.recuentos[fecha] = {
        pollos: num(v.pollos), codillos: num(v.codillos),
        patatas: num(v.patatas), bravas: num(v.bravas),
        q: marca, h: hora,
        /* si lo cambia coordinación, se entiende aprobado */
        aprobado: marca.startsWith('co') ? true : false,
        qAprueba: marca.startsWith('co') ? marca : null
      };
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, version: podado.version,
                                    recuentos: podado.recuentos } };
    }

    /* -------- sugerencias: lo que ya se ha escrito alguna vez */
    if (ruta.endsWith('/sugerencias') && metodo === 'POST') {
      const busca = String((cuerpo && cuerpo.q) || '')
        .toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim();
      const estado = await leer();
      const todos = estado.nombres || [];
      let salida;
      if (!busca) {
        salida = todos.slice(-12).reverse();
      } else {
        salida = todos
          .filter(n => n.toLowerCase().normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '').includes(busca))
          .slice(-12);
      }
      return { status: 200, body: { ok: true, sugerencias: salida } };
    }

    /* -------- las cascadas: una tarea que, al hacerse, hace nacer la siguiente */
    const limpiaTarea = (x) => String(x || '')
      .toLowerCase()
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .replace(/\s+/g, ' ').trim().slice(0, 120);

    /* solo coordinación y la Jefa montan cascadas */
    const puedeCascada = (quien) => /^(co|ge)/.test(String(quien || ''));

    if (ruta.endsWith('/cascada') && metodo === 'POST') {
      if (!cuerpo || !puedeCascada(cuerpo.quien)) {
        return { status: 403, body: { ok: false, error: 'solo coordinación y la Jefa' } };
      }
      const tarea = limpiaTarea(cuerpo.tarea);
      if (!tarea) return { status: 400, body: { ok: false, error: 'falta la tarea' } };
      const hijos = (Array.isArray(cuerpo.hijos) ? cuerpo.hijos : [])
        .map(h => ({
          que: String((h && h.que) || '').trim().slice(0, 200),
          p: ['tienda', 'coordinacion', 'gerencia'].includes(h && h.p) ? h.p : 'tienda',
          turno: ['manana', 'tarde'].includes(h && h.turno) ? h.turno : null,
          cuando: Number.isFinite(Number(h && h.cuando)) ? Math.max(0, Math.min(30, Number(h.cuando))) : 0
        }))
        .filter(h => h.que);
      const estado = await leer();
      if (!estado.cascadas) estado.cascadas = {};
      if (!hijos.length) delete estado.cascadas[tarea];
      else estado.cascadas[tarea] = hijos;
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, cascadas: podado.cascadas } };
    }

    /* lanzar la cascada: se llama al terminar una tarea */
    if (ruta.endsWith('/cascada-lanzar') && metodo === 'POST') {
      const tarea = limpiaTarea(cuerpo && cuerpo.tarea);
      const fecha = String((cuerpo && cuerpo.fecha) || '');
      if (!tarea || !/^\d{4}-\d{2}-\d{2}$/.test(fecha)) {
        return { status: 400, body: { ok: false, error: 'faltan datos' } };
      }
      const estado = await leer();
      const hijos = (estado.cascadas && estado.cascadas[tarea]) || [];
      if (!hijos.length) return { status: 200, body: { ok: true, nacidos: [] } };

      const hoy = hoyISO(zona);
      const creados = [];
      for (const h of hijos) {
        /* la fecha del hijo: nunca en el pasado */
        let f = fecha;
        if (h.cuando > 0) {
          const d = new Date(fecha + 'T12:00:00Z');
          d.setUTCDate(d.getUTCDate() + h.cuando);
          f = d.toISOString().slice(0, 10);
        }
        if (f < hoy) f = hoy;
        /* si ya está puesto para ese día, no se duplica */
        const clave = 'cascada:' + tarea + ':' + limpiaTarea(h.que) + ':' + f;
        const ya = (estado.encargos || []).some(x =>
          x.clave === clave && !x.hecho);
        if (ya) continue;
        const id = Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
        estado.encargos.push({
          id: id, t: h.que, p: h.p, f: f, turno: h.turno,
          diario: false, tipo: 'extra', clave: clave,
          deCascada: tarea, q: marca, h: hora, hecho: false
        });
        creados.push({ id: id, t: h.que, p: h.p, f: f, turno: h.turno });
      }
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, nacidos: creados, encargos: podado.encargos } };
    }

    /* -------- encargos: lo que hay que tener un día y hay que pedir antes */
    if (ruta.endsWith('/encargo-fecha') && metodo === 'POST') {
      const c = cuerpo || {};
      const que = String(c.que || '').trim().slice(0, 200);
      if (!que) return { status: 400, body: { ok: false, error: 'falta qué es' } };
      const tipo = ['dia', 'rango', 'semana'].includes(c.tipo) ? c.tipo : 'dia';
      const desde = String(c.desde || '');
      if (!/^\d{4}-\d{2}-\d{2}$/.test(desde)) {
        return { status: 400, body: { ok: false, error: 'fecha no válida' } };
      }
      let hasta = String(c.hasta || desde);
      if (!/^\d{4}-\d{2}-\d{2}$/.test(hasta) || hasta < desde) hasta = desde;
      if (tipo === 'dia') hasta = desde;
      const dias = Array.isArray(c.dias)
        ? c.dias.map(Number).filter(n => n >= 0 && n <= 6) : [];
      if (tipo === 'semana' && !dias.length) {
        return { status: 400, body: { ok: false, error: 'elige al menos un día' } };
      }
      const antelacion = Number.isFinite(Number(c.antelacion))
        ? Math.max(0, Math.min(60, Number(c.antelacion))) : 0;
      const estado = await leer();
      if (!estado.encargosFecha) estado.encargosFecha = [];
      const e = {
        id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
        que: que,
        cliente: String(c.cliente || '').trim().slice(0, 60),
        tipo: tipo, desde: desde, hasta: hasta, dias: dias,
        antelacion: antelacion,
        quienPide: String(c.quienPide || 'coordinacion').slice(0, 20),
        quienRecibe: String(c.quienRecibe || 'coordinacion').slice(0, 20),
        q: marca, h: hora,
        pedidos: {},      /* por fecha de entrega: true cuando se pidió */
        recibidos: {}     /* por fecha de entrega: true cuando llegó */
      };
      estado.encargosFecha.push(e);
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, version: podado.version,
                                    encargosFecha: podado.encargosFecha } };
    }

    /* -------- marcar un encargo: pedido o recibido, en una fecha de entrega */
    if (ruta.endsWith('/encargo-fecha-hecho') && metodo === 'POST') {
      const c = cuerpo || {};
      const fecha = String(c.fecha || '');
      if (!/^\d{4}-\d{2}-\d{2}$/.test(fecha)) {
        return { status: 400, body: { ok: false, error: 'fecha no válida' } };
      }
      const cual = c.cual === 'recibido' ? 'recibidos' : 'pedidos';
      const estado = await leer();
      const e = (estado.encargosFecha || []).find(x => String(x.id) === String(c.id));
      if (!e) return { status: 404, body: { ok: false, error: 'no existe ese encargo' } };
      if (!e[cual]) e[cual] = {};
      if (c.valor === false) delete e[cual][fecha];
      else e[cual][fecha] = marca || true;
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, encargosFecha: podado.encargosFecha } };
    }

    /* -------- borrar un encargo */
    if (ruta.endsWith('/encargo-fecha-borrar') && metodo === 'POST') {
      const estado = await leer();
      const antes = (estado.encargosFecha || []).length;
      estado.encargosFecha = (estado.encargosFecha || [])
        .filter(x => String(x.id) !== String((cuerpo && cuerpo.id) || ''));
      if (estado.encargosFecha.length === antes) {
        return { status: 404, body: { ok: false, error: 'no existe ese encargo' } };
      }
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, encargosFecha: podado.encargosFecha } };
    }

    /* -------- el visto bueno de coordinación al recuento del lunes */
    if (ruta.endsWith('/recuento-aprobar') && metodo === 'POST') {
      const fecha = String((cuerpo && cuerpo.fecha) || '');
      if (!/^\d{4}-\d{2}-\d{2}$/.test(fecha)) {
        return { status: 400, body: { ok: false, error: 'fecha no válida' } };
      }
      if (!marca) return { status: 400, body: { ok: false, error: 'falta quién' } };
      const estado = await leer();
      const r = estado.recuentos && estado.recuentos[fecha];
      if (!r) return { status: 404, body: { ok: false, error: 'no hay recuento ese día' } };
      r.aprobado = true;
      r.qAprueba = marca;
      r.hAprueba = hora;
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, recuentos: podado.recuentos } };
    }

    /* -------- borrar un recuento (para las pruebas y para deshacer un error) */
    if (ruta.endsWith('/recuento-borrar') && metodo === 'POST') {
      const fecha = String((cuerpo && cuerpo.fecha) || '');
      if (!/^\d{4}-\d{2}-\d{2}$/.test(fecha)) {
        return { status: 400, body: { ok: false, error: 'fecha no válida' } };
      }
      const estado = await leer();
      if (estado.recuentos && estado.recuentos[fecha]) {
        delete estado.recuentos[fecha];
        const podado = podar(estado, zona);
        await escribir(podado);
        return { status: 200, body: { ok: true, recuentos: podado.recuentos } };
      }
      return { status: 200, body: { ok: true, recuentos: estado.recuentos || {} } };
    }

    /* -------- borrar el pan de un día */
    if (ruta.endsWith('/tahona-borrar') && metodo === 'POST') {
      const fecha = String((cuerpo && cuerpo.fecha) || '');
      if (!/^\d{4}-\d{2}-\d{2}$/.test(fecha)) {
        return { status: 400, body: { ok: false, error: 'fecha no válida' } };
      }
      const estado = await leer();
      if (estado.tahona && estado.tahona[fecha]) {
        delete estado.tahona[fecha];
        const podado = podar(estado, zona);
        await escribir(podado);
        return { status: 200, body: { ok: true, tahona: podado.tahona } };
      }
      return { status: 200, body: { ok: true, tahona: estado.tahona || {} } };
    }

    /* -------- el pan de la tahona: entrada por la mañana, devolución por la noche */
    if (ruta.endsWith('/tahona') && metodo === 'POST') {
      if (!cuerpo) return { status: 400, body: { ok: false, error: 'faltan los datos' } };
      const fecha = String(cuerpo.fecha || '');
      if (!/^\d{4}-\d{2}-\d{2}$/.test(fecha)) {
        return { status: 400, body: { ok: false, error: 'fecha no válida' } };
      }
      if (!marca) return { status: 400, body: { ok: false, error: 'falta quién lo apunta' } };
      const cual = cuerpo.cual === 'devolucion' ? 'devolucion' : 'entrada';
      const PANES = ['txapata', 'txapatita', 'barra', 'cuarto', 'txoripan'];
      const v = cuerpo.valores || {};
      const num = (x) => {
        if (x === '' || x === null || x === undefined) return null;
        const n = Number(x);
        return Number.isFinite(n) && n >= 0 ? Math.round(n * 100) / 100 : null;
      };
      const limpio = {};
      for (const pan of PANES) limpio[pan] = num(v[pan]);
      const estado = await leer();
      if (!estado.tahona) estado.tahona = {};
      const dia = estado.tahona[fecha] || {};
      dia[cual] = limpio;
      dia.q = marca; dia.h = hora;
      estado.tahona[fecha] = dia;
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, version: podado.version,
                                    tahona: podado.tahona } };
    }

    /* -------- cambiar el texto o la nota de una tarea del guion */
    if (ruta.endsWith('/plantilla') && metodo === 'POST') {
      const c = cuerpo || {};
      const clave = String(c.clave || '')
        .toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
        .replace(/\s+/g, ' ').trim().slice(0, 120);
      if (!clave) return { status: 400, body: { ok: false, error: 'falta la tarea' } };
      const estado = await leer();
      if (!estado.plantilla) estado.plantilla = {};
      const t2 = String(c.t || '').trim().slice(0, 300);
      const n2 = c.n === undefined ? undefined : String(c.n || '').trim().slice(0, 300);
      if (!t2) {
        delete estado.plantilla[clave];
      } else {
        const antes = estado.plantilla[clave] || {};
        estado.plantilla[clave] = {
          t: t2,
          n: n2 === undefined ? (antes.n || null) : (n2 || null),
          q: marca, h: hora
        };
      }
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, plantilla: podado.plantilla } };
    }

    /* -------- modificar una tarea extra ya creada */
    if (ruta.endsWith('/encargo-editar') && metodo === 'POST') {
      const c = cuerpo || {};
      if (!c.id) return { status: 400, body: { ok: false, error: 'falta el id' } };
      const estado = await leer();
      const e = estado.encargos.find(x => String(x.id) === String(c.id));
      if (!e) return { status: 404, body: { ok: false, error: 'no existe esa tarea' } };
      if (c.t !== undefined) {
        const txt = String(c.t || '').trim().slice(0, 300);
        if (txt) e.t = txt;
      }
      if (c.p !== undefined && ['tienda', 'coordinacion', 'gerencia'].includes(c.p)) e.p = c.p;
      if (c.turno !== undefined) e.turno = ['manana', 'tarde'].includes(c.turno) ? c.turno : null;
      if (c.tipo !== undefined) {
        e.tipo = ['extra', 'urgente', 'arreglar', 'llamada'].includes(c.tipo) ? c.tipo : 'extra';
      }
      if (c.f !== undefined && /^\d{4}-\d{2}-\d{2}$/.test(String(c.f))) e.f = String(c.f);
      if (c.motivo !== undefined) e.motivo = String(c.motivo || '').slice(0, 200) || null;
      e.qEditado = marca; e.hEditado = hora;
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, encargos: podado.encargos } };
    }

    /* -------- la respuesta de una llamada (y cuándo se llamó) */
    if (ruta.endsWith('/encargo-respuesta') && metodo === 'POST') {
      const c = cuerpo || {};
      if (!c.id) return { status: 400, body: { ok: false, error: 'falta el id' } };
      const estado = await leer();
      const e = estado.encargos.find(x => String(x.id) === String(c.id));
      if (!e) return { status: 404, body: { ok: false, error: 'no existe esa tarea' } };
      if (c.llamado === true && !e.llamadoEn) { e.llamadoEn = hora; }
      if (c.respuesta !== undefined) {
        e.respuesta = String(c.respuesta || '').slice(0, 500) || null;
        e.qRespuesta = marca; e.hRespuesta = hora;
      }
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, encargos: podado.encargos } };
    }

    /* -------- mover una tarea extra a otro día (o dejarla sin día) */
    if (ruta.endsWith('/encargo-mover') && metodo === 'POST') {
      if (!cuerpo || !cuerpo.id) {
        return { status: 400, body: { ok: false, error: 'falta el id' } };
      }
      const estado = await leer();
      const e = estado.encargos.find(x => String(x.id) === String(cuerpo.id));
      if (!e) return { status: 404, body: { ok: false, error: 'no existe esa tarea' } };
      const f = cuerpo.f;
      if (f && !/^\d{4}-\d{2}-\d{2}$/.test(String(f))) {
        return { status: 400, body: { ok: false, error: 'fecha no válida' } };
      }
      e.f = f ? String(f) : null;
      e.diario = false;
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, version: podado.version,
                                    encargos: podado.encargos } };
    }

    /* -------- añadir una nota al calendario */
    if (ruta.endsWith('/nota') && metodo === 'POST') {
      if (!cuerpo) return { status: 400, body: { ok: false, error: 'falta la nota' } };
      const fecha = String(cuerpo.fecha || '');
      const texto = String(cuerpo.texto || '').trim().slice(0, 500);
      const ambito = cuerpo.ambito === 'general' ? 'general' : 'personal';
      if (!/^\d{4}-\d{2}-\d{2}$/.test(fecha)) {
        return { status: 400, body: { ok: false, error: 'fecha no válida' } };
      }
      if (!texto) return { status: 400, body: { ok: false, error: 'la nota está vacía' } };
      if (!marca) return { status: 400, body: { ok: false, error: 'falta quién la escribe' } };

      const estado = await leer();
      if (!estado.notas[fecha]) estado.notas[fecha] = [];
      const nota = {
        id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
        q: marca, t: texto, a: ambito, h: hora
      };
      estado.notas[fecha].push(nota);
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, version: podado.version, nota: nota,
                                    notas: podado.notas } };
    }

    /* -------- borrar una nota */
    if (ruta.endsWith('/nota-borrar') && metodo === 'POST') {
      if (!cuerpo || !cuerpo.id) {
        return { status: 400, body: { ok: false, error: 'falta el id' } };
      }
      const estado = await leer();
      let borrada = 0;
      for (const f of Object.keys(estado.notas)) {
        const antes = estado.notas[f].length;
        estado.notas[f] = estado.notas[f].filter(n => n.id !== String(cuerpo.id));
        if (estado.notas[f].length !== antes) { borrada = 1; }
        if (!estado.notas[f].length) delete estado.notas[f];
      }
      if (borrada) await escribir(podar(estado, zona));
      return { status: 200, body: { ok: true, borrada: borrada,
                                    notas: podar(estado, zona).notas } };
    }

    /* -------- pasar una tarea a otro día (o dejarla sin día) */
    if (ruta.endsWith('/trasladar') && metodo === 'POST') {
      if (!cuerpo || !cuerpo.clave) {
        return { status: 400, body: { ok: false, error: 'falta la clave' } };
      }
      if (!/^\d{4}-\d{2}-\d{2}\|/.test(String(cuerpo.clave))) {
        return { status: 400, body: { ok: false, error: 'la clave tiene que llevar fecha' } };
      }
      const estado = await leer();
      const k = String(cuerpo.clave);
      const d = cuerpo.destino;
      /* la app manda la fecha suelta; antes solo se aceptaba un objeto,
         así que «pasar a otro día» no funcionaba y no daba la cara. */
      const esFecha = (x) => /^\d{4}-\d{2}-\d{2}$/.test(String(x || ''));
      if (!d) {
        delete estado.traslados[k];            /* se deja como estaba: sin día */
      } else if (esFecha(d)) {
        estado.traslados[k] = { f: String(d) };
      } else if (d.proxima) {
        estado.traslados[k] = { proxima: true, q: marca || String(d.q || '') };
      } else {
        if (!esFecha(d.f)) {
          return { status: 400, body: { ok: false, error: 'fecha de destino no válida' } };
        }
        const t = String(d.t || '').slice(0, 12);
        estado.traslados[k] = t ? { f: String(d.f), t: t } : { f: String(d.f) };
      }
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: {
        ok: true, version: podado.version, traslados: podado.traslados
      }};
    }

    /* -------- guardar marcas */
    if (ruta.endsWith('/marcas') && metodo === 'POST') {
      if (!cuerpo || !cuerpo.cambios) {
        return { status: 400, body: { ok: false, error: 'faltan los cambios' } };
      }
      const estado = await leer();
      const n = aplicar(estado, cuerpo.cambios, marca, hora);
      const podado = podar(estado, zona);
      if (n > 0) await escribir(podado);
      return { status: 200, body: {
        ok: true, aplicados: n, version: podado.version, hora: hora
      }};
    }

    /* -------- fichar: entrar o salir */
    if (ruta.endsWith('/fichar') && metodo === 'POST') {
      if (!cuerpo || !cuerpo.quien || !cuerpo.puesto) {
        return { status: 400, body: { ok: false, error: 'falta quién o el puesto' } };
      }
      const estado = await leer();
      const q = String(cuerpo.quien).slice(0, 20);
      const p = String(cuerpo.puesto).slice(0, 20);
      /* ¿tenía un fichaje abierto de hoy? */
      const abierto = estado.fichajes.find(f => f.q === q && f.dia === dia && !f.s);
      if (cuerpo.salir) {
        if (abierto) { abierto.s = hora; await escribir(podar(estado, zona)); }
        return { status: 200, body: { ok: true, salida: hora } };
      }
      if (abierto) {
        return { status: 200, body: { ok: true, yaEstaba: true, entrada: abierto.e } };
      }
      estado.fichajes.push({ q: q, p: p, e: hora, s: null, dia: dia });
      await escribir(podar(estado, zona));
      return { status: 200, body: { ok: true, entrada: hora, dia: dia } };
    }

    /* -------- entrar en gerencia: la clave se comprueba AQUÍ, no en el móvil */
    if (ruta.endsWith('/entrar') && metodo === 'POST') {
      const esperado = String(opciones.pinGerencia || '');
      if (!esperado) {
        return { status: 503, body: { ok: false,
          error: 'gerencia no está configurada' } };
      }
      const dado = String((cuerpo && cuerpo.pin) || '').trim();
      /* comparación de tiempo constante, para no filtrar por el tiempo */
      const a = Buffer.from(dado.padEnd(esperado.length, ' ').slice(0, esperado.length));
      const b = Buffer.from(esperado);
      const igual = a.length === b.length && require('node:crypto').timingSafeEqual(a, b);
      if (!igual) {
        return { status: 401, body: { ok: false, error: 'clave incorrecta' } };
      }
      return { status: 200, body: { ok: true, puesto: 'gerencia' } };
    }

    /* -------- olvidar un fichaje concreto (para las pruebas y los errores) */
    if (ruta.endsWith('/olvidar') && metodo === 'POST') {
      if (!cuerpo || !cuerpo.fichaje) {
        return { status: 400, body: { ok: false, error: 'falta el fichaje' } };
      }
      const f = cuerpo.fichaje;
      const estado = await leer();
      const antes = estado.fichajes.length;
      estado.fichajes = estado.fichajes.filter(x =>
        !(x.q === f.q && x.dia === f.dia && x.e === f.e));
      const n = antes - estado.fichajes.length;
      if (n) await escribir(podar(estado, zona));
      return { status: 200, body: { ok: true, borrados: n } };
    }

    /* -------- quién tengo delante */
    if (ruta.endsWith('/estado-fichajes') && metodo === 'GET') {
      const estado = podar(await leer(), zona);
      return { status: 200, body: { ok: true, dia: dia, fichajes: estado.fichajes } };
    }

    return { status: 404, body: { ok: false, error: 'no existe: ' + metodo + ' ' + ruta } };
  };
}

module.exports = { crearManejador, estadoVacio, podar, hoyISO, horaLocal };
