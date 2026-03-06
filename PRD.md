# Product Requirements Document

## Product
FIWARE Supermarkets management web app using Orion NGSIv2 as business data source.

## Goals
- Manage `Store`, `Product`, `Shelf`, `InventoryItem`, `Employee` entities with CRUD and relationship workflows.
- Integrate Orion context providers for store external attributes (`temperature`, `relativeHumidity`, `tweets`).
- Receive Orion subscriptions and update UI in real time through Socket.IO.

## Users
- Store operations staff.
- Inventory managers.
- Supervisors tracking low stock alerts.

## Functional Scope
- Sticky navigation and pages: `Home`, `Products`, `Product detail`, `Stores`, `Store detail`, `Employees`, `Stores Map`.
- CRUD operations for `Product`, `Store`, `Employee`.
- Shelf and inventory management with dynamic filtered selects.
- Purchase action reducing `shelfCount` and `stockCount` with empty shelf protection.
- Real-time price and low-stock notifications.

## Non-functional Requirements
- Flask + Jinja2 + plain HTML/CSS/JS.
- Orion NGSIv2 APIs for all entity persistence.
- Visual effects mostly done in CSS.
- Infrastructure lifecycle via `./services start` and `./services stop`.
