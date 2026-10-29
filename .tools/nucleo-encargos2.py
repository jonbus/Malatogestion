"""Tareas extra: tipo (extra/urgente) y poder moverlas a otro día."""
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


# 1 · el encargo guarda si es extra o urgente
cambia("""        turno: ['manana','tarde'].includes(c.turno) ? c.turno : null,""",
       """        turno: ['manana','tarde'].includes(c.turno) ? c.turno : null,
        /* extra = cuando se pueda · urgente = hoy y ya */
        tipo: c.tipo === 'urgente' ? 'urgente' : 'extra',""",
       "el encargo guarda el tipo")

# 2 · endpoint para mover un encargo de día
cambia("    /* -------- añadir una nota al calendario */",
       """    /* -------- mover una tarea extra a otro día (o dejarla sin día) */
    if (ruta.endsWith('/encargo-mover') && metodo === 'POST') {
      if (!cuerpo || !cuerpo.id) {
        return { status: 400, body: { ok: false, error: 'falta el id' } };
      }
      const estado = await leer();
      const e = estado.encargos.find(x => String(x.id) === String(cuerpo.id));
      if (!e) return { status: 404, body: { ok: false, error: 'no existe esa tarea' } };
      const f = cuerpo.f;
      if (f && !/^\\d{4}-\\d{2}-\\d{2}$/.test(String(f))) {
        return { status: 400, body: { ok: false, error: 'fecha no válida' } };
      }
      e.f = f ? String(f) : null;
      e.diario = false;
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, version: podado.version,
                                    encargos: podado.encargos } };
    }

    /* -------- añadir una nota al calendario */""",
       "endpoint para mover una tarea extra")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
