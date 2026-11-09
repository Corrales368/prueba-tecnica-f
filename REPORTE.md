# Reporte · Prueba técnica Python Developer de Integraciones

## Punto 1 · Problemas de datos

Los encontré perfilando las respuestas de la API (valores distintos por campo, largos, formatos),
cuadrando conteos contra `X-Total-Count` y leyendo el código del mock. En un ERP real no tendría ese
código: lo que sí sirve igual es perfilar y cuadrar.

| Problema | Cómo lo detecté | Qué decidí |
|---|---|---|
| `status` llega como "1", "0", "Activo", "Inactivo" o vacío | Valores distintos del campo | Mapeo explícito; vacío o desconocido se rechaza (9). Inventar un booleano es peor que no cargarlo |
| `acquisition_cost` como texto latino ("1.234,56"), número o vacío | Perfilado | En el texto, "." son miles y "," el decimal; `Decimal` a 2 decimales, redondeo half-up. Vacío se rechaza (9) |
| `installed_at` mezcla ISO con -05:00 y "13/04/2026" sin hora ni zona (18) | Perfilado; 13 y 16 no pueden ser meses, así que es día/mes | Asumo -05:00, la zona de todas las demás fechas del ERP; paso a UTC y dejo un aviso |
| Nombres de 83 caracteres; el contrato admite 50 | Largo en el perfilado | Trunco y lo registro en el log y en `warnings` (2; los otros 2 ya venían rechazados) |
| `LOC-Z` no existe en el catálogo | Cruce con `/locations` | Rechazo sin pedir lecturas (2), como dice el contrato |
| La página 4 repite 3 activos con un `updated_at` más nuevo | 57 leídos contra 54 códigos únicos | Me quedo con el más reciente y registro cada duplicado |
| Códigos con "/" (EQ-012/A…) | Sus lecturas daban 404 | Codifico el código en la URL; si no, eran rechazos falsos |
| La página 3 responde 200 con un error en el cuerpo y `data` vacía | Con "data vacía = fin" se perdían 17 activos sin ninguna excepción | Lo trato como error reintentable, pagino hasta una página vacía sin error y cuadro contra `X-Total-Count` |

Todo rechazo queda en `rejected_assets` con su motivo y el lote sigue. Si un activo ya cargado llega
inválido, conservo su última versión válida; si vuelve a ser válido, sale de rechazados.

**Lo que sospecho que quedó sin encontrar:**

- Un costo en texto con formato estadounidense ("1234.56") se leería como 123456, cien veces más, sin
  ningún error. Asumo formato latino en todo el texto porque así llegó todo. Es la que más me preocupa.
- La zona -05:00 es una suposición: si esas fechas son de otra zona, quedan corridas unas horas.
- Las lecturas no se validan: un medidor que baja, un valor negativo o una fecha futura se cargan igual.
- Si el ERP borra un activo, aquí sigue: la carga inserta y actualiza, pero nunca elimina.
- Un mismo código con espacios o con otras mayúsculas se guardaría como otro activo.

## Punto 2 · Revisión de `transform_registry.py`

El módulo cumple su requisito, pero el nombre de la operación llega desde la web y termina en `eval`.
Ordené por gravedad y comprobé cada caso contra el original.

**a. Qué puede salir mal**

| Gravedad | Problema | Se manifiesta cuando… |
|---|---|---|
| Crítica | `eval` ejecuta cualquier código en el servidor | llega un nombre con `(`, como `__import__('os').environ` |
| Alta | El mismo `eval` puede tumbar el servicio | llega `(9**9**9)` |
| Alta, latente | `getattr` expone todo el módulo, no solo las operaciones | alguien agrega un import o un helper de dos parámetros |
| Media | Las operaciones nuevas no tienen contrato | se agrega una con otra firma, o con un nombre repetido que pisa al anterior |
| Media | Errores sin manejar | se pide una operación que ya no existe, llega `"1,5"` o un número a una operación de texto |
| Media | `float` en montos | se suman `0.1` y `0.2` (el ERP recibe `0.30000000000000004`) o llega `"nan"` |
| Baja | La compuesta devuelve número y la simple, texto | un cliente usa operaciones compuestas |
| Baja | El CLI no valida argumentos; `import os` sobra y facilita el ataque | se ejecuta con menos de tres argumentos |

**b. Corrección mínima:** las salidas legítimas no cambian. Solo lo decorado con `@operation` se puede
llamar; el decorador valida la firma y rechaza nombres repetidos al importar, así que agregar una
operación sigue siendo agregar una función. Las compuestas se mantienen (un cliente las usa), pero pasan
por un evaluador con `ast` que solo acepta operaciones registradas. Los nombres no cambian: son el
contrato con la web. Supuesto: no sé qué compuestas hay guardadas en producción; lo revisaría en los logs
antes de desplegar. Cambio visible: una operación desconocida lanza `OperationNotAllowed`, no
`AttributeError`.

**c. 35 tests** (`docker compose run --rm --build tests` en `part2_transform_registry/`): las entradas
legítimas dan lo mismo que el original, 19 ataques se rechazan sin ejecutarse, y una operación nueva
definida en otro archivo funciona sola y dentro de una compuesta.

**Además del código:** hoy, avisar al líder (es un incidente de seguridad) y buscar en los logs nombres
con `(` que no sean compuestas conocidas; si aparecen, rotar credenciales. Después, coordinado con quienes
reciben los datos: `Decimal`, la coma decimal y tipos consistentes, porque cambian lo que llega al ERP.

## Punto 3 · Revisión de la propuesta de arquitectura

Reviso la propuesta como la de un compañero. La dirección me gusta: eventos en vez de polling donde el
ERP lo permita. Pero hay piezas que no encajan con una base compartida por todas las empresas y otras
que se van a romper en producción. Entre paréntesis, el componente de la propuesta. Diagrama aparte:
[part3_architecture_review/diagram.md](part3_architecture_review/diagram.md).

**a. Qué no aplica a Fracttal**

- **a1. Una base de datos por cliente (2).** Mezcla dos modelos: "propia base de datos" y "un esquema
  por tenant" no son lo mismo. Una base por cliente choca con el contexto, que dice que hay una sola; un
  esquema por cliente vive en el mismo servidor, así que ningún cliente escala por separado. En mi
  experiencia, las bases de los tenants tienen la misma estructura y cambian juntas: separarlas obliga a
  aplicar cada cambio N veces. Además es una decisión de toda la plataforma; la integración debe
  adaptarse al modelo que ya existe.
- **a2. Un worker dedicado por cliente (3).** Se puede separar la CPU de cada cliente, pero la base sigue
  siendo una: la carga de un cliente sí afecta a los demás. Y aunque se automatice, cada cliente nuevo es
  un proceso más que desplegar y vigilar, que es el mismo problema de personal que se quiere resolver.

**b. Qué está mal o se va a romper**

- **b1. Responder 200 solo al terminar (4).** Cuando procesar tarde más que el timeout del ERP (un pico,
  la carga inicial de un cliente, la base lenta), el ERP lo dará por fallido y lo reenviará: el dato
  entra dos veces y la base de todos recibe más carga. Pediría responder 202 apenas el evento quede
  guardado, y procesarlo después.
- **b2. Reintentar "hasta que el servicio responda" (6).** El primer fin de semana que el ERP de un
  cliente esté caído, o con el primer dato que rechace siempre, el evento se reintenta sin fin y los
  siguientes de ese cliente esperan detrás. Si el ERP sí creó la orden pero la respuesta se perdió, el
  reintento la duplica. Pediría un máximo de intentos con backoff.
- **b3. Token en la memoria de cada proceso (7).** Cada réplica pide su propio token con la misma
  credencial. Si el ERP limita los tokens activos, se invalidan entre sí y llegan errores 401 en cascada,
  sobre todo en un despliegue, cuando todas arrancan a la vez. Pediría un almacén compartido (por ejemplo
  Redis) donde una sola réplica renueve el token.

**c. Qué falta antes de aprobarla**

- **c1. Autenticación del webhook:** el cliente debe salir de la credencial, no del mensaje; si no, quien
  conozca la URL podría escribir en los datos de otra empresa.
- **c2. Idempotencia y orden:** una clave por evento para que reenvíos y reintentos no dupliquen, y que un
  dato viejo no pise uno nuevo.
- **c3. Los ERPs que no pueden llamarnos:** los hay on-premise o sin salida a internet por política. Para
  ellos el polling sigue, y adaptarlos vuelve a ser trabajo a medida.
- **c4. Qué pasa cuando algo falla:** cola de errores con reproceso, alertas, métricas y límites por
  cliente. ¿Y cómo se entera el cliente de que un evento suyo falló?
- **c5. Cifras:** cuántos clientes, eventos por segundo y picos, tamaño de los payloads, qué significa
  "tiempo real" y cuánto cuesta operarlo. Sin eso no puedo decir si Kafka hace falta.
- **c6. La migración, para mí lo más delicado:** cómo conviven el polling y los eventos mientras se
  migra, en qué orden pasan los clientes y cómo se vuelve atrás si algo sale mal.

**d. Qué rescataría**

- **d1. Eventos donde el ERP lo permita:** atacan la latencia y las consultas sin datos nuevos.
- **d2. Conectores por ERP con transformaciones en YAML (3 y 5),** con dos condiciones: que las
  diferencias entre clientes del mismo ERP (dos SAP con desarrollos propios pueden responder distinto)
  quepan en configuración, y empezar por los ERPs con más clientes, porque cada conector es más trabajo
  al inicio. El YAML reduce el código a medida, no lo elimina.
- **d3. El bus de eventos (1):** desacoplar está bien; Kafka en particular depende de las cifras.
- **d4. La trazabilidad (8):** sí, pero con los payloads fuera de la base compartida (S3 o equivalente),
  con retención y cifrado.
- **d5. Un piloto, o mejor un laboratorio,** con criterios de éxito y varios clientes simulados: lo que se
  rompe (a2, b3, c4) aparece con muchos clientes, no con uno.
