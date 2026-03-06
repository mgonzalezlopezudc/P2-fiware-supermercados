## [Feature] Aplicacion FIWARE Supermercados (Flask + NGSIv2)

## Context
Se necesita implementar una aplicacion web de gestion de supermercados usando FIWARE Orion (NGSIv2), backend Flask + Jinja2 y frontend HTML/CSS/JS puro. La solucion debe integrar proveedores de contexto externos, suscripciones Orion y actualizaciones en tiempo real en UI.

Restricciones obligatorias:
- Usar `./services start` y `./services stop`.
- No usar `docker-compose.yml` directamente.
- Registrar proveedores de contexto y suscripciones al arrancar la app.
- Priorizar CSS sobre JS para efectos visuales y minimizar generacion de HTML desde JS.

## Scope
Implementar CRUD y vistas para entidades `Store`, `Product`, `Shelf`, `InventoryItem`, `Employee`, con integracion NGSIv2 y flujo de notificaciones en tiempo real.

## Data Model Rules
- Cobertura de atributos obligatoria por entidad:
  - `Store`: `id`, `name`, `address`, `location`, `url`, `telephone`, `countryCode`, `capacity`, `description`, `temperature`, `relativeHumidity`, `tweets`.
  - `Product`: `id`, `name`, `price`, `size`, `color`.
  - `Shelf`: `id`, `name`, `location`, `maxCapacity`, `refStore`.
  - `InventoryItem`: `id`, `refProduct`, `refStore`, `refShelf`, `stockCount`, `shelfCount`.
  - `Employee`: `id`, `name`, `image`, `salary`, `role`, `refStore`, `email`, `dateOfContract`, `skills`, `username`, `password`.
- `Store.address` debe ser compuesto tipo `PostalAddress` (ej. `streetAddress`, `addressRegion`, `addressLocality`, `postalCode`).
- `Store.location` debe ser `geo:json` con `value` GeoJSON `Point` y coordenadas `[longitud, latitud]`.
- Tomar como referencia `import-data` para serializacion NGSIv2 de `Store.address` y `Store.location`.
- `Product.color` en formato `#RRGGBB`.
- `Employee.role` se usara como categoria visual en UI.

## Tasks
- [ ] Configurar arranque de app con registro automatico de proveedores externos en Orion (`temperature`, `relativeHumidity`, `tweets`).
- [ ] Crear suscripciones Orion al arranque:
  - [ ] `Product price change` (attr `price`).
  - [ ] `Low stock` para stores `001`, `002`, `003`, `004` con condicion `shelfCount < 10` y filtro por `refStore`.
- [ ] Implementar endpoints Flask de notificacion:
  - [ ] `/subscription/price-change`
  - [ ] `/subscription/low-stock-store001`
  - [ ] equivalentes para `002`, `003`, `004`.
- [ ] Implementar Socket.IO server/client para propagar cambios en tiempo real.
- [ ] Implementar vistas con navbar sticky y seccion activa:
  - [ ] `Home` (UML Mermaid renderizado)
  - [ ] `Products` con tabla que incluya imagen, nombre, acciones editar/borrar y atributos `color`, `size`, mas boton de alta.
  - [ ] `Product` detalle con inventario agrupado por `Store` (cabecera store con stock agregado, subfilas por shelf con `shelfCount`, accion para anadir inventory item en shelf disponible del mismo store).
  - [ ] `Stores` con tabla que incluya imagen, nombre, acciones editar/borrar y atributos `countryCode`, `temperature`, `relativeHumidity`, mas boton de alta.
  - [ ] `Store` detalle con inventario agrupado por `Shelf` (cabecera con id, progreso y acciones; subfilas con `name`, `price`, `size`, `color`, `stockCount`, `shelfCount`; compra por item).
  - [ ] `Store` detalle mostrando `temperature` y `relativeHumidity` con icono + color + valor, `tweets` con icono estilo X y panel de notificaciones.
  - [ ] `Employees` con tabla que incluya foto, nombre, acciones editar/borrar, `role`/categoria y `skills`, mas boton de alta.
  - [ ] `Stores Map`
- [ ] Implementar CRUD de `Product`, `Store`, `Employee`.
- [ ] Implementar gestion de `Shelf` e `InventoryItem` con selects dinamicos filtrados.
- [ ] Implementar compra por `InventoryItem`:
  - [ ] `PATCH /v2/entities/<inventoryitem_id>/attrs` decrementando `shelfCount` y `stockCount`.
  - [ ] Bloqueo de compra cuando `shelfCount <= 0`.
- [ ] Implementar formularios con validaciones HTML + JS y variedad de inputs (`text`, `email`, `number`, `date`, `color`, `url`, `tel`, `select`, `textarea`).
- [ ] Aplicar requisitos visuales:
  - [ ] Hover zoom en foto de `Employee`.
  - [ ] Hover zoom + rotacion 360 en foto de `Store`.
  - [ ] Barra de progreso por color segun llenado de shelf.
  - [ ] Uso de iconos para compactar informacion.
- [ ] Actualizar documentacion:
  - [ ] `PRD.md`
  - [ ] `architecture.md`
  - [ ] `data_model.md`
  - [ ] Nota en `AGENTS.md` sobre actualizacion documental post-issue.

## Acceptance Criteria
1. Infraestructura
- [ ] `./services start` levanta entorno FIWARE sin errores.
- [ ] App Flask operativa en puerto `5000`.

2. Datos y modelo
- [ ] CRUD operativo para `Product`, `Store`, `Employee`.
- [ ] Gestion de `Shelf` e `InventoryItem` funcional.
- [ ] Todas las entidades incluyen sus atributos obligatorios segun `Data Model Rules`.
- [ ] `Store.address` persiste como objeto `PostalAddress`.
- [ ] `Store.location` persiste como `geo:json` valido (`Point`, `[lon, lat]`).

3. Integraciones externas
- [ ] `temperature`, `relativeHumidity` y `tweets` visibles en detalle de store y alimentados por proveedor externo.

4. Suscripciones y tiempo real
- [ ] Suscripciones `Low stock` configuradas con `shelfCount < 10` y filtro por `refStore` para stores `001..004`.
- [ ] Cambio de precio se refleja en todas las vistas relevantes sin recarga.
- [ ] Bajo stock aparece en panel de notificaciones del store correcto.

5. Operacion de compra
- [ ] PATCH decrementa `shelfCount` y `stockCount`.
- [ ] La compra se bloquea correctamente sin stock en shelf.

6. UI/UX
- [ ] Navbar sticky con item activo.
- [ ] `Products`, `Stores` y `Employees` muestran tablas con imagen, nombre y acciones de edicion/borrado.
- [ ] Vista `Product` agrupa por `Store` y vista `Store` agrupa por `Shelf` segun especificacion.
- [ ] `Stores Map` funcional (hover card + click a detalle).
- [ ] Animaciones y codificacion visual implementadas segun requisitos.

## Definition of Done
- [ ] Todas las tareas del issue completadas.
- [ ] Acceptance Criteria cumplidos y validados manualmente.
- [ ] Documentacion actualizada (`PRD.md`, `architecture.md`, `data_model.md`).
- [ ] Cambios integrados via GitHub Flow (branch, commits, PR/merge).