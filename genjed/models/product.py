"""Product Data Models.

Defines the structure for product data in the content creation workflow.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import uuid
import time


class ProductCategory(str, Enum):
    """Product category enumeration."""
    ELECTRONICS = "electronics"
    FASHION = "fashion"
    HOME_GARDEN = "home_garden"
    BEAUTY = "beauty"
    FOOD_BEVERAGE = "food_beverage"
    SPORTS = "sports"
    TOYS = "toys"
    AUTOMOTIVE = "automotive"
    OTHER = "other"


@dataclass
class Product:
    """Product data model."""
    name: str
    description: str
    image_urls: List[str]
    category: ProductCategory
    price: float
    currency: str = "USD"
    product_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    attributes: Dict = field(default_factory=dict)
    sku: Optional[str] = None
    brand: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "description": self.description,
            "image_urls": self.image_urls,
            "category": self.category.value if isinstance(self.category, ProductCategory) else self.category,
            "price": self.price,
            "currency": self.currency,
            "attributes": self.attributes,
            "sku": self.sku,
            "brand": self.brand,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Product':
        if isinstance(data.get('category'), str):
            data['category'] = ProductCategory(data['category'])
        return cls(**data)


@dataclass
class BrandGuidelines:
    """Brand guidelines model."""
    brand_name: str
    brand_colors: List[str]
    fonts: List[str]
    tone_of_voice: str
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "brand_name": self.brand_name,
            "brand_colors": self.brand_colors,
            "fonts": self.fonts,
            "tone_of_voice": self.tone_of_voice,
            "logo_url": self.logo_url,
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color
        }


@dataclass
class AssetBundle:
    """Asset bundle containing all input materials for content creation."""
    customer_id: str
    campaign_id: str
    products: List[Product]
    brand_guidelines: BrandGuidelines
    created_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        return {
            "customer_id": self.customer_id,
            "campaign_id": self.campaign_id,
            "products": [p.to_dict() for p in self.products],
            "brand_guidelines": self.brand_guidelines.to_dict(),
            "created_at": self.created_at
        }
