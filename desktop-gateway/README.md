# XIL-AC Puerta Local para Windows

## Estado
Prototipo de escritorio en desarrollo. El código incluye una interfaz local y reglas heurísticas. El instalador todavía debe generarse y validarse mediante el flujo de compilación. No es todavía una llave obligatoria que intercepte todas las operaciones del sistema o del backend.

## Política de seguridad
- La transmisión remota está deshabilitada por diseño.
- Esta aplicación no tiene código de red, cliente HTTP, botón de envío ni persistencia del texto.
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
El ejecutable quedará en `dist\XILAC-PuertaLocal.exe`.

Para generar el instalador, instalar Inno Setup y compilar:
```powershell
iscc installer.iss
```
El instalador quedará en `dist\XILAC-PuertaLocal-Setup.exe`.

## Comprobaciones necesarias
- Ejecutar pruebas unitarias.
- Abrir el programa en Windows y revisar la interfaz.
- Verificar con monitorización del sistema que el proceso no realiza conexiones de red.
- Probar instalación, desinstalación y ejecución con permisos de usuario estándar.
- Analizar el ejecutable y el instalador con herramientas de seguridad.
- Firmar los binarios antes de distribución real.

## Limitación esencial
Este programa protege las operaciones realizadas dentro de esta aplicación cuando se usa como revisión local. Todavía no se integra con el backend de XIL-AC ni puede impedir que otra aplicación transmita texto por su cuenta. La integración futura debe hacer que las funciones de XIL-AC utilicen una única puerta de salida controlada y que el servidor mantenga sus propios bloqueos.
