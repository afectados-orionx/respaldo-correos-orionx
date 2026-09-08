#!/usr/bin/env python3
"""
Respaldo de correos de OrionX para afectados por su cierre (Chile, septiembre 2026).

Descarga TODOS los correos relacionados con OrionX desde tu propia casilla y los guarda
en tu computador como evidencia: archivo .eml original, texto legible, adjuntos (boletas PDF),
un índice CSV y una tabla de movimientos (montos, monedas, direcciones y hashes detectados).

Solo lee. No borra, mueve ni marca ningún correo. No envía nada a ningún servidor
que no sea el de tu propio correo. Sin dependencias: solo Python 3.8 o superior.

Tres formas de usarlo:

  1) Conectándose a tu correo por IMAP (Gmail, Outlook, etc.):
       python3 respaldo_correos_orionx.py --correo tu@gmail.com
     Te pedirá la contraseña. En Gmail debes usar una "contraseña de aplicación"
     (ver README). También puedes pasarla en la variable de entorno IMAP_PASSWORD.

  2) Desde un archivo .mbox exportado con Google Takeout (no requiere contraseña):
       python3 respaldo_correos_orionx.py --mbox "Todos los mensajes incluido Spam y Papelera.mbox"

  3) Desde una carpeta con archivos .eml ya descargados:
       python3 respaldo_correos_orionx.py --eml carpeta_con_eml/

Resultado en la carpeta ./respaldo_orionx/ (o la que indiques con --salida).
"""
import argparse
import csv
import datetime as dt
import email
import email.policy
import getpass
import hashlib
import html
import imaplib
import json
import mailbox
import os
import re
import ssl
import sys
from collections import Counter
from email.message import EmailMessage
from html.parser import HTMLParser
from pathlib import Path

VERSION = "1.0.0"

# ----------------------------------------------------------------------------
# Qué se considera "correo de OrionX"
# ----------------------------------------------------------------------------
REMITENTES_ORIONX = ("orionx.com", "orionx.io", "orionx.cl", "email.orionx.com")
PALABRA_CLAVE = re.compile(r"orion\s*x", re.IGNORECASE)

# Remitentes de bancos chilenos que avisan transferencias hacia/desde ORIONX SPA.
REMITENTES_BANCO = (
    "bancochile.cl", "scotiabank.cl", "bci.cl", "santander.cl", "bancoestado.cl",
    "itau.cl", "bice.cl", "security.cl", "falabella.cl", "ripley.cl", "consorcio.cl",
    "tenpo.cl", "mercadopago.cl", "mach.cl", "coopeuch.cl", "bancointernacional.cl",
)

# Categorías por asunto. Se evalúan en orden; la primera que coincide gana.
CATEGORIAS = [
    ("orden",              re.compile(r"se ejecut[oó] tu orden|orden de (compra|venta)|compra de|venta de", re.I)),
    ("abono",              re.compile(r"abono en tu cuenta|dep[oó]sito (acreditado|recibido)|acreditad", re.I)),
    ("retiro",             re.compile(r"retiro|env[ií]o de|has enviado|destino en tu agenda|transferencia de fondos", re.I)),
    ("boleta",             re.compile(r"boleta|factura", re.I)),
    ("comunicado_oficial", re.compile(r"informaci[oó]n importante|comunicado|mantenci[oó]n|suspensi[oó]n|cierre|aviso|cambio de cuenta|nueva cuenta", re.I)),
    ("soporte",            re.compile(r"transcripci[oó]n|chat|ticket|soporte|re:|solicitud", re.I)),
    ("cuenta",             re.compile(r"verific|registro|bienvenid|api key|cuenta bancaria|contrase[ñn]a|dispositivo|autorizaci[oó]n", re.I)),
    ("login",              re.compile(r"inicio de sesi[oó]n|nuevo inicio|login|c[oó]digo de (acceso|verificaci[oó]n)", re.I)),
    ("newsletter",         re.compile(r"newsletter|novedades|promoci[oó]n|descuento|webinar|blog|resumen semanal|mercado", re.I)),
]

# Patrones para detectar montos, monedas, direcciones y hashes en asunto y cuerpo.
RE_MONTO_CLP = re.compile(r"\$\s?([0-9]{1,3}(?:\.[0-9]{3})+|[0-9]+)(?:,[0-9]+)?|\(([0-9]{1,3}(?:\.[0-9]{3})+)\)|CLP\s*\$?\s*([0-9.,]+)", re.I)
RE_MONTO_CRIPTO = re.compile(r"\b([0-9]+(?:[.,][0-9]+)?)\s?(BTC|ETH|DAI|USDC|USDT|XRP|DOT|XLM|TRX|LTC|BCH|SOL|MATIC|POL|ADA|LINK|UNI|AAVE|CHA|LUKA)\b", re.I)
RE_MONEDAS = re.compile(r"\b(Bitcoin|Ethereum|Ether|Polkadot|Litecoin|Ripple|Stellar|Tron|Solana|Polygon|Cardano|Chainlink|Uniswap|BTC|ETH|DAI|USDC|USDT|XRP|DOT|XLM|TRX|LTC|BCH|SOL|MATIC|POL|ADA|LINK|UNI|AAVE)\b", re.I)
RE_DIR_BTC = re.compile(r"\b(bc1[ac-hj-np-z02-9]{25,62}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})\b")
RE_DIR_EVM = re.compile(r"\b(0x[0-9a-fA-F]{40})\b")
RE_HASH_EVM = re.compile(r"\b(0x[0-9a-fA-F]{64})\b")
RE_HASH_64 = re.compile(r"\b([0-9a-fA-F]{64})\b")
RE_DIR_XRP = re.compile(r"\b(r[1-9A-HJ-NP-Za-km-z]{24,34})\b")
RE_DIR_XLM = re.compile(r"\b(G[A-Z2-7]{55})\b")
RE_DIR_TRX = re.compile(r"\b(T[1-9A-HJ-NP-Za-km-z]{33})\b")
RE_DIR_SS58 = re.compile(r"\b(1[1-9A-HJ-NP-Za-km-z]{46,47})\b")  # Polkadot
RE_DIR_SOL = re.compile(r"\b([1-9A-HJ-NP-Za-km-z]{43,44})\b")


# ----------------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------------
class _HTMLaTexto(HTMLParser):
    """Convierte HTML a texto plano legible, conservando saltos de bloque."""
    BLOQUES = {"p", "div", "br", "tr", "li", "h1", "h2", "h3", "h4", "table", "section", "article", "hr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.partes = []
        self._omitir = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script", "head"):
            self._omitir += 1
        elif tag in self.BLOQUES:
            self.partes.append("\n")
        elif tag == "td":
            self.partes.append(" ")
        elif tag == "a":
            href = dict(attrs).get("href")
            if href and not href.startswith(("mailto:", "#")):
                self._href = href
        elif tag == "img":
            alt = dict(attrs).get("alt")
            if alt:
                self.partes.append(f"[{alt}]")

    def handle_endtag(self, tag):
        if tag in ("style", "script", "head") and self._omitir:
            self._omitir -= 1
        elif tag in self.BLOQUES:
            self.partes.append("\n")

    def handle_data(self, data):
        if not self._omitir:
            self.partes.append(data)

    def texto(self):
        t = "".join(self.partes)
        t = re.sub(r"[ \t\r\f\v]+", " ", t)
        t = re.sub(r" *\n *", "\n", t)
        t = re.sub(r"\n{3,}", "\n\n", t)
        return t.strip()


def html_a_texto(h):
    p = _HTMLaTexto()
    try:
        p.feed(h)
        p.close()
    except Exception:
        return re.sub(r"<[^>]+>", " ", h)
    return p.texto()


def decodificar_cabecera(valor):
    if valor is None:
        return ""
    try:
        partes = email.header.decode_header(str(valor))
        out = []
        for texto, cod in partes:
            if isinstance(texto, bytes):
                out.append(texto.decode(cod or "utf-8", errors="replace"))
            else:
                out.append(texto)
        return "".join(out).strip()
    except Exception:
        return str(valor)


def fecha_mensaje(msg):
    """Devuelve datetime UTC del mensaje, o None."""
    try:
        d = email.utils.parsedate_to_datetime(msg.get("Date"))
        if d.tzinfo is None:
            d = d.replace(tzinfo=dt.timezone.utc)
        return d.astimezone(dt.timezone.utc)
    except Exception:
        return None


def direccion_remitente(msg):
    nombre, addr = email.utils.parseaddr(decodificar_cabecera(msg.get("From")))
    return addr.lower(), nombre


def cuerpo_texto(msg):
    """Extrae el mejor texto legible del mensaje (prefiere text/plain, cae a HTML convertido)."""
    plano, htmls = [], []
    for parte in msg.walk():
        if parte.get_content_maintype() == "multipart":
            continue
        if parte.get_content_disposition() == "attachment":
            continue
        ct = parte.get_content_type()
        if ct not in ("text/plain", "text/html"):
            continue
        try:
            contenido = parte.get_content()
        except Exception:
            payload = parte.get_payload(decode=True) or b""
            charset = parte.get_content_charset() or "utf-8"
            contenido = payload.decode(charset, errors="replace")
        if ct == "text/plain":
            plano.append(contenido)
        else:
            htmls.append(contenido)
    texto = "\n".join(plano).strip()
    texto_html = "\n".join(html_a_texto(h) for h in htmls).strip()
    # OrionX suele mandar text/plain vacío o solo con enlaces: usamos el más largo.
    if len(texto_html) > len(texto) * 1.5:
        return texto_html, "\n".join(htmls)
    return texto or texto_html, "\n".join(htmls)


def adjuntos(msg):
    for parte in msg.walk():
        if parte.get_content_maintype() == "multipart":
            continue
        nombre = parte.get_filename()
        if parte.get_content_disposition() == "attachment" or (nombre and parte.get_content_type() not in ("text/plain", "text/html")):
            datos = parte.get_payload(decode=True)
            if datos:
                yield decodificar_cabecera(nombre) or f"adjunto.{parte.get_content_subtype()}", datos, parte.get_content_type()


def es_relacionado(msg, texto):
    """¿El correo tiene que ver con OrionX? Devuelve (bool, motivo)."""
    remitente, _ = direccion_remitente(msg)
    asunto = decodificar_cabecera(msg.get("Subject"))
    if remitente.endswith(REMITENTES_ORIONX) or "orionx" in remitente:
        return True, "remitente_orionx"
    if PALABRA_CLAVE.search(asunto):
        return True, "asunto"
    if remitente.endswith(REMITENTES_BANCO) and PALABRA_CLAVE.search(texto):
        return True, "aviso_bancario"
    if PALABRA_CLAVE.search(texto[:20000]):
        return True, "cuerpo"
    return False, ""


def categorizar(asunto, remitente):
    if remitente.endswith(REMITENTES_BANCO):
        return "transferencia_banco"
    for nombre, patron in CATEGORIAS:
        if patron.search(asunto):
            return nombre
    return "otro"


def limpiar_nombre(s, largo=60):
    s = re.sub(r"[^\w\s.-]", "", s, flags=re.UNICODE).strip()
    s = re.sub(r"\s+", "_", s)
    return s[:largo] or "sin_asunto"


def extraer_movimiento(asunto, texto):
    """Detecta montos, monedas, direcciones y hashes. Devuelve dict con strings separados por ' | '."""
    fuente = asunto + "\n" + texto
    monedas = sorted({m.upper() for m in RE_MONEDAS.findall(fuente)})
    montos_cripto = sorted({f"{a} {b.upper()}" for a, b in RE_MONTO_CRIPTO.findall(fuente)})
    montos_clp = []
    for m in RE_MONTO_CLP.finditer(fuente):
        v = next(g for g in m.groups() if g)
        if len(v.replace(".", "")) >= 4:  # ignora $1, $10, etc.
            montos_clp.append(v)
    montos_clp = sorted(set(montos_clp))

    # Direcciones y hashes. Se descartan candidatos que sean parte de URLs largas o ids de tracking.
    sin_urls = re.sub(r"https?://\S+", " ", fuente)
    hashes = set(RE_HASH_EVM.findall(sin_urls)) | set(RE_HASH_64.findall(sin_urls))
    dirs = {
        "btc": set(RE_DIR_BTC.findall(sin_urls)),
        "evm": set(RE_DIR_EVM.findall(sin_urls)),
        "xrp": set(RE_DIR_XRP.findall(sin_urls)),
        "xlm": set(RE_DIR_XLM.findall(sin_urls)),
        "trx": set(RE_DIR_TRX.findall(sin_urls)),
        "dot": set(RE_DIR_SS58.findall(sin_urls)),
    }
    # Solana solo si el correo menciona SOL/Solana (el patrón es muy genérico).
    if re.search(r"\b(SOL|Solana)\b", fuente, re.I):
        dirs["sol"] = set(RE_DIR_SOL.findall(sin_urls)) - dirs["dot"] - dirs["btc"]
    # Evita que direcciones BTC legacy se confundan con DOT y viceversa: DOT tiene 47-48 chars.
    dirs["btc"] = {d for d in dirs["btc"] if len(d) <= 42}
    direcciones = " | ".join(f"{red}:{d}" for red, ds in dirs.items() for d in sorted(ds))
    return {
        "monedas": " | ".join(monedas),
        "montos_cripto": " | ".join(montos_cripto),
        "montos_clp": " | ".join(montos_clp),
        "direcciones": direcciones,
        "hashes": " | ".join(sorted(hashes)),
    }


# ----------------------------------------------------------------------------
# Escritura del respaldo
# ----------------------------------------------------------------------------
class Respaldo:
    def __init__(self, salida: Path, cuenta: str, guardar_html=False):
        self.salida = salida
        self.cuenta = cuenta
        self.guardar_html = guardar_html
        (salida / "eml").mkdir(parents=True, exist_ok=True)
        (salida / "texto").mkdir(exist_ok=True)
        (salida / "adjuntos").mkdir(exist_ok=True)
        self.indice = []
        self.movimientos = []
        self.vistos = set()
        self.conteo = Counter()
        self.descartados = 0
        self.archivo_estado = salida / "estado.json"
        if self.archivo_estado.exists():
            try:
                self.vistos = set(json.loads(self.archivo_estado.read_text())["message_ids"])
            except Exception:
                pass
        self.vistos_iniciales = len(self.vistos)
        # Carga índice previo para no perderlo al reanudar.
        idx = salida / "indice.csv"
        if idx.exists():
            with idx.open(newline="", encoding="utf-8") as f:
                self.indice = list(csv.DictReader(f))
        mov = salida / "movimientos.csv"
        if mov.exists():
            with mov.open(newline="", encoding="utf-8") as f:
                self.movimientos = list(csv.DictReader(f))

    def procesar(self, raw: bytes, uid_origen=""):
        try:
            msg = email.message_from_bytes(raw, policy=email.policy.default)
        except Exception as e:
            print(f"  ! no se pudo parsear un mensaje ({e})", file=sys.stderr)
            return False
        mid = decodificar_cabecera(msg.get("Message-ID")) or hashlib.sha1(raw).hexdigest()
        if mid in self.vistos:
            return False
        texto, cuerpo_html = cuerpo_texto(msg)
        ok, motivo = es_relacionado(msg, texto)
        if not ok:
            self.descartados += 1
            return False

        remitente, nombre_rem = direccion_remitente(msg)
        asunto = decodificar_cabecera(msg.get("Subject"))
        fecha = fecha_mensaje(msg)
        fecha_iso = fecha.strftime("%Y-%m-%dT%H:%M:%SZ") if fecha else ""
        fecha_corta = fecha.strftime("%Y-%m-%d") if fecha else "sin-fecha"
        categoria = categorizar(asunto, remitente)
        corto = hashlib.sha1(mid.encode()).hexdigest()[:10]
        base = f"{fecha_corta}_{categoria}_{limpiar_nombre(asunto, 50)}_{corto}"

        (self.salida / "eml" / f"{base}.eml").write_bytes(raw)

        nombres_adj = []
        for nombre, datos, ct in adjuntos(msg):
            if nombre.lower().endswith(".p7s") or ct == "application/pkcs7-signature":
                continue  # firmas digitales de bancos, sin valor probatorio propio
            destino = self.salida / "adjuntos" / f"{fecha_corta}_{corto}_{limpiar_nombre(nombre, 80)}"
            destino.write_bytes(datos)
            nombres_adj.append(destino.name)

        encabezado = (
            f"Asunto: {asunto}\nDe: {nombre_rem} <{remitente}>\nPara: {decodificar_cabecera(msg.get('To'))}\n"
            f"Fecha: {fecha_iso}\nMessage-ID: {mid}\nCategoría: {categoria}\nMotivo de inclusión: {motivo}\n"
            f"Adjuntos: {', '.join(nombres_adj) or 'ninguno'}\n"
            f"Archivo original: eml/{base}.eml\n" + "-" * 78 + "\n\n"
        )
        (self.salida / "texto" / f"{base}.txt").write_text(encabezado + texto, encoding="utf-8")
        if self.guardar_html and cuerpo_html:
            (self.salida / "html").mkdir(exist_ok=True)
            (self.salida / "html" / f"{base}.html").write_text(cuerpo_html, encoding="utf-8")

        fila = {
            "fecha_utc": fecha_iso, "categoria": categoria, "remitente": remitente, "asunto": asunto,
            "adjuntos": " | ".join(nombres_adj), "archivo": f"texto/{base}.txt", "message_id": mid, "motivo": motivo,
        }
        self.indice.append(fila)
        if categoria in ("orden", "abono", "retiro", "transferencia_banco", "boleta", "cuenta"):
            mov = extraer_movimiento(asunto, texto)
            if any(mov.values()):
                self.movimientos.append({"fecha_utc": fecha_iso, "categoria": categoria, "asunto": asunto, **mov, "archivo": fila["archivo"]})
        self.vistos.add(mid)
        self.conteo[categoria] += 1
        return True

    def guardar(self):
        self.indice.sort(key=lambda r: r["fecha_utc"])
        self.movimientos.sort(key=lambda r: r["fecha_utc"])
        with (self.salida / "indice.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["fecha_utc", "categoria", "remitente", "asunto", "adjuntos", "archivo", "message_id", "motivo"])
            w.writeheader()
            w.writerows(self.indice)
        with (self.salida / "movimientos.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["fecha_utc", "categoria", "asunto", "monedas", "montos_cripto", "montos_clp", "direcciones", "hashes", "archivo"])
            w.writeheader()
            w.writerows(self.movimientos)
        self.archivo_estado.write_text(json.dumps({"cuenta": self.cuenta, "message_ids": sorted(self.vistos),
                                                   "actualizado": dt.datetime.now(dt.timezone.utc).isoformat()}, indent=1))
        self._resumen()

    def _resumen(self):
        por_cat = Counter(r["categoria"] for r in self.indice)
        por_anio = Counter((r["fecha_utc"] or "????")[:4] for r in self.indice)
        fechas = [r["fecha_utc"] for r in self.indice if r["fecha_utc"]]
        lineas = [
            f"# Resumen del respaldo de correos OrionX",
            "",
            f"- Cuenta: {self.cuenta}",
            f"- Generado: {dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} con respaldo_correos_orionx.py v{VERSION}",
            f"- Correos relacionados con OrionX guardados: {len(self.indice)}",
            f"- Rango de fechas: {min(fechas)[:10] if fechas else '-'} a {max(fechas)[:10] if fechas else '-'}",
            f"- Adjuntos guardados: {sum(1 for r in self.indice if r['adjuntos'])} correos con adjuntos (carpeta adjuntos/)",
            f"- Filas en movimientos.csv: {len(self.movimientos)}",
            "",
            "## Por categoría", "", "| Categoría | Correos |", "|---|---|",
            *[f"| {c} | {n} |" for c, n in sorted(por_cat.items(), key=lambda x: -x[1])],
            "",
            "## Por año", "", "| Año | Correos |", "|---|---|",
            *[f"| {a} | {n} |" for a, n in sorted(por_anio.items())],
            "",
            "## Direcciones y hashes detectados (puntos de partida para rastreo en cadena)", "",
        ]
        dirs, hashes = Counter(), set()
        for m in self.movimientos:
            for d in filter(None, m["direcciones"].split(" | ")):
                dirs[d] += 1
            hashes.update(filter(None, m["hashes"].split(" | ")))
        if dirs:
            lineas += ["| Red:dirección | Veces |", "|---|---|"] + [f"| `{d}` | {n} |" for d, n in dirs.most_common()]
        else:
            lineas.append("Ninguna dirección detectada.")
        lineas += ["", f"Hashes de transacción detectados: {len(hashes)}"] + [f"- `{h}`" for h in sorted(hashes)]
        lineas += ["", "## Archivos", "",
                   "- `indice.csv`: un correo por fila (fecha, categoría, remitente, asunto, adjuntos, archivo).",
                   "- `movimientos.csv`: solo correos de órdenes, abonos, retiros, avisos bancarios y boletas, con montos y monedas detectados.",
                   "- `texto/`: cada correo en texto plano legible.",
                   "- `eml/`: cada correo original completo (formato estándar .eml, sirve como evidencia y se abre con cualquier cliente de correo).",
                   "- `adjuntos/`: boletas PDF y otros archivos adjuntos.",
                   "", "Los montos y direcciones detectados se extraen con expresiones regulares y pueden contener falsos positivos: verifica siempre contra el correo original."]
        (self.salida / "RESUMEN.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")


# ----------------------------------------------------------------------------
# Fuentes: IMAP, mbox, carpeta .eml
# ----------------------------------------------------------------------------
def detectar_servidor(correo):
    dominio = correo.rsplit("@", 1)[-1].lower()
    if dominio in ("gmail.com", "googlemail.com"):
        return "imap.gmail.com"
    if dominio in ("outlook.com", "hotmail.com", "live.com", "msn.com", "outlook.cl", "hotmail.cl"):
        return "outlook.office365.com"
    if dominio in ("yahoo.com", "yahoo.cl", "yahoo.es"):
        return "imap.mail.yahoo.com"
    if dominio in ("icloud.com", "me.com", "mac.com"):
        return "imap.mail.me.com"
    return "imap." + dominio


MESES_IMAP = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def fecha_imap(d):
    """Formato de fecha que exige IMAP (siempre en inglés, sin depender del idioma del sistema)."""
    return f"{d.day:02d}-{MESES_IMAP[d.month - 1]}-{d.year}"


def _uids(respuesta):
    return [u for u in (respuesta[0] or b"").split() if u]


def buscar_uids(imap, es_gmail, desde, hasta):
    """Devuelve UIDs candidatos. En Gmail usa su buscador (X-GM-RAW), que ya mira cuerpo y adjuntos."""
    uids = set()
    rango = []
    if desde:
        rango.append(f"SINCE {fecha_imap(desde)}")
    if hasta:
        rango.append(f"BEFORE {fecha_imap(hasta)}")
    rango = " ".join(rango)
    if es_gmail:
        consultas = ['orionx', '"orionx spa"', 'from:orionx', 'orion x']
        for q in consultas:
            typ, data = imap.uid("SEARCH", None, *(rango.split() + ["X-GM-RAW", f'"{q}"']))
            if typ == "OK":
                uids.update(_uids(data))
    else:
        for criterio in ('FROM "orionx"', 'SUBJECT "orionx"', 'BODY "orionx"', 'BODY "Orionx SPA"'):
            typ, data = imap.uid("SEARCH", None, *(rango.split() + criterio.split(" ", 1)))
            if typ == "OK":
                uids.update(_uids(data))
    return sorted(uids, key=int)


def seleccionar_buzon(imap, es_gmail, buzon):
    if buzon:
        typ, _ = imap.select(f'"{buzon}"', readonly=True)
        if typ == "OK":
            return buzon
        sys.exit(f"No existe el buzón {buzon!r}.")
    if es_gmail:
        typ, data = imap.list()
        for linea in data or []:
            texto = linea.decode(errors="replace") if isinstance(linea, bytes) else str(linea)
            if "\\All" in texto:
                nombre = texto.rsplit(' "/" ', 1)[-1].strip().strip('"')
                if imap.select(f'"{nombre}"', readonly=True)[0] == "OK":
                    return nombre
        for candidato in ("[Gmail]/Todos", "[Gmail]/All Mail", "[Gmail]/Todo el correo"):
            if imap.select(f'"{candidato}"', readonly=True)[0] == "OK":
                return candidato
    imap.select("INBOX", readonly=True)
    return "INBOX"


def desde_imap(args, respaldo):
    servidor = args.servidor or detectar_servidor(args.correo)
    clave = os.environ.get("IMAP_PASSWORD")
    if not clave:
        if not sys.stdin.isatty():
            sys.exit(
                "Este programa necesita pedirte la contraseña por teclado y aquí no hay una terminal interactiva.\n"
                "Ábrelo en una terminal normal (cmd, PowerShell, Terminal) y vuelve a ejecutar el comando,\n"
                "o define la variable de entorno IMAP_PASSWORD con tu contraseña de aplicación."
            )
        try:
            clave = getpass.getpass(f"Contraseña (de aplicación) para {args.correo}: ")
        except (EOFError, KeyboardInterrupt):
            sys.exit("\nNo se ingresó contraseña. Nada se descargó.")
    clave = clave.replace(" ", "")  # Google muestra la clave de aplicación con espacios; se aceptan con o sin ellos
    print(f"Conectando a {servidor} como {args.correo} (solo lectura)...")
    ctx = ssl.create_default_context()
    imap = imaplib.IMAP4_SSL(servidor, 993, ssl_context=ctx)
    try:
        imap.login(args.correo, clave)
    except imaplib.IMAP4.error as e:
        sys.exit(
            f"No se pudo iniciar sesión: {e}\n"
            "Si es Gmail: activa la verificación en dos pasos y crea una 'contraseña de aplicación' en\n"
            "https://myaccount.google.com/apppasswords (la contraseña normal no funciona). Ver README."
        )
    es_gmail = b"X-GM-EXT-1" in (imap.capabilities and b" ".join(imap.capabilities) or b"") or "gmail" in servidor
    buzon = seleccionar_buzon(imap, es_gmail, args.buzon)
    print(f"Buzón: {buzon}. Buscando correos relacionados con OrionX...")
    uids = buscar_uids(imap, es_gmail, args.desde, args.hasta)
    print(f"Candidatos encontrados: {len(uids)}. Descargando en lotes de {args.lote}...")
    nuevos = 0
    for i in range(0, len(uids), args.lote):
        lote = uids[i:i + args.lote]
        conjunto = b",".join(lote).decode()
        typ, data = imap.uid("FETCH", conjunto, "(BODY.PEEK[])")
        if typ != "OK":
            print(f"  ! error al descargar lote {i // args.lote + 1}", file=sys.stderr)
            continue
        for item in data:
            if isinstance(item, tuple) and len(item) >= 2 and isinstance(item[1], (bytes, bytearray)):
                if respaldo.procesar(bytes(item[1])):
                    nuevos += 1
        print(f"  {min(i + args.lote, len(uids))}/{len(uids)} revisados, {nuevos} guardados", end="\r", flush=True)
        if (i // args.lote) % 10 == 9:
            respaldo.guardar()  # guarda progreso periódicamente
    print()
    try:
        imap.close()
        imap.logout()
    except Exception:
        pass
    return nuevos


def desde_mbox(args, respaldo):
    ruta = Path(args.mbox)
    if not ruta.exists():
        sys.exit(f"No existe el archivo {ruta}")
    print(f"Leyendo {ruta} (puede tardar varios minutos si es grande)...")
    caja = mailbox.mbox(str(ruta), create=False)
    nuevos = total = 0
    for llave in caja.iterkeys():
        total += 1
        try:
            raw = caja.get_bytes(llave)
        except Exception:
            continue
        if respaldo.procesar(raw):
            nuevos += 1
        if total % 500 == 0:
            print(f"  {total} mensajes revisados, {nuevos} guardados", end="\r", flush=True)
    print(f"  {total} mensajes revisados, {nuevos} guardados")
    return nuevos


def desde_eml(args, respaldo):
    carpeta = Path(args.eml)
    archivos = sorted(carpeta.rglob("*.eml"))
    if not archivos:
        sys.exit(f"No hay archivos .eml en {carpeta}")
    nuevos = 0
    for a in archivos:
        if respaldo.procesar(a.read_bytes()):
            nuevos += 1
    print(f"  {len(archivos)} archivos revisados, {nuevos} guardados")
    return nuevos


def parse_fecha(s):
    try:
        return dt.datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError("usa el formato AAAA-MM-DD")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    fuente = ap.add_mutually_exclusive_group(required=True)
    fuente.add_argument("--correo", help="tu dirección de correo (modo IMAP)")
    fuente.add_argument("--mbox", help="archivo .mbox exportado con Google Takeout u otro cliente")
    fuente.add_argument("--eml", help="carpeta con archivos .eml")
    ap.add_argument("--servidor", help="servidor IMAP (se detecta solo para Gmail, Outlook, Yahoo, iCloud)")
    ap.add_argument("--buzon", help="buzón IMAP a revisar (por defecto: todo el correo en Gmail, INBOX en otros)")
    ap.add_argument("--salida", default="respaldo_orionx", help="carpeta de salida (por defecto ./respaldo_orionx)")
    ap.add_argument("--desde", type=parse_fecha, help="solo correos desde esta fecha (AAAA-MM-DD)")
    ap.add_argument("--hasta", type=parse_fecha, help="solo correos antes de esta fecha (AAAA-MM-DD)")
    ap.add_argument("--lote", type=int, default=50, help="correos por lote al descargar (por defecto 50)")
    ap.add_argument("--html", action="store_true", help="guardar también el HTML original de cada correo")
    ap.add_argument("--version", action="version", version=VERSION)
    args = ap.parse_args()

    cuenta = args.correo or (Path(args.mbox).name if args.mbox else Path(args.eml).name)
    salida = Path(args.salida)
    respaldo = Respaldo(salida, cuenta, guardar_html=args.html)
    if respaldo.vistos_iniciales:
        print(f"Reanudando: ya había {respaldo.vistos_iniciales} correos respaldados en {salida}/")

    if args.correo:
        nuevos = desde_imap(args, respaldo)
    elif args.mbox:
        nuevos = desde_mbox(args, respaldo)
    else:
        nuevos = desde_eml(args, respaldo)

    respaldo.guardar()
    print(f"\nListo. {nuevos} correos nuevos guardados ({len(respaldo.indice)} en total) en {salida.resolve()}/")
    print(f"Descartados por no estar relacionados con OrionX: {respaldo.descartados}")
    print("Revisa RESUMEN.md, indice.csv y movimientos.csv. Guarda la carpeta completa en un lugar seguro (y una copia fuera del computador).")


if __name__ == "__main__":
    main()
