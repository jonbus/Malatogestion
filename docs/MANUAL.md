# Manual del proyecto y de usuario

**Propósito de este documento:** que cualquier persona —la propiedad, una coordinadora o quien
retome el desarrollo— pueda entender y continuar este trabajo **sin depender de la memoria de
nadie**. Se actualiza **al final de cada sesión de trabajo**.

> **Regla de este manual:** aquí no aparecen nombres propios de personas trabajadoras. Se usan
> etiquetas: `OP 1`–`OP 3` (personas de tienda), `COORD 1`–`COORD 2` (coordinadoras) y **Gerencia**.

**Última actualización:** sesión S-16 (ver §9).

---

## 1 · Qué es este proyecto y para qué

Aplicación de gestión integral para una tienda de alimentación con asador, en Luiaondo (Ayala,
Álava). Seis personas: Gerencia, 2 coordinadoras y 3 personas en tienda.

### El problema que resuelve

1. **Productividad de sala.** «Aprovechamiento del trabajo al 300 %: con el mínimo esfuerzo, la
   mayor rentabilidad.» El ahorro no viene de ir más rápido, sino de dejar de perder tiempo en
   **decidir qué hacer**, **buscarlo** y **repetirlo**.
2. **Acabar con los piques del tipo «tú no has hecho esto y yo sí».** Es el problema emocional de
   fondo, y condiciona todo el diseño.
3. **Evitar los errores que se repiten por rutina.**
4. **Que el trabajo no dependa de que alguien se acuerde de él.**

### Las tres patas del producto

| Pata | Qué incluye | Estado |
|---|---|---|
| **Operación de sala** | Motor de tareas, Kanban, RBAC, alertas | Núcleo construido y probado |
| **Conocimiento y calidad** | Guías con vídeo por tarea, checklists, errores recurrentes | Diseñado, sin construir |
| **RRHH y planificación** | Turnos, fichaje, cómputo por convenio, generador de cuadrantes | Especificado y analizado |

### Reglas de oro que no se deben perder

- **La equidad se mide en tiempo ponderado, no en número de tareas.** Contar tareas premia lo
  trivial y castiga lo pesado, y crearía piques nuevos. La unidad es `estimated_minutes`.
- **El sistema muestra hechos. Cuando ve una asimetría, pregunta. No acusa.** Un sistema que deduce
  injusticias a partir de los datos se convierte en la fuente del pique que venía a resolver.
- **Los roles son sombreros, no identidades.** La gerencia hace de gerente, de coordinadora y de
  tienda. Una persona lleva **varios papeles a la vez** (cocinera *y* coordinadora).
- **Quien puede recibir una tarea se decide por turno, no por rol.**

---

## 2 · Mapa del repositorio

```
docs/                          Documentación. Empezar por este manual
  MANUAL.md                    ← este documento
  DECISIONES.md                Registro de decisiones (D-xx) y errores (E-x)
  RRHH-TURNOS.md               Reglas de plantilla, turnos, convenio y cómputo
  ARQUITECTURA-MODULOS.md      Contratos, eventos y reglas de frontera
  ADOPCION-NESTJS-REACT.md     Cómo enchufar los hosts
  paleta.png                   Paleta de color (verde botella)
  referencia/                  Libros de horarios anonimizados

packages/
  contracts/                   Tipos compartidos: eventos, manifiestos, puertos, RBAC
  core/                        NÚCLEO: registry, bus de eventos, outbox, motor de reglas, RBAC
  module-tasks/                Tareas + subesquema `rules` (motor ECA)
  module-inventory/            Stock, lotes, mermas
  module-pos/                  Caja (FUERA del MVP, esquema listo)
  module-notify/               Alertas
  module-analytics/            KPIs
  module-healthcheck/          Módulo de ejemplo: demuestra la extensibilidad
  module-store-context/        Variables de contexto (calendario, afluencia)
  */migrations/*.sql           Esquema de cada módulo

apps/api/                      Host HTTP (node:http, sin frameworks, sin lógica de negocio)
apps/web/                      Shell React PWA (pendiente; solo hay el plan)

db/init/                       Extensiones, esquemas y funciones de utilidad
db/seed/                       Datos de demostración
tests/                         Suites de test (node:test)
tools/                         Verificadores: fronteras y lanzador de tests
.tools/                        Herramientas de desarrollo NO entregables (ver §8)
```

---

## 3 · Cómo se ejecuta y se verifica

### Requisitos

- **Node 24 o superior.** Ejecuta TypeScript directamente, sin compilar.
- Para el esquema: **PGlite** (PostgreSQL en WASM) ya instalado en `.tools/pglite`.

### Comandos

| Qué | Comando |
|---|---|
| Todos los tests | `node tools/run-tests.mjs` |
| Un solo test | `node tests/rule-engine.test.ts` |
| Reglas de frontera | `node tools/check-boundaries.mjs` |
| Comprobación de tipos | `node node_modules/typescript/bin/tsc -p tsconfig.json` |
| **Ejecutar el esquema SQL de verdad** | `node .tools/pglite/run-schema.mjs` |
| Análisis de horarios | `python .tools/analizar-horarios.py` |

### Estado de verificación (última sesión)

| Comprobación | Resultado |
|---|---|
| Suites de test | **7/7 ficheros, 42 tests en verde** |
| Violaciones de frontera | **0** en 47 ficheros |
| Tipos con `strict` | **0 errores** |
| Esquema sobre PostgreSQL real | **11/11 ficheros, 0 fallos** (PostgreSQL 18.3 vía PGlite) |
| Comportamiento de restricciones | Comprobado: los bugs corregidos siguen corregidos |

### ⚠️ Trampas del entorno (importante para quien retome)

1. **Nunca uses `node --test <carpeta>`.** El runner lanza subprocesos con tuberías y el entorno
   lo bloquea con `spawn EPERM`. **Lanza cada fichero directamente:** `node tests/x.test.ts`.
2. **`pip` falla** al escribir en la carpeta temporal del sistema. **`npm` sí funciona** si se le
   pasa una caché dentro del proyecto: `npm install X --cache .npmcache`.
3. **Este entorno no lee PDF** desde la herramienta web. Hay que descargar el PDF y extraer el
   texto con `pdfjs-dist` (ver `.tools/pdfprobe/extract.mjs`).
4. **`openpyxl` NO conserva los valores calculados de las fórmulas.** Al guardar un libro, las
   fórmulas sobreviven pero sus resultados se pierden: el fichero muestra celdas vacías hasta que
   se abre en Excel. Se arregla recalculando con LibreOffice, que **necesita permiso ampliado**
   porque lanza un subproceso.
5. **Un test sobre una tabla vacía no verifica nada.** Un `UPDATE` sobre cero filas **no dispara el
   trigger**: la primera versión del arnés de esquema daba por buenas las tablas append-only
   precisamente por eso. Hay que **insertar una fila antes** de intentar mutarla.

---

## 4 · Manual de uso de la aplicación

### Estado actual: qué se puede usar hoy

Hoy **no hay interfaz gráfica**. Lo que existe y funciona es:

- El **esquema de base de datos completo**, ejecutable y verificado.
- El **núcleo**: permisos, bus de eventos, motor de reglas y tareas.
- Un **host HTTP de demostración** (`npm start`, puerto 3000) con estas rutas:

| Ruta | Permiso | Para qué |
|---|---|---|
| `POST /auth/login` | — | Entrar con PIN de 4 dígitos |
| `POST /auth/logout` | — | Salir |
| `GET /me/tasks` | `tasks.read` | **Mis tareas** (personas de tienda) |
| `GET /tasks/board` | `tasks.assign` | **Tablero Kanban** (coordinación) |
| `POST /tasks/:id/reassign` | `tasks.reassign` | Reasignar en tiempo real |
| `GET /stock/alerts` | `inventory.read` | Productos bajo mínimo |
| `GET /stock/expiring` | `inventory.read` | Lotes próximos a caducar |
| `GET /health` | público | Estado del núcleo y de los módulos |

Los datos viven **en memoria**: se pierden al apagar. La persistencia real llega en el Bloque 1.

### Cómo funcionará cuando esté terminada

**Tienda.** Entran con PIN en la tablet. Ven **sus tareas de hoy** en tarjetas grandes,
ordenadas por prioridad. Completan con **como máximo dos toques**. Si encuentran menos stock del
indicado, lo reportan en un toque: eso avisa a coordinación y puede disparar una regla de pedido.

**Coordinadoras.** Viven en el **tablero Kanban**. Validan recepciones, resuelven incidencias,
**reasignan tareas en tiempo real según el flujo de la tienda**. Pueden sobreescribir la asignación
que propone el motor, pero **no la regla**.

**Gerencia.** Ve KPIs, márgenes, roturas y mermas. **Configura las reglas** del motor con
simulador antes de activarlas. Ve la carga de trabajo del equipo y su propia carga.

### El motor de tareas, en una frase

La gerencia crea **reglas** del tipo *«si es lunes, hay poca afluencia y el stock de lácteos está
bajo, crear una tarea de reposición prioritaria y asignarla a quien menos carga tenga»*. El motor
las evalúa solo, crea las tareas y las reparte. Las coordinadoras las ajustan a la realidad del día.

---

## 5 · Reglas de negocio esenciales

Están desarrolladas en [RRHH-TURNOS.md](RRHH-TURNOS.md). Resumen:

- **Horario de apertura:** L-V 8:00–14:30 y 17:00–21:00 · Sábado 9:00–14:30 y 17:00–21:00 ·
  Domingo y festivos 10:00–14:30 y 17:00–21:00. **En verano cambia.**
- **El turno NO coincide con la apertura:** se entra **1 hora antes** para preparar y se sale
  **media hora después** para recoger (turno de tarde `17:00–21:30`).
- **El jueves** llega el camión grande. El apoyo son **3 horas exactas**.
- **Los domingos** siempre hay **3 personas por la mañana**.
- **El asador** funciona sábados, domingos y festivos. **La cocina la llevan las coordinadoras**,
  dentro de su propio turno, sin horas extra. Si coinciden dos, **cocina la que entra más tarde**;
  **la cocinera se turna** entre las dos.
- **La Gerencia NUNCA es la cocinera.** Puede ayudar, pero no ejercer ese papel. Por tanto **en
  festivos y fines de semana de asador tiene que haber siempre una coordinadora**: sin coordinadora
  no hay asador.
- **Vacaciones:** cada tienda, un mes entre junio y agosto; lo deciden ellas; como mucho dos
  coinciden una semana; empiezan en lunes. Las coordinadoras las cogen cuando quieren.
- **El desajuste de horas del año se compensa en verano.**
- **Cada día que se trabaja de 2 cuando tocaban 3 se paga un pequeño plus** (marca privada `$$$`
  en los cuadrantes).

### Festivos

- **1 de enero y 25 de diciembre la tienda está CERRADA.** No se trabaja.
- Los demás festivos se trabajan con **horario de festivo: 8:00–15:00 y 17:00–21:30**, y dotación de
  domingo. Los tres de Semana Santa son **móviles** (según la Pascua de cada año).
- **Se trabaja con el horario de un domingo**, manteniendo el turno asignado. Festivos y domingos
  comparten calendario, dotación y reglas.
- **Dotación: 3 personas** — 1 Gerencia + 1 coordinadora + 1 persona de tienda, **o** 2 coordinadoras +
  1 persona de tienda.
- **El festivo lo cubre UNA sola persona de tienda a jornada completa**, para que **las otras dos disfruten
  el festivo entero**. Nada de repartirlo entre dos a medias.
- **Los festivos se reparten equitativamente.** Objetivo: **4-5 por tienda** y **7 por
  coordinadora** al año.

### Los mínimos de fin de semana (horario de Gerencia)

| Día | Mínimo | Entradas |
|---|---|---|
| Sábado por la mañana | **2 personas** | una a las **8:00**, otra a las **10:30** |
| Domingo | **3 personas** | una a las **8:00**, dos a las **9:00** |

### Preferencias del personal (entradas del cuadrante, no obligaciones)

Se recogen persona a persona y **no son obligaciones**: el generador intenta cumplirlas y puede
incumplirlas si chocan con la cobertura. **Se aplican al planificar el cuadrante de verano**, cuando
hay que cubrir vacaciones. **No implican cambiar los turnos ni la rotación.**

| Persona | Preferencia |
|---|---|
| **PG** (tienda) | En verano, **trabajar un día entero y librar otro** en vez de dos medios días |
| **PG** (tienda) | En la parte más calurosa, **solo medio día** (mañana o tarde); en la más suave, mañana y tarde. **Opcional** |

### Cuándo hace mucho calor

Estación **AEMET de Amurrio** (a 6,6 km): junio 19 °C · **julio 21 °C** · **agosto 21 °C** ·
septiembre 19 °C. Fuente: [clima de Ayala/Aiara](https://todopueblos.es/municipio/ayala-01476/clima/).

**Julio y agosto están empatados** a una décima (la propia fuente se contradice sobre cuál es el más
cálido). Los episodios de calor fuerte tienden a **agosto**. Conclusión: **la ventana va de mediados
de julio a mediados de agosto.** Se usa **al planificar**, no para cambiar nada después.

### ⚠️ Restricciones duras del cuadrante

| # | Restricción |
|---|---|
| R-1 | El cuadrante **se entrega 15 días antes** y no se modifica después, salvo emergencia |
| R-2 | **Los turnos no se cambian de un día para otro.** Lo que cambia en tiempo real son las **tareas** |
| R-3 | Los turnos y la rotación **no se tocan**: las preferencias son entradas, no rediseños |

> **El cuadrante se entrega 15 días antes** (D-70) y **los turnos no se cambian de un día para otro**
> (D-71). Por eso la preferencia sobre el calor **se aplica al planificar, nunca en caliente**. Y es
> **opcional**: si no encaja, no se aplica y no pasa nada.

### El ciclo de la Gerencia (4 semanas, ligado al de las coordinadoras)

**Su semana 1 coincide con la semana 1 de las coordinadoras.** El marco de 4 semanas es **compartido**.

| Semana | Horario | Horas |
|---|---|---|
| 1 | L–V **7:00–14:30** · **sábado LIBRE** · domingo **8:00–15:00** | 44,5 |
| 2 | L–V **7:00–14:30** | 37,5 |
| 3 | L–V **7:00–14:30** · **sábado LIBRE** · domingo **8:00–15:00** | 44,5 |
| 4 | L–J **7:00–14:30** · **viernes, sábado y domingo LIBRES** | 30 |

**≈ 39,1 h/semana ≈ 2.034 h/año**, y **además** cubre huecos cuando falta gente.

**Días intocables:** sábados de las semanas 1 y 3, y **viernes, sábado y domingo de la semana 4** —
**también si cae festivo**. En festivo trabaja **8:00–15:00** y trabaja casi todos.

> **Ojo:** cualquier cuadrante que mueva esos días está mal, **por bien que cuadre las horas**. Es el
> error que cometió el calendario de S-11.

---

## 6 · Cómo se calculan las horas (el cómputo anual)

### La fórmula, en palabras de la propiedad

> **Horas pendientes = Horas anuales de convenio − Horas ya trabajadas fuera del verano**
>
> Sumando todas las horas de cada persona **excepto las de verano**, y **teniendo en cuenta en qué
> semana empieza el año de cada una** (cada persona arranca su ciclo en un punto distinto).

El resultado son las horas de las que se dispone para construir el horario de verano. Esas horas
son las que después se reparten en el cuadrante estival, y de ahí sale la tabla que la propiedad
mantiene en su Excel: **«H. Convenio Ptes» frente a «H. Trabajadas»**.

### Las cifras de referencia (convenio de comercio de alimentación de Álava)

| Concepto | Dato |
|---|---|
| Jornada semanal máxima | **40 h** |
| **Jornada anual máxima** | **1.746 h (2024)** · 1.754 h (2023) |
| Horas anuales de un contrato de 32 h | **1.396,8 h** |
| Horas anuales de un contrato de 21,5 h | **938,5 h** |
| Vacaciones | **22 días laborables** (semana de 5 días) |
| Festivos anuales | **14** |
| Bolsín horario | 15 h/año |
| **Distribución irregular** | **máximo el 5 % de la jornada anual** (±69,8 h y ±46,9 h) |

Las **fiestas del sector son las de la localidad del centro de trabajo**. La lista definitiva que
aplica la tienda está en **§5 de este manual** y en `RRHH-TURNOS.md` §7 — **no hay que deducirla de
las fiestas del ayuntamiento**. El calendario laboral **debe fijarse en enero** y entregarse por
escrito a cada persona: eso lo puede generar la aplicación.

---

## 7 · Estado del proyecto y qué falta

### Hoja de ruta

| Bloque | Estado |
|---|---|
| 0 · Núcleo (RBAC, bus de eventos, motor de reglas, fronteras) | ✅ **hecho y verificado** |
| 1 · Catálogo e inventario con persistencia real | siguiente |
| 2 · Motor de tareas + Kanban en tiempo real | pendiente |
| 3 · Pedidos y recepción | pendiente |
| 3.5 · Recuentos y ajustes de stock manuales | pendiente (sustituye al POS) |
| ~~4 · POS~~ | **fuera del MVP**; el esquema ya está preparado y `sale.completed` congelado |
| 5 · Dashboards y alertas por rol | pendiente |
| 6 · Migración de datos, formación y go-live | pendiente |
| **RRHH:** turnos, fichaje y cómputo por convenio | especificado; el fichaje es **obligatorio por ley** (RDL 8/2019) |
| **RRHH:** generador de cuadrantes de verano | especificado; objetivo para el año que viene |

### Lo que falta por decidir o aportar

Todo está numerado en [DECISIONES.md](DECISIONES.md) §Pendientes. Lo más relevante:

- **Los horarios del resto del año** y de dónde sale el saldo acumulado al llegar al verano.
- **El calendario de festivos locales** del año.
- **Las fechas de vacaciones** que quiere cada persona.
- **Quién es la referente del catálogo** (una de las dos coordinadoras).
- **`.tools/`**: decidir si entra en el repositorio o se excluye.
- **Hardware, TPV y cobro con tarjeta**: aparcado hasta la fase de caja.

---

## 8 · Herramientas internas (`.tools/`)

**No forman parte del entregable**, pero son las que han permitido verificar todo. Si se pierden,
se pierde la capacidad de comprobar:

| Fichero | Para qué |
|---|---|
| `validate-sql.mjs` | Parser oficial de PostgreSQL sobre los `.sql` |
| `pglite/run-schema.mjs` | **Ejecuta** el esquema y comprueba su comportamiento |
| `validate-semantics.mjs` | Referencias cruzadas, columnas y aridades |
| `validate-seed-data.mjs` | Coherencia de los datos de demostración |
| `analizar-horarios.py` | Horas de las plantillas frente a los contratos |
| `computo-seccion.py` | Cómputo por persona y semana sobre el libro de verano |
| `anonimizar-libro.py` | Sustituye nombres propios por etiquetas |

---

## 9 · Registro de sesiones

Se actualiza al final de cada jornada. **Orden cronológico inverso** (lo último, arriba).

### S-17 · Los tres puestos dictados, y la aplicación funcionando en la nube

**La sesión más larga del proyecto, y la primera en la que algo se puede usar de verdad.** Se dictan
los **momentos de tienda**, se monta la **pantalla de coordinación**, se registra el **primer
contenido de gerencia**, se clasifica la **fruta y verdura**, se saca el **logotipo** y se **publica
una aplicación en internet** que guarda lo que se marca.

**Lo que se dictó (tienda).** **Mañana**: rutina (9 tareas) + lo de cada día + «antes de irse».
**Tarde**: rutina (10) + lo de cada día + «antes de irse». **Cierre**: **11 bloques, 55 marcas**, con
hora fija a las **20:45**.

**Dos hallazgos que cambiaron el mapa:**

1. **La tienda cierra DOS veces al día** —a las **14:30** y a las **21:30**—, así que hay **dos
   cierres**, cada uno con su «antes de irse». *(Ya estaba escrito en §2 de `RRHH-TURNOS.md` desde el
   primer día y no lo junté: registrado como **E-9**.)*
2. **El «antes de irse» de la tarde y el cierre de la noche eran casi lo mismo** — 3 de sus 7 puntos
   estaban repetidos. Se quitaron del primero y se quedaron en el cierre, que los tiene más
   detallados. **Lo de unificar los dos bloques se vuelve a proponer al final del proyecto.**

**Lo que se dictó (coordinación).** El día (12 de rutina + lo de cada día) y el cierre (4 pasos).
**Pantalla nueva** con las tres pestañas y los dos patrones de apertura.

**Lo que se dictó (gerencia).** 5 tareas de día a día · **4 bloques de los lunes** (Cofresa **antes de
las 11:00**, Digasa con el comercial, la oferta manual, el pedido de planta con la pistola) · los
martes · **4 ventanas mensuales** (horas · asesoría fiscal · hipoteca · extracto bancario) · **la
cadena de las ofertas**. **No está terminado.**

**Cuatro cosas que la aplicación tiene que calcular sola, todas de calendario:** los **días
hábiles** (la hipoteca no se paga un sábado, y **los festivos cuentan como domingos**) · el **rango
del extracto** (empieza **el mismo día** que se sacó el anterior, no al siguiente) · la **caja
acumulada** (el lunes normal son **tres**) · las **ventanas del mes**.

**Fruta y verdura.** 104 productos en **6 familias**, clasificados por la propiedad. **El criterio es
comercial, no botánico**: *si se vende envasado, es **Embolsado*** — zanahoria, apio, endivias,
iceberg, ajos tiernos, higos, arándanos y nueces incluidos. Exportado a `docs/datos/fruta-verdura.json`.

**El logotipo.** Estaba **dentro de un `.doc`**, con «supermercado» como texto y «malato» como imagen.
**No puedo ver imágenes**, así que localicé la «o» **midiendo**: es el último de los 6 glifos y tiene
**anillo cerrado con tronco debajo** — un árbol. Extraída a `docs/marca/`.

**La aplicación en la nube.** Ver **[NUBE.md](NUBE.md)**. Publicada en
**https://tienda-malato.netlify.app**, con el patrón de la agenda de la sobrina (Netlify Functions +
Blobs). **Se hizo sin pedir ningún token**: la sesión de Netlify del ordenador seguía valiendo.

**Errores de esta sesión:** **E-9** (presenté como descubrimiento el cierre de mediodía, que ya
estaba escrito). Y cuatro fallos de despliegue que **casi dan una aplicación que parecía funcionar y
no guardaba nada**: el SSO heredado, un `package.json` mal puesto, y que **el zip por la API no
empaqueta funciones** — hay que usar el CLI.

**Lo que queda pendiente:** gerencia entera · pantalla de fichajes · contraseña para la app ·
el wifi de la tienda · las zonas del etiquetero · la casilla de utillaje · los 10 CI cortados.

### S-16 · El módulo de TAREAS: la base de cada día y las extras

**Sesión larga, y la que abre el segundo bloque del proyecto.** Los horarios quedan aparcados (se
retomarán) y se empieza el **catálogo de tareas**.

**Lo que se leyó:** `TareaseInstrucciones.xls` (8 hojas), `InstruccionesDeHornadasdeDomingoyFestivo.odt`,
`InstruccionesAsadorPolloCodilloCostillaPreparación.doc`, `ProtocoloAcosoSexual.odt` y
`Ventas Pollos.xls` (20 años de histórico del asador, 2007–2026).

**El diagnóstico de partida.** La plantilla dice *«las tareas son obligatorias»*: **30 casillas al día,
todas iguales**. Cuando todo es obligatorio, la cabeza no puede elegir, y lo que se cae es siempre lo
que menos se ve. **Esa es la monotonía que describía la propiedad, y no es culpa de nadie: es la
lista.**

**La estructura que se ha entendido, y es lo principal:**

| | **La base semanal** | **Las extras** |
|---|---|---|
| **Qué es** | Las tareas del Excel | *«Siempre se intenta hacer algo más»* |
| **Cuándo** | **Cada tarea en su día**, a propósito | **Sin día fijo: cuando se necesitan** |
| **Cómo se eligen** | No se eligen, tocan | **Por zona** y luego por tarea |

**Regla de oro:** *«la base sería la nuestra; partiendo de una base semanal añadir extras»*.
**La base no se toca.**

**Artefactos creados:**

| Fichero | Qué es |
|---|---|
| `docs/TAREAS.md` | El documento de trabajo del módulo |
| `docs/tareas-catalogo.json` | El catálogo **como dato**: 94 tareas, base por días y turnos, extras por zonas |
| `docs/vista-tareas.html` | **La pantalla**: botones de día, mañana y tarde, barra de progreso, pendientes y extras por zonas |
| `docs/PEDIDOS.md` | Apartado **aparte** para el bloque de pedidos (ver lo pendiente) |

**Números:** **94 tareas** (57 personas de tienda + 37 coordinadoras), ninguna inventada. Detalle en
`TAREAS.md` §0.

**Cosas que se aprendieron por el camino:**

- **Las dos hojas de personas de tienda valen las dos y se alternan.** Al unirlas, **11 pares eran la misma
  tarea escrita de dos formas** → **68 pasan a 57**, dejando la más descriptiva.
- **La mañana y la tarde no son lo mismo.** En las plantillas hay filas vacías que separan, y
  **«Fichar» marca el principio de cada turno**. *Mi catálogo había perdido esa separación.*
- **Las coordinadoras solo trabajan de mañana.** Por eso su hoja no trae separación.
- **«Limpiar pollos» ya estaba en la lista del viernes**, pero escrita **«si hiciera falta»** — cuando
  **se hace siempre**. Una tarea crítica marcada como condicional es lo que hace que se salte.
- **La «Monta» es el montacargas.** Preparar (coordinadora) → subir (tienda) → colocar (tienda):
  **un trabajo con relevo, no tres tareas sueltas.**
- **El banco de extras se elige por zona**: fruta, verdura, txutxes, lineales, carne, yogures, quesos,
  charcutería, pan y bollería, y toda la tienda.
- **La lista es viva.** Solo coordinadoras y gerencia la cambian. *«Llamar por teléfono»* entró así.
- **El protocolo de acoso va en un canal aparte, siempre**, aunque sea un documento visible por ley:
  un tablero que ve todo el equipo **no puede** contener una queja.

**Cuatro errores míos, y el patrón que comparten:**

- **E-7 · Decidí prioridades que no me tocaban.** Inventé una escala (crítica / alta / media / baja).
- **E-8 · Usé el criterio contrario.** Ordené por **asiduidad** (las de los 7 días como «el núcleo»).
  La propiedad: *«no se deciden por asiduidad, se deciden por **repercusión en el establecimiento**»*.
- **E-9 · Perdí un dato que estaba en el fichero** (mañana y tarde).
- **E-10 · Di por hecho tres veces que algo no estaba resuelto** —las patatas sin gluten, el registro de
  ventas del asador, el cálculo de festivos— **y las tres estaba resuelto.**
  → **Norma: cuando vea un hueco, preguntar si está cubierto antes de proponer cómo cubrirlo.**

**Lo que queda pendiente, y es de la propiedad:**

1. **Los niveles de repercusión** (la prioridad). Es lo que desbloquea el orden dentro de cada día.
2. **Las tareas de la gerencia**, que no existen todavía.
3. **Las 26 de cocina**, sin clasificar desde el primer día.
4. **Los solapes** entre las personas de tienda y coordinadoras: quién manda cuando coinciden.
5. **Qué hace la coordinadora en «Organizar trabajo del día»**.
6. **El logo**, y confirmar el verde.
7. **Los turnos y los mínimos de personal**: aparcados a propósito, se retoman.
8. **El bloque de PEDIDOS**: el método de cálculo ya está recogido en `PEDIDOS.md`, y el **importador
   de los 20 años de ventas está pendiente de hacer**.

**Y un aviso de mantenimiento:** el registro de decisiones tiene **10 números que no existen**
(D-9, D-17 a D-19, D-24 a D-29). Está **declarado** en `DECISIONES.md` para que nadie lo tome por un
error de lectura.

### S-15 · Festivos definitivos, vacaciones y convenio

- **Lista definitiva de festivos: 15 fechas.** **1 de enero y 25 de diciembre la tienda está
  CERRADA**; el resto se trabaja con horario de festivo. Los tres de Semana Santa son **móviles**.
- **En 2026 se trabajan 11 festivos**: el 1 de noviembre y el 6 de diciembre caen en **domingo**.
- **Dos correcciones:** **San Prudencio (28 abril) sí es festivo** (estaba bien supuesto) y **la
  Magdalena (22 julio) NO lo es** — **el calendario de S-11 lo incluyó y es laborable**.
- **Vacaciones: 30 días naturales**, en períodos **mínimos de 15 días que empiezan en lunes**, a veces
  de 7-8 días, y **los eligen las trabajadoras**. **Las horas de las vacaciones no se cuentan**: se
  cuadra el año con los horarios de verano.
- **El convenio de referencia es el último publicado**, no el del año: **puede tardar hasta 5 años**
  en actualizarse, así que las cifras vigentes (**1.746 h**) siguen valiendo.
- **[falta]** Cuadrar por qué el convenio habla de **14 festivos** y la lista tiene **15 fechas**.

### S-14 · El sábado, con detalle

- **Sábado normal: 3 personas.** Una coordinadora a las **8:00** (abre), **otra coordinadora a las
  10:00** —salvo cuando le toque librar según su ciclo— y **una persona de tienda a las 10:30**. **Las tres
  hasta las 15:00.**
- **Cocina la que entra más tarde** (la de las 10:00); la de las 8:00 lleva la coordinación.
- **Cuando la segunda coordinadora libra: 2 personas**, y la de las 8:00 pasa a
  **«cocinera-coordinadora»**.
- **Corrección:** tenía apuntado el sábado como **2 personas** (una a las 8:00 y otra a las 10:30).
  Eso es el **mínimo**, no lo normal: **lo normal son 3**, y la segunda coordinadora entra a las
  **10:00**, no a las 10:30 (que es la persona de tienda).

### S-13 · Los turnos y los mínimos reales

- La propiedad dicta **los turnos reales y los mínimos de personal**, que es la pieza que faltaba.
- **Los turnos son HORAS FIJAS, no se deducen de la apertura.** Normal: L–V `7:00–14:30` y
  `17:00–21:30`; sábados y domingos `8:00–15:00` y `17:00–21:30`. Verano L–S `8:00–14:30` y
  `17:30–21:30`; domingos de verano y **todos los festivos** `8:00–15:00` y `17:00–21:30`.
  **Corregida la regla «1 hora antes / media hora después»: no es la regla.**
- **Mínimos por día:** lunes y viernes **2 desde la apertura**; martes y miércoles **1 hasta las 11:00
  y 2 después**; jueves **1 hasta las 9:00 y 3 después, más un apoyo de 3 h**; sábado **2** (8:00 y
  10:30); domingo y festivo **1 a las 8:00 y 3 desde las 9:00**; **todas las tardes, 1 persona**.
- **Corrección de un diagnóstico mío:** los huecos de una sola persona **están permitidos por
  diseño** en 5 de los 7 días y en todas las tardes. Mi conclusión de S-11 («el calendario adelgaza
  la tienda») **era infundada: me faltaban las reglas, no los datos.**
- **El defecto real del calendario S-11, medido:** **149 incumplimientos** — **99 lunes y viernes**
  sin 2 personas desde la apertura y **50 jueves** sin las 3 personas ni el apoyo. Todo lo demás lo
  cumple.

### S-12 · El ciclo real de la Gerencia

- La propiedad dicta **su horario real: un ciclo fijo de 4 semanas**, **ligado al de las coordinadoras**
  (su semana 1 coincide con la semana 1 de ellas). El marco de 4 semanas es **compartido**.
- **Días intocables:** sábados de las semanas 1 y 3, y **viernes, sábado y domingo de la semana 4**.
  Se respetan **incluso si cae festivo**.
- **≈ 39,1 h/semana ≈ 2.034 h/año**, además de las coberturas puntuales.
- **Validación cruzada:** el ciclo dictado reproduce lo medido en las plantillas reales **salvo un solo
  turno** — un sábado de apoyo de 2 h en la semana 3 (≈ 26 h/año). Dos fuentes coinciden salvo eso.
- **Consecuencia grave para el calendario de S-11:** aquel calendario daba a la Gerencia **1.472 h**,
  cuando su ciclo solo ya produce **2.034 h**. **Eliminaba unas 560 h de su presencia.** Ese es,
  cuantificado, el motivo por el que la propiedad lo rechazó. **El generador queda invalidado en ese
  punto.**

### S-11 · Calendario 2026 generado y verificado

- Se genera el **calendario completo de 2026** (`docs/calendario-2026/`): 17 hojas, las 52 semanas,
  con el escenario de vacaciones inventado a petición de la propiedad.
- **Las horas cuadran**: desviación máxima de **1,5 h al año**. Cero pluses. Cocina **58/58**. La
  Gerencia, **1.472 h** y **ninguna cocina**.
- **Verificación independiente** (recalculando desde el texto de cada turno, no desde los totales del
  generador): horas idénticas, 66/66 domingos y festivos con una sola persona de tienda, 0 descansos por
  debajo de 12 h, y las dos vías suman **6.625,00 h**.
- **Defecto del verificador del generador:** cuenta «personas con turno de mañana» en vez de
  «personas presentes a la vez», así que su «0 incumplimientos» no comprueba la ocupación
  simultánea. **Cuantificado:** en invierno la tienda queda con **una sola persona por la mañana el
  81 % de los días**, frente al **39 %** de las plantillas reales. **El doble.**
- **Causa de diseño:** optimizar «que las horas cuadren» **compite** con «que haya gente suficiente a
  la vez». Se persiguió el primero y se descuidó el segundo.
- **Pendiente de decidir:** ¿la ocupación simultánea debe ser un objetivo del generador o solo un
  indicador que se muestre?

### S-10 · Aclaración de las preferencias y de los límites del cuadrante

- **Corrección de fondo:** el «día entero y día libre» **no es un cambio de turnos**, es una
  preferencia para **planificar el verano** cuando hay que cubrir vacaciones. **Los turnos y la
  rotación no se tocan.**
- **Retiradas dos propuestas mías:** reducir el catálogo de turnos y gestionar el calor de forma
  reactiva. Ninguna procedía.
- **Registradas dos restricciones duras:** el cuadrante **se entrega 15 días antes** (D-70) y **los
  turnos no se cambian de un día para otro**, salvo emergencia (D-71). Lo que cambia en tiempo real
  son las **tareas**, no los turnos.
- **Error propio E-6:** convertir información en propuesta de rediseño. **Tercera vez.** El patrón
  queda escrito, con su consecuencia de producto: *el sistema propone cuando merece la pena; el
  resto del tiempo, informa.*

### S-09 · Festivos, preferencias y propuestas de turnos

- **Festivos:** se trabajan con horario de domingo, misma dotación (3 personas). El festivo lo cubre
  **una sola persona de tienda a jornada completa** para que las otras dos lo libren entero, y **se reparten
  equitativamente**.
- **La Gerencia nunca es la cocinera** (puede ayudar). Implica que siempre debe haber una
  coordinadora en los turnos de asador.
- **La cocinera se turna**, lo que **choca con la regla «entra más tarde, cocina»**: se resuelve
  invirtiendo las entradas cuando tocaría repetir.
- Registradas las **preferencias de PG** y **comprobado el clima**: julio y agosto empatan; los
  picos de calor tienden a agosto. Ventana real: **mediados de julio a mediados de agosto**.
- Se proponen **cuatro mejoras de turnos** (jornada completa con día libre, reducir el catálogo de
  turnos, objetivo numérico de festivos, gestión reactiva del calor). **Pendientes de aprobación.**

### S-08 · Cómputo anual, anonimización y manual

- Se lee el libro de horarios de verano: estructura, cómputo y mecanismo de compensación.
- **Se eliminan todos los nombres propios** de los materiales del proyecto (25 sustituciones) y se
  genera una **copia anonimizada y verificada** del libro: 14.997 celdas comparadas, 0 diferencias.
- Se registra la **fórmula del cómputo anual** y el **horario de verano de Gerencia** con los
  mínimos de fin de semana.
- Se crea **este manual**.
- **Errores propios registrados:** E-4 (presentar como injusticia una decisión libre) y E-5
  (auditar en lugar de aprender). Ver [DECISIONES.md](DECISIONES.md).

### S-07 · Convenio y horarios reales

- Se lee el **convenio de comercio de alimentación de Álava** (PDF descargado y extraído).
- Se analizan las **plantillas reales**: márgenes de apertura y cierre, apoyo del jueves, ciclos de
  3 y 4 semanas, y el significado de `$$$`.
- Se corrigen **E-2** (jornada anual: 1.746 h, no 1.754) y **E-3** (método de cómputo anual).

### S-06 · Plantilla 2+3 y propiedad del catálogo

- Plantilla corregida: **2 coordinadoras + 3 personas en tienda**, con la gerencia cubriendo.
- El catálogo pasa a ser **propiedad de las coordinadoras**.
- Se añaden **bloqueo optimista** en tareas y **lectura de alertas por persona**.

### S-05 · Esqueleto del núcleo

- 42 tests, 0 violaciones de frontera, tipos en 0.
- **Hallazgo grave:** el motor de reglas estaba **muerto en silencio** por un doble envolvimiento
  de los datos. No se detectaba porque el proyecto **nunca se había compilado**.

### S-04 · Esquema SQL ejecutado

- El esquema se ejecuta sobre **PostgreSQL real** (PGlite/WASM): 11/11 ficheros, 0 fallos.
- Se corrigen **tres bugs de negocio** que habrían roto la tienda: pago dividido, numeración de
  ticket por caja y recepción repetida del mismo lote.

### S-01 a S-03 · Arquitectura, modelo de datos, flujos y hoja de ruta

- Fases 1 a 4 aprobadas: monolito modular, un esquema por módulo, roles como sombreros, roadmap.

---

## 10 · Cómo continuar este trabajo

1. **Lee este manual entero** antes de tocar nada.
2. **Lee [DECISIONES.md](DECISIONES.md).** Contiene el porqué de cada cosa y **los errores ya
   cometidos**, para no repetirlos.
3. **Ejecuta las verificaciones** de §3 y comprueba que siguen en verde **antes** de cambiar algo.
4. **No te fíes de ningún resumen, incluido este.** Todo lo que aquí se afirma se puede reproducir
   con los comandos de §3. Si algo no cuadra, **manda el comando, no la memoria**.
5. **Documenta cada decisión nueva** en `DECISIONES.md`, con su motivo.
6. **Añade una entrada de sesión** en §9 al terminar cada jornada.
