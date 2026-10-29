"""Demostracion del metodo de pedido con los datos que ha dado la propiedad."""
import sys

sys.stdout.reconfigure(encoding="utf-8")

# (semana, pollos, codillos, costillas)
ANIO_PASADO = {20: dict(pollos=40, codillos=4, costillas=2),
               21: dict(pollos=30, codillos=5, costillas=None)}
ESTE_ANIO = {20: dict(pollos=35, codillos=4, costillas=None),
             21: dict(pollos=28, codillos=3, costillas=None)}

print("=" * 72)
print("QUÉ DIRÍA EL SISTEMA CON TUS DATOS")
print("=" * 72)

for prod in ("pollos", "codillos"):
    print(f"\n### {prod}")
    print(f"  {'semana':<8}{'año pasado':>12}{'este año':>11}{'variación':>12}")
    ratios = []
    for s in (20, 21):
        ap = ANIO_PASADO[s][prod]
        ea = ESTE_ANIO[s][prod]
        r = ea / ap
        ratios.append(r)
        print(f"  {s:<8}{ap:>12}{ea:>11}{100 * (r - 1):>+11.1f} %")
    media = sum(ratios) / len(ratios)
    tend_ap = ANIO_PASADO[21][prod] / ANIO_PASADO[20][prod] - 1
    tend_ea = ESTE_ANIO[21][prod] / ESTE_ANIO[20][prod] - 1
    print(f"  tendencia del año pasado  (20->21): {100 * tend_ap:+.1f} %")
    print(f"  tendencia de este año     (20->21): {100 * tend_ea:+.1f} %")
    print(f"  -> ratio medio este año / año pasado: {media:.3f}  ({100 * (media - 1):+.1f} %)")
    print("\n  PROPUESTA PARA LA SEMANA 22:")
    hipo = 25 if prod == "pollos" else 5      # valor del año pasado que haria falta
    print(f"    si el año pasado la semana 22 fueron {hipo} {prod},")
    print(f"    el sistema propondría {hipo} x {media:.3f} = {hipo * media:.1f}"
          f"  ->  {round(hipo * media)} {prod}")
