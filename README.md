# Amazon Deals Finder 🛍️

Find the best tech deals on Amazon.ca with automatic price history tracking and historical low detection.

## 🚀 Live Demo

**Deployed on Render:** [Coming Soon]

## ✨ Features

- 🔍 Search thousands of products across tech categories
- 📊 Automatic price history tracking with CamelCamelCamel integration
- 🔥 "ALL TIME LOW" badge detection
- 💾 PostgreSQL database for persistent storage
- ⚡ Optimized scraping with parallel page processing
- 🎯 Smart caching (5-minute TTL)
- 📱 Responsive, modern UI
- 🐳 Docker support for easy deployment

## 🛠️ Tech Stack

**Backend:**
- Python 3.9
- FastAPI
- SQLAlchemy ORM
- PostgreSQL
- BeautifulSoup4 (web scraping)

**Frontend:**
- Vanilla JavaScript
- CSS3 with animations
- Amazon-inspired design

**Infrastructure:**
- Docker & Docker Compose
- PostgreSQL 14
- Render (deployment)

## 📦 Installation

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/amazon-deals-finder.git
cd amazon-deals-finder

# Start everything with Docker
docker-compose up

# Visit http://localhost:8000
```

### Option 2: Local Setup

```bash
# Install PostgreSQL
brew install postgresql@14
brew services start postgresql@14
createdb amazon_deals

# Install Python dependencies
cd backend
pip install -r requirements.txt

# Set up environment
cp .env.example .env

# Run the server
python main.py

# Visit http://localhost:8000
```

## 🎯 Usage

1. **Browse Categories:** Click any tech category to see current deals
2. **Search Products:** Use the search bar to find specific items
3. **Sort Results:** Sort by name, price, or discount percentage
4. **Track Prices:** All products are automatically tracked in the database

## 🗄️ Database Schema

- **products:** Stores product information (ASIN, title, image, etc.)
- **price_history:** Tracks price changes over time

## 📊 Features in Detail

### Price History Tracking
- Automatically fetches historical data from CamelCamelCamel
- Detects when products hit their all-time low price
- Stores price snapshots for trend analysis

### Optimized Scraping
- Parallel page scraping (3x faster)
- 5-minute result caching
- Smart rate limiting to avoid blocks

### PostgreSQL Integration
- Persistent data storage
- Query optimization with indexes
- Connection pooling for performance

## 🚀 Deployment

See [DATABASE_SETUP.md](DATABASE_SETUP.md) for detailed deployment instructions.

### Quick Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Click the button above
2. Connect your GitHub account
3. Database and backend will auto-deploy
4. Done! Get your live URL

## 🤝 Contributing

This is a portfolio project, but suggestions are welcome!

## 📝 License

MIT License - feel free to use this for learning purposes.

## 🎓 Learning Outcomes

This project demonstrates:
- Full-stack web development
- Database design and ORM usage
- Web scraping best practices
- Docker containerization
- Cloud deployment
- REST API design
- Modern frontend development

---

**Built with ❤️ for finding great tech deals**
