# Guía de denuncias individuales: Fiscalía, CMF y SERNAC

Cada afectado puede presentar sus propias denuncias en menos de una hora, sin abogado y sin costo. Mientras más denuncias individuales existan sobre los mismos hechos, más peso tiene la causa y más fácil es que la Fiscalía las agrupe. Esta guía reúne lo que ya hicimos algunos afectados, con los datos exactos que piden los formularios y textos listos para adaptar.

Aviso: escrito por afectados con ayuda de herramientas de inteligencia artificial. No es asesoría legal. Verifica cada dato en las fuentes citadas y consulta a un abogado para decisiones importantes. Si encuentras un error, abre un issue o envía un pull request.

## Antes de denunciar: junta tu evidencia

1. Respalda tus correos de OrionX con el script de este repositorio (ver [README principal](../README.md)) o con Google Takeout.
2. Busca la última captura de pantalla de tu saldo. Desde el 3 de septiembre de 2026 la plataforma no permite ingresar, así que cualquier captura anterior sirve; el saldo posterior se reconstruye con los correos de órdenes ("Se ejecutó tu orden de compra de...").
3. Descarga las cartolas bancarias con tus transferencias a "Orionx SpA".
4. Ten a mano el comunicado de cierre del 3 de septiembre (te llegó por correo; el texto íntegro está en [comunicado_cierre_2026-09-03.md](comunicado_cierre_2026-09-03.md)).

## 1. Denuncia en la Fiscalía (la más importante)

Dónde: https://www.fiscaliadechile.cl, opción "Denuncia en línea", con ClaveÚnica. Gratis, sin abogado. Te convierte en víctima en la causa penal, con derecho a ser informado y a participar de cualquier restitución que ordene un tribunal.

Datos del hecho que pide el formulario:

| Campo | Valor |
|---|---|
| ¿La víctima es menor de 18? | No |
| ¿Es usted la víctima? | Sí |
| ¿Denuncia institucional? | No (denuncias como persona) |
| Región del delito | Metropolitana de Santiago |
| Comuna del delito | Las Condes |
| Dirección del delito | Gertrudis Echeñique 30, oficina 32 (domicilio legal de Orionx SpA, Diario Oficial 27-03-2025) |
| Fecha del hecho | 03/09/2026 |
| Hora del hecho | 14:06 (hora en que llegó el correo de cierre) |
| Involucrados | Sección opcional y solo admite personas naturales (no hay campo para el RUT de la empresa): los datos de Orionx SpA, RUT 76.801.011-0, van en el relato. Si quieres agregar a alguien, pon a los exejecutivos querellados por la propia empresa, Joaquín Díaz y Roberto Zibert, con parentesco "sin parentesco", vinculación "otra/desconocida" y en otros antecedentes: "ex ejecutivo de Orionx SpA, querellado por la empresa el 2-09-2026; no tengo relación con él" |

Adjuntos: hasta 5 archivos en PDF, imagen, DOC o video. Sugeridos: el comunicado de cierre en PDF, tu captura de saldo, un resumen de tus correos (el archivo `RESUMEN.md` que genera el script, convertido a PDF), tus comprobantes bancarios.

Plantilla de relato (en [plantilla_relato_fiscalia.md](plantilla_relato_fiscalia.md)). Adapta los datos entre corchetes y borra lo que no aplique.

Al terminar recibirás un comprobante con un número de folio. **Guárdalo y comparte solo el folio en el grupo**, nunca el comprobante completo: la primera página trae tu RUT, teléfono, correo y dirección.

## 2. Denuncia en la CMF

La CMF informó el 4 de septiembre de 2026 que Orionx SpA no está inscrita ni autorizada, que rechazó su solicitud el 19 de junio de 2026 y que no puede ordenar devoluciones. Por eso **no corresponde un "reclamo"** (solo aplica a entidades fiscalizadas) sino una **"denuncia"**: informar un hecho que puede ser infracción a la Ley 21.521 (Ley Fintec), que exige inscripción y autorización para custodiar e intermediar criptoactivos.

Dónde: https://www.cmfchile.cl/portal/principal/623/w4-propertyvalue-48916.html ("Presentación de denuncias"), con ClaveÚnica.

Texto listo en [plantilla_denuncia_cmf.md](plantilla_denuncia_cmf.md). Pide tres cosas: que se investigue la operación sin autorización y la captación de fondos posterior al rechazo, que se fiscalice el plan de restitución exigiendo plazos y criterios públicos, y que se emita una alerta actualizada. Cita el folio de tu denuncia en Fiscalía.

## 3. Reclamo en el SERNAC

Dónde: https://www.sernac.cl, "Reclamo", con ClaveÚnica. Proveedor: Orionx SpA, RUT 76.801.011-0. Rubro: servicios financieros o inversiones. El SERNAC traslada el reclamo a la empresa, que tiene plazo para responder, y con muchos reclamos sobre el mismo hecho puede iniciar acciones colectivas o una mediación colectiva.

Qué escribir: lo mismo que en la Fiscalía pero en versión corta (ver [plantilla_reclamo_sernac.md](plantilla_reclamo_sernac.md)). Pide la restitución íntegra de tus activos o su equivalente en pesos al valor del 3 de septiembre de 2026, e información pública del plan de restitución.

## 4. Registrar tu caso con OrionX

OrionX anunció en orionx.com/status un plan de restitución en cinco fases y un chat de atención desde el 8 de septiembre de 2026 a las 18:00. Registra tu caso ahí, describe tu saldo y guarda el número de solicitud y las capturas de la conversación. Es requisito para entrar en cualquier reparto.

## 5. Vigilar el Boletín Concursal

Si Orionx SpA entra en liquidación (Ley 20.720), la resolución se publica en https://www.boletinconcursal.cl. Desde esa publicación corren **30 días** para que cada acreedor verifique su crédito ante el liquidador, con la evidencia del punto anterior. Quien no verifica en plazo queda fuera del reparto. Busca "ORIONX" o el RUT 76.801.011-0 cada semana.

## 6. Actuar como colmena

- Comparte en el grupo tu folio de Fiscalía y tu monto aproximado (sin datos personales). Con eso se pide que las denuncias se agrupen en una sola causa y se dimensiona el daño.
- Si retiraste alguna vez desde OrionX Ethereum, DAI, USDC, Polkadot, XRP, Stellar, Tron o Litecoin, comparte el hash de esa transacción: permite identificar las billeteras de OrionX en esa red y vigilarlas, como ya se hizo con Bitcoin.
- Desconfía de cualquier "abogado" o "recuperador" que te escriba por privado. OrionX no pide claves ni códigos por teléfono, WhatsApp o redes sociales.

## Fuentes

- Comunicado de cierre de Orionx SpA, 3 de septiembre de 2026 (correo a clientes) y https://orionx.com/status
- CMF, 4 de septiembre de 2026: https://www.cmfchile.cl/portal/prensa/625/w4-article-113273.html
- La Tercera, 4 de septiembre de 2026: https://www.latercera.com/pulso/noticia/las-operaciones-que-llevaron-al-abrupto-cierre-de-la-plataforma-de-criptomonedas-orionx/
- Domicilio de Orionx SpA: Diario Oficial, 27 de marzo de 2025 (https://dequienes.cl/diario-oficial/2025/03/27/orionx-spa-76801011-0-2626331)
