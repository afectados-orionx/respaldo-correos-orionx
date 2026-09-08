# Respaldar tus correos de OrionX con ayuda de un asistente (guía para quien no usa mucho el computador)

Vas a instalar un asistente gratuito llamado OpenCode. Es un programa normal, con ventana, que se instala haciendo doble clic. Dentro le vas a pegar un mensaje ya escrito. El asistente revisa el programa de respaldo, te dice con sus palabras si es seguro y te guía paso a paso. Tú solo lees y escribes lo que te pida.

Tiempo: unos 20 minutos de trabajo tuyo, más la espera de Google (puede ser de una hora a un día).

Regla de oro: **nunca escribas la contraseña de tu correo dentro del asistente.** Con el camino recomendado de esta guía ni siquiera vas a necesitar una contraseña.

---

## Paso 1. Pedirle a Google una copia de tu correo (se hace primero porque tarda)

Esto se llama Google Takeout. Es la propia Google entregándote tus correos en un archivo. No hay que crear contraseñas ni dar permisos a nadie.

1. Entra a https://takeout.google.com con tu cuenta de Gmail.
2. Pulsa **"Desmarcar todo"**.
3. Baja por la lista hasta **"Correo"** y márcalo. Solo ese.
4. Pulsa **"Siguiente paso"**. Deja todo como está (enviar enlace por correo, exportar una vez, archivo .zip, 2 GB) y pulsa **"Crear exportación"**.
5. Google te enviará un correo con el enlace de descarga. Puede tardar desde una hora hasta un día. Mientras esperas, sigue con los pasos 2 y 3.
6. Cuando llegue, descarga el archivo .zip y descomprímelo (clic derecho, "Extraer todo" en Windows; doble clic en Mac). Dentro, en una carpeta llamada Takeout, hay un archivo que termina en **.mbox**. Ese archivo es tu correo completo. Anota dónde quedó.

Si tu correo no es Gmail, salta a la sección "Si no usas Gmail" al final.

## Paso 2. Instalar Python

Es el lenguaje en que está escrito el programa de respaldo. Se instala una vez.

**Windows**
1. Entra a https://www.python.org/downloads/ y pulsa el botón amarillo "Download Python".
2. Abre el archivo descargado. En la primera pantalla **marca la casilla "Add Python to PATH"**, que está abajo. Es lo único importante. Luego "Install Now".

**Mac**
Suele venir instalado. Si en el paso 4 el asistente te dice que falta, él te indica cómo instalarlo.

## Paso 3. Instalar OpenCode (versión de escritorio)

1. Entra a https://opencode.ai/download y busca la sección **"OpenCode Desktop"**.
2. Descarga la versión para tu computador:
   - Windows: el archivo que termina en `.exe`.
   - Mac: el archivo `.dmg`. Si tu Mac es de 2020 o posterior elige "Apple Silicon"; si es más antiguo, "Intel". Si no sabes, pulsa el logo de la manzana, "Acerca de este Mac": si dice "Chip Apple M1/M2/M3/M4" es Apple Silicon.
3. Instálalo como cualquier programa: doble clic y siguiente. En Mac, arrastra el ícono a la carpeta Aplicaciones. Si Windows muestra un aviso de "editor desconocido", pulsa "Más información" y "Ejecutar de todas formas".
4. Abre OpenCode. Te pedirá elegir una **carpeta de trabajo**: crea una carpeta nueva en tu Escritorio llamada `respaldo-orionx` y elígela.
5. Listo. La aplicación ya viene con un modelo gratuito llamado **Big Pickle**, que funciona sin crear cuenta, sin iniciar sesión y sin tarjeta. No hay que configurar nada más. Si en alguna pantalla ves opciones de "conectar proveedor", "API key" o pago, ignóralas: no hacen falta.

La aplicación de escritorio es reciente y está marcada como "beta". Si algo no funciona, cierra y vuelve a abrir; y si sigue fallando, avisa en el grupo.

## Paso 4. Pegar el mensaje para el asistente

Copia todo el bloque siguiente, pégalo en la casilla de OpenCode y envíalo:

```
Soy un cliente afectado por el cierre del exchange chileno OrionX y quiero respaldar mis correos como evidencia. No sé programar. Por favor haz lo siguiente, en español y explicándome cada paso con palabras simples, y espera mi confirmación antes de pasar de un paso al siguiente:

1. Descarga el repositorio público https://github.com/afectados-orionx/respaldo-correos-orionx en esta carpeta.
2. Lee COMPLETO el archivo respaldo_correos_orionx.py y el README.md. Después dime en pocas líneas: a qué servidores se conecta el programa, si borra o modifica algo en mi correo, si envía mis datos a algún lugar que no sea mi propio computador o mi propio servidor de correo, si guarda contraseñas en algún archivo, y si ves algo peligroso o sospechoso. Responde primero "ES SEGURO" o "NO ES SEGURO" y luego explica por qué. Si no es seguro, detente ahí.
3. Si es seguro, comprueba que Python 3.8 o superior está instalado. Si falta, dime exactamente cómo instalarlo en mi sistema.
4. Tengo un archivo .mbox que descargué con Google Takeout. Pregúntame dónde está y ayúdame a encontrar la ruta exacta si no la sé.
5. Ejecuta el programa con la opción --mbox apuntando a ese archivo y con --salida respaldo_orionx dentro de esta carpeta. Avísame si tarda y cuándo termina. Si aparece un error, explícamelo con palabras simples y propón cómo seguir.
6. Cuando termine, abre RESUMEN.md y movimientos.csv de la carpeta respaldo_orionx y dime cuántos correos se respaldaron, de qué años, y qué saldos o movimientos aparecen. No modifiques ni borres ningún archivo del respaldo.
7. Al final recuérdame copiar la carpeta respaldo_orionx a un pendrive o a mi nube, y borrar de la carpeta de descargas el .zip de Takeout si quiero liberar espacio.

Nunca me pidas contraseñas de mi correo ni las escribas en ningún archivo.
```

## Paso 5. Seguir al asistente

- Lee la respuesta sobre seguridad. Si dice "ES SEGURO" con explicación, escribe "continúa". Si dice "NO ES SEGURO", detente y avisa en el grupo con una captura de pantalla.
- Cuando te pregunte por el archivo .mbox, dile dónde lo guardaste (por ejemplo "está en Descargas, dentro de la carpeta Takeout"). Él lo encuentra.
- El respaldo puede tardar varios minutos si tienes miles de correos. Espera a que el asistente te diga que terminó.
- Léele el resultado. Si algo no cuadra con lo que recuerdas de tus saldos, apúntalo: los correos son la prueba, no la memoria.

## Paso 6. Después

1. Copia la carpeta `respaldo_orionx` (está dentro de `respaldo-orionx` en tu Escritorio) a un pendrive y a tu nube. Que no exista solo en el computador.
2. Esa carpeta contiene tus datos personales. No la compartas entera con nadie. Los dos archivos que sirven para la denuncia son `RESUMEN.md` y `movimientos.csv`.
3. La guía para denunciar en Fiscalía, SERNAC y CMF está en la carpeta `denuncias/` que se descargó junto al programa. Puedes pedirle al asistente que te la lea y te la explique.

## Si no usas Gmail

Outlook, Hotmail, Yahoo e iCloud no tienen Takeout, así que el programa debe entrar a tu correo con una **contraseña de aplicación** (una clave de 16 letras que se crea en la configuración de tu cuenta y se borra al terminar). En ese caso, cambia el punto 4 del mensaje por: "Uso el correo [tu proveedor]. Explícame cómo crear una contraseña de aplicación y dame el comando exacto que debo escribir yo mismo en una terminal, porque el programa pide la contraseña de forma interactiva. No lo ejecutes tú." El asistente te dirá cómo abrir la terminal y qué escribir. La contraseña se escribe ahí, no se ve mientras la escribes, y nunca dentro del asistente.

## Si algo falla

Pégale el error al mismo asistente y pídele que te explique qué pasó y cómo seguir. Si no lo resuelve, toma una captura de pantalla sin mostrar tu correo y pégala en el canal del grupo de afectados.
