# 🛍️ Amazon Deals Finder - Quick Start Guide

## What You Just Got

A **fully functional Amazon tech deals finder** with:

- ✅ Beautiful, modern web interface
- ✅ Real Amazon product scraping
- ✅ 10 tech categories (laptops, monitors, keyboards, etc.)
- ✅ Discount filtering (10%+ to 50%+)
- ✅ Product search
- ✅ Price comparison (original vs. current)
- ✅ Ratings and reviews
- ✅ Prime eligibility badges

## 🚀 Quick Start (2 options)

### Option 1: Use the start script
```bash
cd /Users/jerry/Projects/amazon-deals-finder
./start.sh
```

### Option 2: Manual start
```bash
cd /Users/jerry/Projects/amazon-deals-finder/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Then open: **http://localhost:8000**

## 📁 Project Structure

```
amazon-deals-finder/
├── backend/
│   ├── main.py          # FastAPI server
│   ├── scraper.py       # Amazon scraper
│   └── requirements.txt # Dependencies
├── frontend/
│   ├── index.html       # Main UI
│   ├── style.css        # Styling
│   └── app.js           # Interactive features
└── start.sh             # Quick start script
```

## 🎯 Features

### Search
- Type any tech product
- Filter by minimum discount
- Get up to 30 results

### Categories
- 💻 Laptops
- 🖥️ Monitors
- ⌨️ Keyboards
- 🖱️ Mice
- 🎧 Headphones
- 📱 Phones
- 📲 Tablets
- ⌚ Smartwatches
- 📷 Webcams
- 🎤 Microphones

### Each Product Shows:
- Product image
- Title
- Current price
- Original price (if on sale)
- Discount percentage
- Amount saved
- Star rating
- Number of reviews
- Prime eligibility

## 🔧 How It Works

1. **Backend (Python)**:
   - Scrapes Amazon search results
   - Extracts product data
   - Calculates discounts
   - Serves data via API

2. **Frontend (HTML/CSS/JS)**:
   - Beautiful gradient UI
   - Category buttons
   - Search interface
   - Product cards
   - Responsive design

## ⚠️ Important Notes

### Amazon Scraping
- This scrapes Amazon's public search results
- Amazon may block if you make too many requests
- Use reasonable delays between searches
- For production, consider Amazon's official API

### Rate Limiting
- The scraper includes basic headers to avoid detection
- Don't spam requests
- Add delays if needed

## 🚀 Next Steps / Enhancements

Easy additions you could make:

1. **Price History**
   - Track prices over time
   - Show price trends

2. **Notifications**
   - Email/SMS when price drops
   - Webhook integrations

3. **More Categories**
   - Add gaming, audio, cameras, etc.

4. **Comparison**
   - Compare prices across products
   - Find best value

5. **Favorites**
   - Save products to watch list
   - Browser storage or database

6. **Filters**
   - Min/max price range
   - Prime only
   - Rating threshold
   - Brand filter

## 💡 Tips

- **Search tips**: Be specific ("gaming laptop", "4k monitor", "mechanical keyboard rgb")
- **Discount filter**: Start with 15%+ for good deals, 30%+ for great deals
- **Prime**: Prime products often have better prices/shipping
- **Reviews**: Check rating and review count before buying

## 🐛 Troubleshooting

**No results?**
- Amazon may have changed their HTML structure
- Try a different search term
- Check your internet connection

**Slow performance?**
- Amazon scraping takes a few seconds
- Normal behavior

**Server won't start?**
- Make sure port 8000 isn't in use
- Check Python 3 is installed
- Run `pip install -r requirements.txt` again

## 📊 API Endpoints

If you want to use the API directly:

- `GET /api/categories` - List all categories
- `GET /api/search?q=laptop&min_discount=15` - Search products
- `GET /api/deals/laptops?min_discount=20` - Get category deals

Example:
```bash
curl "http://localhost:8000/api/search?q=gaming%20mouse&min_discount=20"
```

---

**Enjoy finding amazing tech deals!** 🎉
