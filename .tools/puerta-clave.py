"""Una contraseña para abrir la aplicación: Malato20."""
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()

if "puerta-clave" in t:
    print("  ya estaba puesto")
    sys.exit(0)

MARCA = '<div id="aviso-nube"'
if MARCA not in t:
    print("  NO ENCONTRADO el aviso de la nube")
    sys.exit(1)

BLOQUE = '''<!-- LA PUERTA: contraseña para entrar -->
<div id="puerta-clave" style="display:none;position:fixed;inset:0;z-index:99998;
     background:#EEE9DC;color:#1F4A2E;font-family:Arial,Helvetica,sans-serif;
     flex-direction:column;align-items:center;justify-content:center;padding:30px">
  <img src="marca/logo-o-verde.png" alt="" style="width:86px;margin:0 0 26px">
  <h1 style="font-size:23px;margin:0 0 26px;color:#1E9A45;font-weight:bold">Malato</h1>
  <input id="clave" type="password" inputmode="text" autocomplete="off"
         placeholder="Contraseña"
         style="width:100%;max-width:320px;font-size:19px;padding:15px 16px;
                border:2px solid #1E9A45;border-radius:12px;outline:none;
                background:#fff;text-align:center">
  <button onclick="abrirPuerta()" style="width:100%;max-width:320px;margin-top:14px;
          background:#1E9A45;color:#fff;border:0;border-radius:12px;padding:16px;
          font-size:18px;font-weight:bold">Entrar</button>
  <p id="clave-mal" style="display:none;color:#B03030;font-size:15px;margin:16px 0 0">
    Esa no es.</p>
</div>
<script>
function abrirPuerta(){
  var c = document.getElementById("clave");
  if(c && c.value === "Malato20"){
    try{ localStorage.setItem("malato-entrado", "1"); }catch(e){}
    document.getElementById("puerta-clave").style.display = "none";
  } else {
    var m = document.getElementById("clave-mal");
    if(m) m.style.display = "block";
    if(c){ c.value = ""; c.focus(); }
  }
}
(function(){
  var dentro = false;
  try{ dentro = localStorage.getItem("malato-entrado") === "1"; }catch(e){}
  if(dentro) return;
  var d = document.getElementById("puerta-clave");
  if(d) d.style.display = "flex";
  var c = document.getElementById("clave");
  if(c) setTimeout(function(){ c.focus(); }, 300);
})();
</script>

<div id="aviso-nube"'''

t = t.replace(MARCA, BLOQUE, 1)
t = t.replace("v-2026-10-26-98", "v-2026-10-26-99", 1)

open(p, "w", encoding="utf-8").write(t)
print("  ok  la puerta con contraseña, puesta")
