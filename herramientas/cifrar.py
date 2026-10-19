#!/usr/bin/env python3
"""Cifra archivos o carpetas con una clave (AES-256-GCM, clave derivada con scrypt). Genérico: no sabe nada de lo que cifra.

  python3 herramientas/cifrar.py SALIDA.cif RUTA [RUTA ...]

La clave sale de la variable de entorno CLAVE_RESULTADO (en GitHub, un secreto) y NUNCA se imprime. Empaqueta las rutas en un
.tar.gz en memoria y escribe: «CPC1» + sal (16) + nonce (12) + texto cifrado. Necesita el paquete «cryptography».
"""
import io
import os
import sys
import tarfile

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

MAGIA = b"CPC1"


def derivar(clave, sal):
    return Scrypt(salt=sal, length=32, n=2 ** 15, r=8, p=1).derive(clave.encode("utf-8"))


def cifrar(datos, clave):
    sal, nonce = os.urandom(16), os.urandom(12)
    return MAGIA + sal + nonce + AESGCM(derivar(clave, sal)).encrypt(nonce, datos, MAGIA)


def descifrar(blob, clave):
    if blob[:4] != MAGIA:
        raise ValueError("no es un archivo cifrado por estas herramientas")
    sal, nonce, cuerpo = blob[4:20], blob[20:32], blob[32:]
    return AESGCM(derivar(clave, sal)).decrypt(nonce, cuerpo, MAGIA)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    clave = os.environ.get("CLAVE_RESULTADO", "")
    if len(clave) < 24:
        sys.exit("Falta CLAVE_RESULTADO (o es demasiado corta): no se cifra nada.")
    salida, rutas = sys.argv[1], sys.argv[2:]
    memoria = io.BytesIO()
    with tarfile.open(fileobj=memoria, mode="w:gz") as tar:
        for ruta in rutas:
            if os.path.exists(ruta):
                tar.add(ruta, arcname=os.path.basename(os.path.normpath(ruta)))
    os.makedirs(os.path.dirname(os.path.abspath(salida)), exist_ok=True)
    with open(salida, "wb") as f:
        f.write(cifrar(memoria.getvalue(), clave))
    print(f"Cifrado: {os.path.basename(salida)} ({os.path.getsize(salida)} bytes)")


if __name__ == "__main__":
    main()
