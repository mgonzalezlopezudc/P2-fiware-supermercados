# Data Model (NGSIv2)

## Store
Mandatory attributes:
- `id`
- `name`
- `address` (`PostalAddress` object with `streetAddress`, `addressRegion`, `addressLocality`, `postalCode`)
- `location` (`geo:json` `Point` with `[lon, lat]`)
- `url`
- `telephone`
- `countryCode`
- `capacity`
- `description`
- `temperature`
- `relativeHumidity`
- `tweets`

## Product
Mandatory attributes:
- `id`, `name`, `price`, `size`, `color`
- `color` format: `#RRGGBB`

## Shelf
Mandatory attributes:
- `id`, `name`, `location`, `maxCapacity`, `refStore`

## InventoryItem
Mandatory attributes:
- `id`, `refProduct`, `refStore`, `refShelf`, `stockCount`, `shelfCount`

## Employee
Mandatory attributes:
- `id`, `name`, `image`, `salary`, `role`, `refStore`, `email`, `dateOfContract`, `skills`, `username`, `password`

## Business Rule
Purchase action performs:
```json
{
  "shelfCount": {"type": "Integer", "value": {"$inc": -1}},
  "stockCount": {"type": "Integer", "value": {"$inc": -1}}
}
```
and is blocked when `shelfCount <= 0`.
