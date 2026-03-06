# Prompt Maestro de Implementacion

Implementa una aplicacion web de gestion de cadena de supermercados con FIWARE Orion (NGSIv2), Flask + Jinja2 y frontend HTML/CSS/JS puro.

## Objetivo

Construir una aplicacion completa con CRUD, vistas avanzadas, integracion con proveedores de contexto externos, suscripciones Orion y actualizacion en tiempo real de la interfaz mediante Socket.IO.

## Restricciones obligatorias

1. Usar `./services start` y `./services stop` para levantar/parar contenedores.
2. No usar `docker-compose.yml` directamente.
3. Mantener NGSIv2 como fuente principal de datos de negocio.
4. Registrar proveedores de contexto y suscripciones al arrancar la app.
5. Usar CSS para efectos visuales siempre que sea posible y minimizar generacion de HTML desde JS.

## Stack tecnico

1. Backend: Python Flask + plantillas Jinja2.
2. Frontend: HTML + CSS + JS puro.
3. Tiempo real: Flask-SocketIO (server) + Socket.IO (cliente).
4. Broker: FIWARE Orion NGSIv2.

## Modelo de datos (NGSIv2)

Implementar entidades:

1. `Store`
- `id`
- `name`
- `address` compuesto tipo `PostalAddress`.
	Estructura esperada en `value`: `streetAddress`, `addressRegion`, `addressLocality`, `postalCode`.
- `location` tipo `geo:json` con `value` GeoJSON `Point` y coordenadas en formato `[longitud, latitud]`.
- `url`
- `telephone`
- `countryCode` (2 caracteres)
- `capacity` (m3)
- `description`
- `temperature`
- `relativeHumidity`
- `tweets`

2. `Product`
- `id`, `name`, `price`, `size` (`XS|S|M|L|XL`), `color` (`#RRGGBB`).

3. `Shelf`
- `id`, `name`, `location`, `maxCapacity`, `refStore`.

4. `InventoryItem`
- `id`, `refProduct`, `refStore`, `refShelf`, `stockCount`, `shelfCount`.

5. `Employee`
- `id`, `name`, `image`, `salary`, `role`, `refStore`, `email`, `dateOfContract`, `skills`, `username`, `password`.

Nota de consistencia:
Tomar como referencia canonica `import-data` para serializacion NGSIv2 de `Store.address` y `Store.location`.

## Vistas y comportamiento

1. Navbar sticky con seccion activa resaltada: `Home`, `Products`, `Stores`, `Employees`, `Stores Map`.
2. `Home`: renderizar diagrama UML de entidades con Mermaid.
3. `Products`: tabla con imagen, nombre, botones editar/borrar y atributos `color`, `size`; boton para crear.
4. `Product` (detalle): inventario agrupado por `Store`.
- Fila de cabecera por store con stock agregado.
- Subfilas por shelf con `shelfCount`.
- Boton para anadir `InventoryItem` en otra shelf disponible del mismo store (select dinamico filtrado).
5. `Stores`: tabla con imagen, nombre, botones editar/borrar y `countryCode`, `temperature`, `relativeHumidity`; boton para crear.
6. `Store` (detalle): inventario agrupado por `Shelf`.
- Cabecera de shelf con id, progreso de llenado y acciones (editar shelf, anadir producto no presente).
- Subfilas por producto con `name`, `price`, `size`, `color`, `stockCount`, `shelfCount`.
- Boton comprar unidad por inventory item.
- Mostrar `temperature` y `relativeHumidity` con iconos, color y valor.
- Mostrar `tweets` del store con icono estilo X.
- Mostrar panel de notificaciones del store.
7. `Employees`: tabla con foto, nombre, editar/borrar y atributos de rol/categoria y skills; boton para crear.
8. `Stores Map`: mapa con imagenes de stores; hover muestra card; click navega al detalle del store.

## Operaciones de negocio

Compra de una unidad desde vista store:

`PATCH /v2/entities/<inventoryitem_id>/attrs`

Body:

```json
{
	"shelfCount": {"type": "Integer", "value": {"$inc": -1}},
	"stockCount": {"type": "Integer", "value": {"$inc": -1}}
}
```

Validacion requerida:
Si `shelfCount <= 0`, bloquear compra y mostrar error en UI.

## Proveedores de contexto externos

1. `temperature` y `relativeHumidity` de `Store` provienen del contenedor `tutorial`.
2. `tweets` de `Store` provienen del contenedor `tutorial`.
3. Registrar ambos proveedores en Orion al arranque.

## Suscripciones Orion obligatorias

Crear al arranque:

1. `Product price change` para cambios en `price` de `Product`.
2. `Low stock` para stores `001`, `002`, `003`, `004`, con condicion `shelfCount < 10` y filtro por `refStore`.

Endpoints de recepcion en Flask:

1. `/subscription/price-change`
2. `/subscription/low-stock-store001`
3. Equivalentes para `002`, `003`, `004`.

## Tiempo real

1. Al recibir notificacion Orion, emitir evento Socket.IO al navegador.
2. Reflejar cambio de precio en todas las vistas donde aparezca el producto, sin recargar pagina.
3. Mostrar notificaciones de bajo stock en el panel de notificaciones del store correspondiente.

## Formularios y validaciones

1. Usar variedad de inputs: `text`, `email`, `number`, `date`, `color`, `url`, `tel`, `select`, `textarea`.
2. Aplicar validaciones HTML (`required`, `pattern`, `min`, `max`, `step`, etc.).
3. Aplicar validaciones JS con mensajes claros y bloqueo de submit cuando corresponda.
4. Selects dinamicos filtrados:
- En `Product` detalle: shelves del store que aun no contienen el producto.
- En `Store` detalle: productos que aun no estan en la shelf.

## Requisitos visuales

1. Foto de `Employee`: hover zoom con transicion CSS.
2. Foto de `Store`: hover con zoom y rotacion 360 grados (CSS).
3. Barra de progreso de shelf con color segun llenado.
4. Uso de iconos (Font Awesome recomendado) y codificacion visual para compactar informacion en tablas.

## Entregables

1. Aplicacion funcional end-to-end.
2. Registro automatico de proveedores y suscripciones al arranque.
3. Actualizacion en tiempo real con Socket.IO.
4. Actualizacion documental obligatoria tras cerrar el issue:
- `PRD.md`
- `architecture.md`
- `data_model.md`
- Recomendacion en `AGENTS.md` para mantener esa practica en futuros issues.

## Checklist de aceptacion

1. Infraestructura:
- `./services start` levanta entorno FIWARE sin errores.
- App Flask en puerto `5000` operativa.

2. Datos:
- CRUD operativo para `Product`, `Store`, `Employee`.
- Gestion operativa de `Shelf` e `InventoryItem`.
- `Store.address` se persiste como objeto `PostalAddress`.
- `Store.location` se persiste como `geo:json` valido (`Point`, `[lon, lat]`).

3. Integracion externa:
- Temperatura, humedad y tweets visibles en detalle de store y provenientes de proveedor externo.

4. Suscripciones y tiempo real:
- Cambio de precio propagado a toda la UI sin refresh.
- Bajo stock mostrado como notificacion en el store correcto.

5. Operacion de compra:
- PATCH decrementa `shelfCount` y `stockCount`.
- Compra bloqueada cuando no hay stock en shelf.

6. UX/UI:
- Navbar sticky y activa.
- Stores Map funcional con hover y click.
- Animaciones y barras de progreso funcionando segun especificacion.

## Flujo de trabajo de entrega (GitHub Flow)

1. Crear issue con este prompt como alcance.
2. Crear rama de implementacion.
3. Implementar y commitear cambios.
4. Push y PR (o merge directo a `main` si aplica).
5. Actualizar documentacion requerida antes de cerrar.