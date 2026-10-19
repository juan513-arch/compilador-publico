#!/usr/bin/env python3
"""Revisa que este repositorio PÚBLICO siga limpio: solo archivos de la lista blanca, sin compilados, sin llaves, sin
datos ni palabras del proyecto privado y con flujos seguros. Lo corren los hooks (antes de cada commit y push) y el flujo
`revisar.yml` en GitHub. Si falla, NO se sube. Solo usa la biblioteca estándar.

  python3 herramientas/revisar_limpio.py            revisa todos los archivos versionados
  python3 herramientas/revisar_limpio.py --staged   revisa solo lo que se va a confirmar (hook pre-commit)
  python3 herramientas/revisar_limpio.py --remoto   además comprueba que los remotos apuntan a este repositorio

Las palabras que no deben aparecer vienen de la variable PALABRAS_PROHIBIDAS (separadas por comas; en GitHub, un secreto)
o del archivo ~/.config/compilador-publico/palabras.txt (una por línea). La lista NO está en el repositorio a propósito.
"""
import fnmatch
import os
import re
import subprocess
import sys

NOMBRE_DEL_REPO = "compilador-publico"
LISTA_BLANCA = (
    "README.md", "REGLAS.md", ".gitignore",
    ".github/workflows/*.yml",
    "herramientas/*.py", "herramientas/*.sh",
    "herramientas/hooks/pre-commit", "herramientas/hooks/pre-push",
)
EXTENSIONES_PROHIBIDAS = (".pyd", ".so", ".dll", ".exe", ".zip", ".tar", ".gz", ".tgz", ".cif", ".pdf", ".pem", ".key",
                          ".db", ".sqlite", ".bat", ".command", ".app", ".dmg", ".pkg", ".p12")
NOMBRES_PROHIBIDOS = ("config.json", "activacion.json", ".env", "worker.js", "app.py", "panel.py")
MAXIMO_BYTES = 100_000
# Este mismo archivo contiene los patrones de abajo: no se revisa su contenido (sí su nombre y tamaño).
ESTE_ARCHIVO = "herramientas/revisar_limpio.py"
PATRONES_DE_LLAVES = [
    r"gh[pousr]_[A-Za-z0-9]{20,}", r"github_pat_[A-Za-z0-9_]{20,}", r"sk-ant-[A-Za-z0-9_-]{10,}", r"AKIA[0-9A-Z]{16}",
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----", r"xox[bp]-[A-Za-z0-9-]{10,}",
    r"(?i)(api[_-]?key|secret|token|passw(?:or)?d|clave)[\"']?\s*[:=]\s*[\"'][A-Za-z0-9_\-+/=]{24,}[\"']",
]


def git(*args, texto=True):
    return subprocess.run(["git", *args], capture_output=True, text=texto).stdout


def archivos(solo_los_preparados):
    if solo_los_preparados:
        nombres = git("diff", "--cached", "--name-only", "--diff-filter=ACMR")
    else:
        nombres = git("ls-files")
    return [n for n in nombres.splitlines() if n]


def contenido(ruta, solo_los_preparados):
    if solo_los_preparados:
        return subprocess.run(["git", "show", f":{ruta}"], capture_output=True).stdout
    try:
        with open(ruta, "rb") as f:
            return f.read()
    except OSError:
        return b""


def palabras_prohibidas():
    palabras = [p.strip() for p in os.environ.get("PALABRAS_PROHIBIDAS", "").split(",") if p.strip()]
    local = os.path.expanduser("~/.config/compilador-publico/palabras.txt")
    if os.path.isfile(local):
        with open(local, encoding="utf-8") as f:
            palabras += [l.strip() for l in f if l.strip() and not l.startswith("#")]
    return sorted(set(palabras), key=str.lower)


def revisar_flujo(ruta, texto, problemas):
    sin_comentarios = "\n".join(l.split("#", 1)[0] for l in texto.splitlines())
    if "pull_request_target" in sin_comentarios:
        problemas.append(f"{ruta}: usa pull_request_target (prohibido: ejecutaría código ajeno con secretos)")
    usa_secretos = re.search(r"secrets\.(?!GITHUB_TOKEN)", sin_comentarios)
    if usa_secretos and re.search(r"^\s*(push|pull_request|schedule|workflow_run)\s*:", sin_comentarios, re.M):
        problemas.append(f"{ruta}: usa secretos y también se dispara solo; con secretos solo vale workflow_dispatch")
    for linea in sin_comentarios.splitlines():
        m = re.match(r"\s*-?\s*uses:\s*(\S+)", linea)
        if m and not (m.group(1).startswith("actions/") or m.group(1).startswith("./")):
            problemas.append(f"{ruta}: la acción {m.group(1)} no es de GitHub (solo se permite actions/*)")
    if "permissions:" not in sin_comentarios:
        problemas.append(f"{ruta}: falta 'permissions:' (los permisos del ejecutor deben ser mínimos)")


def main():
    solo_preparados = "--staged" in sys.argv
    revisar_remotos = "--remoto" in sys.argv
    problemas = []

    if revisar_remotos:
        remotos = git("remote", "-v").splitlines()
        for linea in remotos:
            partes = linea.split()
            if len(partes) >= 2 and not re.search(r"/" + re.escape(NOMBRE_DEL_REPO) + r"(\.git)?$", partes[1]):
                problemas.append(f"el remoto «{partes[0]}» apunta a otro repositorio ({'***' if partes[1] else ''}): aquí solo se sube a /{NOMBRE_DEL_REPO}")

    palabras = palabras_prohibidas()
    rutas = archivos(solo_preparados)
    for ruta in rutas:
        if not any(fnmatch.fnmatch(ruta, patron) and ruta.count("/") <= patron.count("/") for patron in LISTA_BLANCA):
            problemas.append(f"{ruta}: no está en la lista blanca (REGLAS.md, punto 3)")
        base = os.path.basename(ruta).lower()
        if base.endswith(EXTENSIONES_PROHIBIDAS) or base in NOMBRES_PROHIBIDOS:
            problemas.append(f"{ruta}: tipo de archivo prohibido en un repositorio público")
        datos = contenido(ruta, solo_preparados)
        if len(datos) > MAXIMO_BYTES:
            problemas.append(f"{ruta}: pesa {len(datos)} bytes (máximo {MAXIMO_BYTES}); aquí no van archivos grandes")
        if ruta == ESTE_ARCHIVO:
            continue
        try:
            texto = datos.decode("utf-8")
        except UnicodeDecodeError:
            problemas.append(f"{ruta}: no es texto; aquí solo va texto")
            continue
        for patron in PATRONES_DE_LLAVES:
            if re.search(patron, texto):
                problemas.append(f"{ruta}: parece contener una llave o un token")
                break
        for palabra in palabras:
            if re.search(re.escape(palabra), texto, re.I):
                problemas.append(f"{ruta}: contiene una palabra del proyecto privado (lista secreta)")
                break
        if ruta.startswith(".github/workflows/"):
            revisar_flujo(ruta, texto, problemas)

    if not palabras:
        print("Aviso: no hay lista de palabras prohibidas (PALABRAS_PROHIBIDAS o ~/.config/compilador-publico/palabras.txt); "
              "solo se aplican las demás revisiones.")
    if problemas:
        print("✘ El repositorio público NO está limpio; no se debe subir:")
        for p in problemas:
            print("  -", p)
        sys.exit(1)
    print(f"✔ Limpio: {len(rutas)} archivo(s) revisados.")


if __name__ == "__main__":
    main()
