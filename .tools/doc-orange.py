"""Pone al día el documento del Orange Pi con las dos formas de entrar."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"docs\INSTALACION-ORANGE-PI.md"
t = open(p, encoding="utf-8").read()

viejo = "**Va por Tailscale Funnel**, en el **puerto 8443**."

nuevo = """### Y dos formas de entrar

| | Dirección | Cuándo |
|---|---|---|
| **Desde la tienda** (misma wifi) | **http://orangepi4pro.local:3001** | **lo normal, y lo más rápido** |
| Desde la tienda, si el nombre falla | http://192.168.1.47:3001 | la IP directa |
| **Desde internet** | **https://orangepi4pro.tail369549.ts.net:8443** | **desde fuera** |

> **La de la tienda va por la red local**: **no depende de internet** y **va más rápido**. **Es la de todos los días.**
> **La de internet va por Tailscale Funnel**, en el puerto **8443**.

**El nombre `orangepi4pro.local` no cambia aunque cambie la IP** (mDNS, aviso instalado el 29/10)."""

if viejo not in t:
    print("  NO ENCONTRADO")
    sys.exit(1)

open(p, "w", encoding="utf-8").write(t.replace(viejo, nuevo, 1))
print("  documento al día")
