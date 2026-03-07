# Data Model (NGSIv2)

## Store
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
- `image` (URL)

Presentation usage:
- `location.coordinates` (`[lon, lat]`) feeds Leaflet marker positions in `Stores Map`.
- Store marker popups expose `name`, optional `address.addressLocality`, and a detail-page link.
- If Leaflet assets cannot be loaded from CDN, the UI shows an explicit map load error message instead of a blank area.

## Product
- `id`, `name`, `price`, `size`, `color`
- `color` format: `#RRGGBB`
- `image` (URL)

## Shelf
- `id`, `name`, `location`, `maxCapacity`, `refStore`

## InventoryItem
- `id`, `refProduct`, `refStore`, `refShelf`, `stockCount`, `shelfCount`

## Employee
- `id`, `name`, `image`, `salary`, `role`, `refStore`, `email`, `dateOfContract`, `skills`, `username`, `password`

## Seed Dataset
- `import-data` populates all mandatory attributes for `Store`, `Product`, `Shelf`, `InventoryItem`, and `Employee`.
- `import-data` intentionally omits provider-managed `Store` attributes (`temperature`, `relativeHumidity`, `tweets`), which are supplied at query time by Orion context providers.
- Seed includes 4 employees (one per store) and meaningful free-to-use image URLs for store, product, and employee entities.

## Business Rule
Purchase action performs:
```json
{
  "shelfCount": {"type": "Integer", "value": {"$inc": -1}},
  "stockCount": {"type": "Integer", "value": {"$inc": -1}}
}
```
and is blocked when `shelfCount <= 0`.

## Provider Registrations
- External attributes for `Store` (`temperature`, `relativeHumidity`, `tweets`) are served through Orion registrations scoped by exact store IDs.
- The app maintains 8 registrations at startup:
  - weather provider for `urn:ngsi-ld:Store:001`, `002`, `003`, `004`
  - tweets provider for `urn:ngsi-ld:Store:001`, `002`, `003`, `004`
- Wildcard registrations using `idPattern: ".*"` are considered legacy and are removed by bootstrap.
- In the store detail page, `temperature` and `relativeHumidity` are displayed as metric cards, while `tweets` is rendered in a full-width content block.
- Tweets are rendered in responsive columns (desktop/tablet/mobile: 3/2/1).
