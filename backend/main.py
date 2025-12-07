"""
Amazon Deals Finder - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional
from sqlalchemy.orm import Session
import uvicorn
from pathlib import Path

from scraper import AmazonScraper
from database import get_db, init_db, engine
import crud
import models

# Initialize FastAPI app
app = FastAPI(
    title="Amazon Deals Finder API",
    description="Find the best tech deals on Amazon with price history",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup():
    """Initialize database tables"""
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")

# Initialize scraper
scraper = AmazonScraper()

# Mount frontend static files
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")


@app.get("/")
async def root():
    """Serve frontend HTML"""
    html_file = frontend_path / "index.html"
    if html_file.exists():
        return FileResponse(str(html_file))
    return {
        "app": "Amazon Deals Finder API",
        "version": "1.0.0",
        "endpoints": {
            "/api/search": "Search for products",
            "/api/categories": "Get available categories",
            "/api/deals/{category}": "Get deals by category"
        }
    }


@app.get("/api/categories")
async def get_categories():
    """Get list of available product categories"""
    return {
        "categories": scraper.get_all_categories()
    }


@app.get("/api/search")
async def search_products(
    q: str = Query(..., description="Search query"),
    max_results: int = Query(20, ge=1, le=100),
    min_discount: int = Query(0, ge=0, le=100),
    db: Session = Depends(get_db)
):
    """
    Search Amazon for products
    
    Args:
        q: Search query (e.g., 'laptop', 'gaming mouse')
        max_results: Maximum number of results (1-100)
        min_discount: Minimum discount percentage (0-100)
    """
    try:
        # CACHE-FIRST: Check database for recent results (last 5 minutes)
        from datetime import datetime, timedelta
        cache_cutoff = datetime.utcnow() - timedelta(minutes=5)
        
        # Search database for cached results
        cached_products = db.query(models.Product).filter(
            models.Product.title.ilike(f'%{q}%'),
            models.Product.updated_at >= cache_cutoff
        ).limit(max_results).all()
        
        # If we have recent cached results, return them (FAST!)
        if cached_products:
            print(f"✓ Cache HIT: {len(cached_products)} products from database")
            products = [{
                'asin': p.asin,
                'title': p.title,
                'url': p.url,
                'image_url': p.image_url,
                'current_price': None,  # Price from latest price_history
                'discount_percent': 0,
                'rating': p.rating,
                'num_reviews': p.num_reviews,
                'is_prime': p.is_prime
            } for p in cached_products]
            return {
                "query": q,
                "count": len(products),
                "products": products,
                "cached": True
            }
        
        # Cache MISS: Scrape Amazon for fresh product data
        print(f"✗ Cache MISS: Scraping Amazon for '{q}'")
        products = scraper.search_products(q, max_results=max_results, min_discount=min_discount)
        
        # Save scraped products to database (for future cache hits)
        if products:
            for product in products:
                product['category'] = 'search'
            try:
                crud.save_scraped_products_batch(db, products)
                print(f"✓ Saved {len(products)} products to cache")
            except Exception as e:
                print(f"Error batch saving products: {e}")
        
        return {
            "query": q,
            "count": len(products),
            "products": products,
            "cached": False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/deals/{category}")
async def get_category_deals(
    category: str,
    min_discount: int = Query(15, ge=0, le=100, description="Minimum discount %"),
    db: Session = Depends(get_db)
):
    """
    Get deals for a specific tech category
    
    Args:
        category: Category name (laptops, monitors, keyboards, etc.)
        min_discount: Minimum discount percentage
    """
    try:
        # CACHE-FIRST: Check database for recent category results (last 5 minutes)
        from datetime import datetime, timedelta
        cache_cutoff = datetime.utcnow() - timedelta(minutes=5)
        
        # Search database for cached category deals
        cached_deals = db.query(models.Product).filter(
            models.Product.category == category,
            models.Product.updated_at >= cache_cutoff
        ).limit(50).all()
        
        # If we have recent cached results, return them (FAST!)
        if cached_deals:
            print(f"✓ Cache HIT: {len(cached_deals)} {category} deals from database")
            deals = [{
                'asin': p.asin,
                'title': p.title,
                'url': p.url,
                'image_url': p.image_url,
                'current_price': None,
                'discount_percent': 0,
                'rating': p.rating,
                'num_reviews': p.num_reviews,
                'is_prime': p.is_prime
            } for p in cached_deals]
            return {
                "category": category,
                "min_discount": min_discount,
                "count": len(deals),
                "deals": deals,
                "cached": True
            }
        
        # Cache MISS: Scrape deals for this category
        print(f"✗ Cache MISS: Scraping {category} deals")
        deals = scraper.get_category_deals(category, min_discount=min_discount)
        
        # Save to database (for future cache hits)
        if deals:
            for product in deals:
                product['category'] = category
            try:
                crud.save_scraped_products_batch(db, deals)
                print(f"✓ Saved {len(deals)} {category} deals to cache")
            except Exception as e:
                print(f"Error batch saving category deals: {e}")
        
        return {
            "category": category,
            "min_discount": min_discount,
            "count": len(deals),
            "deals": deals,
            "cached": False
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
