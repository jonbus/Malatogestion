# Las horas del año — cálculo corregido

> **Este documento corrige al anterior.** El primer cálculo daba **208 h de margen**. **Estaba mal**,
> y la propiedad lo detectó antes de que el error hiciera daño: *«con esas horas no llega ni para
> rellenar sus turnos»*.

---

## 1 · Qué hice mal

Usé **43,65 semanas** como divisor del año. Ese número sale de `1.396,8 ÷ 32` — **es la base del
convenio**, que ya descuenta lo que el convenio descuenta.

**Pero la pregunta era otra:** *«si trabajaran todo el año en su turno, menos un mes de vacaciones,
¿las horas estarían cuadradas?»* Y para eso hay que contar **las semanas que de verdad se trabaja**,
no la base del convenio.

**43,65 semanas son 306 días.** Un año con **un mes de vacaciones** y **14 festivos** tiene
**más días de trabajo que eso**. Cuantos más días, más horas — y el «margen» desaparece.

---

## 2 · El cálculo bueno

```
semanas que se trabaja  =  52,14  −  vacaciones(4,29)  −  festivos(2,00)  =  45,86
horas al año            =  media semanal  ×  45,86
```

| Persona | Media | × 45,86 | Contrato | **Diferencia** |
|---|---|---|---|---|
| **Tienda 1** | 20,33 h | **932 h** | 938,5 | **−6 h** |
| **Tienda 2** | 20,33 h | **932 h** | 938,5 | **−6 h** |
| **Tienda 3** | 20,33 h | **932 h** | 938,5 | **−6 h** |
| **Coordinadora 1** | 31,25 h | **1.433 h** | 1.396,8 | **+36 h** |
| **Coordinadora 2** | 21,00 h | **963 h** | 938,5 | **+25 h** |
| **Oficina** | 39,13 h | **1.794 h** | ≈ 2.034 | **−240 h** |

## 3 · La respuesta, sin rodeos

**Sí: con la rotación y un mes de vacaciones, las horas quedan cuadradas.**

**Tienda se queda a 6 h** — un 0,6 %, que es redondeo y festivos que caen en día libre.

> **Y por eso tienes razón: NO hay horas sobrantes.**
>
> Las 208 h que calculé antes **no existen**. El horario **está ajustado al contrato**, no por debajo.
> **No hay margen con el que cubrir el verano.**

**La conclusión cambia de signo:**

| Antes (mal) | Ahora |
|---|---|
| «Sobra 208 h para el verano» | **«No sobra nada: el año está justo»** |
| El verano se cubre con el margen | **El verano hay que sacarlo de otro sitio** |

---

## 4 · De dónde salen entonces las horas del verano

**De lo único que se puede: de trabajar menos gente los días que se puede.**

> *«Donde trabajan 3 (sólo de lunes a viernes y siempre y cuando no sea festivo) podrían trabajar 2.»*

**Ese es el yacimiento.** Un día de lunes a viernes, no festivo, en el que en vez de 3 personas
trabajan 2, **libera las horas de una persona**.

**Y con eso se paga la cobertura del verano:** quien está de vacaciones **no genera esas horas**, y
quien la cubre **las gana**. El total del equipo no cambia — **cambia de manos**.

### Los números, que salen redondos

| | |
|---|---|
| Un mes de vacaciones de una persona de tienda | **4,29 semanas × 20,33 h = 87 h** |
| Lo que libera un día a 2 en vez de 3 | **6,5 h** |
| **Días a 2 que hacen falta para cubrirlo** | **87 ÷ 6,5 = 13 días** |

> **Trece días al año.** De lunes a viernes, no festivos, en los que se trabaje a 2 en vez de 3.
>
> **Y eso cubre el mes entero de una persona.** No hace falta ni una hora extra: **sale de
> reorganizar**.

> **Por eso tu nota no es un detalle: es el mecanismo entero.** Sin esos días a 2, cubrir el verano
> sale de horas extra; con ellos, sale de reorganizar.

---

## 5 · Lo que falta para cerrarlo del todo

| # | Qué | Por qué importa |
|---|---|---|
| 1 | **Las horas reales de cada turno de tienda** | Las medias (20,33 h) son buenas, pero para repartir el verano hay que saber **qué día son cuántas horas** |
| 2 | **El ciclo de 4 semanas de coordinación** | Tengo las medias, no el reparto |
| 3 | **Cuántos días al año van a 2** | Es el yacimiento del punto 4 |
| 4 | **Las fechas de vacaciones** | Cambian quién falta y cuándo |

**Con esos cuatro, el cierre del año se puede dar por bueno con números, no con impresiones.**

---

## 4b · CORRECCIÓN: el reparto SÍ lo tengo

Dije que tenía «las medias pero no el reparto». **Estaba mal dicho: el reparto ES el ciclo, y está en
el Excel** con las marcas `1º`–`4º`. Sacado de ahí:

### Coordinadora 1

| Semana | Total | Trabaja | Libre |
|---|---|---|---|
| **1** | 39,0 | L · M · J · V · S · D | **X** |
| **2** | 35,5 | L · X · J · S · D | **M · V** |
| **3** | 26,5 | L (doble) · X · J | **M · V · S · D** |
| **4** | 36,5 | X · J · V · S · D | **L · M** |

### Coordinadora 2

| Semana | Total | Trabaja | Libre |
|---|---|---|---|
| **1** | 9,5 | X · J (3 h de apoyo) | **L · M · V · S · D** |
| **2** | 14,5 | V · S | **L · M · X · J · D** |
| **3** | 27,5 | M (3 h) · X · V · S · D | **L · J** |
| **4** | 29,0 | L · M (3 h) · V · S · D | **X · J** |

**Medias: Coordinadora 1 = 34,4 h/semana · Coordinadora 2 = 20,1 h/semana.**

> **Y aquí está lo que de verdad faltaba, y es más pequeño de lo que dije:** los días de cada semana
> **ya los tengo**. Lo que no tengo son **las horas de temporada normal**, porque **ese Excel es el de
> verano**, donde las horas están compensadas (6,5 h en vez de 7,5 h por la mañana).
>
> **La rotación no cambia; cambian las horas del día.**

---

## 5 · Cómo se cierra, entonces

| Pregunta | Respuesta |
|---|---|
| **¿Con el horario de verano lo puedes calcular?** | **Sí.** El año tiene dos tramos: **la rotación normal** (que ya está calculada: **−6 h** en tienda) y **el verano**. Con el verano dentro, el año se cierra |
| **¿Cuántos días hay que trabajar a 2?** | **Es el resultado, no el dato.** Se despeja: lo que falte para cuadrar, dividido por 6,5 h |
| **¿Las vacaciones?** | **Hasta mayo no se saben** — y no bloquean nada: el tramo normal ya está cerrado. **El verano se cierra en mayo** |

> **Un mes de vacaciones de tienda = 87 h.** Y como ya está dicho: **13 días a 2** las cubren.

---

## 6 · La lección

**Este es el tercer error de la misma familia** (E-1, E-2, E-3): **usar un divisor que no toca y dar
por bueno el primer número que sale.**

- E-1: calculé las horas de apertura de 7 días cuando la tienda cierra al mediodía.
- E-2: cogí la jornada de 2023 en vez de la de 2024.
- E-3: multipliqué una desviación semanal por 52 cuando el convenio ya descuenta.
- **Y ahora: usé la base del convenio para responder una pregunta sobre vacaciones.**

**El patrón:** el número salía con una operación plausible, **y no lo contrasté con la pregunta**.
**La pregunta era «¿cuadra con un mes de vacaciones?», y yo respondí con «¿cuánto da la base del
convenio?».** No son la misma pregunta.

> **Norma:** antes de dar una cifra, **releer qué se preguntó** y comprobar que el cálculo responde
> **a eso**.
