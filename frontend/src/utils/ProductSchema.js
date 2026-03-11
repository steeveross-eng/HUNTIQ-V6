/**
 * Product JSON-LD Schema Generator - PHASE F BIONIC ULTIMATE
 * 
 * Génère les schemas JSON-LD Product conformes à Schema.org
 * pour améliorer le SEO e-commerce
 * 
 * @module ProductSchema
 * @version 1.0.0
 * @phase F
 */

const SITE_URL = process.env.REACT_APP_SITE_URL || process.env.REACT_APP_BACKEND_URL || 'https://bionic-huntiq.com';
const SITE_NAME = 'Chasse Bionic TM';

/**
 * Generate Product Schema JSON-LD
 * @param {Object} product - Product data
 * @returns {Object} JSON-LD schema
 */
export const generateProductSchema = (product) => {
  if (!product) return null;
  
  const schema = {
    "@context": "https://schema.org",
    "@type": "Product",
    "@id": `${SITE_URL}/shop/product/${product.id || product._id}#product`,
    "name": product.name,
    "description": product.description || product.short_description,
    "image": product.image_url ? [product.image_url] : [],
    "brand": {
      "@type": "Brand",
      "name": product.brand || SITE_NAME
    },
    "manufacturer": {
      "@type": "Organization",
      "name": product.manufacturer || product.brand || "Fabricant"
    },
    "category": product.category || "Attractants de chasse",
    "url": `${SITE_URL}/shop/product/${product.id || product._id}`,
    "sku": product.sku || product.id || product._id,
    "mpn": product.mpn || product.sku,
    "productID": product.id || product._id
  };
  
  // Add offers (pricing)
  if (product.price !== undefined) {
    schema.offers = {
      "@type": "Offer",
      "url": `${SITE_URL}/shop/product/${product.id || product._id}`,
      "priceCurrency": "CAD",
      "price": product.price,
      "priceValidUntil": getNextYearDate(),
      "availability": product.in_stock !== false 
        ? "https://schema.org/InStock" 
        : "https://schema.org/OutOfStock",
      "seller": {
        "@type": "Organization",
        "name": SITE_NAME
      }
    };
    
    // Add sale price if applicable
    if (product.sale_price && product.sale_price < product.price) {
      schema.offers.price = product.sale_price;
      schema.offers.priceSpecification = {
        "@type": "PriceSpecification",
        "price": product.sale_price,
        "priceCurrency": "CAD",
        "valueAddedTaxIncluded": true
      };
    }
  }
  
  // Add aggregate rating if available
  if (product.rating && product.review_count) {
    schema.aggregateRating = {
      "@type": "AggregateRating",
      "ratingValue": product.rating,
      "bestRating": 5,
      "worstRating": 1,
      "ratingCount": product.review_count,
      "reviewCount": product.review_count
    };
  }
  
  // Add BIONIC score as additional property
  if (product.bionic_score !== undefined) {
    schema.additionalProperty = [
      {
        "@type": "PropertyValue",
        "name": "Score BIONIC",
        "value": product.bionic_score,
        "maxValue": 100,
        "unitText": "points"
      }
    ];
    
    // Add species if available
    if (product.species) {
      const speciesMap = {
        'deer': 'Chevreuil',
        'moose': 'Orignal',
        'bear': 'Ours',
        'wild_turkey': 'Dindon sauvage'
      };
      
      schema.additionalProperty.push({
        "@type": "PropertyValue",
        "name": "Espèce cible",
        "value": speciesMap[product.species] || product.species
      });
    }
  }
  
  // Add weight if available
  if (product.weight) {
    schema.weight = {
      "@type": "QuantitativeValue",
      "value": product.weight,
      "unitCode": "KGM"
    };
  }
  
  return schema;
};

/**
 * Generate Product List Schema (for category pages)
 * @param {Array} products - Array of products
 * @param {string} categoryName - Category name
 * @returns {Object} JSON-LD schema
 */
export const generateProductListSchema = (products, categoryName = "Attractants") => {
  if (!products || products.length === 0) return null;
  
  return {
    "@context": "https://schema.org",
    "@type": "ItemList",
    "name": `${categoryName} - ${SITE_NAME}`,
    "description": `Liste des ${categoryName.toLowerCase()} disponibles chez ${SITE_NAME}`,
    "numberOfItems": products.length,
    "itemListElement": products.slice(0, 10).map((product, index) => ({
      "@type": "ListItem",
      "position": index + 1,
      "item": {
        "@type": "Product",
        "@id": `${SITE_URL}/shop/product/${product.id || product._id}#product`,
        "name": product.name,
        "image": product.image_url,
        "url": `${SITE_URL}/shop/product/${product.id || product._id}`,
        "offers": product.price !== undefined ? {
          "@type": "Offer",
          "price": product.sale_price || product.price,
          "priceCurrency": "CAD",
          "availability": product.in_stock !== false 
            ? "https://schema.org/InStock" 
            : "https://schema.org/OutOfStock"
        } : undefined
      }
    }))
  };
};

/**
 * Generate FAQ Schema for product pages
 * @param {Array} faqs - Array of FAQ items
 * @returns {Object} JSON-LD schema
 */
export const generateFAQSchema = (faqs) => {
  if (!faqs || faqs.length === 0) return null;
  
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": faqs.map(faq => ({
      "@type": "Question",
      "name": faq.question,
      "acceptedAnswer": {
        "@type": "Answer",
        "text": faq.answer
      }
    }))
  };
};

/**
 * Generate Review Schema
 * @param {Object} review - Review data
 * @param {Object} product - Product data
 * @returns {Object} JSON-LD schema
 */
export const generateReviewSchema = (review, product) => {
  if (!review) return null;
  
  return {
    "@context": "https://schema.org",
    "@type": "Review",
    "itemReviewed": {
      "@type": "Product",
      "name": product?.name || "Produit",
      "@id": product ? `${SITE_URL}/shop/product/${product.id || product._id}#product` : undefined
    },
    "reviewRating": {
      "@type": "Rating",
      "ratingValue": review.rating,
      "bestRating": 5,
      "worstRating": 1
    },
    "author": {
      "@type": "Person",
      "name": review.author_name || "Chasseur vérifié"
    },
    "datePublished": review.date || new Date().toISOString(),
    "reviewBody": review.content || review.text
  };
};

/**
 * Inject schema into document head
 * @param {Object} schema - JSON-LD schema
 * @param {string} id - Unique identifier for the script tag
 */
export const injectProductSchema = (schema, id = 'product-schema') => {
  if (!schema) return;
  
  // Remove existing schema with same ID
  const existing = document.querySelector(`script[data-schema-id="${id}"]`);
  if (existing) {
    existing.remove();
  }
  
  // Create new script tag
  const script = document.createElement('script');
  script.type = 'application/ld+json';
  script.setAttribute('data-schema-id', id);
  script.textContent = JSON.stringify(schema);
  document.head.appendChild(script);
};

/**
 * Remove schema from document head
 * @param {string} id - Unique identifier for the script tag
 */
export const removeProductSchema = (id = 'product-schema') => {
  const existing = document.querySelector(`script[data-schema-id="${id}"]`);
  if (existing) {
    existing.remove();
  }
};

/**
 * Get date one year from now (for priceValidUntil)
 */
function getNextYearDate() {
  const date = new Date();
  date.setFullYear(date.getFullYear() + 1);
  return date.toISOString().split('T')[0];
}

export default {
  generateProductSchema,
  generateProductListSchema,
  generateFAQSchema,
  generateReviewSchema,
  injectProductSchema,
  removeProductSchema
};
