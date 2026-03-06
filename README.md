# FIWARE Supermarkets (Flask + NGSIv2)

## Quick Start
1. Start FIWARE services:
```bash
./services start
```
2. Install Python dependencies:
```bash
pip install -r requirements.txt
```
3. Run app:
```bash
python run.py
```
4. Open:
- App: `http://localhost:5000`
- Orion monitor: `http://localhost:3000/app/monitor`

Stop FIWARE services:
```bash
./services stop
```

## Environment Variables
- `ORION_BASE_URL` (default `http://localhost:1026`)
- `APP_BASE_URL` (default `http://localhost:5000`)
- `CONTEXT_PROVIDER_URL` (default `http://tutorial:3000`)
- `FIWARE_SERVICE` (default `openiot`)
- `FIWARE_SERVICEPATH` (default `/`)
- `AUTO_BOOTSTRAP` (default `true`)

## Notes
- App startup ensures provider registrations and subscriptions exist.
- Orion remains the source of truth for business entities.
