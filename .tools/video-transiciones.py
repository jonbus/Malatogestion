"""El vídeo con transiciones de verdad, con ffmpeg.

Cada fotograma entra con un xfade distinto, solapado con el anterior.
Los tiempos se calculan para que el total sea exactamente la canción.
"""
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = r"C:\Users\Usuario\Desktop\APP Malato\Video aniversario"
FF = r"C:\Users\Usuario\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"

cuadros = sorted(f for f in os.listdir(os.path.join(RAIZ, "cuadros")) if f.endswith(".png"))
N = len(cuadros)
print(f"  cuadros: {N}")

AUDIO_SEG = 124.36
SOLAPE = 0.60     # más largas: el vídeo gana aire sin cambiar el orden
# N clips de D segundos, con N-1 solapes de SOLAPE: total = N*D - (N-1)*SOLAPE
D = (AUDIO_SEG + (N - 1) * SOLAPE) / N
PASO = D - SOLAPE
print(f"  cada clip: {D:.3f} s · solape: {SOLAPE} s · paso: {PASO:.3f} s")
print(f"  total previsto: {N*D - (N-1)*SOLAPE:.2f} s")

TRANSICIONES = [
    "fade", "slideleft", "circleopen", "pixelize",
    "wipeleft", "radial", "hblur", "slideup",
    "circleclose", "fadeblack", "smoothleft", "distance",
]

# --- el guion de filtros
lineas = []
for i in range(N):
    lineas.append(f"[{i}:v]fps=25,format=yuv420p,setsar=1[v{i}]")

anterior = "v0"
for i in range(1, N):
    t = TRANSICIONES[(i - 1) % len(TRANSICIONES)]
    offset = i * PASO
    salida = f"x{i}"
    lineas.append(f"[{anterior}][v{i}]xfade=transition={t}:duration={SOLAPE}:offset={offset:.3f}[{salida}]")
    anterior = salida

lineas.append(f"[{anterior}]null[final]")
guion = ";\n".join(lineas)
ruta_guion = os.path.join(RAIZ, "transiciones.txt")
open(ruta_guion, "w", encoding="utf-8").write(guion)
print(f"  guion de filtros: {len(guion)} caracteres · {N-1} transiciones")

# --- la orden
audio = [f for f in os.listdir(RAIZ) if f.lower().endswith(".mpeg")][0]
orden = [FF, "-y"]
for c in cuadros:
    orden += ["-loop", "1", "-t", f"{D:.3f}", "-i", os.path.join(RAIZ, "cuadros", c)]
orden += ["-i", os.path.join(RAIZ, audio)]
orden += ["-filter_complex", guion]
orden += ["-map", "[final]", "-map", f"{N}:a"]
orden += ["-c:v", "libx264", "-preset", "medium", "-crf", "21", "-r", "25"]
orden += ["-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart"]
salida = os.path.join(RAIZ, "VIDEO-9x16-CON-TRANSICIONES.mp4")
orden.append(salida)

print("  montando… (esto tarda)")
r = subprocess.run(orden, capture_output=True)
if r.returncode != 0:
    print("  FALLO:")
    print(r.stderr.decode("utf-8", "replace")[-1500:])
    sys.exit(1)

print(f"  hecho: {round(os.path.getsize(salida)/1024/1024,1)} MB")
