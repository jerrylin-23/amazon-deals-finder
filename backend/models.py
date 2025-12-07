"""
Database models for Amazon Deals Finder
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Product(Base):
    """Product information from Amazon"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    asin = Column(String(20), unique=True, nullable=False, index=True)
    title = Column(Text, nullable=False)
    url = Column(Text)
    image_url = Column(Text)
    category = Column(String(50), index=True)
    is_prime = Column(Boolean, default=False)
    rating = Column(Float)
    num_reviews = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to price history
    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Product(asin='{self.asin}', title='{self.title[:30]}...')>"


class PriceHistory(Base):
    """Historical price data for products"""
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=True)
    asin = Column(String(20), nullable=False, index=True)
    
    # Price information
    current_price = Column(Float)
    original_price = Column(Float)
    discount_percent = Column(Integer, default=0)
    
    # Historical context from CamelCamelCamel
    lowest_ever = Column(Float)
    highest_ever = Column(Float)
    is_historical_low = Column(Boolean, default=False)
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationship to product
    product = relationship("Product", back_populates="price_history")
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('ix_price_history_asin_timestamp', 'asin', 'timestamp'),
        Index('ix_price_history_product_timestamp', 'product_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<PriceHistory(asin='{self.asin}', price=${self.current_price}, timestamp='{self.timestamp}')>"
