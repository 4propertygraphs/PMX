# Property Market Dashboard - Český návod

Kompletní dashboard pro analýzu irského trhu nemovitostí s daty z ippi.io.

## 🚀 Rychlé spuštění

### 1. Kompletní setup
```bash
python setup_complete.py
```
Tento script:
- Nainstaluje všechny Python závislosti
- Nastaví MySQL databázi
- Nainstaluje Node.js závislosti
- Vytvoří test uživatele s API klíčem

### 2. Import dat (volitelné - může trvat dlouho)
```bash
python import_data.py
```
Importuje data z Elasticsearch do MySQL. Pokud selže nebo trvá příliš dlouho, můžeš použít jednoduché API.

### 3A. Spuštění s MySQL daty
```bash
python start_api.py
```

### 3B. Nebo spuštění s přímým napojením (rychlejší)
```bash
python start_simple_api.py
```

### 4. Spuštění frontendu
```bash
python start_frontend.py
# nebo
npm run dev
```

## 📊 Funkce dashboardu

### 🏠 Overview
- Celkové metriky trhu
- Top kraje podle cen
- Year-over-year změny
- Interaktivní grafy

### 🗺️ County Analysis
- Detailní analýza podle krajů
- Ceny podle počtu ložnic
- Market trends
- Porovnání krajů

### 🏘️ Rent Analysis
- Analýza nájemního trhu
- Porovnání krajů
- Trendy podle ložnic
- YoY změny v nájmech

### 🔍 Property Search
- Vyhledávání konkrétních nemovitostí
- Pokročilé filtry (kraj, ložnice, cena)
- Detailní informace o nemovitostech
- Export dat

## 🔧 API Endpointy

### Základní endpointy:
- `GET /api/pmx/all` - Všechna data (county/region/area)
- `GET /api/pmx/yoy` - Year-over-year změny
- `GET /api/pmx/average` - Průměrné ceny
- `GET /api/pmx/rent` - Data o nájmech
- `GET /api/eval/property` - Detaily nemovitostí

### Příklady použití:
```bash
# Průměrné ceny v Dublinu
curl "http://localhost:8000/api/pmx/average?county=Dublin&key=test_api_key_123&domain=localhost"

# YoY změny pro 2-3 ložnicové byty v Corku
curl "http://localhost:8000/api/pmx/yoy?county=Cork&beds=2,3&key=test_api_key_123&domain=localhost"

# Všechna data o nájmech
curl "http://localhost:8000/api/pmx/rent?version=avg&key=test_api_key_123&domain=localhost"
```

## 🛠 Technologie

### Backend:
- **FastAPI** - REST API framework
- **SQLAlchemy** - ORM pro databázi
- **MySQL** - Hlavní databáze
- **Pandas** - Zpracování dat
- **Elasticsearch** - Import z ippi.io

### Frontend:
- **React** + **TypeScript** - UI framework
- **Tailwind CSS** - Styling
- **Recharts** - Grafy a vizualizace
- **Axios** - HTTP klient

## 🔍 Řešení problémů

### MySQL Connection Error:
```bash
# Zkontroluj, že MySQL běží
sudo systemctl start mysql
# nebo na macOS
brew services start mysql
```

### Elasticsearch Import Error:
- Zkontroluj API token v `elasticsearch_to_mysql/data_manager/data_manager.py`
- Token může být expirovaný - použij `start_simple_api.py`

### Frontend API Error:
- Zkontroluj, že API běží na portu 8000
- Ověř API credentials (test_api_key_123, localhost)

### Pomalé načítání:
- Použij `start_simple_api.py` místo MySQL verze
- Omez rozsah dat ve filtrech

## 📈 Struktura dat

### Sales Data (Prodeje):
- Ceny nemovitostí podle krajů
- Počet ložnic (1-6+)
- Datum prodeje
- Adresa a lokace
- Velikost v m²

### Rent Data (Nájmy):
- Nájemné podle krajů
- YoY změny v nájmech
- Trendy podle velikosti

### Calculated Metrics:
- Rolling averages
- Year-over-year změny
- Z-scores pro outlier detection
- Regional aggregations

## 🔐 Bezpečnost

- API klíče jsou hashovány v databázi
- CORS nakonfigurován pro localhost
- Autentifikace přes domain + API key
- Rate limiting na API endpointech

## 📝 Poznámky

- Data pocházejí z ippi.io Elasticsearch
- Import může trvat 5-15 minut
- Pro rychlé testování použij simple API
- Frontend automaticky detekuje dostupné API