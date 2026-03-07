# Data Model (NGSIv2)

## Localization boundary
- Entity attributes and identifier values stored in Orion are canonical business data and are not translated.
- UI labels, navigation text, flash messages, and frontend notifications are localized (`es`/`en`) at presentation layer.
- Relationship fields (`refStore`, `refShelf`, `refProduct`) and entity IDs remain unchanged across locales.

## Naming and IDs
- Entity IDs use URN-like prefixes:
- `urn:ngsi-ld:Store:*`
- `urn:ngsi-ld:Product:*`
- `urn:ngsi-ld:Shelf:*`
- `urn:ngsi-ld:InventoryItem:*`
- `urn:ngsi-ld:Employee:*`

## Store
- `id` (`Text`)
- `name` (`Text`)
- `address` (`PostalAddress`):
- `streetAddress`, `addressRegion`, `addressLocality`, `postalCode`
- `location` (`geo:json` Point): `coordinates = [lon, lat]`
- `url` (`Text`)
- `telephone` (`Text`)
- `countryCode` (`Text`, 2 letters in form validation)
- `capacity` (`Number`)
- `description` (`Text`)
- `image` (`Text`, URL string)
- Provider-managed attrs:
- `temperature`
- `relativeHumidity`
- `tweets`

UI usage:
- `location.coordinates` powers map markers in `Stores Map`.
- Store detail renders temperature/humidity metrics and tweets content.

## Product
- `id` (`Text`)
- `name` (`Text`)
- `price` (`Number`)
- `size` (`Text`, UI options `XS|S|M|L|XL`)
- `color` (`Text`, form pattern `#RRGGBB`)
- `image` (`Text`, URL string)

## Shelf
- `id` (`Text`)
- `name` (`Text`)
- `location` (`geo:json` Point)
- `maxCapacity` (`Integer`)
- `refStore` (`Relationship`, Store ID)

## InventoryItem
- `id` (`Text`)
- `refProduct` (`Relationship`, Product ID)
- `refStore` (`Relationship`, Store ID)
- `refShelf` (`Relationship`, Shelf ID)
- `stockCount` (`Integer`)
- `shelfCount` (`Integer`)

## Employee
- `id` (`Text`)
- `name` (`Text`)
- `image` (`Text`, URL string)
- `salary` (`Number`)
- `role` (`Text`)
- `refStore` (`Relationship`, Store ID)
- `email` (`Text`)
- `dateOfContract` (`Date`)
- `skills` (`StructuredValue`, array of strings)
- `username` (`Text`)
- `password` (`Text`)

## Derived constraints and business rules
- Purchase operation updates Orion with:
```json
{
  "shelfCount": {"type": "Integer", "value": {"$inc": -1}},
  "stockCount": {"type": "Integer", "value": {"$inc": -1}}
}
```
- Purchase is rejected when `shelfCount <= 0`.
- Dynamic assignment APIs enforce one inventory relation per product/shelf combination in context:
- Available shelves for a given `store + product`.
- Available products for a given shelf.

## Real-time event payload model
- Orion callbacks are normalized to flat key-value objects before socket emit.
- Socket events delivered to clients:
- `price_change` with product item list.
- `low_stock_001`, `low_stock_002`, `low_stock_003`, `low_stock_004` with inventory item list.

## Provider registration model
- On bootstrap, app maintains 8 registrations (weather + tweets for store codes `001` to `004`).
- Registration scope is exact entity IDs (not wildcard patterns).
- Legacy generic registration descriptions are removed when found.

## Seed dataset (`import-data`)
- Seeds baseline `Store`, `Shelf`, `Product`, `InventoryItem`, and `Employee` entities.
- Includes 4 employees (one per store).
- Store external attrs (`temperature`, `relativeHumidity`, `tweets`) are not seeded and are expected from context providers.
