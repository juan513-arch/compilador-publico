#!/bin/sh
# Genera la clave que cifra el resultado de la compilación: queda en el LLAVERO de esta Mac (para descifrar) y como secreto
# CLAVE_RESULTADO del repositorio público en GitHub (para cifrar). La clave NUNCA se imprime ni se guarda en un archivo.
# Lo corre el dueño, en su terminal:   /bin/sh ~/Documentos/compilador-publico/herramientas/generar_clave.sh
# Si ya existía una clave, la reemplaza en los dos lados (lo cifrado antes con la anterior ya no se podrá abrir).
set -e
REPO="juan513-arch/compilador-publico"
GH="$HOME/.local/bin/gh"
[ -x "$GH" ] || GH="$(command -v gh)"
[ -n "$GH" ] || { echo "✘ No encuentro gh (GitHub CLI)."; exit 1; }
AQUI="$(cd "$(dirname "$0")/.." && pwd)"
case "$AQUI" in
  */compilador-publico) ;;
  *) echo "✘ Este script no está dentro de la carpeta compilador-publico: no sigo."; exit 1 ;;
esac
CLAVE="$(/usr/bin/openssl rand -base64 36)"
/usr/bin/security add-generic-password -U -a "$USER" -s compilador-publico-clave -w "$CLAVE"
printf '%s' "$CLAVE" | "$GH" secret set CLAVE_RESULTADO --repo "$REPO"
unset CLAVE
echo "✔ Clave creada: en el llavero (servicio compilador-publico-clave) y como secreto CLAVE_RESULTADO. No se mostró."
