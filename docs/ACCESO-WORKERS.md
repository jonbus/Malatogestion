# Acceso a la gestión desde `supermalato.es/workers`

> **Puesto en marcha el 29 de octubre de 2026.**
> La app sigue en la OrangePi, en `/opt/malato-gestion`, y sus datos siguen en
> `/opt/malato-gestion/.datos/estado.json`. **No se ha movido nada.**

---

## 1 · Las dos puertas

| Puerta | Dirección | Quién entra | Clave |
|---|---|---|---|
| **Pública** | **https://supermalato.es/workers/** | Cualquier móvil o navegador | **clave de la tienda** |
| **Privada** | **https://orangepi4pro.tail369549.ts.net:8443/** | Solo dispositivos dentro de la tailnet | **La identidad de Tailscale** |

**La puerta pública ya no está abierta sin clave.** Antes, el 8443 era un
**Tailscale Funnel público** y cualquiera con la dirección entraba. Ahora ese
puerto es **solo tailnet** (`tailscale serve`), y la única puerta pública es
`supermalato.es/workers`, que pide la clave.

**El resto del dominio no cambia**: `https://supermalato.es/` sigue llevando al
asador (`/asador/`), como estaba configurado.

---

## 2 · La puerta pública: la clave

### Dónde está la clave

```
/opt/malato-gestion/.workers-pin
```

- **Propietario:** `jonserver`
- **Permisos:** `600` (solo su usuario)
- **Formato:** entre 6 y 32 caracteres (letras, números, guion o guion bajo)
- **La clave actual se entregó aparte, no se escribe en este documento.**

### Cómo se cambia

```bash
ssh jonserver@orangepi4pro
printf 'NUEVA_CLAVE\n' | sudo tee /opt/malato-gestion/.workers-pin >/dev/null
sudo chmod 600 /opt/malato-gestion/.workers-pin
sudo systemctl restart malato-workers-gateway
```

**Al cambiar la clave, las sesiones abiertas siguen valiendo** (la cookie está
firmada con otro secreto). Para cerrarlas todas:

```bash
sudo rm /opt/malato-gestion/.workers-secret
sudo systemctl restart malato-workers-gateway
```

El portero crea un secreto nuevo y **todas las cookies antiguas dejan de valer**.

### Cómo se entra y se sale

- Se abre **https://supermalato.es/workers/**
- Se escribe la clave y se pulsa **Entrar**.
- La sesión dura **30 días** en ese dispositivo.
- Para cerrar la sesión de ese dispositivo:
  **https://supermalato.es/workers/salir**

### Cómo funciona por dentro

```
navegador
   │  https://supermalato.es/workers/
   ▼
Cloudflare  (DNS + túnel; NO se usa Cloudflare Workers ni Cloudflare Access)
   │
   ▼
cloudflared-supermalato  (en la OrangePi)
   │  /workers/*  ->  127.0.0.1:3002
   ▼
malato-workers-gateway  (portero con clave)
   │  /workers/api/*  ->  127.0.0.1:3001/api/*
   ▼
malato-gestion  (la app de siempre, en el 3001)
```

- El portero **no toca la app**: lee `public/index.html`, cambia las llamadas
  `"/api/..."` por `"/workers/api/..."` y las pasa al 3001.
- **Los datos no se duplican**: se sigue escribiendo en el mismo `estado.json`.
- **Si el portero se cae**, la app sigue viva en la red local (`:3001`) y en
  Tailscale (`:8443`); solo deja de responder la URL pública.

### Límites

- **8 intentos fallidos por IP cada 10 minutos.** Después responde 429.
- La cookie es `HttpOnly`, `Secure`, `SameSite=Lax`, válida 30 días.
- **Es una clave compartida de tienda**, no una cuenta por persona. No hay registro
  de “quién entró” en la puerta; el fichaje y las marcas de la app sí guardan
  quién hizo cada cosa.

---

## 3 · La puerta privada: Tailscale

### Dirección

```
https://orangepi4pro.tail369549.ts.net:8443/
```

**Solo funciona desde un dispositivo que esté dentro de la tailnet.** Ya no es
un Funnel público.

### Cómo se añade un dispositivo

**Opción A · con la misma cuenta de Tailscale (la más simple)**

1. Instalar Tailscale en el móvil o el ordenador.
2. Entrar con la cuenta de la propiedad (`jon.sarean@`).
3. Abrir la dirección `https://orangepi4pro.tail369549.ts.net:8443/`.

**Opción B · con una clave de acceso (auth key)**

1. Entrar en **https://login.tailscale.com/admin/settings/keys**
2. **Generate auth key**.
   - **Reusable:** no (mejor una por dispositivo).
   - **Ephemeral:** no.
   - **Expiry:** 90 días.
   - **Tags:** si se usa `tag:tienda`, hay que tenerlo declarado en el ACL.
3. En el dispositivo, instalar Tailscale y ejecutar:

```bash
sudo tailscale up --auth-key=tskey-auth-XXXXXXXXXXXX
```

En móvil, se pega la clave en la pantalla de instalación.

> **Aviso importante:** una auth key da acceso a **toda la tailnet** según el ACL.
> **No se debe repartir la misma clave a todo el equipo sin ACL.** Para el día a
> día de la tienda, lo normal es usar **la puerta pública con clave** y reservar
> Tailscale para la propiedad y los administradores.

### ACL recomendado (opcional, pero importante si hay más gente)

En **https://login.tailscale.com/admin/acls**, dentro del bloque `acls`, añadir
una regla para que el grupo de tienda **solo** pueda llegar al 8443 de la Pi, y
no al SSH ni a los otros servicios:

```json
{
  "groups": {
    "group:tienda": ["jon.sarean@", "persona2@ejemplo.com"],
    "group:admin": ["jon.sarean@"]
  },
  "acls": [
    {
      "action": "accept",
      "src": ["group:tienda"],
      "dst": ["orangepi4pro:8443"]
    },
    {
      "action": "accept",
      "src": ["group:admin"],
      "dst": ["orangepi4pro:22,8443"]
    }
  ]
}
```

**No sustituyas todo el ACL por este bloque**: hay que **fusionarlo** con las
reglas que ya existan. Si se pega entero, se pueden perder otros accesos.

---

## 4 · Cloudflare: qué se usa y qué no

`supermalato.es` tiene los DNS en Cloudflare. El dominio **no se puede servir
sin pasar por Cloudflare** salvo que se cambien los DNS y se abra un puerto
público o se ponga un VPS por medio. Lo que **sí** se ha evitado:

| | |
|---|---|
| **Cloudflare Workers** | **No se usa** para esta app |
| **Cloudflare Access** | **No se usa**; la clave la pone el portero |
| **Cloudflare Tunnel** | **Sí**, es la puerta de entrada del dominio |

El túnel está en:

```
/etc/cloudflared/config.yml
```

y su servicio es:

```
cloudflared-supermalato.service
```

**Reglas:**

| Host | Ruta | Destino |
|---|---|---|
| `supermalato.es` | `^/workers` | `http://localhost:3002` |
| `www.supermalato.es` | `^/workers` | `http://localhost:3002` |
| `supermalato.es` | resto | `http://localhost:8082` (asador) |
| `www.supermalato.es` | resto | `http://localhost:8082` (asador) |

**Copia de la configuración anterior:** `/etc/cloudflared/config.yml.bak-20261029-171820`.

---

## 5 · Servicios y logs

| Servicio | Qué hace | Puerto |
|---|---|---|
| `malato-gestion` | La app de gestión | `3001` (red local) |
| `malato-workers-gateway` | Portero con clave para `/workers` | `3002` (solo `127.0.0.1`) |
| `cloudflared-supermalato` | Túnel del dominio | sale a Cloudflare |
| `tailscaled` | Tailscale + Serve del 8443 | `8443` (solo tailnet) |

```bash
sudo systemctl status malato-gestion
sudo systemctl status malato-workers-gateway
sudo systemctl status cloudflared-supermalato

sudo journalctl -u malato-workers-gateway -n 40 --no-pager
sudo journalctl -u cloudflared-supermalato -n 40 --no-pager
```

Los tres están **enabled**: arrancan solos al encender la OrangePi.

---

## 6 · Pruebas rápidas

```bash
# La puerta pública tiene que dar 200 con la página de la clave
curl -I https://supermalato.es/workers/

# La API sin sesión tiene que dar 401
curl -i https://supermalato.es/workers/api/estado

# El resto del dominio sigue yendo al asador
curl -I https://supermalato.es/asador/

# La puerta privada, solo desde la tailnet
curl -I https://orangepi4pro.tail369549.ts.net:8443/
```

Prueba completa con clave (sin imprimir la clave en el historial):

```bash
read -rs CLAVE
curl -sS -c /tmp/cookies -o /dev/null -X POST -d "pin=$CLAVE" \
  https://supermalato.es/workers/login
curl -sS -b /tmp/cookies -o /dev/null -w '%{http_code}\n' \
  https://supermalato.es/workers/
curl -sS -b /tmp/cookies https://supermalato.es/workers/api/estado | head -c 200
rm -f /tmp/cookies
```

---

## 7 · Lo que hay que saber (y lo que falta)

| | |
|---|---|
| **Clave compartida** | Es una llave de tienda, no una cuenta por persona |
| **Sin auditoría en la puerta** | La app sí guarda quién marca y quién ficha |
| **Sesión de 30 días** | Un móvil de tienda queda dentro hasta que se use `/workers/salir` o se rote el secreto |
| **Gerencia en la Pi** | **No tiene `GERENCIA_PIN` configurado**: `POST /api/entrar` devuelve 503. Hay que poner `/opt/malato-gestion/.pin` y reiniciar `malato-gestion` |
| **Dos datos separados** | La Pi y `app.supermalato.workers.dev` **no se sincronizan**. El 29/10/2026 se copió una vez el estado de Cloudflare a la Pi; a partir de ahí cada una escribe en su sitio |
| **Tailscale ACL** | **No se ha tocado**. Si se añaden personas a la tailnet, hay que poner el ACL antes |
| **Certificado** | Cloudflare pone el TLS de la puerta pública; Tailscale pone el del 8443. No hay certificados que renovar a mano |

---

## 8 · Cómo se deshace

Si algo va mal:

```bash
# 1. Parar la puerta pública nueva
sudo systemctl disable --now cloudflared-supermalato

# 2. Volver a la configuración anterior del túnel (si se quiere)
sudo cp /etc/cloudflared/config.yml.bak-20261029-171820 /etc/cloudflared/config.yml

# 3. Parar el portero
sudo systemctl disable --now malato-workers-gateway

# 4. Dejar el 8443 como estaba (Funnel público) — solo si se decide volver atrás
sudo tailscale serve --https=8443 off
sudo tailscale funnel --bg --https=8443 http://127.0.0.1:3001
```

**La app y los datos no se tocan en ningún caso.**

---

## 9 · Archivos

| Archivo | Para qué |
|---|---|
| `deploy/workers-gateway.mjs` | El portero (código) |
| `deploy/malato-workers-gateway.service` | Servicio systemd del portero |
| `deploy/cloudflared-supermalato.service` | Servicio systemd del túnel |
| `/opt/malato-gestion/workers-gateway.mjs` | Copia que corre en la Pi |
| `/opt/malato-gestion/.workers-pin` | La clave |
| `/opt/malato-gestion/.workers-secret` | Secreto que firma las sesiones |
| `/etc/cloudflared/config.yml` | Reglas del túnel |
