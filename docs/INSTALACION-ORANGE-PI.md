# La aplicación en el Orange Pi

> **Instalada el 29 de octubre de 2026.** **Comparte máquina con el asador**, y **no lo toca**.

---

## 1 · Dónde está

| Puerta | Dirección | Quién entra |
|---|---|---|
| **Portada** | **https://supermalato.es/** | **página «en construcción»** |
| **Asador** | **https://supermalato.es/asador/** · **https://supermalato.es/erretegia** | **clientes y tienda** |
| **Gestión pública, con clave** | **https://supermalato.es/workers/** | **cualquier móvil o navegador** |
| **Gestión privada, Tailscale** | **https://orangepi4pro.tail369549.ts.net:8443/** | **solo equipos dentro de la tailnet** |

### Y desde la tienda

| | Dirección | Cuándo |
|---|---|---|
| **Desde la tienda** (misma wifi) | **http://orangepi4pro.local:3001** | **lo normal, y lo más rápido** |
| Desde la tienda, si el nombre falla | http://192.168.1.47:3001 | la IP directa |

> **La de la tienda va por la red local**: **no depende de internet** y **va más rápido**. **Es la de todos los días.**
> **La raíz del dominio es una portada «en construcción»**: **no lleva al asador**.
> **El asador se abre solo por `/asador` y por `/erretegia`**.
> **La gestión pública pasa por el túnel de Cloudflare y pide una clave** (ver `ACCESO-WORKERS.md`).
> **La gestión privada es Tailscale Serve**: **el Funnel público del 8443 ya está apagado**.

**El nombre `orangepi4pro.local` no cambia aunque cambie la IP** (mDNS, aviso instalado el 29/10).

| Lo que hay en esa máquina | Dónde |
|---|---|
| **La portada** | `https://supermalato.es/` · servidor en **3003** |
| **El asador** (recepción de pedidos) | `https://supermalato.es/asador/` y `/erretegia` · puerto **8082** |
| **El asador por Tailscale** | `https://orangepi4pro.tail369549.ts.net` · puerto **8080** |
| **Otra cosa** | `https://orangepi4pro.tail369549.ts.net:10000` · puerto **8082** |
| **La gestión, privada** | `https://orangepi4pro.tail369549.ts.net:8443` · puerto **3001** |
| **La gestión, pública** | `https://supermalato.es/workers/` · portero en **3002** |

**Nada se comparte entre ellos.** **Cada uno tiene su puerto y su carpeta.**

---

## 2 · Cómo está montado

```
/opt/malato-gestion/
   servidor-local.mjs          el servidor (sirve la app y su API)
   workers-gateway.mjs         el portero de /workers (clave)
   landing-servidor.mjs        la portada «en construcción»
   landing/index.html          el HTML de la portada
   landing/logo-o-verde.png    el logo de la portada
   public/index.html           la aplicación
   netlify/functions/nucleo.js el núcleo
   .datos/estado.json          LOS DATOS — aquí, en un fichero
   .workers-pin                la clave de la puerta pública
   .workers-secret             el secreto que firma las sesiones
```

**Servicios** — los cuatro **arrancan solos al encender** y **se reinician si se caen**:

| Servicio | Qué hace |
|---|---|
| `malato-gestion.service` | La app en el **3001** |
| `malato-workers-gateway.service` | El portero con clave en el **3002** (solo `127.0.0.1`) |
| `malato-landing.service` | La portada «en construcción» en el **3003** (solo `127.0.0.1`) |
| `cloudflared-supermalato.service` | El túnel de **supermalato.es** |

```bash
sudo systemctl status malato-gestion
sudo systemctl status malato-workers-gateway
sudo systemctl status malato-landing
sudo systemctl status cloudflared-supermalato
sudo systemctl restart malato-gestion
sudo journalctl -u malato-gestion -n 40     # ver qué ha pasado
sudo journalctl -u malato-workers-gateway -n 40
sudo journalctl -u malato-landing -n 40
sudo journalctl -u cloudflared-supermalato -n 40
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

**Cuando haya que unificarlas**, hay que decidir **cuál manda** y **cómo se copia**.

**El 29 de octubre de 2026 se copió una vez el estado de Cloudflare a la Pi** (marcas, encargos, notas, recuentos, tahona y cascadas), con el visto bueno de la propiedad. **A partir de ahí las dos listas siguen separadas**: la Pi no escribe en Cloudflare ni al revés.

**Copia del estado importado:** `/opt/malato-gestion/.datos/estado.json` · nota: `/opt/malato-gestion/.datos/COPIADO-DESDE-CLOUDFLARE.txt`.

### Copia diaria de los datos de gestión

**Todos los días a las 23:00**, el `malato-backup-gestion.timer` lanza una copia
de `estado.json` a:

```
/home/jonserver/copias-gestion/<fecha>/
   estado.json     la copia
   INFO.txt        fecha, tamaño, SHA256 y número de marcas/encargos
```

- **Se conservan las últimas 30 copias.**
- **`/home/jonserver/copias-gestion/ultima`** apunta siempre a la más reciente.
- **Si la Pi estaba apagada a las 23:00**, la copia se hace al encender
  (`Persistent=true`).
- **La copia se valida como JSON**; si pilla una escritura a medias, reintenta.
- **Servicio:** `malato-backup-gestion.service`.
- **Script:** `/usr/local/bin/malato-backup-gestion.sh`.

**Desde la app:** en la bandeja de la **Jefa** hay un botón **Copias de
seguridad**. Muestra las copias disponibles y permite descargar cada
`estado.json`. Solo responde con la sesión de gerencia; la puerta pública sigue
pidiendo `Malato20`.

```bash
# Ver la próxima copia
systemctl list-timers malato-backup-gestion

# Forzar una copia ahora
sudo systemctl start malato-backup-gestion.service
sudo journalctl -u malato-backup-gestion -n 30 --no-pager

# Ver la última
ls -lah /home/jonserver/copias-gestion/ultima/
cat /home/jonserver/copias-gestion/ultima/INFO.txt
```

**Para restaurar una copia:**

```bash
sudo systemctl stop malato-gestion
sudo cp /home/jonserver/copias-gestion/ultima/estado.json \
        /opt/malato-gestion/.datos/estado.json
sudo chown jonserver:jonserver /opt/malato-gestion/.datos/estado.json
sudo chmod 600 /opt/malato-gestion/.datos/estado.json
sudo systemctl start malato-gestion
```

> **Aviso:** esta copia está **en la misma eMMC**. Protege de un borrado, de una
> escritura a medias o de una corrupción lógica, **pero no de que falle el disco**.
> Cuando se pueda, hay que llevar una copia fuera de la Pi.

> **Servicio ajeno desactivado:** `futbooking` (servicio de usuario de
> `jonserver`) estaba en bucle porque faltaba `/home/jonserver/futbooking`.
> Se desactivó el **29/10/2026**. No era de Malato.

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

**El portero no hay que tocarlo** cuando cambia la app: lee el `index.html` nuevo
y reescribe las llamadas `"/api/"` cada vez. Solo se actualiza
`workers-gateway.mjs` si cambia el propio portero.

**La portada «en construcción»** se cambia en
`/opt/malato-gestion/landing/index.html` (o en `deploy/landing/index.html` y se
copia). El servidor la lee en cada petición: **no hace falta reiniciar**.

> **Detalle completo del acceso público, la clave y Tailscale:**
> **[`ACCESO-WORKERS.md`](ACCESO-WORKERS.md)**.

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
