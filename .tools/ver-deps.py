"""Qué necesita el núcleo para funcionar fuera de Netlify."""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
t = open("docs/nube/netlify/functions/nucleo.js", encoding="utf-8").read()
print("  require(...):", sorted(set(re.findall(r"require\('([^']+)'\)", t))))
print("  usa crypto/timingSafeEqual:", "timingSafeEqual" in t)
print("  usa Buffer:", "Buffer" in t)
print("  usa process:", "process." in t)
