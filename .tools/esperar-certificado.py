"""Espera a que el certificado del subdominio esté listo, reintentando."""
import ssl
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
URL = "https://app.supermalato.workers.dev/api/estado"

for intento in range(1, 13):
    try:
        with urllib.request.urlopen(URL, timeout=20) as r:
            print(f"  intento {intento:>2}: OK · HTTP {r.status}")
            print("  ", r.read()[:140].decode("utf-8", "replace"))
            sys.exit(0)
    except Exception as e:
        print(f"  intento {intento:>2}: {type(e).__name__}: {str(e)[:80]}")
    time.sleep(10)

print("\n  no ha arrancado en dos minutos")
sys.exit(1)
