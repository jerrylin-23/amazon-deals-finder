// Amazon Deals Finder - Frontend JavaScript

const API_BASE = window.location.origin;

// DOM Elements
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const discountFilter = document.getElementById('discountFilter');
const sortFilter = document.getElementById('sortFilter');
const categoriesGrid = document.getElementById('categoriesGrid');
const productsGrid = document.getElementById('productsGrid');
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const resultsHeader = document.getElementById('resultsHeader');
const resultsTitle = document.getElementById('resultsTitle');
const resultsCount = document.getElementById('resultsCount');

let currentProducts = []; // Store current results for sorting

// Load categories on page load
document.addEventListener('DOMContentLoaded', () => {
    loadCategories();

    // Event listeners
    searchBtn.addEventListener('click', handleSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
    });
    sortFilter.addEventListener('change', () => {
        if (currentProducts.length > 0) {
            displayResults(currentProducts, resultsTitle.textContent);
        }
    });
});

// Load categories
async function loadCategories() {
    try {
        const response = await fetch(`${API_BASE}/api/categories`);
        const data = await response.json();

        displayCategories(data.categories);
    } catch (err) {
        console.error('Error loading categories:', err);
    }
}

// Display categories
function displayCategories(categories) {
    categoriesGrid.innerHTML = categories.map(category => `
        <button class="category-card" onclick="searchCategory('${category}')">
            ${getCategoryIcon(category)} ${formatCategory(category)}
        </button>
    `).join('');
}

// Get category icon
function getCategoryIcon(category) {
    const icons = {
        'laptops': '💻',
        'monitors': '🖥️',
        'keyboards': '⌨️',
        'mice': '🖱️',
        'headphones': '🎧',
        'phones': '📱',
        'tablets': '📲',
        'smartwatches': '⌚',
        'webcams': '📷',
        'microphones': '🎤'
    };
    return icons[category] || '📦';
}

// Format category name
function formatCategory(category) {
    return category.charAt(0).toUpperCase() + category.slice(1);
}

// Search by category
async function searchCategory(category) {
    const minDiscount = discountFilter.value;
    showLoading();

    try {
        const response = await fetch(`${API_BASE}/api/deals/${category}?min_discount=${minDiscount}`);
        const data = await response.json();

        // Fetch price history for deals
        await enrichWithPriceHistory(data.deals);

        displayResults(data.deals, `${formatCategory(category)} Deals`);
    } catch (err) {
        showError(`Failed to load ${category} deals. Please try again.`);
    }
}

// Handle search
async function handleSearch() {
    const query = searchInput.value.trim();
    if (!query) {
        showError('Please enter a search term');
        return;
    }

    const minDiscount = discountFilter.value;
    showLoading();

    try {
        const response = await fetch(`${API_BASE}/api/search?q=${encodeURIComponent(query)}&max_results=60&min_discount=${minDiscount}`);
        const data = await response.json();

        // Fetch price history for products
        await enrichWithPriceHistory(data.products);

        displayResults(data.products, `Search Results for "${query}"`);
    } catch (err) {
        showError('Failed to search products. Please try again.');
    }
}

// Enrich products with price history from CamelCamelCamel
async function enrichWithPriceHistory(products) {
    const promises = products.map(async (product) => {
        if (!product.asin) return;

        try {
            const response = await fetch(`${API_BASE}/api/price-history/${product.asin}`);
            if (response.ok) {
                const history = await response.json();
                product.price_history = {
                    lowest_ever: history.price_stats?.lowest_amazon,
                    highest_ever: history.price_stats?.highest_amazon,
                    is_historical_low: false
                };

                // Check if at historical low
                if (product.current_price && history.price_stats?.lowest_amazon) {
                    const lowest = history.price_stats.lowest_amazon;
                    if (product.current_price <= lowest + 1.0) {
                        product.price_history.is_historical_low = true;
                    }
                }
            }
        } catch (err) {
            // Silently fail - not all products have price history
        }
    });

    await Promise.all(promises);
}

// Sort products based on selected option
function sortProducts(products) {
    const sortBy = sortFilter.value;

    switch (sortBy) {
        case 'name-asc':
            return products.sort((a, b) => a.title.localeCompare(b.title));
        case 'name-desc':
            return products.sort((a, b) => b.title.localeCompare(a.title));
        case 'price-low':
            return products.sort((a, b) => {
                const priceA = a.current_price || 999999;
                const priceB = b.current_price || 999999;
                return priceA - priceB;
            });
        case 'price-high':
            return products.sort((a, b) => {
                const priceA = a.current_price || 0;
                const priceB = b.current_price || 0;
                return priceB - priceA;
            });
        case 'discount-high':
            return products.sort((a, b) => b.discount_percent - a.discount_percent);
        default: // relevance
            return products;
    }
}

// Display results
function displayResults(products, title) {
    hideLoading();
    hideError();

    // Store products for re-sorting
    currentProducts = products;

    // Sort products
    const sortedProducts = sortProducts([...products]);

    resultsTitle.textContent = title;
    resultsCount.textContent = `${sortedProducts.length} deals found`;
    resultsHeader.style.display = 'block';

    if (sortedProducts.length === 0) {
        productsGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px;">
                <p style="font-size: 1.5rem; color: #565959;">No deals found. Try adjusting your filters!</p>
            </div>
        `;
        return;
    }

    productsGrid.innerHTML = sortedProducts.map(product => createProductCard(product)).join('');
}

// Create product card
function createProductCard(product) {
    const hasDiscount = product.discount_percent > 0;
    const hasPrime = product.is_prime;
    const hasRating = product.rating && product.num_reviews > 0;
    const hasHistory = product.price_history;
    const isHistoricalLow = hasHistory && product.price_history.is_historical_low;

    return `
        <div class="product-card" onclick="openProduct('${product.url}')">
            ${isHistoricalLow ? `
                <div class="historical-low-badge">
                    🔥 ALL TIME LOW
                </div>
            ` : hasDiscount ? `
                <div class="product-badge">
                    ${product.discount_percent}% OFF
                </div>
            ` : ''}
            
            <img src="${product.image_url}" alt="${product.title}" class="product-image">
            
            <h3 class="product-title">${truncate(product.title, 80)}</h3>
            
            ${hasRating ? `
                <div class="product-rating">
                    <span class="stars">${generateStars(product.rating)}</span>
                    <span class="reviews-count">(${product.num_reviews.toLocaleString()})</span>
                </div>
            ` : ''}
            
            <div class="product-pricing">
                <div>
                    ${product.current_price ? `
                        <span class="current-price">CAD $${product.current_price.toFixed(2)}</span>
                    ` : '<span class="current-price">Price unavailable</span>'}
                    ${product.original_price && hasDiscount ? `
                        <span class="original-price">CAD $${product.original_price.toFixed(2)}</span>
                    ` : ''}
                </div>
                ${hasDiscount && product.current_price && product.original_price ? `
                    <div class="savings">
                        Save CAD $${(product.original_price - product.current_price).toFixed(2)}
                    </div>
                ` : ''}
                ${hasHistory && hasHistory.lowest_ever ? `
                    <div class="price-context">
                        Lowest ever: CAD $${hasHistory.lowest_ever.toFixed(2)}
                    </div>
                ` : ''}
            </div>
            
            ${hasPrime ? `
                <div class="prime-badge">
                    <span>✓</span> Prime
                </div>
            ` : ''}
        </div>
    `;
}

// Utility functions
function generateStars(rating) {
    const fullStars = Math.floor(rating);
    const halfStar = rating % 1 >= 0.5;
    let stars = '★'.repeat(fullStars);
    if (halfStar) stars += '⯨';
    stars += '☆'.repeat(5 - Math.ceil(rating));
    return stars;
}

function truncate(str, length) {
    return str.length > length ? str.substring(0, length) + '...' : str;
}

function openProduct(url) {
    if (url) {
        window.open(url, '_blank');
    }
}

function showLoading() {
    loading.style.display = 'block';
    productsGrid.innerHTML = '';
    resultsHeader.style.display = 'none';
    hideError();
}

function hideLoading() {
    loading.style.display = 'none';
}

function showError(message) {
    error.textContent = message;
    error.style.display = 'block';
    hideLoading();
    productsGrid.innerHTML = '';
    resultsHeader.style.display = 'none';
}

function hideError() {
    error.style.display = 'none';
}
