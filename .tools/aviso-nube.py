"""Aviso en la versión de Cloudflare: «esta no es la aplicación buena».

Solo salta cuando la página se abre desde workers.dev. En el Orange Pi
no aparece nada. El mismo fichero sirve para los dos.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()

if "aviso-nube" in t:
    print("  ya estaba puesto")
    sys.exit(0)

MARCA = "<body>"
if MARCA not in t:
    print("  NO ENCONTRADO <body>")
    sys.exit(1)

BLOQUE = '''<body>

<!-- AVISO: si esta página se abre desde la nube, no es la aplicación buena -->
<div id="aviso-nube" style="display:none;position:fixed;inset:0;z-index:99999;
     background:#EEE9DC;color:#1F4A2E;font-family:Arial,Helvetica,sans-serif;
     padding:32px 22px;text-align:center;overflow-y:auto">
  <div style="max-width:560px;margin:0 auto">
    <img src="marca/logo-o-verde.png" alt="" style="width:78px;margin:14px 0 26px">
    <h1 style="font-size:27px;line-height:1.3;margin:0 0 18px;color:#1E9A45">
      Esta no es la<br>aplicación de la tienda
    </h1>
    <p style="font-size:17px;line-height:1.55;margin:0 0 14px">
      Estás en la <b>versión de pruebas de la nube</b>.
    </p>
    <p style="font-size:17px;line-height:1.55;margin:0 0 26px">
      <b>Todo lo que apuntes aquí no lo verá nadie más.</b>
      Ni la tienda, ni coordinación, ni la Jefa.
    </p>
    <a href="https://orangepi4pro.tail369549.ts.net:8443" style="display:block;
       background:#1E9A45;color:#fff;text-decoration:none;font-weight:bold;
       font-size:19px;padding:18px 20px;border-radius:14px;margin:0 0 18px">
      Ir a la aplicación buena
    </a>
    <p style="font-size:13px;color:#6B7F70;margin:0">
      orangepi4pro.tail369549.ts.net:8443
    </p>
  </div>
</div>
<script>
(function(){
  var h = location.hostname || "";
  if(h.indexOf("workers.dev") === -1) return;   /* en el Orange Pi no sale */
  var d = document.getElementById("aviso-nube");
  if(!d) return;
  d.style.display = "block";
  /* y que no se pueda seguir usando por debajo */
  document.documentElement.style.overflow = "hidden";
})();
</script>'''

t = t.replace(MARCA, BLOQUE, 1)
t = t.replace("v-2026-10-26-97", "v-2026-10-26-98", 1)
t = t.replace("v-2026-10-26-96", "v-2026-10-26-98", 1)
t = t.replace("v-2026-10-26-95", "v-2026-10-26-98", 1)

open(p, "w", encoding="utf-8").write(t)
print("  ok  el aviso de la nube, puesto")
