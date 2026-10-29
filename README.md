# Malato · gestión de la tienda

> **Aplicación de gestión de una tienda de alimentación.** Tres puestos —
> **Tienda**, **Coordinación** y **Jefa** — y un cuarto en camino, **Cocina**.
> Funciona en la nube, sin depender de ningún ordenador encendido.

**Dirección**: https://app.supermalato.workers.dev

---

## Qué hace

| | |
|---|---|
| **Las tareas del día** | por puesto y por turno, con partes, y **bloques plegados** con su progreso |
| **Tareas extra** | tres tipos (extra, urgente, para arreglar), se marcan, se destachan y se pasan de día |
| **Encargos** | lo que hay que tener un día; si hay que pedirlo antes, **sale un aviso el día de pedir** |
| **Llamadas** | 31 proveedores con sus teléfonos; se llama desde la app y **se apunta lo que dijeron** |
| **Cascadas** | una tarea que, al hacerse, **hace nacer la siguiente** para otro puesto |
| **La Tahona** | los cinco panes: entrada por la mañana, devolución por la noche |
| **Recuento del lunes** | tienda apunta, coordinación da el visto bueno |
| **Informes** | el pan del mes, con rango de fechas, para WhatsApp y para Excel |
| **El asador** | las instrucciones de pollo, codillo, costilla y patatas |

---

## Cómo está montado

```
apps/              la aplicación
packages/          el núcleo, separado de la interfaz
docs/              todo lo que hay que saber
  EMPIEZA-AQUI.md    ← lo primero que hay que leer
  DECISIONES.md      las decisiones tomadas, con su porqué
  asador/            las instrucciones del asador, una por producto
.tools/            los generadores y las pruebas
tools/             las comprobaciones de arquitectura
```

**La aplicación son tres piezas:**

1. **El núcleo** (`docs/nube/netlify/functions/nucleo.js`) — **no sabe dónde se guarda nada**;
   solo dice qué se hace con una petición.
2. **El adaptador** (`docs/nube/cloudflare/worker.js`) — **le pone el almacén** (Cloudflare KV).
3. **La pantalla** (`docs/nube/public/index.html`) — **se genera** desde `.tools/generar-nube.py`.

**Cambiar de almacén no toca el núcleo.** **Y cambiar la pantalla no toca nada de lo demás.**

---

## Las normas del proyecto

**Están en `docs/DECISIONES.md`, y salen de fallos de verdad:**

- **La orden va DENTRO del control**: si un botón se pinta en varias pantallas, lleva su `onclick` propio.
- **Cuidado con los nombres**: un nombre que ya existe **no da error al escribir, da error al usar**.
- **Si algo se pinta en una pantalla, comprobar que se pinta en TODAS.**
- **Probar el camino completo, no la lógica** — **el botón, no la función**.
- **Las pruebas no escriben en días reales.**
- **Todo lo que se guarda avisa.**

---

## Los secretos NO están aquí

**La clave de la Jefa y el token de Cloudflare no se escriben en el código.** **Se pasan por variable de entorno:**

```powershell
$env:CLOUDFLARE_API_TOKEN = "..."
$env:CLOUDFLARE_ACCOUNT_ID = "..."
```

**Y el estado de la tienda** (lo que ha apuntado la propiedad) **tampoco se sube**: está en `.gitignore`.

---

## El histórico del proyecto

**En `docs/` está todo el porqué**, decisión por decisión: **295 decisiones**, cada una
con **lo que se decidió y de dónde salió**. **Y en `docs/EMPIEZA-AQUI.md`**, el estado
del trabajo y lo que queda por hacer.
