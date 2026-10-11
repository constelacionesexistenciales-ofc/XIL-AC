# XIL-AC Puerta Local para Windows

## Estado
Prototipo de escritorio en desarrollo. La compilación automatizada del ejecutable y del instalador ya funciona en CI, pero aún requiere instalación, ejecución, desinstalación y revisión de seguridad manual en un equipo Windows de prueba.

## Acceso personal
- En el primer inicio, el programa solicita configurar usuario, contraseña y PIN.
- La contraseña debe tener al menos 10 caracteres; el PIN, entre 4 y 8 dígitos.
- En los inicios posteriores se ingresa con usuario y una sola credencial: contraseña o PIN.
- Tras cinco intentos fallidos, el acceso se bloquea temporalmente durante 60 segundos.
- En Windows, el almacén de credenciales se protege con DPAPI para el usuario de Windows actual. No se incluyen credenciales iniciales ni secretos en el repositorio.
- Esta primera versión configura una cuenta local. La administración de varias cuentas y la recuperación segura de acceso todavía deben implementarse antes de un despliegue multiusuario.

**Importante:** como la contraseña se compartió en una conversación, no la reutilices para el alta inicial. Elegí una contraseña nueva y única. El PIN es una vía cómoda, pero más débil que la contraseña; el bloqueo de intentos y DPAPI reducen riesgos, no convierten el PIN en una credencial fuerte frente a un equipo comprometido.

## Política de privacidad
- La transmisión remota está deshabilitada por diseño.
- Esta aplicación no tiene código de red, cliente HTTP, botón de envío ni persistencia del texto revisado.
- La revisión ocurre en memoria local y muestra categorías, no los valores coincidentes.
- La falta de señales no se interpreta como prueba de anonimización.
- El backend remoto de sesiones debe permanecer deshabilitado.

## Compilar manualmente en Windows
Con Python 3.12 instalado:
```powershell
cd desktop-gateway
python -m unittest discover -s tests -v
python -m pip install pyinstaller
pyinstaller --noconfirm --clean --onefile --windowed --name XILAC-PuertaLocal main.py
```
El ejecutable quedará en `dist\\XILAC-PuertaLocal.exe`.

Para generar el instalador, instalar Inno Setup y compilar:
```powershell
iscc installer.iss
```
El instalador quedará en `dist\\XILAC-PuertaLocal-Setup.exe`.

## Comprobaciones necesarias
- Ejecutar pruebas unitarias.
- Abrir el programa en Windows y probar configuración inicial, acceso con contraseña, acceso con PIN y bloqueo por intentos.
- Verificar con monitorización del sistema que el proceso no realiza conexiones de red.
- Probar instalación, desinstalación y ejecución con permisos de usuario estándar.
- Analizar el ejecutable y el instalador con herramientas de seguridad.
- Firmar los binarios antes de distribución real.

## Limitación esencial
Este programa protege las operaciones realizadas dentro de esta aplicación cuando se usa como revisión local. Todavía no se integra con el backend de XIL-AC ni puede impedir que otra aplicación transmita texto por su cuenta. La integración futura debe hacer que las funciones de XIL-AC utilicen una única puerta de salida controlada y que el servidor mantenga sus propios bloqueos.
