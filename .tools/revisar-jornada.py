"""Relectura rigurosa del articulo de jornada del convenio.

Busca el texto COMPLETO del articulo 4 y cualquier cifra anual, para verificar si
la lectura de 1.754 horas fue correcta o si hay cifras distintas por año.
"""
import re

for f in ['convenio-ccoo-2024.pdf.txt', 'convenio-lab.pdf.txt']:
    txt = open(f'.tools/docs/{f}', encoding='utf-8').read()
    txt = re.sub(r'\s+', ' ', txt).replace('­', '')
    print("=" * 78)
    print(f)
    print("=" * 78)

    # 1) Cifras de 4 digitos cerca de 'hora'
    print("\n--- cifras anuales (4 digitos junto a 'hora'/'jornada') ---")
    for m in re.finditer(r'(.{110}?)(\d[.\s]?\d{3})\s*(horas|h\b)(.{110})', txt, re.I):
        print(f"  ...{m.group(1)}{m.group(2)} {m.group(3)}{m.group(4)}...\n")

    # 2) Texto completo del articulo de jornada
    print("--- texto del articulo de jornada laboral ---")
    for m in re.finditer(r'[Aa]rt[íi]culo\s*4[.\s]*[Jj]ornada', txt):
        ini = m.start()
        print(f"  [{f}]\n  {txt[ini:ini + 1100]}\n")
        break

    # 3) Menciones a jornada parcial / tiempo parcial
    print("--- menciones a jornada parcial ---")
    n = 0
    for m in re.finditer(r'(jornada parcial|tiempo parcial|jornada reducida)', txt, re.I):
        frag = txt[max(0, m.start() - 180):m.start() + 260]
        print(f"  ...{frag}...\n")
        n += 1
        if n >= 3:
            break
    if n == 0:
        print("  SIN APARICIONES\n")
