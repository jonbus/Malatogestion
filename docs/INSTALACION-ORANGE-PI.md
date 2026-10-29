# La aplicación en el Orange Pi

> **Instalada el 29 de octubre de 2026.** **Comparte máquina con el asador**, y **no lo toca**.

---

## 1 · Dónde está

```
https://orangepi4pro.tail369549.ts.net:8443/
```

### Y dos formas de entrar

| | Dirección | Cuándo |
|---|---|---|
| **Desde la tienda** (misma wifi) | **http://orangepi4pro.local:3001** | **lo normal, y lo más rápido** |
| Desde la tienda, si el nombre falla | http://192.168.1.47:3001 | la IP directa |
| **Desde internet** | **https://orangepi4pro.tail369549.ts.net:8443** | **desde fuera** |

> **La de la tienda va por la red local**: **no depende de internet** y **va más rápido**. **Es la de todos los días.**
> **La de internet va por Tailscale Funnel**, en el puerto **8443**.

**El nombre `orangepi4pro.local` no cambia aunque cambie la IP** (mDNS, aviso instalado el 29/10).

| Lo que hay en esa máquina | Dónde |
|---|---|
| **El asador** (recepción de pedidos) | `https://orangepi4pro.tail369549.ts.net` · puerto **8080** |
| **Otra cosa** | `https://orangepi4pro.tail369549.ts.net:10000` · puerto **8082** |
| **La gestión** | `https://orangepi4pro.tail369549.ts.net:8443` · puerto **3001** |

**Nada se comparte entre ellos.** **Cada uno tiene su puerto y su carpeta.**

---

## 2 · Cómo está montado

```
/opt/malato-gestion/
   servidor-local.mjs          el servidor (sirve la app y su API)
   public/index.html           la aplicación
   netlify/functions/nucleo.js el núcleo
   .datos/estado.json          LOS DATOS — aquí, en un fichero
```

**Servicio**: `malato-gestion.service` — **arranca solo al encender**, y **se reinicia si se cae**.

```bash
sudo systemctl status malato-gestion
sudo systemctl restart malato-gestion
sudo journalctl -u malato-gestion -n 40     # ver qué ha pasado
```

**El asador sigue con su servicio** (`malato.service`). **No se ha tocado.**

---

## 3 · Los datos: dos listas separadas

**Decisión de la propiedad** («mantén las dos»):

| | |
|---|---|
| **En el Orange Pi** | `estado.json` — **la de la tienda**, en su propia máquina |
| **En Cloudflare** | `app.supermalato.workers.dev` — **la de fuera** |

> ⚠ **NO se sincronizan.** **Una tarea marcada en el Pi no aparece marcada en Cloudflare, y al revés.**

**Cuando haya que unificarlas**, hay que decidir **cuál manda** y **cómo se copia**. **Hoy empiezan las dos vacías.**

---

## 4 · La copia del asador

**Antes de escribir una sola línea**, se copió su carpeta entera:

```
~/copias-asador/app-pedidos_20261029_1515
785 ficheros · 25 MB
```

**Comprobado después**: el asador **seguía respondiendo** (HTTP 200) **y su servicio activo**.

---

## 5 · Cómo se actualiza

**Cuando cambie la aplicación**, hay que volver a subir **dos ficheros**:

```
docs/nube/public/index.html
docs/nube/netlify/functions/nucleo.js
```

**Y reiniciar el servicio**:

```bash
sudo systemctl restart malato-gestion
```

**Los datos NO se tocan**: están en `.datos/estado.json`, aparte del código.

---

## 6 · Lo que hay que saber de esta máquina

| | |
|---|---|
| **Sistema** | Armbian 26.11 (Debian 13) · **aarch64** |
| **Node** | **v24.20.0** |
| **Python** | 3.13.5 |
| **Disco** | 58 GB · **53 GB libres** |
| **Usuario** | `jonserver` (con `sudo`) |
| **El asador** | usuario `malato` · `/home/malato/app-pedidos` |

**Y una regla**: **en esta máquina hay dos aplicaciones de la propiedad.** **Antes de tocar nada, la copia del asador** — **como se hizo este día.**
