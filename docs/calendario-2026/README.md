# Calendario laboral 2026 — explicación

> ## ⚠️ ESTE CALENDARIO NO VALE. NO APLICAR.
>
> **Corregido en la sesión S-12, con el horario real de la propiedad sobre la mesa.**
>
> 1. **Ignora el ciclo fijo de 4 semanas de la Gerencia**, que está **ligado al de las coordinadoras**.
>    Su ciclo solo ya produce **≈ 2.034 h/año**; este calendario le da **1.472 h**. Es decir,
>    **elimina unas 560 h de su presencia en la tienda**: más de una cuarta parte de su año.
> 2. **Adelgaza la tienda.** Deja **una sola persona por la mañana el 81 % de los días de invierno**,
>    frente al **39 %** de las plantillas reales. **El doble.**
> 3. Por eso decía aquí que la Gerencia «baja» de horas **como si fuera una mejora. No lo es: es que
>    hay menos gente.**
>
> **La causa:** el generador optimizó «que las horas de cada persona cuadren», que **compite** con
> «que haya gente suficiente a la vez». Puso el objetivo equivocado en primer lugar.
>
> **Se conserva como registro del intento**, no como propuesta. Ver `docs/DECISIONES.md` (aviso tras
> D-75) y `docs/RRHH-TURNOS.md` §1b.

Este documento está escrito para que se entienda sin ser programador. Explica **qué contiene** el
calendario, **por qué está montado así** y **qué precio tiene** cada decisión.

**Ficheros:**
- `calendario-2026.xlsx` — el calendario completo, mes a mes.
- `calendario-2026.json` — los mismos datos en formato máquina, por si hay que reprocesarlos.

---

## 1 · Qué hay en el Excel

| Hoja | Para qué |
|---|---|
| **01-ENERO … 12-DICIEMBRE** | Un mes por hoja. Cada semana en un bloque: filas = personas, columnas = los 7 días con la fecha, y una **columna de horas de la semana**. Es la vista para mirar y discutir |
| **CALENDARIO** | Las 52 semanas seguidas, en el mismo formato |
| **RESUMEN** | Horas anuales de cada persona, contrato, desvío, festivos, cocinas, días trabajados, días libres y pluses |
| **FESTIVOS** | Los 14 festivos, quién trabaja cada uno y una nota en los días delicados |
| **VACACIONES** | Los períodos de cada persona y los solapes entre ellas |
| **DÍAS CRÍTICOS** | Los días en que no hay margen, con la razón |

**Colores:** verde = día de cocina · amarillo = festivo · gris = vacaciones · **rojo = día crítico** ·
verde claro = fin de semana trabajado.

---

## 2 · Los turnos que se usan

**No he inventado ni un horario.** Son los que ya están en las plantillas de la tienda, ordenados por
temporada.

| Turno | Horas | Cuándo |
|---|---|---|
| 7:00 – 14:30 | 7,5 | apertura de invierno (se entra 1 h antes de abrir) |
| 8:00 – 14:30 | 6,5 | apertura de verano |
| 8:00 – 15:00 | 7,0 | sábado y domingo |
| 9:00 – 15:00 | 6,0 | domingo y festivo |
| 10:30 – 15:00 | 4,5 | sábado, segunda entrada |
| 11:00 – 14:30 | 3,5 | mañana corta |
| 9:00 – 12:00 | **3,0** | **apoyo del camión, jueves** |
| 17:00 – 21:30 | 4,5 | tarde (media hora de recogida) |
| 17:30 – 21:30 | 4,0 | tarde de verano |

**El turno nunca coincide con la apertura:** se entra antes para preparar y se sale media hora
después de cerrar. Eso está en el calendario tal cual.

---

## 3 · Cómo reparte el algoritmo

Tres reglas, por este orden:

1. **Primero se cubren los mínimos.** Nunca se deja un turno obligatorio sin cubrir. Si hay que
   elegir, se cubre.
2. **Después, cada turno va a quien más le falta** para llegar a sus horas del año. Se mide en horas
   pendientes, no en número de turnos.
3. **La Gerencia es la última de la cola.** Solo cubre lo que sobra. Es su papel real de comodín.

Además, **nadie puede trabajar dos turnos solapados** y **tiene que haber 12 horas de descanso**
entre la tarde y la mañana siguiente. Esta segunda regla fue la que más costó: mover una tarde a
alguien que entra a las 8:00 al día siguiente **no vale**, y el programa lo comprueba en las dos
direcciones.

**Las semanas son de lunes a domingo.** Las personas de tienda giran en un ciclo de 3 semanas (mañana / tarde
/ fin de semana) y las coordinadoras en uno de 4. Se mantienen los ciclos que ya usáis.

---

## 4 · El caso difícil que pediste: 25 de julio

**Sábado y festivo. COORD 2 está de vacaciones del 13 al 26 de julio.**

| | |
|---|---|
| Quiénes trabajan | **Gerencia + COORD 1 + OP 1** |
| Quién cocina | **COORD 1** |
| Por qué | Es la **única coordinadora disponible**. La Gerencia **no puede** hacer de cocinera |

**No hay alternancia posible ese día.** La cocina le toca a COORD 1 por obligación, no por turno.
Está marcado en rojo en el Excel y explicado en las hojas FESTIVOS y DÍAS CRÍTICOS.

Este es exactamente el tipo de día que a mano se escapa: cuando alguien revisa el cuadrante ve «3
personas, correcto» y no ve que **una de ellas no puede estar ahí**. El sistema sí lo ve.

---

## 5 · Las vacaciones del escenario

| Persona | Período | Días |
|---|---|---|
| OP 1 | 1 – 30 de junio | 30 |
| OP 2 | 6 de julio – 2 de agosto | 28 |
| OP 3 | 3 – 30 de agosto | 28 |
| COORD 2 | 13 – 26 de julio | 14 |
| COORD 1 | 26 de enero – 15 de febrero | 21 |

**Las tres personas de tienda nunca coinciden**, pero **COORD 2 y OP 2 coinciden dos semanas** (13–26 julio).
Eso supera la regla de «como mucho una semana de solape», y **está puesto a propósito** porque es el
caso que querías ver. Está señalado como excepción en la hoja VACACIONES.

---

## 6 · Los números reales

| Persona | Horas del año | Contrato | Desvío | ¿Dentro del 5 %? |
|---|---|---|---|---|
| COORD 1 | 1.398,0 | 1.396,8 | **+1,2** (+0,09 %) | Sí |
| COORD 2 | 939,0 | 938,5 | **+0,5** (+0,05 %) | Sí |
| OP 1 | 938,0 | 938,5 | **−0,5** (−0,05 %) | Sí |
| OP 2 | 938,0 | 938,5 | **−0,5** (−0,05 %) | Sí |
| OP 3 | 940,0 | 938,5 | **+1,5** (+0,16 %) | Sí |
| **Gerencia** | **1.472,0** | autónoma | — | — |

**Ninguna persona se desvía más de 1,5 horas al año.** El margen legal es de 46,9 h y 69,8 h: vamos
muy por dentro.

### Festivos

| | Gerencia | COORD 1 | COORD 2 | OP 1 | OP 2 | OP 3 |
|---|---|---|---|---|---|---|
| Festivos trabajados | 8 | 10 | 10 | **5** | **5** | **4** |

Las personas de tienda se reparten los 14 festivos **una por festivo y a jornada completa**, para que las
otras dos libren el día entero. Reparto: 5 / 5 / 4.

### Cocina

**58 días cada coordinadora**, exactamente iguales. **La Gerencia no cocina ni un día.**

### Plus (`$$$`)

**Cero días.** En ningún día se trabaja con menos gente de la que toca. Si se hubiera trabajado de 2
cuando tocaban 3, aparecería marcado y contado — no hay ninguno.

---

## 7 · Qué mejora respecto a como está hoy

| Mejora | Qué gana | Qué cuesta |
|---|---|---|
| **Las horas del año cuadran solas** | Nadie tiene que ajustar a mano el saldo anual ni llevar la cuenta en un Excel aparte | Ninguno: es aritmética |
| ~~**La Gerencia baja de ~2.060 h a 1.472 h al año**~~ | ~~Unas 590 horas menos~~ **FALSO: no es una mejora, es que hay menos gente en la tienda.** Ver el aviso de arriba | Este calendario **eliminaba 560 h de la presencia de la propiedad** y dejaba la tienda sola por las mañanas |
| **Cero días de plus** | Ahorro directo: ningún plus que pagar | Ninguno |
| **Cocina 58/58 entre las dos coordinadoras** | Alternancia real, sin que nadie tenga que acordarse | Ninguno |
| **Festivos repartidos 5/5/4** | Deja de haber años en que una trabaja más que las otras | Ninguno |
| **Descanso de 12 h garantizado** | Cumple con el convenio y evita jornadas imposibles | Obliga a no poner a la misma persona en la tarde del sábado y la mañana del domingo |
| **Los días sin margen salen marcados** | El 25 de julio, por ejemplo, se ve antes de que llegue | Ninguno |

---

## 8 · Lo que NO se ha podido cumplir, y por qué

Lo digo con el número delante, no lo escondo.

1. **Solape de 14 días entre COORD 2 y OP 2** (13–26 julio). **La regla dice un máximo de una
   semana.** Se ha superado **porque lo pediste expresamente** para ver el caso duro. Con ese solape,
   la cobertura sigue cuadrando: **no ha hecho falta dejar ningún día sin cubrir**. Si se redujera a
   una semana, no cambiaría nada de la cobertura — solo desaparecería el día crítico del 25 de julio.

2. **Festivos: uno de los dos locales que supuse NO existe.** Usé **28 de abril (San Prudencio)** —
   **correcto, está confirmado** — y **22 de julio (La Magdalena)**, que según la lista definitiva de
   la propiedad **NO es festivo**: ese día es laborable. Además, en esta lista **el 1 de enero y el
   25 de diciembre la tienda está CERRADA**, y aquí se trabajaban. Los tres errores mueven horas y
   obligan a rehacer el calendario.

3. **La Gerencia trabaja 1.472 horas al año.** ~~No es un fallo: es lo que hace falta para cubrir los
   mínimos.~~ **Sí es un fallo, y grave.** Su **ciclo fijo de 4 semanas** ya produce ≈ **2.034 h**.
   Este calendario **le quitaba 560 h de presencia** porque ignoraba ese ciclo. Ver el aviso de arriba
   y `docs/RRHH-TURNOS.md` §1b.

4. **Los mínimos se han cubierto siempre, pero son mínimos.** El calendario garantiza que **nunca
   hay menos gente de la que toca**. No dice nada de si hay bastante gente cuando la tienda está
   llena: eso depende de la clientela, no del cuadrante.

---

## 9 · Cómo se comprueba

El fichero `tools/verificar-calendario-2026.py` **lee el propio Excel** y comprueba una a una todas
las reglas: cobertura, horas, festivos, cocina, solapes, descanso, vacaciones y pluses. No se fía de
los cálculos intermedios.

```
python tools/verificar-calendario-2026.py
```

**Resultado: 0 fallos duros.** Quedan dos avisos, los dos explicados en el punto 8: el solape pedido
a propósito y los dos festivos locales sin confirmar.

---

## 10 · Nota sobre el 15 de agosto

También es **sábado y festivo**, y coincide con las vacaciones de OP 3 (3–30 de agosto). Ese día
**no hay problema**: quedan OP 1 y OP 2, y las dos coordinadoras están disponibles, así que la cocina
turna con normalidad. Está en la hoja DÍAS CRÍTICOS para poder comparar los dos casos.
