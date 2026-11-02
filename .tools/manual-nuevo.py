"""Mete en el manual lo nuevo: papelera y cajita, el parking, las napolitanas,
la carpa montada, los regalos de la batukada y el anuncio."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"docs\ANIVERSARIO-PROCEDIMIENTO.md"
t = open(p, encoding="utf-8").read()
fallos = 0


def rep(v, n, e):
    global t, fallos
    if v in t:
        t = t.replace(v, n, 1)
        fallos += 1
        print("  ok  " + e)
    else:
        print("  NO ENCONTRADO: " + e)


# --- 1 · la papelera y la cajita del canje
rep("""- [ ] **Los premios, a mano y a la vista** — **para que se vea que existen**""",
    """- [ ] **Los premios, a mano y a la vista** — **para que se vea que existen**
- [ ] **La PAPELERA**: donde van las papeletas **no premiadas**
- [ ] **La CAJITA**: donde van las papeletas **premiadas** — **esas se guardan, son el control**
- [ ] **Las dos, ya preparadas**, al lado de la urna""",
    "papelera y cajita")

rep("""- [ ] **El platito de las gominolas**

**También va en la mesa de la tarta: un platito con caramelos gummy jellys.**""",
    """- [ ] **El platito de las gominolas**

**También va en la mesa de la tarta: un platito con caramelos gummy jellys.**""",
    "(sin cambio)")

# --- 2 · el parking, a primera hora
rep("""| **10:00** | **Abrir.** **Los dos niños en la puerta** con las palmeras y las bolsas |""",
    """| **9:00** | **Hacer o reservar sitio en el PARKING** para la batukada |
| **10:00** | **Abrir.** **Los dos niños en la puerta** con las palmeras y las bolsas |""",
    "el parking, a primera hora")

# --- 3 · las napolitanas
rep("""| **Las gominolas** | un platito con gummy jellys | — | — |""",
    """| **Las gominolas** | un platito con gummy jellys | — | — |
| **Las mini napolitanas** | **las manda Cadagua** — **por si no llegan las palmeras, y para la batukada** | — | — |""",
    "las napolitanas, en la lista")

rep("""- [ ] **Taparlas hasta la hora** — **están en la calle y son comida**""",
    """- [ ] **Taparlas hasta la hora** — **están en la calle y son comida**
- [ ] **Las mini napolitanas de Cadagua, aparte** — **son el recambio si se acaban las palmeras**, y una parte **va para la batukada**""",
    "las napolitanas, en la mesa")

# --- 4 · la carpa se queda montada
rep("""- [ ] **Comprobar que no tapa la entrada** ni la mesa de la tarta""",
    """- [ ] **Comprobar que no tapa la entrada** ni la mesa de la tarta
- [ ] **Dejarla MONTADA todo el día**, aunque salga el sol — **por si llueve de repente o por lo que pueda pasar**""",
    "la carpa, montada todo el dia")

# --- 5 · los regalos de la batukada
rep("""- [ ] **Las botellas negras de agua de Pepsi** — **son el regalo**""",
    """- [ ] **Las botellas negras de agua de Pepsi** — **son el regalo**

**Y a cada integrante de la batukada se le regala una bolsa del 20 aniversario con unos calcetines y una cantimplora.**

- [ ] **Preparar tantas bolsas como integrantes vengan**
- [ ] **Las preparan los niños**, en un rato que no haya clientes
- [ ] **Que estén listas antes de que la batukada termine** — **se entregan al acabar, no después**""",
    "los regalos de la batukada")

# --- 6 · el anuncio y el video
rep("""## 11 · El día, hora a hora""",
    """## 11 · El anuncio, unos días antes

**Antes del domingo hay que avisar a todo el mundo**, o el día llega y no se ha enterado nadie.

- [ ] **A la familia** — por teléfono, no por el estado
- [ ] **A los amigos**
- [ ] **A los clientes** — **en la tienda, en voz alta**: *«el domingo 8 hacemos 20 años, ven»*
- [ ] **En el estado de WhatsApp**
- [ ] **El cartel, pegado en la tienda**

**Y el vídeo:**

- [ ] **Fotos de las trabajadoras**
- [ ] **La canción de samba de Malato** por debajo
- [ ] **Montarlo y mandarlo** — **cuanto antes, mejor**: **un vídeo el sábado por la noche no lo ve nadie**

> **Y una cosa**: **el cartel dice «domingo 8, por la mañana»** — **cuando lo mandes, di la hora**: **de 10:00 a 14:30**. **«Por la mañana» se convierte en «a las 9 y media» si no se dice.**

## 12 · El día, hora a hora""",
    "el anuncio y el video")

# se renumera
import re

n = 0


def num(m):
    global n
    n += 1
    return f"## {n} ·"


t = re.sub(r"^## \d+ ·", num, t, flags=re.M)

open(p, "w", encoding="utf-8").write(t)
print(f"\n  apartados: {n}")
print(f"  cambios: {fallos}")
