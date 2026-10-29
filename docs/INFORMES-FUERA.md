# Sacar los informes de la aplicación

> **Para qué**: a final de mes la Jefa necesita **el informe del pan** fuera de la aplicación,
> para **imprimirlo**, **mandarlo por WhatsApp** al panadero, o **guardarlo**.

---

## 1 · Las tres formas, y cuál vale

| | Cómo se hace | Vale en el móvil | Traba |
|---|---|---|---|
| **PDF** | Habría que generarlo en el servidor | Sí | **Pesa y complica**: hay que añadir una librería al Worker |
| **Excel (.xlsx)** | Igual | Sí | **Peor todavía**: un Excel real necesita otra librería |
| **Texto + CSV** | **En el propio móvil**, sin tocar el servidor | **Sí** | **Ninguna** |

> **La tercera es la buena**, y no por comodidad: **no añade nada al servidor**
> y **funciona igual en un móvil, en una tablet y en el ordenador**.

---

## 2 · Lo que se va a poner

**Dos botones, al lado del informe del pan:**

```
TAHONA · EL PAN DE OCTUBRE
  Pan         Entra   Sale   Queda
  Txapata       420     38     382
  ...
  Total       1.993    194   1.799

  [ Compartir ]   [ Descargar para Excel ]
```

### **Compartir** — para WhatsApp

**Usa el botón de compartir del propio móvil.** Al pulsarlo sale el menú de siempre:
**WhatsApp, correo, imprimir, guardar en el teléfono**.

**Y lo que manda es un texto ordenado**, no una imagen:

```
TAHONA · OCTUBRE 2026
Entradas menos devoluciones

Pan          Entra   Sale   Queda
Txapata        420     38     382
Txapatita      240     21     219
Barra          850     96     754
Cuarto         315     30     285
Txoripan       168      9     159
TOTAL        1.993    194   1.799
```

**Se lee en WhatsApp sin abrir nada.** **Y el panadero puede contestar ahí mismo.**

### **Descargar para Excel** — para imprimir

**Descarga un archivo `.csv`**, que **Excel abre con doble clic** y **se imprime como cualquier hoja**.

**No necesita conexión después.**

---

## 3 · Y lo mismo, más adelante, para el recuento

**El recuento del lunes** —pollos, codillos, patatas, bravas— **necesitará lo mismo**:
**compartir y descargar**. **Se hará con el mismo mecanismo**, así que **solo se construye una vez**.

**Y el histórico de los lunes** también — **para enseñar cómo ha ido el mes**.

---

## 4 · Lo que NO se va a hacer

- **Un PDF de verdad** — salvo que haga falta el logo y el formato exacto
- **Un Excel con formato** — el `.csv` se abre igual y no cuesta nada
- **Mandar solo por WhatsApp** — el botón de compartir **es más ancho**: el mismo botón vale
  para WhatsApp, para el correo y para imprimir

---

## 5 · Lo que hay que decidir cuando se construya

| # | Pregunta |
|---|---|
| **1** | **¿El informe lleva el nombre de la tienda y la fecha?** *«Supermalato · octubre 2026»* |
| **2** | **¿Se manda el mes entero o solo los días con pan apuntado?** |
| **3** | **¿Hace falta el precio?** — hasta que lleguen los precios, solo habrá unidades |
