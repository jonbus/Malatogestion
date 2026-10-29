"""Corrige la prueba de usuario con las rutas y cuerpos de verdad."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/prueba-usuario-completa.mjs"
t = open(p, encoding="utf-8").read()
antes = t

# --- E: la ruta es /api/marcas y se manda un cambio
t = t.replace(
    "const m1 = await post('/api/marcar', { clave, valor: true, q: 'op1' });",
    "const m1 = await post('/api/marcas', { quien: 'op1', cambios: { [clave]: { q: 'op1' } } });")
t = t.replace(
    "const m2 = await post('/api/marcar', { clave, valor: false });",
    "const m2 = await post('/api/marcas', { quien: 'op1', cambios: { [clave]: null } });")
t = t.replace(
    "await post('/api/marcar', { clave, valor: false });",
    "await post('/api/marcas', { quien: 'op1', cambios: { [clave]: null } });")

# --- F: la nota lleva `fecha`, no `f`
t = t.replace(
    "const n1 = await post('/api/nota', { f: hoy, texto: T, ambito: 'general', q: 'op1' });",
    "const n1 = await post('/api/nota', { quien: 'op1', fecha: hoy, texto: T, ambito: 'general' });")
t = t.replace(
    "const n2 = await post('/api/nota', { f: hoy, texto: '', ambito: 'general' });",
    "const n2 = await post('/api/nota', { quien: 'op1', fecha: hoy, texto: '', ambito: 'general' });")

# --- I: la ruta es /api/trasladar
t = t.replace(
    "const t1 = await post('/api/traslado', { clave: T + ':x', destino: lunes });",
    "const t1 = await post('/api/trasladar', { quien: 'op1', clave: T + ':x', destino: lunes });")
t = t.replace(
    "const t2 = await post('/api/traslado', { clave: T + ':x', destino: null });",
    "const t2 = await post('/api/trasladar', { quien: 'op1', clave: T + ':x', destino: null });")
t = t.replace(
    "await post('/api/traslado', { clave: T + ':x', destino: null });",
    "await post('/api/trasladar', { quien: 'op1', clave: T + ':x', destino: null });")

if t == antes:
    print("  SIN CAMBIOS (revisar)")
else:
    open(p, "w", encoding="utf-8").write(t)
    print("  prueba corregida con las rutas de verdad")
