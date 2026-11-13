# NOTAS DEL CALENDARIO · lo que hay que montar

> **Decidido con la propiedad. Solo falta el código.**
> **Va entero o no va: toca base de datos, calendario y tickeo.**

---

## 1 · Qué es una nota

```
texto      lo que se escribe
fecha      el día en que se puso. NO cambia nunca.
tipo       "general"  o  "personal"
quien      el puesto que la escribió
para       el puesto destinatario (solo si es personal)
hecha      tickada o no
```

**Se guardan en `estado.notas`**, una lista. **Nunca se borran al tickear: cambian `hecha` a true.**

---

## 2 · El arrastre — lo importante

**Una nota NO se copia al día siguiente.** **Se queda en su día y aparece en los días posteriores mientras no esté hecha.**

```
nota puesta el martes 4:
  martes 4    →  aparece normal
  miércoles 5 →  aparece marcada «de ayer»
  jueves 6    →  aparece marcada «del martes»
  ...
  cuando se tickea, deja de aparecer en los días posteriores
  y se queda en su día, tachada.
```

**¿Por qué así y no copiándola?** **Copiándola, a los cuatro días hay cuatro notas iguales, y tickar una no quita las otras tres.** **Así hay una sola y siempre se sabe de cuándo viene.**

**Se arrastra PARA SIEMPRE.** **Sin límite de días.**

### Cómo se calcula

Para pintar el día `D`, se enseña:

1. **Las notas con `fecha === D`** (las de ese día)
2. **Las notas con `fecha < D` y `hecha === false`** (las arrastradas), con su etiqueta de origen

**Y no hay que guardar nada extra**: **el arrastre es visual, se calcula al pintar.** **Eso evita duplicados y estados raros.**

---

## 3 · Las generales

- **Una sola casilla para todos.** **La tickea quien sea y desaparece para todos.**
- **`para` vacío.**
- **La Jefa las puede crear.**

## 4 · Las personales

- **Cada puesto ve la suya. Solo la suya.**
- **La Jefa las ve TODAS, y ve de quién es cada una.**
- **Al crearlas, la Jefa ELIGE EL PUESTO en un desplegable.**
  **No vale «personal» a secas: sin destinatario, la nota no se guarda.**
- **`para` = el id del puesto destinatario.**

### Quién puede tickear

| | |
|---|---|
| **general** | **cualquiera que la vea** |
| **personal** | **solo el puesto destinatario, y la Jefa** |

---

## 5 · La pantalla

**Dentro del calendario, un bloque nuevo: «Notas».**

```
┌────────────────────────────────────────────┐
│ Notas · viernes 6 de noviembre             │
│                                            │
│ [ + Escribir una nota ]                    │
│                                            │
│ ┌────────────────────────────────────────┐ │
│ │ ○  Llamar a Cadagua        del martes  │ │
│ │    (de coordinación)                   │ │
│ ├────────────────────────────────────────┤ │
│ │ ○  Revisar la cámara       general     │ │
│ ├────────────────────────────────────────┤ │
│ │ ●  Pedir las bolsas        hecho       │ │
│ │    (tachada, del miércoles)            │ │
│ └────────────────────────────────────────┘ │
└────────────────────────────────────────────┘
```

- **La casilla a la izquierda, grande, para tickear con el dedo**
- **La etiqueta de origen a la derecha**, **en pequeño y en gris**
- **Las hechas, tachadas y abajo**
- **Las generales van primero** (son de todos)

### Al escribir

**Un formulario corto:**

```
[ escribe la nota...                    ]
( ) General — para todos
( ) Personal — para:  [ desplegable de puestos ▾ ]
                                  [ Guardar ]
```

**El desplegable de puestos solo sale si se elige «Personal».**

---

## 6 · Lo que hay que tocar

### En `nucleo.js`

1. **`estadoVacio`**: `notas: []`
2. **`leer`/`podar`**: que `notas` sobreviva
3. **`/api/estado`**: que devuelva `notas`
4. **`/api/nota`** (nueva): crear
5. **`/api/nota-hecha`** (nueva): tickear
6. **`/api/nota-borrar`** (nueva): borrar *(solo quien la escribió o la Jefa)*

### En `generar-nube.py`

7. **`pintaNotas()`**: el bloque, con el cálculo del arrastre
8. **`escribirNota()`**: el formulario
9. **`tickNota(id)`**: la casilla
10. **El bloque dentro del calendario**, **como «Tareas» o «Encargos»**

---

## 7 · Lo que NO se hace

- **No se copian notas de un día a otro.** **El arrastre es visual.**
- **No se mezcla con «Novedades».** **Las novedades llevan un tick POR PUESTO** *(saber quién lo ha visto)*; **las notas, una casilla.** **Son cosas distintas y van en pantallas distintas.**
- **No se arrastran las hechas.** **Solo las pendientes.**

---

## 8 · Cómo se prueba antes de subir

1. **Crear una general** → **aparece hoy, con una casilla**
2. **Crear una personal de coordinación** → **verla desde coordinación; NO verla desde tienda**
3. **Entrar como Jefa** → **ver las dos, y ver de quién es la personal**
4. **Pasar el día a mañana** → **la general y la personal siguen ahí, con su etiqueta «de ayer»**
5. **Tickear la general desde tienda** → **desaparece para todos**
6. **Pasar tres días** → **la personal sigue arrastrándose**
7. **Tickearla** → **desaparece de los días posteriores y queda tachada en el suyo**

**Si los siete salen bien, se sube.** **Si falla uno, no se sube.**
