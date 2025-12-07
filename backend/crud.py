"""
CRUD operations for database
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
import models


# ============= PRODUCT OPERATIONS =============

def get_product_by_asin(db: Session, asin: str) -> Optional[models.Product]:
    """Get product by ASIN"""
    return db.query(models.Product).filter(models.Product.asin == asin).first()


def get_products_by_category(
    db: Session, 
    category: str, 
    min_discount: int = 0,
    limit: int = 50
) -> List[models.Product]:
    """Get products by category with optional discount filter"""
    query = db.query(models.Product).filter(models.Product.category == category)
    
    if min_discount > 0:
        # Join with latest price history to filter by discount
        query = query.join(models.PriceHistory).filter(
            models.PriceHistory.discount_percent >= min_discount
        )
    
    return query.order_by(desc(models.Product.created_at)).limit(limit).all()


def search_products(
    db: Session,
    query: str,
    min_discount: int = 0,
    limit: int = 50
) -> List[models.Product]:
    """Search products by title"""
    search_query = db.query(models.Product).filter(
        models.Product.title.ilike(f'%{query}%')
    )
    
    return search_query.order_by(desc(models.Product.created_at)).limit(limit).all()


def create_product(db: Session, product_data: dict, commit: bool = True) -> models.Product:
    """Create new product"""
    product = models.Product(**product_data)
    db.add(product)
    if commit:
        db.commit()
        db.refresh(product)
    return product


def update_product(db: Session, asin: str, product_data: dict, commit: bool = True) -> Optional[models.Product]:
    """Update existing product"""
    product = get_product_by_asin(db, asin)
    if product:
        for key, value in product_data.items():
            setattr(product, key, value)
        if commit:
            db.commit()
            db.refresh(product)
    return product


def upsert_product(db: Session, product_data: dict, commit: bool = True) -> models.Product:
    """Create product if not exists, update if exists"""
    asin = product_data.get('asin')
    existing = get_product_by_asin(db, asin)
    
    if existing:
        return update_product(db, asin, product_data, commit=commit)
    else:
        return create_product(db, product_data, commit=commit)


# ============= PRICE HISTORY OPERATIONS =============

def create_price_history(db: Session, price_data: dict, commit: bool = True) -> models.PriceHistory:
    """Create price history entry"""
    price_history = models.PriceHistory(**price_data)
    db.add(price_history)
    if commit:
        db.commit()
        db.refresh(price_history)
    return price_history


def get_price_history_by_asin(
    db: Session,
    asin: str,
    days: int = 90,
    limit: int = 100
) -> List[models.PriceHistory]:
    """Get price history for a product"""
    since = datetime.now() - timedelta(days=days)
    
    return db.query(models.PriceHistory).filter(
        and_(
            models.PriceHistory.asin == asin,
            models.PriceHistory.timestamp >= since
        )
    ).order_by(desc(models.PriceHistory.timestamp)).limit(limit).all()


def get_latest_price(db: Session, asin: str) -> Optional[models.PriceHistory]:
    """Get most recent price for a product"""
    return db.query(models.PriceHistory).filter(
        models.PriceHistory.asin == asin
    ).order_by(desc(models.PriceHistory.timestamp)).first()


def get_lowest_price(db: Session, asin: str, days: int = 90) -> Optional[float]:
    """Get lowest price in the specified period"""
    since = datetime.now() - timedelta(days=days)
    
    result = db.query(models.PriceHistory).filter(
        and_(
            models.PriceHistory.asin == asin,
            models.PriceHistory.timestamp >= since,
            models.PriceHistory.current_price.isnot(None)
        )
    ).order_by(models.PriceHistory.current_price).first()
    
    return result.current_price if result else None


def save_scraped_product(db: Session, product_dict: dict) -> tuple[models.Product, models.PriceHistory]:
    """
    Save a scraped product and its price history
    Returns tuple of (Product, PriceHistory)
    """
    # Extract product data
    product_data = {
        'asin': product_dict['asin'],
        'title': product_dict['title'],
        'url': product_dict.get('url'),
        'image_url': product_dict.get('image_url'),
        'category': product_dict.get('category'),
        'is_prime': product_dict.get('is_prime', False),
        'rating': product_dict.get('rating'),
        'num_reviews': product_dict.get('num_reviews')
    }
    
    # Upsert product
    product = upsert_product(db, product_data)
    
    # Create price history entry
    price_data = {
        'product_id': product.id,
        'asin': product.asin,
        'current_price': product_dict.get('current_price'),
        'original_price': product_dict.get('original_price'),
        'discount_percent': product_dict.get('discount_percent', 0),
        'lowest_ever': product_dict.get('price_history', {}).get('lowest_ever'),
        'highest_ever': product_dict.get('price_history', {}).get('highest_ever'),
        'is_historical_low': product_dict.get('price_history', {}).get('is_historical_low', False)
    }
    
    price_history = create_price_history(db, price_data)
    
    return product, price_history


def save_scraped_products_batch(db: Session, product_dicts: List[dict]) -> int:
    """
    Save multiple scraped products in a single transaction (MUCH faster!)
    Returns count of products saved
    """
    saved_count = 0
    
    try:
        for product_dict in product_dicts:
            # Extract product data
            product_data = {
                'asin': product_dict['asin'],
                'title': product_dict['title'],
                'url': product_dict.get('url'),
                'image_url': product_dict.get('image_url'),
                'category': product_dict.get('category'),
                'is_prime': product_dict.get('is_prime', False),
                'rating': product_dict.get('rating'),
                'num_reviews': product_dict.get('num_reviews')
            }
            
            # Upsert product (without committing)
            product = upsert_product(db, product_data, commit=False)
            db.flush()  # Get the ID without committing
            
            # Create price history entry (without committing)
            price_data = {
                'product_id': product.id,
                'asin': product.asin,
                'current_price': product_dict.get('current_price'),
                'original_price': product_dict.get('original_price'),
                'discount_percent': product_dict.get('discount_percent', 0),
                'lowest_ever': product_dict.get('price_history', {}).get('lowest_ever'),
                'highest_ever': product_dict.get('price_history', {}).get('highest_ever'),
                'is_historical_low': product_dict.get('price_history', {}).get('is_historical_low', False)
            }
            
            create_price_history(db, price_data, commit=False)
            saved_count += 1
        
        # Commit everything at once!
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise e
    
    return saved_count
