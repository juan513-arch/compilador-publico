# Reglas de este repositorio PÚBLICO

Léelas antes de cambiar o subir cualquier cosa aquí (personas y sesiones de Claude por igual).

## 1. Qué es y qué no es
- Es **público**: todo lo que se suba, y todo lo que alguna vez se haya subido, lo puede leer cualquiera. Borrar un archivo después no lo borra del historial.
- Es **solo automatización de compilación** para Windows (minutos gratuitos de GitHub en repos públicos).
- **No es** el repositorio de trabajo. Ese es **privado**, tiene **otro nombre**, otra carpeta en la Mac y otro remoto. Nada del uno pasa al otro por git.

## 2. Qué NO se sube nunca (ni "por un momento", ni "para probar")
- Código fuente de cualquier aplicación o del servidor, aunque sea un trozo o un ejemplo.
- Archivos compilados (`.pyd`, `.so`, `.dll`, `.exe`), paquetes (`.zip`, `.tar`, `.gz`), PDF, bases de datos.
- Configuraciones reales (`config.json`, activaciones, `.env`), llaves (`.pem`, `.key`), tokens, contraseñas.
- Datos de personas o de clientes: nombres, correos, números de proceso, direcciones.
- Notas internas, decisiones, registros o capturas del proyecto privado.
- El nombre del repositorio privado, su dirección o la de cualquier servidor propio.
- Registros de ejecución sin cifrar de las pruebas (podrían mostrar cómo funciona el producto por dentro).

## 3. Qué SÍ puede haber aquí (lista blanca)
`README.md`, `REGLAS.md`, `.gitignore`, `.github/workflows/*.yml` y `herramientas/*` (scripts genéricos de revisión y de cifrado). Nada más. El `.gitignore` ignora todo lo que no esté en esta lista, para que un archivo ajeno ni siquiera pueda agregarse por descuido.

## 4. Secretos (se crean a mano en GitHub, nunca en un archivo)
| Secreto | Para qué | Cómo debe ser |
|---|---|---|
| `FUENTE_REPO` | Dirección del repositorio privado (`dueño/nombre`) | Solo como secreto: así ni su nombre aparece en este repositorio |
| `FUENTE_CLAVE_SSH` | Leer ese repositorio al compilar | Clave de despliegue (*deploy key*) **de solo lectura de un único repositorio**; no es un token de cuenta. Se revoca borrándola del repositorio privado |
| `CLAVE_RESULTADO` | Cifrar el resultado y los registros | Aleatoria, larga; una copia queda en el llavero de la Mac del dueño, nunca en un archivo |
| `PALABRAS_PROHIBIDAS` | Lista (separada por comas) de palabras que no deben aparecer nunca aquí | Opcional; la usa la revisión automática |

Ningún flujo imprime un secreto. Si un secreto llegara a verse en un registro, se **revoca de inmediato** y se crea otro.

## 5. Cómo funciona el flujo de compilación
1. Se lanza **a mano** (*Actions → Compilar Windows → Run workflow*), indicando la rama o el commit del repositorio privado.
2. Descarga ese código con `FUENTE_CLAVE_SSH` en una carpeta temporal del ejecutor (se destruye al terminar).
3. Compila y, si se pidió, corre las pruebas **en silencio**: en el registro público solo salen "bien/falló" y conteos.
4. El resultado y los registros detallados se **cifran** con `CLAVE_RESULTADO` antes de subirse como artefacto (3 días de vida).
5. El dueño lo baja, lo descifra en su Mac con `herramientas/descifrar.py` y lo usa en el repositorio privado.

## 6. Reglas del flujo
- Solo `workflow_dispatch` (a mano). **Nunca** `pull_request_target`, ni `pull_request` con secretos, ni disparos automáticos por push que usen secretos.
- Los permisos del ejecutor son de solo lectura (`permissions: contents: read`).
- Solo acciones de GitHub (`actions/*`); no se agregan acciones de terceros sin revisarlas y fijarlas por versión.
- No hay colaboradores, ni *issues*, ni wiki, ni solicitudes de terceros. Las ejecuciones desde forks exigen aprobación.

## 7. Antes de cada commit y de cada push (lista de verificación)
- [ ] `pwd` es la carpeta de este repositorio (`compilador-publico`), **no** la del proyecto privado.
- [ ] `git remote -v` termina en `/compilador-publico`.
- [ ] `git status` muestra solo archivos de la lista blanca del punto 3.
- [ ] `python3 herramientas/revisar_limpio.py` termina en verde (los *hooks* lo corren solos).
- [ ] No hay ninguna llave, token, ni nombre del proyecto privado en lo que se va a subir.

## 8. Si algo salió mal
1. **No borres y vuelvas a subir**: el historial público ya lo tiene.
2. Revoca de inmediato el secreto o token implicado.
3. Si se subió algo sensible: borra este repositorio (Settings → Danger zone) y créalo de nuevo; no hay otra forma de quitarlo del historial.
4. Cambia de lugar o de clave todo lo que ese contenido pudiera dar a conocer.
