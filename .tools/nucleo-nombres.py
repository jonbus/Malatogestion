"""La memoria de los nombres: lo que se escribe una vez se ofrece después.

Se guardan SOLO los nombres, sin fechas ni cantidades, y no caducan.
Así las sugerencias no se pierden cuando se limpian las tareas viejas.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"docs/nube/netlify/functions/nucleo.js"
t = open(p, encoding="utf-8").read()
fallos = 0


def cambia(viejo, nuevo, etiqueta):
    global t, fallos
    if viejo not in t:
        print(f"   NO ENCONTRADO: {etiqueta}")
        fallos += 1
        return
    t = t.replace(viejo, nuevo, 1)
    print(f"   ok  {etiqueta}")


# ---------------------------------------------------------------- 1 · el estado
cambia("encargosFecha: [], cascadas: {} };",
       "encargosFecha: [], cascadas: {}, nombres: [] };",
       "estadoVacio con nombres")

cambia("""      cascadas: guardado.cascadas && typeof guardado.cascadas === 'object'
        ? guardado.cascadas : {}""",
       """      cascadas: guardado.cascadas && typeof guardado.cascadas === 'object'
        ? guardado.cascadas : {},
      /* la memoria de los nombres: no caduca nunca */
      nombres: Array.isArray(guardado.nombres) ? guardado.nombres : []""",
       "leer devuelve nombres")

cambia("    cascadas: estado.cascadas || {},",
       "    cascadas: estado.cascadas || {},\n    nombres: estado.nombres || [],",
       "podar conserva nombres")

cambia("        cascadas: estado.cascadas",
       "        cascadas: estado.cascadas, nombres: estado.nombres",
       "el estado los devuelve")

# ---------------------------------------------------------------- 2 · se apunta cada nombre
cambia("""      estado.encargos.push(c);""",
       """      /* la memoria de los nombres: se apunta el texto, sin fechas ni cantidades */
      estado.nombres = estado.nombres || [];
      if (!estado.nombres.includes(c.t)) {
        estado.nombres.push(c.t);
        if (estado.nombres.length > 500) estado.nombres.shift();
      }
      estado.encargos.push(c);""",
       "cada tarea nueva apunta su nombre")

# ---------------------------------------------------------------- 3 · las sugerencias
cambia("    /* -------- las cascadas: una tarea que, al hacerse, hace nacer la siguiente */",
       """    /* -------- sugerencias: lo que ya se ha escrito alguna vez */
    if (ruta.endsWith('/sugerencias') && metodo === 'POST') {
      const busca = String((cuerpo && cuerpo.q) || '')
        .toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').trim();
      const estado = await leer();
      const todos = estado.nombres || [];
      let salida;
      if (!busca) {
        salida = todos.slice(-12).reverse();
      } else {
        salida = todos
          .filter(n => n.toLowerCase().normalize('NFD')
            .replace(/[\\u0300-\\u036f]/g, '').includes(busca))
          .slice(-12);
      }
      return { status: 200, body: { ok: true, sugerencias: salida } };
    }

    /* -------- las cascadas: una tarea que, al hacerse, hace nacer la siguiente */""",
       "el endpoint de sugerencias")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
