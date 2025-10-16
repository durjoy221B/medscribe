from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn

from database import get_db, check_database_exists, get_medicine_table, execute_raw_query
from models import Medicine
from schemas import (
    MedicineCreate, 
    MedicineUpdate, 
    MedicineResponse, 
    MedicineSearch, 
    SearchResponse,
    MedicineStats
)
from routers.prescription_route import prescription_router
from routers.chatbot_route import chatbot_router
import crud

# Create FastAPI app
app = FastAPI(
    title="Medicine Inventory System",
    description="Premium medicine inventory management system with advanced search",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(prescription_router, tags=["Prescriptions"])
app.include_router(chatbot_router, tags=["Chatbot"])

# Templates
templates = Jinja2Templates(directory="templates")

# Check database on startup
@app.on_event("startup")
async def startup_event():
    if not check_database_exists():
        print("Warning: medicines.db not found. Please ensure the database file exists.")
    else:
        print("Database connection established successfully.")

# Root endpoint - Serve the landing page
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

# Additional Pages
@app.get("/landing", response_class=HTMLResponse)
async def landing_page(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/inventory", response_class=HTMLResponse)
async def inventory_page(request: Request):
    return templates.TemplateResponse("inventory.html", {"request": request})

@app.get("/upload", response_class=HTMLResponse)
async def upload_prescription_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

# @app.get("/chatbot", response_class=HTMLResponse)
# async def chatbot_page(request: Request):
#     prescription_info = getattr(request.app.state, "extra_info_prompt", None)
#     print(":::::::: ->",prescription_info)
#     return templates.TemplateResponse("chatbot.html", {"request": request})

# API Endpoints

@app.get("/api/medicines", response_model=SearchResponse)
async def get_medicines(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all medicines with pagination"""
    try:
        medicines = crud.get_medicines(db, skip=skip, limit=limit)
        total = db.query(Medicine).count()
        
        return SearchResponse(
            medicines=medicines,
            total=total,
            page=(skip // limit) + 1,
            per_page=limit,
            total_pages=(total + limit - 1) // limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/medicines/search", response_model=SearchResponse)
async def search_medicines(
    query: Optional[str] = None,
    search_type: str = Query("brand_name", description="Type of search: 'brand_name' or 'generic_name'"),
    type: Optional[str] = None,
    dosage_form: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: str = "brand_name",
    sort_order: str = "asc",
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Advanced search with multiple filters"""
    try:
        search_params = MedicineSearch(
            query=query,
            search_type=search_type,
            type=type,
            dosage_form=dosage_form,
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            per_page=per_page
        )
        
        medicines, total = crud.search_medicines(db, search_params)
        
        return SearchResponse(
            medicines=medicines,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=(total + per_page - 1) // per_page
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/medicines/{medicine_id}", response_model=MedicineResponse)
async def get_medicine(medicine_id: int, db: Session = Depends(get_db)):
    """Get a specific medicine by ID"""
    medicine = crud.get_medicine(db, medicine_id)
    if medicine is None:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return medicine

@app.post("/api/medicines", response_model=MedicineResponse)
async def create_medicine(
    medicine: MedicineCreate, 
    db: Session = Depends(get_db)
):
    """Create a new medicine"""
    try:
        return crud.create_medicine(db, medicine)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/medicines/{medicine_id}", response_model=MedicineResponse)
async def update_medicine(
    medicine_id: int, 
    medicine: MedicineUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing medicine"""
    db_medicine = crud.update_medicine(db, medicine_id, medicine)
    if db_medicine is None:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return db_medicine

@app.delete("/api/medicines/{medicine_id}")
async def delete_medicine(medicine_id: int, db: Session = Depends(get_db)):
    """Delete a medicine"""
    success = crud.delete_medicine(db, medicine_id)
    if not success:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return {"message": "Medicine deleted successfully"}

@app.get("/api/statistics", response_model=MedicineStats)
async def get_statistics(db: Session = Depends(get_db)):
    """Get medicine inventory statistics"""
    try:
        return crud.get_medicine_statistics(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/filters")
async def get_filter_options(db: Session = Depends(get_db)):
    """Get filter options for search interface"""
    try:
        return crud.get_filter_options(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Raw data endpoints for existing database
@app.get("/api/raw/medicines")
async def get_raw_medicines():
    """Get medicines from raw database query"""
    try:
        # Use reflection to get data from existing table
        medicine_table = get_medicine_table()
        if medicine_table is None:
            raise HTTPException(status_code=404, detail="Medicine table not found")
        
        # Execute raw query
        query = f"SELECT * FROM {medicine_table.name} LIMIT 100"
        results = execute_raw_query(query)
        
        # Convert to list of dictionaries
        columns = medicine_table.columns.keys()
        medicines = [dict(zip(columns, row)) for row in results]
        
        return {
            "medicines": medicines,
            "total": len(medicines),
            "columns": columns
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "database": check_database_exists()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)