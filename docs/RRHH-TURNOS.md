# Planificación de plantilla, turnos y cómputo de horas

Especificación de las reglas reales de la tienda. Cada dato lleva su origen marcado:

- **[NEGOCIO]** — lo ha dictado la propiedad. Es un requisito.
- **[CONVENIO]** — está en el convenio colectivo. Es una obligación legal.
- **[inferencia]** — deducción mía. Se puede equivocar.
- **[falta]** — no lo sé. No lo relleno con algo plausible.

---

## 1 · Plantilla y contratos

| Persona | Papeles | Contrato semanal | Horas anuales |
|---|---|---|---|
| Gerencia | Gerencia + coordinación + sala (**nunca cocina**) | Autónoma · **ciclo fijo ≈ 39,1 h/semana** | ≈ **2.034 h** + coberturas |
| Coordinadora 1 | Coordinación (+ cocina fin de semana) | **32 h** | ≈ **1.403 h** |
| Coordinadora 2 | Coordinación (+ cocina fin de semana) | **21,5 h** | ≈ **943 h** |
| Tienda 1 | Sala | **21,5 h** | ≈ **943 h** |
| Tienda 2 | Sala | **21,5 h** | ≈ **943 h** |
| Tienda 3 | Sala | **21,5 h** | ≈ **943 h** |

**Horas contratadas del equipo (sin gerencia): 118 h/semana · ≈ 5.174 h/año.**

La gerencia es **autónoma**, pero **no es un comodín sin horario**: tiene un **ciclo fijo de 4 semanas**
y **encima** cubre huecos. Ver §1b.

### 1b · El ciclo de la Gerencia (4 semanas)

**[NEGOCIO] Está ligado al de las coordinadoras: la semana 1 de la Gerencia coincide con la semana 1
de las coordinadoras.** El marco de 4 semanas es, por tanto, **compartido** entre las tres.

| Semana | Horario | Horas |
|---|---|---|
| **1** | Lunes a viernes **7:00–14:30** · **sábado LIBRE** · domingo **8:00–15:00** | 44,5 |
| **2** | Lunes a viernes **7:00–14:30** | 37,5 |
| **3** | Lunes a viernes **7:00–14:30** · **sábado LIBRE** · domingo **8:00–15:00** | 44,5 |
| **4** | Lunes a jueves **7:00–14:30** · **viernes, sábado y domingo LIBRES** | 30 |

**Ciclo: 156,5 h · media 39,125 h/semana · ≈ 2.034,5 h/año.**

**Días intocables:** los **sábados de las semanas 1 y 3** («los necesito siempre») y el **viernes,
sábado y domingo de la semana 4**.

**Festivos:** trabaja **casi todos**, con horario **8:00–15:00**, pero **los días libres de la semana 4
se respetan siempre**, aunque caiga festivo. El resto puede variar, aunque procura que no.

**Validación cruzada:** este ciclo reproduce **exactamente** lo medido en la hoja `Turnos Gerencia` de
las plantillas reales (44,5 / 37,5 / **46,5** / 30), con **una sola diferencia**: en la semana 3 la
plantilla tiene además un **sábado de apoyo de 2 h** (`8:00–10:00`). Son 2 h × 13 ciclos = **26 h al
año** de cobertura extra. **Dos fuentes independientes coinciden salvo un turno.**

> **[NEGOCIO] Corrección del modelo.** Una versión anterior de este documento decía que la gerencia es
> «autónoma, sin tope, comodín». Es autónoma, sí, pero **tiene un horario fijo de ≈ 39,1 h/semana
> ≈ 2.034 h/año**, y solo *además* cubre huecos. No es una figura sin horario.

---

## 2 · Horario de apertura y turnos de trabajo

### Apertura de la tienda

| Temporada | Lunes a viernes | Sábado | Domingo y festivos |
|---|---|---|---|
| **Normal** | 8:00–14:30 y 17:00–21:00 | 9:00–14:30 y 17:00–21:00 | 10:00–14:30 y 17:00–21:00 |
| **Verano** (junio, julio, agosto y hasta mediados de septiembre) | 9:00–14:30 y 17:30–21:00 | 9:00–14:30 y 17:30–21:00 | 10:00–14:30 y 17:00–21:00 |

**70,5 h de apertura semanal** en temporada normal · **62,5 h** en verano.

### Turnos de trabajo [NEGOCIO] — son HORAS FIJAS

| Temporada | Lunes a viernes | Sábado y domingo |
|---|---|---|
| **Normal** | **7:00–14:30** y **17:00–21:30** | **8:00–15:00** y **17:00–21:30** |
| **Verano** | **lunes a sábado**: **8:00–14:30** y **17:30–21:30** | **domingo**: **8:00–15:00** y **17:00–21:30** |
| **Festivos** (todos los del año) | **8:00–15:00** y **17:00–21:30** | igual |

> **CORRECCIÓN.** Una versión anterior de este documento decía que el turno se obtiene «entrando 1 hora
> antes y saliendo media hora después». **Los turnos son horas fijas y no se deducen.** La relación
> existe, pero **no es la regla**, y **no se cumple igual en todos los casos**:

| Caso | Abre | Turno de mañana | Entra |
|---|---|---|---|
| Normal, lunes a viernes | 8:00 | 7:00–14:30 | 1 h antes |
| Normal, sábado | 9:00 | 8:00–15:00 | 1 h antes |
| **Normal, domingo** | 10:00 | 8:00–15:00 | **2 h antes** |
| Verano, lunes a sábado | 9:00 | 8:00–14:30 | 1 h antes |
| **Verano, domingo** | 10:00 | 8:00–15:00 | **2 h antes** |
| **Festivos** | 10:00 | 8:00–15:00 | **2 h antes** |

En cambio **la tarde sí termina siempre 30 minutos después de cerrar**: `17:00–21:30` y `17:30–21:30`
con cierre a las 21:00.

**Turnos parciales que existen:** `11:00–14:30` (tienda, lunes y viernes, **opcional**) y el **apoyo
del jueves de 3 h** (`9:30–12:30` o `10:00–13:00`).

**[NEGOCIO] 24 y 31 de diciembre: la jornada termina a las 18:30.** Coincide con lo que dice el
convenio, y **lo confirma la propiedad**: esos dos días se acaba antes.

---

## 3 · Mínimos de personal [NEGOCIO]

| Día | Desde la apertura | Desde las 11:00 | Tarde |
|---|---|---|---|
| **Lunes y viernes** | **2 personas desde la apertura**: 2 coordinadoras, o gerencia + 1 coordinadora | la 3.ª (**tienda**) es **opcional**, de **11:00 a 14:30** | **1** |
| **Martes y miércoles** | **1 persona** (gerencia o coordinadora) | **2 personas** (gerencia/coordinadora + tienda) | **1** |
| **Jueves** | **1 persona hasta las 9:00** | a las **9:00 → 3 personas** (2 coordinadoras + 1 persona de tienda, o gerencia + coordinadora + tienda) **+ 1 de apoyo 3 h** (`9:30–12:30` o `10:00–13:00`) | **1** |
| **Sábado** | **3 personas**: coordinadora a las **8:00**, **otra coordinadora a las 10:00** y **tienda a las 10:30** — las tres hasta las **15:00** | | **1** |
| **Domingo y festivos** | a las **8:00 → 1 persona** (coordinadora o gerencia) | a las **9:00 entran la cocinera (coordinadora) y una persona de tienda** → **3 personas hasta las 15:00** | **1** |

**Todas las tardes del año: 1 sola persona**, tienda; y si no hay más remedio, coordinadora.

### El sábado, con detalle [NEGOCIO]

| Hora | Quién entra |
|---|---|
| **8:00** | **1 coordinadora** (abre) |
| **10:00** | **otra coordinadora** — **salvo cuando le toque librar** según su ciclo de 4 semanas |
| **10:30** | **1 persona de tienda** |
| **15:00** | **Salen las tres** |

**Con las dos coordinadoras: 3 personas.** Cocina **la que entra más tarde** (la de las 10:00) y la de
las 8:00 lleva la coordinación.

**Cuando la segunda coordinadora libra: 2 personas.** La de las 8:00 pasa a ser
**«cocinera-coordinadora»** (hace las dos cosas) y la persona de tienda entra a las 10:30.

> **CORRECCIÓN.** Tenía apuntado que el sábado eran **2 personas** «una a las 8:00 y otra a las
> 10:30». Eso es el **mínimo**, no lo normal: **lo normal son 3**, con la segunda coordinadora
> entrando a las **10:00** (no a las 10:30, que es la persona de tienda).

### Consecuencia: la tienda funciona con UNA persona buena parte del día, y es a propósito

| Día | Hueco de una sola persona en la mañana |
|---|---|
| Lunes y viernes | **ninguno**: 2 desde la apertura |
| Martes y miércoles | 7:00–11:00 |
| Jueves | 7:00–9:00 |
| Sábado | **8:00–10:00** (y 8:00–10:30 si la 2.ª coordinadora libra) |
| Domingo y festivo | 8:00–9:00 |
| **Todas las tardes** | **toda la tarde, 1 persona** |

> **[NEGOCIO] Corrección de un diagnóstico mío.** En la sesión S-11 medí los huecos de una sola
> persona del calendario generado (**81 %** de los días de invierno), los comparé con las plantillas
> reales (**39 %**) y **concluí que el calendario «adelgazaba la tienda»**. **Ese diagnóstico era
> infundado:** las reglas **permiten** una sola persona en la mañana **5 de los 7 días** y **en todas
> las tardes**. No me faltaban datos: **me faltaban las reglas**, que son las de esta sección.
>
> **El defecto real del calendario generado es otro, y ya está medido** contra estas reglas
> (`.tools/verificar-minimos-reales.py`): **149 incumplimientos**, todos de dos tipos.
>
> | Regla incumplida | Días |
> |---|---|
> | **Lunes y viernes: 2 personas desde la apertura** | **99** (de 104 lunes y viernes del año) |
> | **Jueves: 3 personas a las 9:00 y apoyo de 3 h** | **50** (de 52 jueves) |
>
> **Todo lo demás lo cumple**: domingos y festivos, sábados, martes y miércoles, y las tardes.
> Es decir, el calendario no era «demasiado fino»: **es que se saltaba dos reglas y las saltaba
> casi siempre**.

---

## 4 · El asador

Se asan **pollos y codillos**, y también **costilla**; se fríen **patatas y croquetas**, y se
preparan **raciones varias**.

**Decisión [NEGOCIO]:** ante la dificultad de encontrar cocinero para fines de semana y festivos, y
tras experiencias decepcionantes, **las coordinadoras asumen la cocina los sábados, domingos y
festivos**.

### Horario de cocina [NEGOCIO]

**Empieza a las 9:00 o a las 10:00 y termina a las 15:00.** Es decir, entre **5 y 6 horas**.

### Reparto del papel de cocina [NEGOCIO]

| Personas en el turno | Reparto |
|---|---|
| 3 (p. ej. sábado por la mañana) | **Cocinera + coordinadora + tienda** |
| 2 | **Cocinera-coordinadora** (misma persona) **+ tienda** |
| **Dos coordinadoras coinciden** | **Cocina la que entra MÁS TARDE** |

La última es la regla más concreta y la más fácil de equivocar a mano.

### Consecuencias duras para el sistema

1. **Sin coordinadora (o gerencia) no hay asador.** Sábados, domingos y festivos tiene que haber
   siempre una coordinadora o la gerencia en el turno. **Es una restricción del cuadrante, no una
   preferencia.**
2. **La cocina es un papel superpuesto, no un rol excluyente.** Una persona es cocinera *y*
   coordinadora a la vez: los papeles se acumulan, no se sustituyen.
3. El asador **no es reposición ni venta: es elaboración**, con sus propias tareas e indicadores.

**[falta]** Si quien cocina está 5-6 horas en la cocina, **¿puede además atender el mostrador?** De
la respuesta depende cuánta gente hace falta realmente esos días.

---

## 5 · Vacaciones [NEGOCIO]

- **Todo el mundo coge 30 días naturales.** En **períodos mínimos de 15 días**, que **empiezan siempre
  en lunes**, y a veces en **períodos de 7 a 8 días**.
- **Normalmente las eligen las trabajadoras.**
- En verano se procura que **como mucho coincidan 2 personas, y una semana**.
- **Las coordinadoras** las cogen cuando quieren y se cubren entre ellas ajustando los horarios.
- **La gerencia** las coge cuando puede.

**Las horas de las vacaciones no hace falta contarlas [NEGOCIO]:** «da igual las horas que cada una
utilice para las vacaciones, ya que con los horarios improvisados de verano se cuadran para cumplir
con el número de horas anuales». Eso simplifica el cómputo: **solo hay que cuadrar el año, no cada
período vacacional.**

**El mecanismo del verano [NEGOCIO]:** de junio a la segunda quincena de septiembre los horarios se
modifican para (a) cubrirse sin contratar y (b) **cuadrar las horas por convenio de cada persona**.

> **En verano no se baja a 2 personas por ahorrar: es el mecanismo de ajuste de horas anuales.**

Por eso el objetivo del generador de cuadrantes no es «cubrir la tienda», sino:

> **Cubrir la tienda cumpliendo las reglas de dotación, mientras las horas anuales de cada persona
> aterrizan exactamente en las de su contrato.**

**[falta]** ¿Esos **30 días naturales** son iguales para una jornada de 32 h que para una de 21,5 h?
(El convenio fija 22 días laborables en semana de 5 días y 26 en semana de 6.)

---

## 6 · Convenio de comercio de alimentación de Álava

> **[NEGOCIO] Qué convenio se aplica.** Se toma como referencia **el último convenio publicado** hasta
> que salga uno nuevo. **No se actualiza cada año**: puede tardar **hasta 5 años**. Por tanto las
> cifras de abajo (**1.746 h para 2024**) **siguen vigentes** hasta que se publique otro.

Datos extraídos del texto del convenio. Fuentes consultadas:
[BOP de Álava, 15/01/2024 (CC.OO.)](http://www.ccoo-servicios.es/archivos/euskadi/20250115_Conv-Alimetacion-Alava-2024.pdf)
y [texto anterior (LAB)](http://biltegia.lab.eus/Hitzarmenak/Zerbitzuak/Merkataritza/Araba/Arabako%20elikagaien%20merkataritzarako%20hitzarmen%20kolektiboa.%20%20%20.pdf).

| Concepto | Dato | Artículo |
|---|---|---|
| Jornada semanal máxima | **40 h** de trabajo efectivo | Art. 4 |
| **Jornada anual máxima** | **1.746 h efectivas para 2024** · 1.754 h para 2023 | Art. 4 |
| **Vacaciones** | **22 días laborables** en semana de 5 días; **26** en semana de 6 días | Art. 9 |
| **Festivos anuales** | **14** | Calendario laboral |
| **Bolsín horario** | La empresa puede disponer de hasta **15 h/año** por persona | Art. 8 |
| **Distribución irregular** | Limitada al **5 % de la jornada anual** | — |
| Calendario laboral | La empresa debe fijarlo **en enero** y entregar copia individual a cada persona: jornada anual, jornada diaria, descansos, vacaciones y 14 festivos | — |
| Fiestas del sector | **Las de la LOCALIDAD del centro de trabajo** (calendario oficial + fiestas patronales locales). La lista de Vitoria (Olárizu, 4 de agosto, La Blanca, San Miguel) es solo el criterio por defecto. Medias jornadas **en turno de mañana** por el cierre de tardes, **manteniéndose la jornada anual** | Art. 4 |
| 24 y 31 de diciembre | La jornada termina **como máximo a las 18:30** | — |
| Domingos y festivos | **Plus** específico | Art. 18 |
| Pluses | Hornero, cámaras frigoríficas negativas, domingos y festivos | Art. 13 |

### Horas anuales por contrato (prorrateo de 1.746 h · año 2024)

| Contrato | Cálculo | Horas/año | Tope de distribución irregular (5 %) |
|---|---|---|---|
| 40 h (jornada completa) | 1.746 | 1.746 | 87,3 h |
| **32 h** (Coordinadora 1) | 1.746 × 32/40 | **1.396,8** | 69,8 h |
| **21,5 h** (Coordinadora 2 y 3 personas en tienda) | 1.746 × 21,5/40 | **938,5** | 46,9 h |

> **CORRECCIÓN.** Una versión anterior de este documento usaba **1.754 h** porque me detuve en la
> primera cifra del artículo y no leí la frase siguiente, que dice: *«Para el año 2024 la jornada
> máxima anual será de 1746 horas efectivas de trabajo.»* La cifra de 2024 es **1.746 h**. Si existe
> un convenio posterior, hay que volver a sustituirla.

**[inferencia]** El tope del 5 % es una restricción de primer orden para el generador: **no se puede
mover a una persona más de ~47 h al año** respecto de su jornada regular. Es margen, no comodín.

**[inferencia]** Nótese que 22 días laborables ≈ un mes. Las «vacaciones de un mes» que describe la
propiedad **coinciden con el convenio**.

### Advertencias sobre estos datos

1. **La cifra de 1.754 h es la referencia de 2023** en el texto consultado. **[falta]** Hay que
   confirmar la cifra vigente del año en curso.
2. Las **fiestas del sector** listadas son de Vitoria (Olárizu, La Blanca, 4 de agosto). **[falta]**
   Confirmar cuáles aplican en una tienda de **Luiaondo (Ayala)**, porque la lista es provincial
   pero algunas son locales de Vitoria.
3. **No soy asesoría laboral.** Estas cifras sirven para construir y validar el modelo; la cifra
   que cuenta es la que aplique la asesoría en las nóminas.

---

## 7 · Festivos [NEGOCIO]

**Lista definitiva, dictada por la propiedad.** Los tres de Semana Santa son **móviles**: dependen de
la Pascua de cada año.

| Fecha | Festividad | |
|---|---|---|
| **1 de enero** | Año Nuevo | **TIENDA CERRADA** |
| 6 de enero | Día de Reyes | |
| 19 de marzo | Día del Padre | |
| **Jueves Santo** | móvil | |
| **Viernes Santo** | móvil | |
| **Lunes de Pascua** | móvil | |
| 28 de abril | **San Prudencio** | |
| 1 de mayo | Día del Trabajador | |
| 25 de julio | Día de Santiago | |
| 15 de agosto | Nuestra Señora | |
| 12 de octubre | Día de la Hispanidad | |
| 1 de noviembre | Día de Todos los Santos | |
| 6 de diciembre | Día de la Constitución | |
| 8 de diciembre | La Inmaculada Concepción | |
| **25 de diciembre** | Navidad | **TIENDA CERRADA** |

**Los dos días de tienda cerrada no se trabajan.** El resto se trabajan con horario de festivo
(**8:00–15:00 y 17:00–21:30**) y dotación de domingo.

### Cómo caen en 2026

| Fecha | Día | Festividad | Qué pasa |
|---|---|---|---|
| 01/01 | jueves | Año Nuevo | **CERRADA** |
| 06/01 | martes | Reyes | se trabaja |
| 19/03 | jueves | Día del Padre | se trabaja |
| 02/04 | jueves | Jueves Santo | se trabaja |
| 03/04 | viernes | Viernes Santo | se trabaja |
| 06/04 | lunes | Lunes de Pascua | se trabaja |
| 28/04 | martes | San Prudencio | se trabaja |
| 01/05 | viernes | Día del Trabajador | se trabaja |
| 25/07 | **sábado** | Santiago | se trabaja |
| 15/08 | **sábado** | Nuestra Señora | se trabaja |
| 12/10 | lunes | Hispanidad | se trabaja |
| 01/11 | **DOMINGO** | Todos los Santos | **no genera trabajo aparte** |
| 06/12 | **DOMINGO** | Constitución | **no genera trabajo aparte** |
| 08/12 | martes | Inmaculada | se trabaja |
| 25/12 | viernes | Navidad | **CERRADA** |

> **En 2026 se trabajan 11 festivos** que no caen ni en domingo ni en día de cierre.

### Correcciones sobre suposiciones anteriores

1. **San Prudencio (28 de abril) queda CONFIRMADO.** Estaba bien supuesto.
2. **La Magdalena (22 de julio) NO es festivo.** Yo lo supuse a partir de las fiestas del
   ayuntamiento y **estaba equivocado**: no está en la lista. **El calendario 2026 generado lo incluyó
   como festivo, y ese día es laborable.**
3. **[falta] Cuadre de la cifra.** El convenio habla de **14 festivos anuales**; esta lista tiene
   **15 fechas** (13 sin contar los dos cierres), y **en 2026 solo se trabajan 11** porque el 1 de
   noviembre y el 6 de diciembre caen en domingo. Conviene confirmarlo con la asesoría, porque
   **cambia el reparto de festivos entre las personas**.

**La tienda está en Luiaondo (Luiaondo/Luyando), municipio de Ayala/Aiara, Álava.**

---

## 8 · Lo que falta

| # | Qué | Para qué | Estado |
|---|---|---|---|
| 1 | **Plantillas de horarios en Excel** | Fuente de verdad de los patrones reales | **Pedido** |
| 2 | Cifra vigente de **jornada anual** y fiestas del sector aplicables en Ayala | Cómputo legal | Parcial (§6) |
| 3 | **Calendario de festivos locales** del año | Asador, fichaje y cómputo | Pedido |
| 4 | **Vacaciones de las coordinadoras**: cuántas semanas por convenio | Cuadrante de verano | Pedido |
| 5 | **Duración real del turno de cocina** y si permite atender mostrador | Dotación de sábados, domingos y festivos | Pedido |
| 6 | **Margen de preparación y recogida** sobre la apertura | Modelar turno ≠ apertura | Saldrá del Excel |

---

## 9 · Lo que dicen las plantillas reales

Análisis de `PlantillasHorarios.xlsx` (4 hojas: Gerencia, Encargadas, Tienda y una vacía).
Script reproducible: `.tools/analizar-horarios.py`.

### Reglas CONFIRMADAS por los datos

| Regla | Evidencia en las plantillas |
|---|---|
| **El turno de apertura empieza 1 h antes de abrir** | Turno `7–14:30` con apertura a las 8:00 · `8–15` con apertura a las 9:00 (sábado) · `9–15` con apertura a las 10:00 (domingo) |
| **El turno de tarde acaba 30 min después de cerrar** | Turno `17–21:30` con cierre a las 21:00 |
| **El apoyo del jueves son 3 horas exactas** | La Coordinadora 2 hace `9–12` los jueves en las 4 semanas: **3,0 h**. Es la «tercera persona de apoyo» que describe la propiedad |
| **El ciclo de las personas de tienda es de 3 semanas** | Tres turnos que se repiten: **mañana, tarde y fin de semana** |
| **El ciclo de las coordinadoras es de 4 semanas** | Cuatro semanas que vuelven a la primera |
| **Dos ciclos distintos (3 y 4 semanas)** | Se realinean cada **12 semanas** (mínimo común múltiplo). El generador tiene que manejar los dos |
| **`$$$` = plus por trabajar de 2 cuando tocaban 3** | Marca privada de la propiedad: ese día se paga un **pequeño plus** a quien cubre con menos gente de la debida |

### Catálogo real de turnos (extraído, no inventado)

| Turno | Duración | Cuándo |
|---|---|---|
| 7:00 – 14:30 | 7,5 h | apertura larga (invierno) |
| 7:00 – 13:30 | 6,5 h | |
| 7:00 – 13:00 | 6,0 h | |
| 8:00 – 15:00 | 7,0 h | apertura sábado / domingo |
| 9:00 – 15:00 | 6,0 h | domingo |
| 9:00 – 12:00 | **3,0 h** | **apoyo del camión, jueves** |
| 9:30 – 14:30 | 5,0 h | mañana de jueves |
| 10:00 – 15:00 | 5,0 h | |
| 10:30 – 15:00 | 4,5 h | sábado |
| 11:00 – 14:30 | 3,5 h | mañana corta |
| 8:00 – 10:00 | 2,0 h | apoyo sábado |
| **17:00 – 21:30** | **4,5 h** | tarde, con la media hora de recogida |

### Horas que generan las plantillas

> **CORRECCIÓN METODOLÓGICA.** La primera versión de este análisis comparaba la media semanal de
> cada persona con sus horas semanales de contrato y multiplicaba la diferencia por 52. **Eso está
> mal** y la propiedad lo detectó. Las horas anuales del convenio (**1.746 h** a jornada completa)
> son horas **efectivas de trabajo**: ya excluyen vacaciones y festivos. Multiplicar por 52 una
> desviación semanal mezcla dos bases distintas y exagera el resultado.
>
> La comparación correcta es **anual**: horas que genera el ciclo × semanas realmente trabajadas
> (52 − vacaciones − festivos) contra las horas anuales del contrato. Con ese método la desviación
> deja de ser de decenas de horas y pasa a ser de un orden de magnitud menor — coherente con lo que
> dice la propiedad: **el exceso o el déficit se ajusta con los horarios de verano.**

| Persona | Ciclo | Media semanal | Horas/año de contrato (2024) |
|---|---|---|---|
| Gerencia | 4 semanas | **39,6 h** | autónoma → ≈ **2.060 h/año** |
| Coordinadora 1 | 4 semanas | 31,25 h | 1.396,8 h |
| Coordinadora 2 | 4 semanas | 21,00 h | 938,5 h |
| Tienda 1, 2 y 3 | 3 semanas | 20,33 h cada una | 938,5 h cada una |

**El cálculo del saldo anual queda pendiente de las semanas de verano.** Solo con la rotación base
no se puede cerrar: el ajuste vive precisamente en las semanas en que el horario cambia.

**[NEGOCIO] Sobre la gerencia:** las filas `YO` de la hoja de encargadas son **los mismos turnos de
fin de semana vistos desde el otro lado** (se olvidaron al preparar el fichero), no horas
adicionales. Por tanto la gerencia trabaja **~39,6 h/semana ≈ 2.060 h/año**, unas **300 h más que
una jornada completa** del convenio.

### Lo que la propiedad ha aclarado (y corrige este documento)

1. **`$$$` = plus por trabajar de 2 cuando tocaban 3.** Ese día se paga un pequeño plus a quien
   cubre con menos gente de la debida. **[inferencia]** Es, de hecho, el mecanismo **actual** para
   compensar el esfuerzo extra — y por tanto el sistema debe registrarlo y repartirlo con equidad,
   o se convertirá en un motivo de pique más.
2. **No existen plantillas de asador, ni hacen falta.** La cocina va **dentro del turno de las
   coordinadoras**: no hay horas que añadir. El papel de cocinera es un sombrero superpuesto a su
   jornada, no una jornada aparte.
3. **Las filas `YO` eran un resto.** Confirmado.
4. **Ciclos distintos:** personas de tienda **3 semanas** (mañana / tarde / fin de semana), coordinadoras
   **4 semanas**. Se realinean cada 12 semanas.
5. **El saldo anual se cierra en verano.** No es que las plantillas base estén «mal»: están
   deliberadamente por debajo, y las semanas de verano son donde se mete el resto de horas.

### Huecos que siguen abiertos en este fichero

1. **No hay ninguna codificación de festivos:** cero colores de relleno en todo el libro.
2. **No aparecen las semanas de vacaciones ni las de verano**, que son justo donde el horario
   cambia y donde se cuadran las horas. → **Pendiente: Excel de horarios de verano.**

---

## 10 · El Excel de verano 2026 (referencia anonimizada)

> **Referencia de trabajo:** `docs/referencia/horarios-verano-2026-anonimizado.xlsx`.
> Es una copia **fiel al original salvo las etiquetas**: 14.997 celdas comparadas, 0 diferencias de
> fórmulas, 0 valores perdidos y 0 valores distintos. Los nombres propios se sustituyeron por
> `OP 1`–`OP 3` y `COORD 1`–`COORD 2` en 67 celdas, y se recalcularon las fórmulas para que la
> copia muestre los resultados sin necesidad de abrirla en Excel.

833 filas, una hoja con contenido (`VacasTodas2026`) y tres vacías.

### Estructura descifrada

- **B** = persona · **R** = total semanal (fórmula)
- Horas por día: **D** lunes, **F** martes, **H** miércoles, **J** jueves, **L** viernes, **N** sábado, **P** domingo
- Cada persona ocupa **2 filas** (el turno puede estar repartido entre ambas)
- **Q** = marca: `M`/`T`/`FD` para personas de tienda (mañana / tarde / fin de semana), `1ª`–`4ª` para coordinadoras
- `VAC` = vacaciones · `libre` = descanso
- El libro contiene **el verano dos veces**: una con etiquetas genéricas (`OP 1`, `COORD 1`) y otra
  con nombres propios. **Los nombres se han eliminado de este documento y de todo el proyecto:
  aquí solo se usan etiquetas.** Las personas se identifican como `OP 1`–`OP 3` y `COORD 1`–`COORD 2`.

> **Este fichero es material de APRENDIZAJE, no de corrección.** La propiedad lo ha aportado para
> que entendamos **cómo se compensa a lo largo del año el desajuste que genera la rotación**. Sus
> cifras están cuadradas y sus notas tienen origen conocido: no se corrigen ni se auditan.

### Verano completo (16 semanas, 15/06 → 04/10) · sección de etiquetas genéricas

| Persona | Horas | Media/semana | Días VAC | Días libre |
|---|---|---|---|---|
| OP 1 | 233,0 | 14,56 | 22 | 1 |
| OP 2 | 252,0 | 15,75 | 28 | 2 |
| OP 3 | 239,0 | 14,94 | 28 | 3 |
| COORD 1 | 519,0 | 32,44 | 0 | 4 |
| COORD 2 | 306,5 | 19,16 | 16 | 8 |
| Gerencia | — | — | — | 9 |

### La tabla de compensación del libro (filas 634-640)

| Persona | H. Convenio Ptes | H. Trabajadas (9 semanas) | Diferencia |
|---|---|---|---|
| OP 1 | 143 | **138** | −5 |
| OP 2 | 108 | **107,5** | −0,5 |
| OP 3 | 122,5 | **146,5** | +24 |
| COORD 1 | 279 | **310** | +31 |
| COORD 2 | — | sin fórmula | — |

**Nuestro cálculo independiente reproduce 138 / 107,5 / 146,5 clavados.** La lectura de la hoja
está validada contra el propio libro, así que el modelo de datos que construyamos a partir de ella
parte de una interpretación correcta.

### Cómo funciona el mecanismo (lo que había que entender)

1. **La rotación base del año genera un desajuste** respecto a las horas de convenio de cada persona.
2. **El verano es donde se compensa** (D-53): quien no está de vacaciones trabaja más horas, y quien
   las disfruta trabaja menos. Una parte del equipo coge además vacaciones fuera del verano, cuando
   le conviene.
3. **La tabla `H. Convenio Ptes` / `H. Trabajadas` sigue ese saldo por persona**, con ajustes
   manuales anotados cuando hace falta.
4. **No es un error de las plantillas: es un equilibrio gestionado.** Por eso el objetivo del
   generador no es «cuadrar la semana», sino **cerrar el año**.

### Observaciones de forma (no de fondo)

1. **Las dos secciones del libro usan semanas distintas:** la de etiquetas va de **lunes a domingo**;
   la otra, de **martes a lunes** (30/06/2026 es martes). El mismo día cae en semanas diferentes
   según dónde se mire, y eso desplaza horas entre semanas. Conviene unificar el criterio antes de
   automatizar, o el cómputo arrastrará ese desfase.
2. **No todos los cómputos del libro están cerrados por fórmula.** Alguno se calcula a mano.
3. **El horario de la gerencia es fijo y por eso no figura en las hojas de turnos variables.** Es un
   dato conocido, no un olvido.

## 11 · Festivos

### Cómo se trabaja un festivo [NEGOCIO]

- **El turno se mantiene** (quien estaba asignado sigue asignado), pero **se trabaja con el horario
  de un domingo**: **10:00–14:30 y 17:00–21:00**.
- **Dotación de un festivo, igual que un domingo:** **1 Gerencia + 1 coordinadora + 1 persona de tienda**, o
  bien **2 coordinadoras + 1 persona de tienda**. En total, **3 personas**.
- **Una de las coordinadoras que trabaje es siempre la cocinera.** No tiene por qué ser la misma:
  **lo ideal es que se vayan turnando**.

### Reparto de festivos [NEGOCIO]

1. **El festivo lo cubre UNA sola persona de tienda, a jornada completa** (mañana y tarde), para que **las
   otras dos disfruten del festivo entero** — en lugar de trabajar una por la mañana, otra por la
   tarde y que solo una lo libre.
2. **Los festivos se reparten equitativamente** entre las personas.
3. **La Gerencia nunca es la cocinera.** Puede **ayudar** en la cocina, pero no hacer de cocinera.
   Por tanto **en un festivo tiene que haber siempre al menos una coordinadora**: sin coordinadora
   no hay asador, y la gerencia no puede sustituirla en esa función.

**[inferencia] Objetivo numérico de reparto.** Con **14 festivos al año**:

| Colectivo | Reparto | Por persona |
|---|---|---|
| 3 personas en tienda (1 por festivo) | 14 entre 3 | **4 o 5 festivos cada una** |
| 2 coordinadoras (la cocinera rota) | 14 entre 2 | **7 cada una** |

### Tensión detectada en la regla de la cocina

La regla vigente dice **«cocina la que entra más tarde»**. La intención nueva es que **se turnen**.
**Las dos cosas pueden chocar:** si una coordinadora entra siempre más tarde, **cocinará siempre
ella** y no habrá alternancia.

**Propuesta:** mantener la regla como criterio por defecto y añadir un **interruptor de equidad**:
el sistema recuerda quién cocinó la última vez y, si le tocaría repetir dos veces seguidas,
**invierte las horas de entrada** de las dos coordinadoras ese día. Se conserva la lógica («entra más
tarde, cocina») y se logra la rotación sin excepciones a mano.

---

## 12 · Preferencias del personal

Se recogen **persona a persona** y **no son obligaciones**: son restricciones blandas que el
generador intenta cumplir y **puede no cumplir si chocan con la cobertura**.

### PG (tienda)

| Situación | Preferencia |
|---|---|
| Verano, en general | **Trabajar un día entero y librar otro**, en lugar de dos medios días |
| Días de mucho calor | **Solo medio día** |

**[inferencia] Qué está pidiendo en realidad:** que se **eliminen los turnos fragmentados**. Su
queja no es contra el medio día en sí, sino contra **partir la jornada en trozos pequeños** (los
turnos de 3, 3,5 y 4,5 horas). Trabajar 10,5 h y librar el día siguiente da **más días libres
completos** con las mismas horas.

### Cuándo hace mucho calor [DATO EXTERNO]

Estación **AEMET de Amurrio**, a 6,6 km de Ayala:

| Mes | Media |
|---|---|
| Junio | 19 °C |
| **Julio** | **21 °C** |
| **Agosto** | **21 °C** |
| Septiembre | 19 °C |

Fuente: [clima de Ayala/Aiara (AEMET, estación de Amurrio)](https://todopueblos.es/municipio/ayala-01476/clima/).

- **Julio y agosto están empatados** a una décima. La propia fuente se contradice sobre cuál es el
  más cálido (20,6 °C julio / 20,7 °C agosto): es un empate estadístico, no un dato.
- Los **episodios de calor fuerte** tienden a concentrarse en **agosto** (Euskalmet sitúa el más
  destacado del verano de 2022 entre el 10 y el 13 de agosto).
- **Conclusión: la ventana de calor va de mediados de julio a mediados de agosto.**

> **El cuadrante se entrega 15 días antes y no se modifica después** salvo emergencia (D-71). Por
> eso **no se puede decidir «el día antes»**: el calor es una **preferencia que se aplica al
> planificar**, no un mecanismo reactivo. Y es una preferencia **opcional**: si no encaja, no se
> aplica y no pasa nada.

---

## 13 · Información de entrada para el cuadrante de verano

**Esto NO son propuestas para cambiar los turnos.** Los turnos y la rotación **están como están**.
Lo que sigue son **datos y preferencias que hay que tener en cuenta al construir el cuadrante de
verano**, cuando alguien coge vacaciones y hay que cubrirla. **No son obligaciones**: hasta ahora no
se han aplicado. Si al planificar resultan una mejora —sobre todo para el negocio— se pueden usar;
si no, se hace como siempre.

### Restricciones duras del cuadrante

| # | Restricción |
|---|---|
| R-1 | **El cuadrante se entrega 15 días antes.** No se modifica después, salvo emergencia |
| R-2 | **Los turnos no se cambian de un día para otro.** Lo que cambia en tiempo real son las **tareas**, no los turnos |
| R-3 | Sin **coordinadora** no hay asador; la gerencia no puede sustituirla en la cocina (D-66) |
| R-4 | Festivos y domingos: **3 personas**, con horario de domingo (D-63, D-64) |

> **Distinción clave:** el motor de tareas puede reasignar trabajo en tiempo real —para eso está—,
> pero **el cuadrante de turnos es un documento cerrado con 15 días de antelación**. Confundir las
> dos cosas es la forma más rápida de que el equipo deje de fiarse del horario.

### Entradas del cuadrante

**1 · Preferencia de PG: día entero y día libre.** Se aplica **al planificar el verano**, cuando hay
que cubrir vacaciones: en lugar de partir su jornada en dos medios días, se le pueden dar **días
completos (10,5 h: 8:00–14:30 + 17:00–21:30) alternados con días libres**. Mismas horas, más días
libres completos, y menos días de presencia.

**2 · Preferencia de PG sobre el calor (opcional).** En la parte más calurosa del verano prefiere
**solo medio día** (mañana o tarde); en la más suave, **mañana y tarde**. Se resuelve **al planificar**,
sabiendo que la ventana cálida va de mediados de julio a mediados de agosto. Como el cuadrante se
hace con 15 días de antelación, **es subjetivo**: si no encaja, no se aplica.

**3 · Reparto equitativo de festivos (esto SÍ es un cambio pedido).** Hoy hay años en que la misma
persona trabaja más festivos que las demás. Con **14 festivos al año**, el objetivo es:

| Colectivo | Por persona |
|---|---|
| 3 personas en tienda (una por festivo, a jornada completa) | **4 o 5 festivos** |
| 2 coordinadoras (turnándose la cocina) | **7 festivos** |

El sistema lleva la cuenta y **asigna el festivo a quien menos lleve**, en lugar de depender de la
memoria.

### Retiradas

| # | Propuesta retirada | Motivo |
|---|---|---|
| ~~P-2~~ | Reducir el catálogo de turnos de 9 a 3 o 4 | **La rotación y los turnos no se tocan.** No era una propuesta pedida y no procede |
| ~~P-4~~ | Gestionar el calor de forma reactiva, el día antes | **Imposible: el cuadrante se entrega 15 días antes** y no se modifica salvo emergencia |

---

## 14 · Errores míos, registrados

Se anotan para que nadie vuelva a razonar sobre ellos.

| # | Error | Corrección |
|---|---|---|
| E-1 | **91 h/semana de apertura** (calculé 13 h/día los 7 días) y sobre esa cifra argumenté que hacían falta 3 coordinadoras | Son **70,5 h** (invierno) y **62,5 h** (verano): hay cierre de mediodía. La plantilla correcta es **2 coordinadoras + 3 personas en tienda** |
| E-2 | **Jornada anual de 1.754 h** | Es la de **2023**. La de **2024 es 1.746 h**. Me detuve en la primera cifra del artículo 4 y no leí la frase siguiente. Lo detectó la propiedad |
| E-3 | **Desvío de −61 h/año por tienda** y **−247 h/año del equipo** | Método incorrecto: multipliqué una desviación semanal por 52, cuando las horas anuales del convenio **ya excluyen vacaciones y festivos**. El desajuste es real y **se compensa en verano**, que es justo lo que la propiedad venía diciendo |
| E-4 | Presenté como **desequilibrio** que una coordinadora no coja vacaciones en verano | **Era una decisión libre y acordada**: las dos coordinadoras prefieren otras fechas y tienen libertad para elegirlas porque su trabajo lo permite. Convertí un acuerdo entre ellas en una injusticia |
| E-5 | Traté sus cifras como algo que **había que verificar y corregir** | El fichero se aportó para **entender el mecanismo**, no para auditarlo. Las cifras están cuadradas y sus notas tienen origen conocido |
| E-6 | Convertí una **preferencia de planificación** (día entero y día libre) en una **propuesta de rediseñar el catálogo de turnos**, y propuse **cambiar el horario el día antes** | Ni los turnos ni la rotación se tocan, y el cuadrante se entrega **15 días antes**. Lo que me dieron eran **entradas para el cuadrante de verano**, no un encargo de rediseño |
| E-7 | **Diagnostiqué que el calendario «adelgazaba la tienda»**, comparando los huecos de una sola persona (81 %) con las plantillas reales (39 %) | **Infundado.** Las reglas **permiten** una sola persona en la mañana **5 de los 7 días** y **en todas las tardes**: es el diseño, no un defecto. **Me faltaban las reglas, no los datos.** El defecto real, medido después, son **149 incumplimientos concretos**: 99 lunes y viernes y 50 jueves |
| E-8 | **Deduje la relación entre turno y apertura** («se entra 1 h antes y se sale 30 min después») en lugar de pedir los horarios | **Los turnos son horas fijas.** La relación existe pero **no se cumple igual**: domingos y festivos se entra **2 h antes**. Deduje una regla de una coincidencia |
| E-9 | **Presenté como un «descubrimiento» que la tienda cierra al mediodía**, al llegar al cierre de tienda | **Ya lo tenía escrito desde el principio**, en la tabla de horarios de **§2 de este mismo documento** y en `MANUAL.md` §5: **cierra de 14:30 a 17:00**. Y el turno de mañana **termina a las 14:30**, que también estaba en §2. **El fallo no fue el dato: fue no cruzar dos cosas que ya tenía.** Ese cruce —*el turno acaba cuando la tienda cierra, luego la mañana acaba con un cierre*— es lo que debí ver al estructurar el cierre, no cuatro mensajes después |

**Patrón de E-1, E-2 y E-3:** comparar magnitudes de bases distintas y dar por bueno el primer
número que encuentro. Los tres apuntaban en la misma dirección —más horas de las reales—, que es
justo la dirección en la que uno no se cuestiona el resultado.

**Patrón de E-4, E-5 y E-6:** **recibir información y responder proponiendo un cambio.** Me cuentan
un hecho y yo devuelvo una reforma. Lo que se me pide la mayoría de las veces es **entender y
guardar**, no rediseñar.

**Patrón de E-7 y E-8, el más caro:** **deducir las reglas a partir de los datos.** Los datos no
dicen lo que está *permitido*: dicen lo que *pasó*. De una coincidencia saqué una regla (E-8), y de
una ausencia saqué un defecto (E-7). **Las dos veces el error se habría evitado preguntando antes de
concluir.**

**Patrón de E-9, distinto y también caro:** **no cruzar lo que ya tengo.** El dato del cierre de
mediodía estaba en la tabla de horarios de §2 desde el primer día, junto al turno que termina a las
14:30. **Los dos datos estaban a una línea de distancia y no los junté.**
→ **Norma:** antes de concluir algo sobre un momento del día, **mirar los horarios que ya están
escritos**. Casi todo lo que necesito para eso ya lo tengo.

> **Esto también es un requisito de producto.** Si la aplicación propone cambios cada vez que ve un
> dato, se convierte en ruido y el equipo deja de leerla. **Propone cuando merece la pena; el resto
> del tiempo, informa.**

**Patrón de E-4 y E-5, que es más grave:** **deducir una injusticia a partir de un dato.** Vi
«cero días de vacaciones en verano» y concluí «el peso cae sobre ella», cuando lo que había era una
decisión tomada libremente por las dos.

> **Esto es un requisito de producto, no una anécdota.** La aplicación existe, en parte, para
> acabar con el «yo sí, tú no». Si el sistema señala desequilibrios a partir de los datos sin
> preguntar antes, **se convierte en la fuente del pique que venía a resolver**. Regla: **el
> sistema muestra hechos; cuando ve una asimetría, pregunta. No acusa.**



