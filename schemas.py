from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class MedicineBase(BaseModel):
    """Base schema for medicine"""
    brand_id: Optional[int] = None
    brand_name: Optional[str] = None
    type: Optional[str] = None
    slug: Optional[str] = None
    dosage_form: Optional[str] = None
    generic: Optional[str] = None
    strength: Optional[str] = None
    manufacturer: Optional[str] = None
    package_container: Optional[str] = None
    package_size: Optional[str] = None
    price: Optional[float] = None

class MedicineCreate(MedicineBase):
    """Schema for creating new medicine"""
    pass

class MedicineUpdate(MedicineBase):
    """Schema for updating medicine"""
    pass

class MedicineResponse(MedicineBase):
    """Schema for medicine response"""
    id: int
    
    class Config:
        from_attributes = True

class MedicineSearch(BaseModel):
    """Schema for medicine search parameters"""
    query: Optional[str] = None
    search_type: str = Field("brand_name", description="Type of search: 'brand_name' or 'generic_name'")
    type: Optional[str] = None
    dosage_form: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    sort_by: Optional[str] = "brand_name"
    sort_order: Optional[str] = "asc"
    page: int = 1
    per_page: int = 20

class SearchResponse(BaseModel):
    """Schema for search response"""
    medicines: List[MedicineResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

class MedicineStats(BaseModel):
    """Schema for medicine statistics"""
    total_medicines: int
    total_manufacturers: int
    total_types: int
    total_dosage_forms: int
    average_price: float
    price_range: dict