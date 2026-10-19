# ⚠️ REPOSITORIO PÚBLICO · solo compila, no contiene código

**Este repositorio es PÚBLICO. Cualquier persona en internet puede leer todo lo que haya aquí, incluido su historial.**

Solo guarda la automatización que compila un programa para Windows usando los minutos gratuitos de GitHub. **No contiene el código de ninguna aplicación, ni llaves, ni datos de personas.** El código que se compila vive en otro repositorio, que es **privado** y tiene otro nombre; aquí solo se descarga durante la compilación, con un permiso de solo lectura, y nunca se imprime.

> ## ¿Estás en el repositorio correcto?
> | | Este (público) | El de trabajo (privado) |
> |---|---|---|
> | Nombre | `compilador-publico` | otro nombre |
> | Qué hay | flujos de compilación y reglas | el código de la aplicación |
> | Visible para | cualquiera | solo su dueño |
> | Carpeta en la Mac | `~/Documentos/compilador-publico` | otra carpeta, nunca dentro de ésta |
>
> Compruébalo siempre con `git remote -v`: aquí la dirección **termina en `/compilador-publico`**. Si no termina así, **no hagas push**.

## Reglas (resumen; el detalle está en [REGLAS.md](REGLAS.md))
1. **Nunca** se copia aquí nada del repositorio de trabajo: ni un archivo de código, ni notas, ni configuraciones, ni compilados.
2. **Nunca** se escribe aquí una llave, un token, una contraseña ni un dato de una persona. Los secretos viven solo en *Settings → Secrets and variables → Actions*.
3. Solo se sube lo que está en la lista blanca del archivo `.gitignore`; todo lo demás se ignora a propósito.
4. El flujo de compilación se lanza **solo a mano** y su resultado sale **cifrado**.
5. Antes de cada commit y cada push corren revisiones automáticas (`herramientas/revisar_limpio.py`); si fallan, no se sube.

Este repositorio no recibe contribuciones ni solicitudes de terceros.
