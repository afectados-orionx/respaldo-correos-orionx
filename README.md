# Respaldo de correos de OrionX para afectados

Herramienta para que cualquier cliente de OrionX (exchange chileno que anunció su cierre y suspendió retiros el 3 de septiembre de 2026) descargue a su computador **todos los correos que prueban sus depósitos, compras, ventas, retiros y saldos**, antes de que el acceso a la plataforma desaparezca.

Guarda cada correo original (.eml), una versión en texto legible, los adjuntos (boletas PDF), un índice y una tabla de movimientos con montos, monedas, direcciones y hashes detectados. Con eso puedes acreditar tu saldo ante la Fiscalía, el SERNAC, la CMF, un abogado o el plan de restitución.

**Solo lee tu correo. No borra, mueve ni marca nada. No envía datos a ningún lugar que no sea el servidor de tu propio correo.** Es un único archivo de Python sin dependencias externas. Puedes leerlo completo antes de ejecutarlo.

> Aviso: esto no es asesoría legal. El respaldo es evidencia; qué hacer con ella lo decides tú con un abogado. La detección automática de montos y direcciones puede tener errores: verifica siempre contra el correo original.

## Requisitos

- Python 3.8 o superior. En Windows descárgalo desde https://www.python.org/downloads/ (marca la casilla "Add Python to PATH" al instalar). En macOS y Linux ya suele venir instalado.
- Descarga el archivo `respaldo_correos_orionx.py` de este repositorio (botón "Code" > "Download ZIP", o clic en el archivo > "Download raw file").

## Opción A: conectarse a Gmail (recomendada, 5 minutos)

Gmail no permite que un programa entre con tu contraseña normal. Debes crear una **contraseña de aplicación**, que es una clave de 16 letras que sirve solo para esto y que puedes borrar al terminar.

1. Activa la verificación en dos pasos en tu cuenta Google si no la tienes: https://myaccount.google.com/signinoptions/two-step-verification
2. Crea una contraseña de aplicación en https://myaccount.google.com/apppasswords. Ponle un nombre como "respaldo orionx" y copia la clave de 16 letras que aparece.
3. Abre una terminal (en Windows: busca "cmd" o "PowerShell"; en macOS: "Terminal") en la carpeta donde descargaste el script y ejecuta:

```bash
python3 respaldo_correos_orionx.py --correo tu_correo@gmail.com
```

En Windows suele ser `python` en vez de `python3`.

4. Cuando pida la contraseña, pega la clave de 16 letras (no se ve mientras escribes; es normal) y presiona Enter.
5. Espera. Con más de mil correos puede tardar 10 a 20 minutos. Si se corta, vuelve a ejecutar el mismo comando: continúa donde quedó.
6. Al terminar, **borra la contraseña de aplicación** en la misma página donde la creaste.

Funciona también con Outlook/Hotmail, Yahoo e iCloud (todos exigen una contraseña de aplicación similar). Para otro proveedor agrega `--servidor imap.tuproveedor.cl`.

## Opción B: desde Google Takeout (sin contraseñas, más lento)

Si prefieres no crear contraseñas de aplicación:

1. Entra a https://takeout.google.com, deselecciona todo y marca solo **Correo**. Puedes elegir "Todos los datos de correo incluidos" o filtrar por etiquetas.
2. Pide la exportación. Google te enviará un enlace de descarga (puede tardar horas). Descomprime el archivo: dentro hay un archivo `.mbox`.
3. Ejecuta:

```bash
python3 respaldo_correos_orionx.py --mbox "ruta/al/archivo.mbox"
```

## Opción C: archivos .eml

Si ya descargaste correos uno a uno desde tu cliente de correo (Thunderbird, Outlook, Apple Mail exportan .eml):

```bash
python3 respaldo_correos_orionx.py --eml carpeta_con_los_eml/
```

## Qué obtienes

Se crea la carpeta `respaldo_orionx/` con:

| Archivo o carpeta | Contenido |
|---|---|
| `RESUMEN.md` | Cuántos correos hay por categoría y por año, y qué direcciones y hashes de transacciones aparecen. |
| `indice.csv` | Un correo por fila: fecha, categoría, remitente, asunto, adjuntos, archivo. Se abre en Excel o LibreOffice. |
| `movimientos.csv` | Solo órdenes, abonos, retiros, avisos bancarios y boletas, con montos en CLP y cripto, monedas, direcciones y hashes detectados. Sirve para reconstruir tu saldo. |
| `texto/` | Cada correo en texto plano, con encabezados. |
| `eml/` | Cada correo original completo. Es la evidencia formal: conserva cabeceras técnicas que acreditan origen y fecha. |
| `adjuntos/` | Boletas PDF y otros adjuntos. |

Categorías: `orden` (compra o venta ejecutada), `abono` (acreditación de CLP), `retiro`, `transferencia_banco` (avisos de tu banco de transferencias hacia o desde ORIONX SPA), `boleta`, `comunicado_oficial`, `soporte`, `cuenta`, `login`, `newsletter`, `otro`.

## Opciones útiles

```
--salida carpeta       dónde guardar (por defecto ./respaldo_orionx)
--desde 2017-01-01     solo correos desde esa fecha
--hasta 2026-12-31     solo correos anteriores a esa fecha
--html                 guardar también el HTML original de cada correo
--buzon "INBOX"        revisar solo un buzón IMAP (por defecto busca en todo el correo de Gmail)
--lote 20              descargar de a menos correos si la conexión es lenta
```

## Después de respaldar

En la carpeta [`denuncias/`](denuncias/README.md) está la guía paso a paso para presentar tu propia denuncia en la Fiscalía, la CMF y el SERNAC, con los datos exactos de los formularios y textos listos para adaptar.

1. Copia la carpeta completa a un pendrive o disco externo y a una nube tuya. Que no exista solo en el computador.
2. Toma capturas de pantalla de tu saldo e historial en la plataforma de OrionX mientras siga en línea, y exporta el historial a CSV si la plataforma lo permite.
3. Presenta tu denuncia como víctima en https://www.fiscaliadechile.cl y reclama en SERNAC y CMF. Adjunta `RESUMEN.md`, `movimientos.csv` y los correos relevantes.
4. Si en `RESUMEN.md` aparecen direcciones o hashes de retiros en Bitcoin, Ethereum, Polkadot u otra red, esos datos permiten identificar en la cadena las billeteras que OrionX controlaba. Compártelos (sin datos personales) con el grupo de afectados para el rastreo colectivo.
5. Desconfía de cualquier persona que te contacte ofreciendo "recuperar" tus fondos. Nadie puede hacerlo fuera de la vía legal.

## Privacidad y seguridad

- El script se conecta únicamente a tu servidor de correo, por conexión cifrada (IMAP sobre TLS), en modo solo lectura.
- La contraseña se pide por teclado y no se guarda en ningún archivo. Si la pasas en la variable de entorno `IMAP_PASSWORD`, tampoco se escribe a disco.
- El archivo `estado.json` guarda solo los identificadores de mensaje ya procesados, para poder reanudar.
- Los correos respaldados contienen datos personales (tu nombre, RUT, cuentas bancarias). No publiques la carpeta. Comparte solo lo que decidas, y siempre sin datos de terceros.

## Cómo colaborar

Si OrionX te enviaba correos con un formato que el script no clasifica bien, abre un issue con el asunto del correo (sin datos personales) o envía un pull request ajustando los patrones en `CATEGORIAS` al inicio del script.

Este proyecto es de afectados para afectados, sin fines de lucro. Licencia MIT.
