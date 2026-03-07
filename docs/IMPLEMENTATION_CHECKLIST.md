# FIWARE Supermercados - Implementation Checklist

Issue source: `#2` -> https://github.com/mgonzalezlopezudc/P2-fiware-supermercados/issues/2
Branch: `feat/fiware-implementation-issue-2`

## Workflow
- [ ] Keep all implementation commits in this branch
- [ ] Open PR from `feat/fiware-implementation-issue-2` into `main`
- [ ] Validate all acceptance criteria before merge
- [ ] Update docs before close: `PRD.md`, `architecture.md`, `data_model.md`, `AGENTS.md`

## Environment and Runtime
- [ ] Start infra only with `./services start`
- [ ] Stop infra only with `./services stop`
- [ ] Flask app running on `http://localhost:5000`

## Boot-time FIWARE Setup
- [ ] Register external context providers on app startup: `temperature`, `relativeHumidity`, `tweets`
- [ ] Register Orion subscriptions on app startup
- [ ] Create product price-change subscription (`Product.price`)
- [ ] Create low-stock subscriptions (`shelfCount < 10`) for stores `001`, `002`, `003`, `004`
- [ ] Expose notification endpoints:
- [ ] `/subscription/price-change`
- [ ] `/subscription/low-stock-store001`
- [ ] `/subscription/low-stock-store002`
- [ ] `/subscription/low-stock-store003`
- [ ] `/subscription/low-stock-store004`

## Data Model and CRUD
- [ ] Implement `Product` CRUD with required fields (`id`, `name`, `price`, `size`, `color`)
- [ ] Implement `Store` CRUD with required fields and constraints
- [ ] Implement `Employee` CRUD with required fields
- [ ] Implement `Shelf` and `InventoryItem` management with dynamic filtered selects
- [ ] Enforce `Store.address` as `PostalAddress` object
- [ ] Enforce `Store.location` as `geo:json` `Point` with `[lon, lat]`
- [ ] Validate `Product.color` format as `#RRGGBB`

## Real-time Updates
- [ ] Add Flask-SocketIO server integration
- [ ] Add Socket.IO client integration
- [ ] Broadcast Orion notifications via socket events
- [ ] Reflect product price changes in all relevant views without refresh
- [ ] Show low-stock notifications in matching store notification panel

## Business Operations
- [ ] Implement purchase action on `InventoryItem`
- [ ] Execute `PATCH /v2/entities/<inventoryitem_id>/attrs` decrementing `shelfCount` and `stockCount`
- [ ] Block purchases when `shelfCount <= 0`

## Views and UX
- [ ] Sticky navbar with active section highlighting
- [ ] `Home` with Mermaid UML
- [ ] `Products` list with image, name, edit/delete, `color`, `size`, create action
- [ ] `Product` detail grouped by `Store` + shelf rows + add inventory in available shelf
- [ ] `Stores` list with image, name, edit/delete, `countryCode`, `temperature`, `relativeHumidity`, create action
- [ ] `Store` detail grouped by `Shelf` with progress + actions + inventory item purchase
- [ ] `Store` detail weather/tweets widgets with icons and notifications panel
- [ ] `Employees` list with image, name, edit/delete, `role` category and `skills`, create action
- [ ] `Stores Map` with hover card and click-through to store detail

## Forms and Validation
- [ ] Use input variety: `text`, `email`, `number`, `date`, `color`, `url`, `tel`, `select`, `textarea`
- [ ] HTML validation attributes (`required`, `pattern`, `min`, `max`, `step`, etc.)
- [ ] JS validation with clear error messages and submit blocking

## Internationalization (EN/ES)
- [ ] Add Flask-Babel dependency and app initialization
- [ ] Configure locale resolution and persistence (`?lang`, session, cookie)
- [ ] Add navbar language switcher and apply safe redirect handling
- [ ] Externalize and translate route flash messages
- [ ] Externalize and translate template UI strings
- [ ] Externalize and translate frontend JS dynamic messages/toasts
- [ ] Maintain translation catalogs under `translations/` and compile `.mo` files
- [ ] Validate language switching behavior with automated tests

## Visual Requirements
- [ ] Employee photo hover zoom (CSS)
- [ ] Store photo hover zoom + 360 deg rotation (CSS)
- [ ] Shelf fill progress bars with color coding
- [ ] Compact info using icons (e.g. Font Awesome)

## Manual Acceptance Checks
- [ ] Infrastructure checks completed
- [ ] Data model and CRUD checks completed
- [ ] External provider integration checks completed
- [ ] Subscriptions and real-time checks completed
- [ ] Purchase operation checks completed
- [ ] UI/UX checks completed
- [ ] i18n checks completed for both locales (`es` and `en`)
