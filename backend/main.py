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
        # Scrape Amazon for fresh product data
        products = scraper.search_products(q, max_results=max_results, min_discount=min_discount)
        
        # Save scraped products to database (batch commit for performance)
        if products:
            for product in products:
                product['category'] = 'search'  # Tag as search result
            try:
                crud.save_scraped_products_batch(db, products)
            except Exception as e:
                print(f"Error batch saving products: {e}")
        
        return {
            "query": q,
            "count": len(products),
            "products": products
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
        # Scrape deals for this category
        deals = scraper.get_category_deals(category, min_discount=min_discount)
        
        # Save to database (batch commit for performance)
        if deals:
            for product in deals:
                product['category'] = category  # Tag with actual category
            try:
                crud.save_scraped_products_batch(db, deals)
            except Exception as e:
                print(f"Error batch saving category deals: {e}")
        
        return {
            "category": category,
            "min_discount": min_discount,
            "count": len(deals),
            "deals": deals
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
