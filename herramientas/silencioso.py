#!/usr/bin/env python3
"""Corre un comando guardando TODA su salida en un archivo (que luego se cifra) y mostrando en el registro público solo
«bien / falló» y, si se pide, las líneas que cumplan un patrón seguro (conteos). Genérico: no sabe qué corre.

  python3 herramientas/silencioso.py --nombre "Pruebas" --log salida/registros/pruebas.txt [--cwd DIR] [--mostrar REGEX] -- COMANDO ...

Sale con el mismo código que el comando.
"""
import argparse
import os
import re
import subprocess
import sys
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nombre", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--cwd", default=None)
    ap.add_argument("--mostrar", default=None)
    ap.add_argument("comando", nargs=argparse.REMAINDER)
    args = ap.parse_args()
    comando = args.comando[1:] if args.comando[:1] == ["--"] else args.comando
    if not comando:
        sys.exit("Falta el comando.")
    os.makedirs(os.path.dirname(os.path.abspath(args.log)), exist_ok=True)
    inicio = time.time()
    with open(args.log, "wb") as f:
        r = subprocess.run(comando, cwd=args.cwd, stdout=f, stderr=subprocess.STDOUT)
    segundos = int(time.time() - inicio)
    print(f"[{'BIEN' if r.returncode == 0 else 'FALLÓ'}] {args.nombre} ({segundos} s, código {r.returncode})")
    if args.mostrar:
        patron = re.compile(args.mostrar)
        with open(args.log, encoding="utf-8", errors="replace") as f:
            for linea in f:
                if patron.search(linea):
                    print("   " + linea.rstrip()[:160])
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
