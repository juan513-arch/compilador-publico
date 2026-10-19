#!/bin/sh
# Prepara ESTA copia local del repositorio público: activa los hooks de revisión y comprueba que no es el repositorio
# de trabajo. Se corre una sola vez después de clonar:  sh herramientas/preparar_local.sh
set -e
RAIZ="$(git rev-parse --show-toplevel)"
cd "$RAIZ"
case "$(basename "$RAIZ")" in
  compilador-publico) ;;
  *) echo "✘ Esta carpeta no se llama compilador-publico: no es el repositorio público. No sigo."; exit 1 ;;
esac
chmod +x herramientas/hooks/pre-commit herramientas/hooks/pre-push
git config core.hooksPath herramientas/hooks
# La identidad de los commits de un repositorio público no debe ser la personal: se usa el correo «noreply» de GitHub.
if git config user.email | grep -qv "users.noreply.github.com"; then
  echo "✘ user.email de este repositorio no es el correo noreply de GitHub; ajústalo antes de confirmar nada:"
  echo "    git config user.email 'ID+usuario@users.noreply.github.com'"
  exit 1
fi
python3 herramientas/revisar_limpio.py --remoto
echo "✔ Hooks activados en $RAIZ"
