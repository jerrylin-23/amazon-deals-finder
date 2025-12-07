# PostgreSQL Database Setup Guide

## Quick Start (Choose One Method)

### Method 1: Docker (Recommended - Easiest)

```bash
# Start everything with one command
docker-compose up

# The app will be available at http://localhost:8000
# Database will be automatically created and initialized
```

That's it! Docker handles PostgreSQL installation and setup automatically.

---

### Method 2: Local PostgreSQL

**Step 1: Install PostgreSQL**
```bash
# macOS with Homebrew
brew install postgresql@14

# Start PostgreSQL service
brew services start postgresql@14
```

**Step 2: Create Database**
```bash
# Create the database
createdb amazon_deals
```

**Step 3: Set Environment Variable**
```bash
# Copy the example env file
cp backend/.env.example backend/.env

# Edit backend/.env if needed (default works for local)
DATABASE_URL=postgresql://localhost/amazon_deals
```

**Step 4: Install Python Dependencies**
```bash
cd backend
pip3 install -r requirements.txt
```

**Step 5: Initialize Database**
```bash
# Tables will be created automatically on first run
python3 main.py
```

**Step 6: Verify**
```bash
# Check if tables were created
psql amazon_deals -c "\dt"

# Should show: products, price_history
```

---

## Database Schema

### Products Table
```sql
id              SERIAL PRIMARY KEY
asin            VARCHAR(20) UNIQUE NOT NULL
title           TEXT NOT NULL
url             TEXT
image_url       TEXT
category        VARCHAR(50)
is_prime        BOOLEAN
rating          NUMERIC(2,1)
num_reviews     INTEGER
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

### Price History Table
```sql
id                  SERIAL PRIMARY KEY
product_id          INTEGER (FK to products)
asin                VARCHAR(20) NOT NULL
current_price       NUMERIC(10,2)
original_price      NUMERIC(10,2)
discount_percent    INTEGER
lowest_ever         NUMERIC(10,2)
highest_ever        NUMERIC(10,2)
is_historical_low   BOOLEAN
timestamp           TIMESTAMP
```

---

## Usage

### Scraping Products
Products are automatically saved to the database when scraped.

```python
# Search API scrapes and saves to DB
GET /api/search?q=laptop

# Category API scrapes and saves to DB
GET /api/deals/laptops
```

### Querying Database
```bash
# View all products
psql amazon_deals -c "SELECT asin, title, current_price FROM products LIMIT 10;"

# View price history
psql amazon_deals -c "SELECT asin, current_price, timestamp FROM price_history ORDER BY timestamp DESC LIMIT 20;"

# Find  historical lows
psql amazon_deals -c "SELECT asin, current_price FROM price_history WHERE is_historical_low = true;"
```

---

## Troubleshooting

### "Could not connect to database"
```bash
# Check if PostgreSQL is running
brew services list

# Restart PostgreSQL
brew services restart postgresql@14
```

### "Database does not exist"
```bash
# Create the database
createdb amazon_deals
```

### "Permission denied"
```bash
# Make sure you're using the correct user
# Default is your Mac username with no password
DATABASE_URL=postgresql://localhost/amazon_deals
```

### Docker Issues
```bash
# Reset everything
docker-compose down -v
docker-compose up --build
```

---

## Maintenance

### View Database Size
```bash
psql amazon_deals -c "SELECT pg_size_pretty(pg_database_size('amazon_deals'));"
```

### Clear Old Price History
```sql
-- Delete price history older than 90 days
DELETE FROM price_history 
WHERE timestamp < NOW() - INTERVAL '90 days';
```

### Backup Database
```bash
pg_dump amazon_deals > backup.sql
```

### Restore Database
```bash
psql amazon_deals < backup.sql
```

---

## What Changed

**Before (In-Memory):**
- Data lost on restart
- Slow (scrape every time)
- No history tracking

**After (PostgreSQL):**
- ✅ Data persists forever
- ✅ Fast (query database)
- ✅ Price history tracking
- ✅ Ready for user accounts
- ✅ Production-ready

---

## Next Steps

With PostgreSQL set up, you can now add:
1. User accounts and authentication
2. Price drop alerts
3. Favorite products/watchlists
4. Historical price charts
5. Background scraping jobs

