# EMPIEZA AQUÍ · lo primero que hay que leer al volver

> **Actualizado:** final del **28 de octubre de 2026**.
> **Lo primero que hay que abrir.** Si algo se quedó a medias, está aquí.

---

## 1 · Dónde está la aplicación

```
https://app.supermalato.workers.dev        versión  v-2026-10-26-77
```

**Clave de la Jefa**: `«la clave de la Jefa — se dice aparte, no se escribe»` — **y ahora dura hasta las 15:00** (D-294).

**Copia de seguridad**: `COPIA-APP-MALATO-*.zip` en el proyecto, en OneDrive y en **Documentación**.

---

## 2 · Lo que funciona hoy, probado

| | |
|---|---|
| **Menú de botones con dibujos** | en tienda, coordinación **y la Jefa** — los avisos arriba y «◀ Menú» para volver |
| **Bloques plegados** | solo el título y «3 de 12» · **se puede entrar aunque esté terminado** |
| **Calendario** | con **📦 Encargos · 📞 Llamadas · ✏️ Tareas · 🔗 Cascadas** |
| **Llamadas** | 31 proveedores · 59 teléfonos · **por letras** · **respuesta obligatoria antes de tachar** |
| **Cascadas** | **saltan en el servidor** al tachar · se montan en cualquier tarea · **lista para verlas y quitarlas** |
| **Tareas extra** | tres tipos · **se marcan, se destachan, se pasan de día** · **pendientes y terminadas** · **✎ modificar y ✎ cambiar el guion** |
| **Avisos de guardado** | **todo lo que se guarda avisa con un cartel** |
| **Tahona** | cinco panes · entrada en apertura · devolución en el cierre |
| **Informe del pan** | rango de fechas · corregir un día · WhatsApp · resumen y detalle |
| **Visto bueno del recuento** | tienda apunta · coordinación aprueba o corrige |
| **Para arreglar** | como una tarea más |

---

## 3 · Lo que está a medias y lo que falta

### Lo que queda de las cascadas

| | |
|---|---|
| **Mover tareas entre puestos desde la app** | **hoy se hace a mano en el guion** |
| **El ✎ en las tareas de la Jefa** | las de tienda y coordinación ya se cambian |

### Lo siguiente, por orden

| # | Qué | Nota |
|---|---|---|
| **1** | **El puesto «Cocina»** | **D-291 y D-295**: puesto propio, **no** sección de coordinación. Login, clave, menú y el botón **🔥 Instrucciones del asador** |
| **2** | **Mover tareas entre puestos** | desde la app, con prueba de que sale de uno y entra en otro |
| **3** | **La cocinera** | sus tareas — **falta que las dicte la propiedad** |
| **4** | **Gerencia: verlo todo con registros** | **D-288**: quién, cuándo, cómo. **Los datos ya se guardan**; falta la pantalla |
| **5** | **Productos y utillaje** | **D-280**, aparcado: AL28 y Fairy, cuándo se rellenan y su histórico |
| **6** | **Precios de la Tahona** | cuando lleguen: importe en el informe |
| **7** | **El dominio** | falta saber la extensión (`.com`, `.es`) |
| **8** | **«Mi turno»** en la ficha de cada una | |

---

## 4 · El asador: los documentos están hechos

**En `docs/asador/`**, un documento por producto, **con las palabras de la propiedad**:

| | | Tiempo |
|---|---|---|
| **🍗 Pollo** | `pollo.md` | 2,5 horas |
| **🍖 Codillo** | `codillo.md` | 2 horas |
| **🥩 Costilla** | `costilla.md` | 2 horas + 1 de reposo · **dos opciones** |
| **🍟 Patatas fritas** | `patatas-fritas.md` | 30 min antes · **SIN GLUTEN** |

**No hay que rehacerlos.** **Solo hay que enseñarlos cuando exista el puesto de cocina.**

---

## 5 · El Excel de las tareas

**`TAREAS-APP-MALATO.xlsx`** — **220 tareas**: Tienda 120 · Coordinación 86 · Jefa 14.

**Con columnas vacías para que la propiedad marque** cuáles son cascada y a qué puesto va el siguiente.

**Se genera solo**: `python .tools\excel-tareas.py`

---

## 6 · Las normas que han salido de los fallos

**Están en `DECISIONES.md`. Las que más han costado:**

> **D-275 · La orden va DENTRO del control.** Si un botón se pinta en varias pantallas, lleva su `onclick` propio.
> **Y ojo con los DOBLES**: un botón con dos manejadores **se anula a sí mismo**.

> **D-276 · Las pruebas NO escriben en días reales.** Fechas de mentira (2099) y **borrar, no poner ceros**.

> **Ojo con los nombres.** Tres fallos en un día por poner un nombre que ya existía:
> **`clave`** (tapaba una función) · **`quien`** (se tapaba a sí misma) · **`quiénCorta`** (con tilde).
> **Antes de poner un nombre, mirar si existe. Y los nombres de variable, distintos de los de función.**

> **Si algo se pinta en una pantalla, comprobar que se pinta en TODAS.** El panel de modificar no se pintaba
> ni en la Jefa ni en «Tareas extra» — **y los botones parecían muertos**.

> **Probar el camino completo, no la lógica.** Lo que falló cuatro veces con las tareas extra no era la función:
> era **el botón que abría el formulario**.

---

## 7 · Las pruebas que hay

```powershell
node .tools\probar-clic-tarea.mjs        # SIMULA EL CLIC: la que caza los botones muertos
node .tools\probar-cascadas.mjs          # el motor de las cascadas
node .tools\probar-cascadas-sembradas.mjs
node .tools\probar-cascada-entera.mjs
node .tools\probar-llamadas.mjs
node .tools\probar-letras.mjs
node .tools\probar-menu.mjs
node .tools\probar-volver.mjs
node .tools\probar-bloque-abierto.mjs    # que un bloque cerrado NO enseñe las tareas
node .tools\probar-plegables.mjs
node .tools\probar-modificar.mjs
node .tools\probar-extra-urgente.mjs
node .tools\probar-tahona.mjs
node .tools\probar-informe-rango.mjs
node .tools\probar-detalle.mjs
node .tools\probar-cloudflare.mjs
node docs\nube\prueba-nucleo.mjs
```

**Si algo se rompe, empezar por `probar-clic-tarea.mjs`.**

---

## 8 · Cómo se publica

```powershell
python .tools\generar-nube.py
cd .tools
$env:CLOUDFLARE_API_TOKEN = "..."
node node_modules\wrangler\bin\wrangler.js deploy --config "..\docs\nube\wrangler.toml"
```

**Y después, comprobar en la dirección con un `?t=<hora>`** — **el borde de Cloudflare tarda unos segundos en servir la versión nueva.**
