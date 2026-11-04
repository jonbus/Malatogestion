"""El pedido se pide HOY lo de MAÑANA, con la vista previa delante."""
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()

VIEJO = '''  html += `<div style="display:flex;gap:8px;margin:10px 0;flex-wrap:wrap">
      <button class="btn-add-2" type="button" onclick="mandarPedidoProveedor('Zuaza')"
        style="${lista.some(e => e.que === 'Zuaza') ? '' : 'opacity:.45'}">📲 Pedido a Zuaza (Patxi)</button>
      <button class="btn-add-2" type="button" onclick="mandarPedidoProveedor('Tahona')"
        style="${lista.some(e => e.que === 'Tahona') ? '' : 'opacity:.45'}">📲 Pedido a la Tahona (Jon)</button>
    </div>`;'''

NUEVO = '''  /* pedir HOY lo de MAÑANA, con lo que va a salir a la vista */
  if(f === DIA){
    const deManana = (encargosFecha || []).filter(e => e.desde === manana);
    const vista = deManana.map(e =>
      e.producto ? `<b>${e.cantidad || "?"}</b> ${e.producto}` : e.que).join(" · ");
    const hayZu = deManana.some(e => e.que === "Zuaza");
    const hayTa = deManana.some(e => e.que === "Tahona");

    html += `<div class="lista"><div class="item">
      <div class="cab-item"><span class="txt"><b>Pedir hoy lo de mañana</b>
        <span class="n">${bonito(manana)}</span></span></div>
      <div style="padding:8px 0;font-size:13px">${
        vista || "Todavía no hay nada apuntado para mañana."}</div>
      <div class="nueva-nota" style="border:none">
        <button class="btn-add-2" type="button" onclick="mandarPedidoProveedor('Zuaza')"
          style="${hayZu ? "" : "opacity:.45"}">📲 Pedido a Zuaza (Patxi)</button>
        <button class="btn-add-2" type="button" onclick="mandarPedidoProveedor('Tahona')"
          style="${hayTa ? "" : "opacity:.45"}">📲 Pedido a la Tahona (Jon)</button>
      </div>
    </div></div>`;
  }'''

if t.count(VIEJO) != 1:
    print(f"  NO ENCONTRADO (aparece {t.count(VIEJO)} veces)")
    sys.exit(1)

t = t.replace(VIEJO, NUEVO, 1)
t = t.replace("v-2026-10-26-96", "v-2026-10-26-97", 1)
open(p, "w", encoding="utf-8").write(t)
print("  ok  pedir hoy lo de mañana, con la vista previa")
