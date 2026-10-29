# Fruta y verdura · las seis familias

> **Clasificación hecha por la propiedad.** Fuente: `fruta-verdura-familias.xlsx`.
> Exportada como dato para la aplicación en `fruta-verdura.json`.

---

## 1 · Lo que he aprendido al verla terminada, y no lo tenía claro

**Las familias no son botánicas: son comerciales.** Yo había clasificado por lo que es cada cosa. La
propiedad clasifica **por cómo se vende**.

| Producto | Yo lo puse en | Va en | Por qué |
|---|---|---|---|
| Zanahoria · apio · endivias · iceberg · corazones de lechuga | Verdura | **Embolsado** | Se venden **envasados** |
| Ajos tiernos · espárragos tiernos | Verdura | **Embolsado** | También |
| Higos cuello dama · arándanos / frambuesas | Fruta | **Embolsado** | También |
| Nueces | Varios | **Embolsado** | También |
| Escarola | Verdura | **Ensaladas Preparadas** | Va con las bolsas de ensalada |
| Castañas | Varios | **Fruta** | Fruto seco de temporada |

> **La regla:** si se vende envasado, es **Embolsado** — sea fruta, verdura o fruto seco.
> Y **Ensaladas Preparadas** son las bolsas de mezcla (Gourmet, 4 Estaciones, César, Florette,
> Canónigos, Escarola).

**Esto importa para la aplicación:** cuando se pida «revisar toda la fruta y verdura», **el desplegable
se organiza por familia** — y la familia dice **dónde mirar en la tienda**, no qué es el producto.

---

## 2 · El reparto

| Familia | Productos |
|---|---|
| **Fruta** | **50** |
| **Verdura** | **20** |
| **Embolsado** | **19** |
| **Ensaladas Preparadas** | **7** |
| **Legumbres** | **4** |
| **Varios** | **4** |
| | **104** |

---

## 3 · El CI es interno

> *«Sólo sirve a gerencia y coordinadoras, y es desde donde se hacen los pedidos de la fruta.»*

- **Va en los datos**, pero **no se enseña** a las personas de tienda.
- **Es la llave para los pedidos**: cuando entremos en ese bloque, esta lista se cruza con el
  histórico de ventas.
- **[falta] Para qué se usará exactamente** en la pantalla de pedidos.

---

## 4 · Tres cosas que hay que revisar

| # | Qué | Detalle |
|---|---|---|
| 1 | **10 CI valen «96»** | Están **cortados**. Son los que el OCR no pudo leer y quedaron a medias: Manzana Chantecler · Pera Champion · Ciruela Amarilla · Arándanos/Frambuesas · Romanescu · Escarola · Hierbabuena · Cebollino · Pimiento Cristal/Piparra · Perejil |
| 2 | **`960156` está repetido** | En **Naranja Zumo Barata** y en **Naranja Barata**. Uno de los dos no es. |
| 3 | **ICEBERG lleva el CI dentro del nombre** | La fila dice CI `800013` y el nombre `ICEBERG (960954)`. **Parece que el CI bueno es `960954`** y `800013` es otra cosa. |

**[falta]** Con esos tres arreglados, la lista queda cerrada del todo.
