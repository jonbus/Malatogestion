#!/usr/bin/env bash
#
# Copia diaria de los datos de la app de gestión.
#
# Origen:  /opt/malato-gestion/.datos/estado.json
# Destino: /home/jonserver/copias-gestion/<fecha>/
# Se conservan las últimas 30 copias.
#
# La app escribe el fichero sin bloqueo. Por eso la copia se valida como JSON
# y, si pilla una escritura a medias, se reintenta antes de darla por buena.

set -euo pipefail

ORIGEN="${ORIGEN:-/opt/malato-gestion/.datos/estado.json}"
DESTINO="${DESTINO:-/home/jonserver/copias-gestion}"
CONSERVAR="${CONSERVAR:-30}"

if ! [[ "$CONSERVAR" =~ ^[0-9]+$ ]] || [ "$CONSERVAR" -lt 1 ]; then
  echo "✗ CONSERVAR debe ser un número mayor que cero"
  exit 1
fi

if [ ! -f "$ORIGEN" ]; then
  echo "✗ no existe el fichero de datos: $ORIGEN"
  exit 1
fi

umask 077
mkdir -p "$DESTINO"

STAMP="$(date +%Y-%m-%d_%H%M%S)"
SALIDA="$DESTINO/$STAMP"
mkdir -p "$SALIDA"

# Copia con reintentos y validación.
COPIA_OK=0
for intento in 1 2 3 4 5; do
  cp -a "$ORIGEN" "$SALIDA/estado.json.tmp"
  if python3 -c '
import json, sys
with open(sys.argv[1], encoding="utf-8") as f:
    d = json.load(f)
assert isinstance(d, dict)
assert isinstance(d.get("estado"), dict)
' "$SALIDA/estado.json.tmp" 2>/dev/null; then
    COPIA_OK=1
    break
  fi
  rm -f "$SALIDA/estado.json.tmp"
  echo "  aviso: la copia no era un JSON válido; reintento $intento"
  sleep 1
done

if [ "$COPIA_OK" -ne 1 ]; then
  echo "✗ no se pudo obtener una copia válida de $ORIGEN"
  rmdir "$SALIDA" 2>/dev/null || true
  exit 1
fi

mv "$SALIDA/estado.json.tmp" "$SALIDA/estado.json"
chmod 600 "$SALIDA/estado.json"

# Resumen legible y comprobación de que se han copiado los datos de verdad.
python3 - "$SALIDA/estado.json" "$SALIDA/INFO.txt" "$ORIGEN" <<'PY'
import datetime
import hashlib
import json
import sys

copia, info, origen = sys.argv[1], sys.argv[2], sys.argv[3]
with open(copia, "rb") as f:
    crudo = f.read()
d = json.loads(crudo)
estado = d.get("estado", {})

def cuenta(clave):
    v = estado.get(clave)
    return len(v) if isinstance(v, (dict, list)) else "?"

lineas = [
    "MALATO · copia de seguridad de gestión",
    "Fecha: " + datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    "Origen: " + origen,
    "Tamaño: " + str(len(crudo)) + " bytes",
    "SHA256: " + hashlib.sha256(crudo).hexdigest(),
    "Marcas: " + str(cuenta("marcas")),
    "Encargos: " + str(cuenta("encargos")),
    "Fichajes: " + str(cuenta("fichajes")),
    "Notas: " + str(cuenta("notas")),
    "Recuentos: " + str(cuenta("recuentos")),
    "",
]
with open(info, "w", encoding="utf-8") as f:
    f.write("\n".join(lineas))
print("\n".join(lineas))
PY

ln -sfn "$SALIDA" "$DESTINO/ultima"
echo "  copia hecha: $SALIDA"

# Conservar solo las últimas N copias.
mapfile -t copias < <(find "$DESTINO" -mindepth 1 -maxdepth 1 -type d \
  -name '20??-??-??_*' -printf '%f\n' | sort)
TOTAL="${#copias[@]}"

if [ "$TOTAL" -gt "$CONSERVAR" ]; then
  BORRAR=$((TOTAL - CONSERVAR))
  for ((i = 0; i < BORRAR; i++)); do
    D="${copias[$i]}"
    if [[ "$D" =~ ^20[0-9]{2}-[0-9]{2}-[0-9]{2}_[0-9]{6}$ ]]; then
      rm -rf -- "${DESTINO:?}/$D"
    fi
  done
  echo "  borradas $BORRAR copias antiguas; quedan $CONSERVAR"
else
  echo "  copias guardadas: $TOTAL de $CONSERVAR"
fi
