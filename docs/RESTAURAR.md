# Cómo rehacerlo todo desde cero

> **Copia de seguridad del proyecto · 21 de octubre de 2026.**
>
> Si mañana el ordenador se rompe, se borra la carpeta o alguien toca lo que no debe, **con este
> documento y el fichero `.zip` que va al lado se vuelve a montar todo.**
>
> Léelo de arriba abajo antes de tocar nada. **No hace falta recordar nada**: todo lo que hay está
> escrito en `docs/`.

---

## 0 · Dónde están las copias

**Hay tres, y son idénticas** (comprobado por huella):

| # | Dónde | Por qué |
|---|---|---|
| 1 | **`OneDrive\COPIA-APP-MALATO\`** | **La buena.** Se sincroniza sola a la nube: sobrevive a que se rompa el ordenador |
| 2 | **`Desktop\APP Malato Documentación\COPIA-APP-MALATO\`** | En la carpeta de siempre, a mano |
| 3 | `Desktop\APP Malato\` | Una más, dentro del proyecto |

**Nombre:** `COPIA-APP-MALATO-AAAA-MM-DD_HHMM.zip` · **1,68 MB**

> **Si hay que rehacerlo todo, se usa la del OneDrive.** Las otras dos son por comodidad.
>
> **Y se ha probado:** se descomprimió en una carpeta limpia y **las pantallas se regeneraron
> enteras** solo con lo que va dentro. No es una copia que «debería» servir: **se comprobó**.

---

## 1 · Qué es este proyecto, en cinco líneas

**Una aplicación de gestión para un supermercado de barrio**, hecha a medida, con **tres puestos**:
**Gerencia**, **Coordinación** y **Tienda**. Lo que hoy está terminado y funcionando es:

- **El catálogo de tareas de los tres puestos** — dictado por la propiedad.
- **Dos pantallas** (tienda y coordinación) que se pueden abrir y marcar.
- **Una aplicación publicada en internet** que guarda lo que se marca.

**No hay que leer nada más para empezar.** Pero si se va a seguir trabajando, **hay que leer
[MANUAL.md](MANUAL.md) entero** (sobre todo el registro de sesiones y los errores ya cometidos).

---

## 2 · Qué hay dentro de la copia

| Carpeta | Qué es | ¿Hace falta para rehacer? |
|---|---|---|
| **`docs/`** | **Todo el conocimiento del proyecto.** Decisiones, manual, tareas, RRHH, pedidos, calendario, los momentos de cada puesto, el logotipo y **la aplicación de la nube** | **Sí. Es lo más importante** |
| **`.tools/`** *(solo los `.py` y `.ps1`)* | **Los generadores**: convierten los datos en las pantallas y en el Excel | **Sí.** Sin ellos hay que rehacer las pantallas a mano |
| **`tools/`** | Comprobador de fronteras y lanzador de pruebas | Sí |
| **`tests/`** | Las 7 suites, 42 pruebas | Sí |
| **`apps/`, `packages/`, `db/`** | El código del núcleo (monolito modular) y el esquema SQL | Sí |
| **`package.json`, `tsconfig.json`, `pnpm-workspace.yaml`** | Configuración | Sí |

**Lo que NO va en la copia, porque se reinstala solo:**

- `.tools/cli` (214 MB) — el CLI de Netlify, se reinstala con un comando
- `.npmcache` (280 MB) — caché de npm
- `node_modules` — dependencias
- `.tools/webprobe`, `pdfprobe`, `nestprobe`, `pglite` — herramientas de sondeo

---

## 3 · Restaurar, paso a paso

### 3.1 · Descomprimir

Descomprimir el `.zip` en `C:\Users\Usuario\Desktop\APP Malato`.

Debe quedar esta forma:

```
APP Malato/
  docs/            <-  todos los documentos
  .tools/          <-  los generadores
  tools/  tests/  apps/  packages/  db/
  package.json  tsconfig.json  README.md
```

### 3.2 · Comprobar que el proyecto sigue entero

```powershell
# dependencias del núcleo
npm install

# las 7 suites de pruebas (deben pasar las 42)
foreach ($x in Get-ChildItem tests\*.test.ts) { node $x.FullName }

# fronteras entre módulos: 0 violaciones
node tools\check-boundaries.mjs

# tipos: tiene que salir 0
node node_modules\typescript\bin\tsc -p tsconfig.json
```

**Si algo falla, para y dilo.** No sigas construyendo encima.

### 3.3 · Regenerar las pantallas desde los datos

**Las pantallas no se editan a mano: se generan.** Si hay que cambiar algo, se cambia el generador.

```powershell
$py = "C:\Users\Usuario\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"

& $py .tools\generar-tienda.py       # docs/momentos/tienda.html
& $py .tools\generar-coordinacion.py   # docs/momentos/coordinacion.html
& $py .tools\generar-nube.py           # docs/nube/public/index.html  (la app de internet)
```

### 3.4 · Volver a publicar la aplicación en internet

**La aplicación sigue viva aunque se pierda el ordenador.** Está en Netlify, en la cuenta del
supermercado. Ver **[NUBE.md](NUBE.md)** §4.

Si hay que volver a publicar desde un ordenador nuevo:

```powershell
# 1. instalar el CLI (una sola vez)
npm install netlify-cli --prefix .tools\cli --cache .npm-cache

# 2. entrar en Netlify
node .tools\cli\node_modules\netlify-cli\bin\run.js login

# 3. desplegar
node .tools\cli\node_modules\netlify-cli\bin\run.js deploy --prod `
  --site 8c31f843-9327-40af-ac66-ae1de35f5740 `
  --dir docs\nube\public --functions docs\nube\netlify\functions

# 4. comprobar que está DE VERDAD
node docs\nube\prueba-en-vivo.mjs
```

**El paso 4 no es opcional.** Ya pasó una vez que el despliegue decía «deploy is live» y la
aplicación **no guardaba nada**.

---

## 4 · Los datos que no están en el `.zip`

**Nada de lo dictado se pierde, porque está escrito en `docs/`.** Pero hay cuatro cosas que viven
fuera y conviene saber dónde:

| Qué | Dónde |
|---|---|
| **Lo que marquen en la app** | **Netlify Blobs**, sitio `tienda-malato`. **Sobrevive al ordenador** |
| **La cuenta de Netlify** | La del supermercado. **La contraseña solo la sabe la propiedad** |
| **El convenio colectivo** | `.tools/docs/convenio-*.pdf` (va en el zip) |
| **Los ficheros originales** | `C:\Users\Usuario\Desktop\APP Malato Documentación` — **NO va en el zip**: son sus originales, no hay que tocarlos |

> **Aviso importante:** la copia **no** incluye la contraseña de Netlify ni la del correo. Si se
> pierde el ordenador, **hace falta la contraseña** para volver a entrar en la cuenta. **Eso lo tiene
> que guardar la propiedad por su cuenta** — no es algo que pueda ir en este fichero.

---

## 5 · El estado exacto del proyecto hoy

**Terminado y funcionando:**

- Catálogo de tareas de **tienda** (mañana, tarde y cierre) y **coordinación** (apertura con dos
  patrones, el día y el cierre)
- **Dos pantallas** que se abren y se marcan
- **Una app en internet** con login por puesto y número, que guarda en la nube
- **104 productos** de fruta y verdura clasificados en 6 familias
- **El logotipo**, extraído y puesto

**A medias:**

- **Gerencia**: hay contenido (5 de día a día, 4 bloques de los lunes, los martes, 4 ventanas
  mensuales y la cadena de las ofertas) pero **no está terminada** y **no tiene pantalla**

**Sin empezar:**

- **Pantalla de fichajes** (se guardan, no se ven)
- **Contraseña** para la app de internet
- **Restringirla al wifi de la tienda**
- Las zonas del etiquetero · la casilla de utillaje · los 10 CI cortados · el cierre de caja con
  instrucciones

---

## 6 · Lo que NO debe repetirse

Está todo en [DECISIONES.md](DECISIONES.md) y en `RRHH-TURNOS.md` §14, pero **lo esencial**:

1. **No decidir prioridades que no son mías.**
2. **El sistema muestra hechos; si ve una asimetría, pregunta. No acusa.**
3. **Cuando veo un hueco, preguntar si ya está cubierto antes de proponer cómo cubrirlo.**
4. **Cuidado con mezclar mañana y tarde**: son turnos distintos y la propiedad lo dijo desde el
   principio.
5. **Antes de concluir algo de un momento del día, mirar los horarios que ya están escritos.**
   (E-9: el cierre de mediodía llevaba meses escrito en la tabla de horarios.)
6. **No dar por bueno un despliegue porque diga que fue bien**: comprobar que **guarda**.
7. **No usar nombres propios** en los documentos: los puestos, y las personas de fuera por su papel.
