# Property Market Dashboard

Kompletní dashboard pro analýzu irského trhu nemovitostí s daty z ippi.io.

## 🚀 Rychlé spuštění

### 1. Příprava databáze
```bash
# Ujisti se, že MySQL běží na localhost:3306
# Spusť setup databáze
python setup_database.py
```

### 2. Import dat z Elasticsearch
```bash
# Import dat z ippi.io Elasticsearch
python run_data_import.py
```

### 3. Spuštění backendu
```bash
# Spustí FastAPI server na portu 8000
python start_backend.py
```

### 4. Spuštění frontendu
Frontend už běží na `http://localhost:5173`

## 🔧 Konfigurace

### API Credentials pro testování:
- **API Key**: `test_api_key_123`
- **Domain**: `localhost`
- **Base URL**: `http://localhost:8000`

### Databáze:
- **PMX Data**: `mysql://root@localhost:3306/pmx_report`
- **API Auth**: `mysql://root@localhost:3306/pmx_api_auth`

## 📊 Funkce dashboardu

### Overview
- Celkové metriky trhu
- Top kraje podle cen
- YoY změny
- Interaktivní grafy

### County Analysis
- Detailní analýza podle krajů
- Ceny podle počtu ložnic
- Market trends

### Rent Analysis
- Analýza nájemního trhu
- Porovnání krajů
- Trendy podle ložnic

### Property Search
- Vyhledávání nemovitostí
- Pokročilé filtry
- Detailní informace

## 🛠 Technologie

### Backend:
- **FastAPI** - REST API
- **SQLAlchemy** - ORM
- **MySQL** - Databáze
- **Pandas** - Data processing

### Frontend:
- **React** + **TypeScript**
- **Tailwind CSS** - Styling
- **Recharts** - Grafy
- **Axios** - HTTP client

## 📝 API Endpointy

- `GET /api/pmx/all` - Všechna data (county/region/area)
- `GET /api/pmx/yoy` - Year-over-year změny
- `GET /api/pmx/average` - Průměrné ceny
- `GET /api/pmx/rent` - Data o nájmech
- `GET /api/eval/property` - Detaily nemovitostí

## 🔍 Troubleshooting

### MySQL Connection Error:
```bash
# Zkontroluj, že MySQL běží
sudo systemctl start mysql
# nebo
brew services start mysql
```

### Elasticsearch Connection Error:
- Zkontroluj API token v `elasticsearch_to_mysql/data_manager/data_manager.py`
- Ujisti se, že máš přístup k ippi.io API

### Frontend API Error:
- Zkontroluj, že backend běží na portu 8000
- Ověř API credentials v konfiguraci

## 📈 Data Flow

1. **Elasticsearch** (ippi.io) → **Python Scripts** → **MySQL**
2. **MySQL** → **FastAPI** → **React Frontend**

## 🔐 Bezpečnost

- API klíče jsou hashovány v databázi
- CORS je nakonfigurován pro localhost
- Autentifikace přes domain + API key