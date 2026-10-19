#!/usr/bin/env python3
"""Descifra lo que dejó cifrar.py y lo extrae en una carpeta. Se usa en la Mac del dueño, nunca en GitHub.

  python3 herramientas/descifrar.py ARCHIVO.cif CARPETA_DESTINO

La clave se toma de la variable CLAVE_RESULTADO o, en macOS, del llavero (servicio «compilador-publico-clave»). Nunca se
imprime. Extrae con filtro de seguridad (sin rutas absolutas ni «..»).
"""
import io
import os
import subprocess
import sys
import tarfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cifrar import descifrar  # noqa: E402


def clave():
    valor = os.environ.get("CLAVE_RESULTADO", "")
    if not valor and sys.platform == "darwin":
        r = subprocess.run(["security", "find-generic-password", "-s", "compilador-publico-clave", "-w"],
                           capture_output=True, text=True)
        valor = r.stdout.strip() if r.returncode == 0 else ""
    return valor


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    archivo, destino = sys.argv[1], sys.argv[2]
    k = clave()
    if not k:
        sys.exit("No encuentro la clave (ni en CLAVE_RESULTADO ni en el llavero).")
    with open(archivo, "rb") as f:
        datos = descifrar(f.read(), k)
    os.makedirs(destino, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(datos), mode="r:gz") as tar:
        tar.extractall(destino, filter="data")
    print(f"Descifrado en {destino}")


if __name__ == "__main__":
    main()
