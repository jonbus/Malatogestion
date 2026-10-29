# La aplicación en la nube

> **Funcionando desde el 21 de octubre de 2026.** Se entra desde cualquier dispositivo con internet,
> y **lo que marca una lo ven las demás al momento**.

---

## 0 · AHORA MISMO: Cloudflare

> **Desde el 26 de octubre de 2026 la aplicación vive en Cloudflare.** Netlify se quedó bloqueado
> (*«Account credit usage exceeded»*) y no dejaba publicar nada.

| Qué | Dónde |
|---|---|
| **Dirección** | **https://app.supermalato.workers.dev** |
| **Dónde se guardan los datos** | **Cloudflare KV**, almacén `ESTADO` |
| **El proyecto** | `docs/nube/cloudflare/` + `docs/nube/wrangler.toml` |
| **Para publicar** | `wrangler deploy --config docs/nube/wrangler.toml` |
| **Cuenta** | la del supermercado (`malatosupermercado@yahoo.es`) |
| **Subdominio** | `supermalato.workers.dev` |

**Y lo importante:**
- **No hay que tener ningún ordenador encendido** — es lo que resuelve el problema de raíz
- **La dirección no cambia nunca**
- **No gasta créditos de despliegue**: se puede publicar las veces que haga falta

**Lo que hay que saber:**
- **La clave de la Jefa** está como **secreto `GERENCIA_PIN`** en el Worker
- **Cloudflare rechaza con 403 a los programas** que no se identifican como navegador.
  **Un móvil o un ordenador entran sin problema**; una prueba automática tiene que mandar
  un `User-Agent` de navegador
- **Repetir un despliegue** es un solo comando, y **los datos no se tocan**

---

## 0b · Lo de antes (queda como reserva)

### Netlify

| Qué | Dónde |
|---|---|
| **Dirección** | **https://tienda-malato.netlify.app** — **bloqueada, no se puede publicar** |
| **Panel** | https://app.netlify.com/projects/tienda-malato |
| **Dónde se guardan los datos** | **Netlify Blobs**, en el sitio `tienda-malato` |

---

## 1 · Lo imprescindible

| Qué | Dónde |
|---|---|
| **Dirección** | **https://app.supermalato.workers.dev** |
| **Cómo se entra** | Se elige **el puesto** (Tienda / Coordinación) y **el número**. **Gerencia pide una clave** — ver §3e |
| **Cuenta** | la del supermercado |
| **Dónde se guardan los datos** | **Cloudflare KV**, almacén `ESTADO` |
| **El proyecto en el ordenador** | `docs/nube/` |

**No hay que instalar nada.** Es una página web: se abre en el móvil, la tablet o el ordenador.

---

## 2 · Cómo se usa

1. Se abre la dirección.
2. **¿En qué puesto estás?** → Tienda o Coordinación.
3. **¿Cuál eres?** → el número.
4. **Entrar.** A partir de ahí:
   - **Se ficha solo** (queda la hora de entrada).
   - Aparecen **las tres pestañas** del puesto.
   - Se marca tocando cada tarea. **Se guarda solo**, no hay que darle a guardar.

**Los números son 1, 2 y 3 en personas de tienda, y 1 y 2 en coordinación.**

> **El dispositivo recuerda quién entró.** La próxima vez que se abra en ese móvil, entra directo.
> Para cambiar de persona, botón **Salir**.

---

## 3 · Las tres cosas que hay que entender del comportamiento

**1 · Las marcas son de todos; el fichaje es de cada una.**

Si la Tienda 1 marca una tarea, **la Tienda 2 la ve marcada**, con **quién** la marcó y **a qué
hora**. Es lo que pediste: *«si un día se ha hecho una zona, el resto sabe qué zonas quedan sin hacer»*.

**Pero el fichaje es individual**: cada entrada queda con su número y su hora.

**2 · Cada día empieza limpio.**

Las marcas llevan la fecha dentro. **Mañana el tablero vuelve a estar vacío**, aunque hoy esté todo
marcado. Y se guardan **30 días**; lo más viejo se borra solo.

**3 · Si se cae el internet, no se pierde lo marcado.**

Se sigue marcando. Lo que no se haya podido subir **vuelve a la cola** y se reintenta. Arriba, en la
franja de estado, se ve:
- **verde** — al día
- **amarillo** — guardando
- **rojo** — sin conexión, se reintentará

---

## 3b · Lo que se quedó sin hacer: el bloque **SIN HACER**

**La rutina diaria NO se arrastra nunca.** Si no se hizo, no quedó pendiente: se hizo mal. Arrastrar
*«frentear los lineales»* de ayer a hoy sería **acumular excusas, no trabajo**.

**Lo que sí se arrastra** es **lo del día específico** (y, cuando existan, lo urgente y lo
preferente). Y **no salta solo: pregunta.**

```
SIN HACER
  ☐ Limpiar el expositor azul        Martes 20 de octubre · hace 2 días
       [ ¿Para cuándo lo pasas? ]
```

Al pulsar salen los destinos: **mañana por la mañana · mañana por la tarde · dentro de dos días ·
la próxima vez que yo vuelva · otro día**.

- **En cuanto tiene día**, desaparece de SIN HACER y **aparece ese día**, con la marca
  **«venía del martes 20»**, para que quien lo haga sepa que viene de atrás.
- **Si nadie le pone día**, se queda en SIN HACER, **«sin día»**, hasta que alguien la coja.
- **Se marca siempre en su día de origen**, no en el día al que se pasó: así **la marca es una sola**
  y el histórico no dice que se hizo dos veces lo que se hizo una.

**«La próxima vez que yo vuelva»** no necesita el cuadrante: **la app ya sabe cuándo entra cada una**,
porque lo apunta al fichar.

---

## 3c · Navegar por días y por meses

`[◀] [ fecha ] [▶] [Hoy] [Mes]`

Se puede **ver y marcar cualquier día**. Si el día que miras no es hoy, el subtítulo lo dice:
**«(no es hoy)»**.

---

## 3d · El calendario: general y personal

**Una pestaña más**, junto a los momentos del turno.

**Es para apuntar cosas, no para ver tareas de otros días.** Las tareas se ven en sus pestañas.

```
            ◀   noviembre de 2026   ▶   [Hoy]

   L   M   X   J   V   S   D
                         1   2
   3   4   5   6   7   8   9
  ...
   ●  = ese día tiene notas

   ── GENERAL · lo ve todo el mundo ────────
     Cierra a las 14:00            co1 · 10:23
   ── PERSONAL · solo lo ves tú ────────────
     Recordar pedir el cambio       op1 · 10:25

   [ Añadir una nota… ]  [General ▾]  [Añadir]
```

**Las dos clases de nota:**

| | Quién la ve | Quién la escribe |
|---|---|---|
| **General** | **Todo el mundo** | **Cualquiera** |
| **Personal** | **Solo su dueña** *(y gerencia, cuando exista)* | Su dueña |

**Cada uno puede borrar sus notas** con la ✕.

> **Aviso honesto:** lo personal **se filtra en el móvil**, no en el servidor. Con la aplicación
> abierta, **nadie ve tus notas personales** — pero alguien que sepa mirar por dentro **sí podría**.
> Es lo que hay mientras no haya contraseña. **Lo personal sensible no debe ir aquí.**

**Se guardan 60 días hacia atrás** y **todas las futuras** (una nota para dentro de dos meses no
caduca).

---

## 3e · Gerencia: la bandeja y la clave

**Es el tercer puesto, y no funciona como los otros dos.**

| Puesto | Cómo trabaja |
|---|---|
| **Tienda** | Un **orden** que seguir |
| **Coordinación** | Un **orden** que seguir |
| **Gerencia** | **Una bandeja** — elige por dónde empieza |

**No tiene pestañas.** Al entrar, ve **todo lo suyo en una sola lista**, agrupado por cuándo toca:

- **Lo de cada día** (lunes a viernes)
- **Los lunes · los pedidos** — con **Cofresa antes de las 11:00**
- **Los martes · cerrar lo del lunes**
- **Abierto este mes** — las ventanas que están abiertas hoy
- **Las ofertas**
- **Y el panel de las cuatro ventanas**, con cuántos días quedan

### La clave

**La pestaña de gerencia no se abre sin clave.** Y la clave **no está escrita en la página**: se
comprueba **en el servidor**, contra una variable de entorno (`GERENCIA_PIN`).

- Se pide al elegir **Gerencia 🔒**
- Con clave mala devuelve **401** y **no dice si la clave existe**
- **La clave no viaja en el código**: la página no la contiene

**Para cambiarla:**

```powershell
$env:APPDATA = "C:\Users\Usuario\Desktop\APP Malato\.tools\appdata"
node .tools\cli\node_modules\netlify-cli\bin\run.js env:set GERENCIA_PIN LA_NUEVA `
  --site 8c31f843-9327-40af-ac66-ae1de35f5740
```
Y **volver a desplegar**, porque Netlify no aplica la variable hasta el siguiente despliegue.

> **Aviso honesto, y es importante:** lo que la clave protege es **la puerta**, no el contenido.
> **Las tareas de gerencia están dentro de la página**, así que **alguien que mire el código fuente
> las podría leer**. Para una tienda de seis personas es aceptable —no es información sensible—,
> **pero no es una caja fuerte**. Si algún día tiene que serlo, hay que mover esa parte al servidor.

### Lo que sabe calcular

| | |
|---|---|
| **Días hábiles** | Ni sábado, ni domingo, ni festivo. **Los 15 festivos de 2026 están dentro** |
| **La hipoteca** | **El último día hábil antes del 17** — si el 16 cae en domingo, es el viernes 14 |
| **El rango del extracto** | Empieza donde acabó el anterior |
| **La caja acumulada** | Se ve en su tarea, con las pendientes |

> **Los festivos hay que actualizarlos cada año.** Están en `DATOS.gerencia.festivos`, dentro de
> `generar-nube.py`.

---

## 4 · Cómo se publica un cambio

> ## ⚠️ AVISO — 23/10/2026
>
> **Netlify ha bloqueado los despliegues nuevos.** El error no es de permisos ni del código:
>
> ```
> Account credit usage exceeded - new deploys are blocked until credits are added
> ```
>
> **Se han agotado los créditos de despliegue de la cuenta** (hoy se ha desplegado muchas veces).
> **La aplicación publicada sigue funcionando** con la última versión que subió bien.
>
> **Para seguir publicando:** añadir créditos o pasar a un plan de pago en Netlify, o esperar a que
> se renueve el ciclo. **El código está listo**: en cuanto se pueda, se sube y ya está.

**Esto es lo único técnico.** Cuando se cambie algo de las pantallas:

```powershell
# 1. regenerar la app
python .tools\generar-nube.py

# 2. desplegar
$env:APPDATA = "C:\Users\Usuario\Desktop\APP Malato\.tools\appdata"
node .tools\cli\node_modules\netlify-cli\bin\run.js deploy --prod `
  --site 8c31f843-9327-40af-ac66-ae1de35f5740 `
  --dir public --functions netlify/functions
```

Y **comprobar que está**, que no basta con que diga «deploy is live»:

```powershell
node docs\nube\prueba-en-vivo.mjs
```

---

## 5 · Qué hay dentro

```
docs/nube/
  public/index.html                  la aplicación entera (66 KB, con el logo dentro)
  netlify/functions/nucleo.js        la lógica, sin depender de Netlify
  netlify/functions/api.mjs          el adaptador (30 líneas)
  netlify.toml                       configuración
  servidor-local.mjs                 para probar en el ordenador
  prueba-nucleo.mjs                  24 comprobaciones de la lógica
  prueba-en-vivo.mjs                 16 comprobaciones contra la app publicada
```

**La lógica está separada de Netlify a propósito** (`nucleo.js`): así se prueba en el ordenador con un
almacén falso, sin gastar despliegues. Es el mismo patrón que la agenda de la sobrina.

---

## 6 · Lo que aún NO tiene

| | |
|---|---|
| **Gerencia** | No está. Solo tienda y coordinación |
| **Pantalla de fichajes** | Se guardan, pero **no hay dónde verlos** todavía |
| **Instalar como app** | No lleva manifiesto; se abre desde el navegador |
| **Contraseña o PIN** | **No tiene**. Cualquiera con la dirección entra |
| **Solo desde el wifi de la tienda** | No. Ahora es abierto, como pediste |

> **Sobre la contraseña:** ahora mismo la dirección es pública y **no hay llave**. Para una prueba de
> un día es aceptable —no hay datos personales, solo números y tareas—, **pero no debe quedarse así**.
> Cuando la pruebes, lo siguiente es ponerle llave.

---

## 7 · Lo que se aprendió por el camino

| Problema | Causa | Solución |
|---|---|---|
| El sitio daba **401 Login Redirect** | El sitio nuevo heredó **SSO activado** de la cuenta | `sso_login: false` |
| **0 funciones** en el despliegue | Un `package.json` dentro de `netlify/functions/` | Quitarlo |
| **0 funciones** otra vez | El despliegue por zip de la API **no empaqueta funciones** | **Hay que usar el CLI** |
| `spawn EPERM` al desplegar | El CLI lanza esbuild como subproceso y el sandbox lo bloquea | Permiso amplio para ese comando |
| El CLI no podía escribir su configuración | Su config vive fuera del proyecto | `APPDATA` apuntando a `.tools/appdata` |
| npm fallaba con `EPERM` | Su caché vive fuera del proyecto | `--cache .npm-cache` |
