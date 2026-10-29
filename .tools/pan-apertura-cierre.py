"""El pan: la entrada en la apertura y la devolución en el cierre."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
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


# --- tienda: la devolución, del «tarde» al cierre
cambia('      if(tab === "tarde") html += bloqueTahona("devolucion");\n',
       '',
       "se quita la devolución de la tarde")

cambia("""    if(tab === "cierre"){
      P.forEach((s, si)=>{ html += bloque(s.sec, s.tareas, si + "_"); sumar(s.tareas, si + "_"); });
      document.getElementById("sub").textContent = "Cierre · " + NOMBRE_DIA + " " + bonito(fechaSel);""",
       """    if(tab === "cierre"){
      P.forEach((s, si)=>{ html += bloque(s.sec, s.tareas, si + "_"); sumar(s.tareas, si + "_"); });
      html += bloqueTahona("devolucion");        /* el pan que se devuelve */
      document.getElementById("sub").textContent = "Cierre · " + NOMBRE_DIA + " " + bonito(fechaSel);""",
       "la devolución va al cierre de tienda")

# --- coordinación: la entrada, del «día» a la apertura
cambia('      html += bloqueTahona("entrada");\n',
       '',
       "se quita la entrada del día")

cambia("""      P.bloques.forEach((b, bi)=>{ html += bloque(b.sec, b.tareas, patron + bi + "_");
                                    sumar(b.tareas, patron + bi + "_"); });
      document.getElementById("sub").textContent = "Apertura · " + P.nombre;""",
       """      P.bloques.forEach((b, bi)=>{ html += bloque(b.sec, b.tareas, patron + bi + "_");
                                    sumar(b.tareas, patron + bi + "_"); });
      html += bloqueTahona("entrada");            /* el pan que llega */
      document.getElementById("sub").textContent = "Apertura · " + P.nombre;""",
       "la entrada va a la apertura")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
