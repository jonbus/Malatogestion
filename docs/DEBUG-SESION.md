# Sesión de depuración · 23 de octubre de 2026

> **Encargo**: depurar los tres perfiles (Tienda, Coordinadora, Jefa), comprobar que las
> **tareas en cascada** se ejecutan correctamente y dejar constancia de lo hecho.

---

## 0 · Resumen en una tabla

| # | Qué se ha hecho | Resultado |
|---|---|---|
| 1 | Reproducir el error reportado al entrar como **coordinadora** | **Causa encontrada**: el fichero servido tenía `[2]` convertido en `[2][2]` |
| 2 | Comprobar la integridad del fichero generado | **0 ocurrencias** de corrupción tras regenerar |
| 3 | Verificar el **nombre de los cinco puestos** | Los cinco correctos |
| 4 | Verificar las **pestañas de cada perfil** | Correctas |
| 5 | Simular el **clic en sub-pasos** con los **tres perfiles** | Los 6 casos pasan |
| 6 | Probar la **cascada de las ofertas de principio a fin** | **10 comprobaciones, todas bien** |
| 7 | Verificar los **turnos de hoy** contra la plantilla | Correctos |
| 8 | Prueba de usuario completa | **51 comprobaciones · 0 fallos** |
| 9 | Puertas del proyecto (suites, fronteras, tipos) | 7/7 · 0 violaciones · 0 |

---

## 1 · El error reportado

```
La aplicación ha tenido un fallo
promesa: Cannot read properties of undefined (reading '2')
```

**Aparecía al abrir coordinación.** El cartel rojo lo cazó — **el sistema de aviso funcionó**.

### La causa

El fichero `docs/nube/public/index.html` que se estaba sirviendo tenía **`[2]` sustituido por `[2][2]`** en ocho sitios. Por ejemplo:

```js
const f = trozos[0], k = trozos[2][2];      // ← dos veces [2]
const wd = new Date(p[0], p[1] - 1, p[2][2]).getDay();
if(m[1] === "co") return "Coordinadora " + m[2][2];
```

**Por qué revienta solo en coordinación**: en `trozos[2][2]`, si una clave de marca no tiene tres trozos, `trozos[2]` es `undefined`, y leer `[2]` de `undefined` **lanza el error**. Con las claves de coordinación eso ocurría; con las de tienda, no.

**Y de paso**: `nombreDe` devolvía `"Coordinadora undefined"` y las fechas se construían con `undefined`.

### El arreglo

**Regenerar desde el generador.** Se comprobó que `generar-nube.py` tenía el `[2]` correcto en sus ocho apariciones — **la corrupción estaba solo en la salida**, no en el origen.

```
ocurrencias de [2][2] en la salida antes: 8
ocurrencias de [2][2] en la salida ahora: 0
```

**Y se ha añadido una comprobación permanente** que falla si vuelve a aparecer.

---

## 2 · Cómo se ha probado, y qué NO se ha podido probar

**Honestidad sobre el método**: no hay navegador disponible. **No se puede pulsar con el dedo.**

Lo que **sí** se ha hecho:

| Técnica | Qué permite comprobar |
|---|---|
| **Sacar las funciones del fichero y ejecutarlas** | La lógica exacta que corre en el móvil, con datos reales |
| **Simular el DOM** (nodos con `closest`) | Que un clic llega al manejador y hace lo que debe |
| **Llamar a la API de verdad** | El servidor, con datos reales |
| **Leer los datos incrustados** (`DATOS`) | Que cada perfil tiene lo que le toca |

Lo que **no** se ha podido comprobar: **el tacto real**, el aspecto, y el comportamiento de un navegador concreto (Safari de iOS, por ejemplo).

---

## 3 · Los tres perfiles, uno a uno

### 3.1 · El nombre y el título de cada uno

| Identificador | Debe salir |
|---|---|
| `op1` | **Tienda 1** |
| `op3` | **Tienda 3** |
| `co1` | **Coordinadora 1** |
| `co2` | **Coordinadora 2** |
| `ge1` | **Jefa** |

**Los cinco correctos.** (El de la Jefa estaba mal hasta esta tarde: caía en «Coordinadora» porque había dos ternarios con solo dos casos.)

### 3.2 · Las pestañas de cada perfil

| Perfil | Pestañas |
|---|---|
| **Tienda** | General · Mañana · Tarde · Cierre · Calendario |
| **Coordinación** | General · Apertura · El día · Cierre · Calendario |
| **Jefa** | Bandeja · General · Calendario |

**La coordinación tiene los 2 patrones de apertura (`A` y `B`)**, que es un diccionario, no una lista.

### 3.3 · El clic en los sub-pasos, con los tres perfiles

**Es la prueba que faltaba.** Se simula el mismo clic con Tienda, con Coordinación y con la Jefa:

```
OK  tienda:        el sub-paso se marca
OK  tienda:        la tarea entera responde
OK  coordinación:  el sub-paso se marca
OK  coordinación:  la tarea entera responde
OK  jefa:          el sub-paso se marca
OK  jefa:          la tarea entera responde
```

**Y se comprueba lo contrario también**: que un clic en un desplegable o en el menú de pasar **no marque la tarea sin querer**.

---

## 4 · La cascada de las ofertas, de principio a fin

**Esta es la prueba importante**: se recorre la cadena completa con datos reales, contra el servidor.

### El guion

```
1. La Jefa crea la tarea de preparar, con sus dos hijas dentro
2. SE COMPRUEBA que coordinación NO ve nada todavía
3. La Jefa marca «preparar»
4. Nacen las dos hijas
5. Coordinación recibe la suya y la marca
```

### El resultado

```
OK  la jefa crea la tarea de preparar
OK  va para hoy
OK  coordinación NO ve nada aún          ← el corazón de la cascada
OK  al marcarla nacen 2
OK  coordinación recibe la de lineales
OK  la jefa recibe la de cartelería
OK  las dos para el lunes
OK  coordinación puede marcarla
OK  y queda marcada
OK  no queda basura
```

### Por qué importa el paso 2

> **Hasta que la Jefa no marca, la tarea de coordinación NO EXISTE.**

Si las tres vivieran sueltas, un lunes alguien vería *«quitar las ofertas vencidas»* y las quitaría — **y resulta que las nuevas no estaban preparadas**. **Ahora eso no puede pasar: no hay nada que quitar hasta que hay algo que poner.**

---

## 5 · Los turnos

Contra la plantilla real (`docs/referencia/PlantillasHorarios.xlsx`):

```
OK  Tienda 2 hace mañanas                    (turno A)
OK  Tienda 3 hace tardes                     (turno B)
OK  Tienda 1 hace el fin de semana           (turno C)
OK  la Coordinadora 2 está de vacaciones     (19 al 25, la cubre la Jefa)
OK  la Coordinadora 1 trabaja hoy
```

---

## 6 · Los comandos que quedan

| Comando | Qué comprueba |
|---|---|
| `node .tools\probar-tres-perfiles.mjs` | **Los tres perfiles y la cascada completa** |
| `node .tools\prueba-usuario-completa.mjs` | 51 comprobaciones de toda la app |
| `node .tools\probar-subpasos.mjs` | El clic en los sub-pasos |
| `node .tools\probar-menu-pasar.mjs` | El menú «¿para cuándo lo pasas?» |
| `node .tools\probar-turnos-reales.mjs` | Los turnos contra la plantilla |
| `node docs\nube\prueba-nucleo.mjs` | El servidor por dentro |
| `node tools\check-boundaries.mjs` | Las reglas de arquitectura |

---

## 7 · Fallos encontrados y corregidos en esta sesión

| Fallo | Causa | Cómo se cazó |
|---|---|---|
| **`[2][2]` corrompido** | El fichero servido tenía `[2]` duplicado en 8 sitios | **El cartel rojo**, al entrar como coordinadora |
| **Sub-pasos muertos para la Jefa** | Se enganchaban dentro de `pinta()`, y esa función **sale antes** para gerencia | **La foto de la propiedad** (0/4 partes sin responder) |
| **Menú de pasar sin efecto** | Buscaba la tarea en `ARR[k]` al pulsar y hacía `return` **en silencio** | **Prueba que genera el menú y verifica cada botón** |
| **`origenDe()` no existía** | El clic reventaba en su primera línea | **El cartel rojo** |
| **La Jefa salía como «Coordinadora»** | Dos ternarios con solo dos casos | **Probar el perfil de la Jefa** |
| **El traslado a otro día no funcionaba** | La app mandaba una fecha; el servidor esperaba un objeto | **La prueba completa** |
| **Las pruebas con rutas inventadas** | `/api/marcar` en vez de `/api/marcas` | **Leer lo que manda la app** |

### El patrón

> **Casi todos son de la misma familia: enganchar algo en un sitio que no corre para todos los perfiles, o fiarse de una búsqueda que puede fallar.**
>
> **Y los peores: los que no dan la cara.**

### Las tres normas que salen de aquí

1. **Todo lo que se pulsa va al escuchador delegado** — uno solo, puesto una vez, que vale para los tres perfiles.
2. **Un `return` sin aviso es un fallo disfrazado** — si una orden no se puede ejecutar, se dice en pantalla.
3. **Al probar un control, se prueba con los tres perfiles.** Tienda funcionando no significa que la Jefa funcione.

---

## 8 · Lo que sigue abierto

| | |
|---|---|
| **El tacto real en el móvil** | Necesita un dedo. **Es lo primero que hay que confirmar** |
| **La pantalla de fichajes** | El cálculo del turno está; la pantalla no |
| **«Mi turno» en la ficha de cada una** | Acordado, sin hacer |
| **Mover pendientes entre días** | Acordado, sin hacer |
| **El túnel con nombre** | Para que la dirección no cambie |
