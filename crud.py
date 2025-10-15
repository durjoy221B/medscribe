from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional
from models import Medicine
from schemas import MedicineCreate, MedicineUpdate, MedicineSearch

def get_medicine(db: Session, medicine_id: int):
    """Get medicine by ID"""
    return db.query(Medicine).filter(Medicine.id == medicine_id).first()

def get_medicines(db: Session, skip: int = 0, limit: int = 100):
    """Get all medicines with pagination"""
    return db.query(Medicine).offset(skip).limit(limit).all()

def create_medicine(db: Session, medicine: MedicineCreate):
    """Create new medicine"""
    db_medicine = Medicine(**medicine.dict(exclude_unset=True))
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    return db_medicine

def update_medicine(db: Session, medicine_id: int, medicine: MedicineUpdate):
    """Update medicine"""
    db_medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if db_medicine:
        update_data = medicine.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_medicine, field, value)
        db.commit()
        db.refresh(db_medicine)
    return db_medicine

def delete_medicine(db: Session, medicine_id: int):
    """Delete medicine"""
    db_medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if db_medicine:
        db.delete(db_medicine)
        db.commit()
    return db_medicine

def search_medicines(db: Session, search_params: MedicineSearch):
    """Advanced search functionality"""
    base_query = db.query(Medicine)
    
    # Apply specific field filters first
    if search_params.type:
        base_query = base_query.filter(Medicine.type.ilike(f"%{search_params.type}%"))
    
    if search_params.dosage_form:
        base_query = base_query.filter(Medicine.dosage_form.ilike(f"%{search_params.dosage_form}%"))
    
    # Price range filters
    if search_params.min_price is not None:
        base_query = base_query.filter(Medicine.price >= search_params.min_price)
    
    if search_params.max_price is not None:
        base_query = base_query.filter(Medicine.price <= search_params.max_price)

    # Handle general search query with exact match priority
    if search_params.query:
        exact_match_clause = None
        partial_match_clause = None

        if search_params.search_type == "brand_name":
            exact_match_clause = (Medicine.brand_name.ilike(search_params.query))
            partial_match_clause = (Medicine.brand_name.ilike(f"%{search_params.query}%"))
        elif search_params.search_type == "generic_name":
            exact_match_clause = (Medicine.generic.ilike(search_params.query))
            partial_match_clause = (Medicine.generic.ilike(f"%{search_params.query}%"))
        
        if exact_match_clause is not None and partial_match_clause is not None:
            # Order by exact match first, then partial match
            base_query = base_query.filter(or_(exact_match_clause, partial_match_clause))
            base_query = base_query.order_by(exact_match_clause.desc())

    # Sorting
    sort_column = getattr(Medicine, search_params.sort_by, Medicine.brand_name)
    if search_params.sort_order == "desc":
        base_query = base_query.order_by(sort_column.desc())
    else:
        base_query = base_query.order_by(sort_column.asc())
    
    # Pagination
    total = base_query.count()
    offset = (search_params.page - 1) * search_params.per_page
    medicines = base_query.offset(offset).limit(search_params.per_page).all()
    
    return medicines, total

def get_medicine_statistics(db: Session):
    """Get medicine inventory statistics"""
    total_medicines = db.query(Medicine).count()
    total_manufacturers = db.query(Medicine.manufacturer).distinct().count()
    total_types = db.query(Medicine.type).distinct().count()
    total_dosage_forms = db.query(Medicine.dosage_form).distinct().count()
    
    # Price statistics
    price_stats = db.query(
        func.avg(Medicine.price).label('average_price'),
        func.min(Medicine.price).label('min_price'),
        func.max(Medicine.price).label('max_price')
    ).filter(Medicine.price.isnot(None)).first()
    
    return {
        "total_medicines": total_medicines,
        "total_manufacturers": total_manufacturers,
        "total_types": total_types,
        "total_dosage_forms": total_dosage_forms,
        "average_price": float(price_stats.average_price) if price_stats.average_price else 0,
        "price_range": {
            "min": float(price_stats.min_price) if price_stats.min_price else 0,
            "max": float(price_stats.max_price) if price_stats.max_price else 0
        }
    }

def get_filter_options(db: Session):
    """Get filter options for search interface"""
    types = [t[0] for t in db.query(Medicine.type).distinct().all() if t[0]]
    dosage_forms = [d[0] for d in db.query(Medicine.dosage_form).distinct().all() if d[0]]
    
    return {
        "types": sorted(types),
        "dosage_forms": sorted(dosage_forms)
    }