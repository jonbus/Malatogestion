# Hoja de depuración

> **Para qué sirve este documento.** Cuando algo falle en la aplicación, **no se toca nada a ciegas**:
> se sigue esta hoja, en este orden, hasta dar con la causa. **Y se anota lo que se aprende.**

---

## 0 · Lo primero, siempre: la marca de versión

**Abajo del todo de la app** hay una marca: `v-2026-10-23-18`.

| Qué pasa | Qué significa |
|---|---|
| **No veo la marca** | Estás viendo **una copia guardada**. Cierra la pestaña y vuelve a abrir. **No es un fallo de la app** |
| **La marca es vieja** | El cambio no ha llegado. **Mira si el túnel o el servidor están vivos** |
| **La marca es la buena y falla** | **Ahora sí: hay un fallo de verdad** |

> **Sin este paso se pierden horas persiguiendo fallos que no existen.** Ya nos ha pasado.

---

## 1 · Sale el cartel rojo

**La app avisa sola.** Copia el texto y busca la línea.

| Lo que dice | Dónde mirar |
|---|---|
| `X is not defined` | Se llama a una función que **no existe**. Es el fallo de `enganchar()` — ya nos costó dos vueltas |
| `Cannot read properties of null` | Se busca un elemento de la pantalla que **no está**: alguien cambió el HTML y no el código |
| `Failed to fetch` | **No hay conexión con el servidor.** Paso 2 |
| `HTTP 400` / `401` / `404` | El servidor **rechaza** lo que se le manda. Paso 3 |

---

## 2 · La app no abre o no carga

**Se comprueba de dentro hacia fuera. Siempre en este orden:**

```
1. ¿Responde el servidor?      http://127.0.0.1:8100/api/estado
2. ¿Responde por el túnel?     la dirección publicada
3. ¿Está el túnel vivo?        el proceso cloudflared
```

| Falla en | Entonces |
|---|---|
| **1** | El servidor está parado. Se levanta: `node docs/nube/servidor-local.mjs 8100` |
| **2** | **El túnel se ha caído.** Se levanta otro **y cambia la dirección** |
| **3** | Igual: el túnel murió |

> **El túnel sin cuenta de Cloudflare se cae solo.** Su propia documentación lo dice: *«sin garantía de continuidad»*. **Es la causa más frecuente de «no me abre».**

---

## 3 · El servidor responde con error

**La regla de oro: comparar lo que la app manda con lo que el servidor espera.**

```
app:      fetch("/api/nota", { body: { quien, fecha, texto, ambito } })
servidor: ruta.endsWith('/nota')  →  lee cuerpo.fecha, cuerpo.texto…
```

| Error | Qué comprobar |
|---|---|
| `no existe: POST /api/X` | **La ruta no está en el núcleo.** O el nombre está mal escrito (`/api/marcar` vs `/api/marcas`) |
| `falta la clave` | El cuerpo llega vacío: mira si el `fetch` envía `Content-Type` |
| `la clave tiene que llevar fecha` | Las claves de tarea son `día\|puesto\|clave`. **Sin fecha no valen** |
| `fecha de destino no válida` | **Ojo**: el traslado espera un **objeto** `{f}` o `{proxima}`, **no una fecha suelta** |
| `401` | La clave de la Jefa. **Se comprueba con `/api/entrar`** |

---

## 4 · Se ve, pero no responde al pulsar

**Este es el fallo más traicionero: no da error, simplemente no hace nada.**

| Causa | Cómo se descarta |
|---|---|
| **No hay escuchador de clic** | Debe haber **un solo** escuchador sobre `#cuerpo` (delegado). Si hay uno por tarea, **se pierde al repintar** |
| **El elemento no tiene `data-k`** | Sin clave, el clic no sabe qué marcar |
| **La función de marcar falla en silencio** | Abre la consola: `tocar("clave", true)` y mira si la marca aparece |
| **El guardado falla y nadie lo dice** | Mira la respuesta de `/api/marcas` |

> **Norma**: **todo clic tiene que producir algo visible** — una marca, un aviso, o un error. **Si no produce nada, es un fallo.**

---

## 5 · Los datos no cuadran

**Las tres fuentes de verdad, y en qué orden manda cada una:**

| Dato | Manda |
|---|---|
| **Turnos** | `docs/referencia/PlantillasHorarios.xlsx` — **la plantilla** |
| **Horas y contratos** | `docs/RRHH-TURNOS.md` |
| **Tareas** | `docs/momentos/*.md` y los generadores `.tools/generar-*.py` |

**Nunca se deduce lo que ya está escrito.** Antes de concluir algo de un momento del día, **se mira lo que ya está documentado**. Es la norma que salió de E-9.

---

## 6 · Antes de dar algo por arreglado

```
☐ ¿La marca de versión es la nueva?
☐ ¿He probado los CINCO perfiles? (Tienda ×3, Coordinación ×2, Jefa)
☐ ¿He probado el día de hoy Y otro día?
☐ ¿He probado un domingo o un festivo?
☐ ¿Sale algo en el cartel rojo?
☐ ¿He dejado datos de prueba? (limpiarlos)
☐ ¿Está la copia de seguridad al día?
```

---

## 7 · Las pruebas que ya existen

| Comando | Qué comprueba |
|---|---|
| `node .tools\prueba-usuario-completa.mjs` | **Los cinco perfiles y todas las funciones** |
| `node .tools\probar-turnos-reales.mjs` | Turnos contra la plantilla |
| `node docs\nube\prueba-nucleo.mjs` | El servidor por dentro |
| `node .tools\probar-funciones.mjs` | **Llamadas a funciones que no existen** |
| `node tools\check-boundaries.mjs` | Las reglas de arquitectura |
| `node node_modules\typescript\bin\tsc -p tsconfig.json` | Los tipos |

---

## 8 · Los fallos que ya nos han costado tiempo

**Se apuntan aquí para no repetirlos.**

| Fallo | Qué pasó | Lo que lo habría cazado |
|---|---|---|
| **`enganchar()` no existía** | La pantalla de la Jefa se cortaba **en silencio** | El cartel rojo · la prueba de funciones |
| **El nombre de la Jefa** | Dos ternarios con solo dos casos: **la Jefa caía en «Coordinadora»** | **Probar el perfil de la Jefa**, no solo Tienda |
| **El logo blanco sobre caja blanca** | Invisible | Mirar la pantalla, no el código |
| **El pie de página inexistente** | Puse la versión en un `<footer>` que **no existía**, y no dio error | Comprobar que el elemento está |
| **El servidor local sin clave** | La Jefa no podía entrar; **no era la contraseña** | Probar la entrada de verdad |
| **«Los lunes» todos los días** | Los bloques no preguntaban qué día era | **Probar en un día que no fuera lunes** |
| **Mi prueba con rutas inventadas** | `/api/marcar` en vez de `/api/marcas` | **Leer lo que manda la app**, no suponerlo |
| **`origenDe()` no existía** | El clic reventaba en su primera línea: **no marcaba nada** | **El cartel rojo** — lo cazó la propiedad, no yo |
| **El menú «¿Para cuándo lo pasas?»** | Se abría y **no pasaba nada al elegir**. Buscaba la tarea en `ARR[k]` al pulsar; si esa búsqueda fallaba, hacía `return` **en silencio** | **Prueba que genera el menú y comprueba que cada botón lleva su destino** |
| **Los sub-pasos de la Jefa** | *«0 / 4 partes»* y **no se podía marcar ninguno**. Se enganchaban dentro de `pinta()`, y **la pantalla de la Jefa sale antes de llegar ahí** | **Probar el mismo control con los TRES perfiles**, no solo con uno |

> **El patrón de casi todos**: **suponer en vez de comprobar.** Y el de los peores: **que el fallo no se vea.**

### La norma que sale del menú de pasar

> **Un `return` sin aviso es un fallo disfrazado.** Si una orden no se puede ejecutar,
> **se dice en pantalla**. Nunca se vuelve en silencio.
>
> **Y los datos que necesita un botón, que los lleve el botón** — no que los busque
> después en una tabla que puede haber cambiado.

### Y la que sale de los sub-pasos

> **Si algo se engancha dentro de una función que solo corre para unos perfiles,**
> **los demás se quedan con botones muertos.** Todo lo que se pulsa va al **escuchador
> delegado**, que vale para todos.
>
> **Y al probar un control, se prueba con los tres perfiles.** Tienda funcionando
> no significa que la Jefa funcione.

---

## 9 · Y la norma que resume la hoja

> **Un fallo que se ve, se arregla.**
> **Un fallo callado se queda meses.**
