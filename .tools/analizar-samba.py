"""Analiza la samba: tempo, estructura y el trozo con más energía.

Con eso se puede cortar el vídeo al ritmo y elegir el estribillo sin oírlo.
"""
import subprocess
import sys
import wave

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

FF = r"C:\Users\Usuario\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
ENTRADA = r"C:\Users\Usuario\Desktop\APP Malato Documentación\SambaMalato.mpeg"
WAV = ".tmp-audio.wav"

subprocess.run([FF, "-y", "-i", ENTRADA, "-ac", "1", "-ar", "22050", "-vn", WAV],
               capture_output=True)

with wave.open(WAV, "rb") as w:
    sr = w.getframerate()
    datos = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0

dur = len(datos) / sr
print(f"  duración: {dur:.1f} s  ·  {sr} Hz  ·  {len(datos)} muestras")

# --- energía por ventanas de 50 ms
paso = int(sr * 0.05)
ventanas = len(datos) // paso
energia = np.array([np.sqrt(np.mean(datos[i * paso:(i + 1) * paso] ** 2))
                    for i in range(ventanas)])

# --- los golpes: subidas bruscas de energía
dif = np.diff(energia, prepend=energia[0])
umbral = np.mean(dif) + 1.8 * np.std(dif)
golpes = np.where(dif > umbral)[0]
print(f"  golpes detectados: {len(golpes)}")

if len(golpes) > 4:
    intervalos = np.diff(golpes) * 0.05
    intervalos = intervalos[(intervalos > 0.25) & (intervalos < 1.2)]
    if len(intervalos):
        medio = float(np.median(intervalos))
        print(f"  intervalo medio entre golpes: {medio:.3f} s  →  {60/medio:.0f} golpes por minuto")

# --- mapa de energía por tercios y por bloques de 5 s
print("\n  energía por bloques de 5 s (0 = silencio, 1 = lo más fuerte):")
tope = energia.max() or 1
lineas = []
for i in range(0, ventanas, 100):
    trozo = energia[i:i + 100]
    if not len(trozo):
        break
    v = trozo.mean() / tope
    barra = "█" * int(v * 40)
    lineas.append((i * 0.05, v, barra))
for t, v, barra in lineas:
    print(f"   {int(t//60)}:{int(t%60):02d}  {v:4.2f}  {barra}")

# --- el trozo de 25 s más intenso
largo = int(25 / 0.05)
if ventanas > largo:
    sumas = np.convolve(energia, np.ones(largo), mode="valid")
    mejor = int(np.argmax(sumas))
    print(f"\n  el trozo de 25 s con más energía: del segundo {mejor*0.05:.0f} al {mejor*0.05+25:.0f}")

# --- el estribillo suele ser lo que más se repite: bloques parecidos
print(f"\n  primeros 3 s: energía {energia[:60].mean()/tope:.2f}")
print(f"  últimos 3 s:  energía {energia[-60:].mean()/tope:.2f}")

import os
os.remove(WAV)
