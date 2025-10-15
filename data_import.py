#!/usr/bin/env python3
"""
Medicine Inventory System - Data Import Script
This script helps import data from the existing medicines.db database
"""

import sqlite3
import pandas as pd
from sqlalchemy import create_engine
from models import Medicine, Base
from database import engine, SessionLocal
import re

def extract_price(package_info):
    """Extract price from package container string"""
    if not package_info:
        return None
    
    # Look for price pattern like "৳ 40.12" or "৳40.12"
    price_match = re.search(r'৳\s*(\d+(?:\.\d{2})?)', str(package_info))
    if price_match:
        return float(price_match.group(1))
    
    return None

def clean_medicine_data(row):
    """Clean and structure medicine data from CSV format"""
    return {
        'brand_id': row.get('brand id'),
        'brand_name': row.get('brand_name'),
        'type': row.get('type'),
        'slug': row.get('slug'),
        'dosage_form': row.get('dosage_form'),
        'generic': row.get('generic'),
        'strength': row.get('strength'),
        'manufacturer': row.get('manufacturer'),
        'package_container': row.get('package_container'),
        'package_size': row.get('Package Size'),
        'price': extract_price(row.get('package_container', ''))
    }

def import_from_existing_db():
    """Import data from existing medicines.db"""
    try:
        # Connect to existing database
        conn = sqlite3.connect('medicines.db')
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Found tables: {tables}")
        
        # Try to get data from the first table
        if tables:
            table_name = tables[0][0]
            print(f"Reading from table: {table_name}")
            
            # Get all data
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            print(f"Found {len(rows)} rows with columns: {columns}")
            
            # Create new session
            db = SessionLocal()
            
            # Clear existing data
            db.query(Medicine).delete()
            
            # Import data
            imported_count = 0
            for row in rows:
                # Create dictionary from row data
                row_dict = dict(zip(columns, row))
                
                # Clean and create medicine object
                medicine_data = clean_medicine_data(row_dict)
                
                # Create medicine object
                medicine = Medicine(**medicine_data)
                db.add(medicine)
                imported_count += 1
                
                if imported_count % 100 == 0:
                    print(f"Imported {imported_count} medicines...")
            
            db.commit()
            db.close()
            
            print(f"Successfully imported {imported_count} medicines")
            return imported_count
            
        else:
            print("No tables found in the database")
            return 0
            
    except Exception as e:
        print(f"Error importing data: {e}")
        return 0
    finally:
        if 'conn' in locals():
            conn.close()

def create_sample_data():
    """Create sample data if no existing database is found"""
    db = SessionLocal()
    
    # Sample medicine data
    sample_medicines = [
        {
            'brand_id': 4077,
            'brand_name': 'A-Cold',
            'type': 'allopathic',
            'slug': 'a-coldsyrup4-mg5-ml',
            'dosage_form': 'Syrup',
            'generic': 'Bromhexine Hydrochloride',
            'strength': '4 mg/5 ml',
            'manufacturer': 'ACME Laboratories Ltd.',
            'package_container': '100 ml bottle: ৳ 40.12',
            'package_size': '100 ml',
            'price': 40.12
        },
        {
            'brand_id': 4006,
            'brand_name': 'A-Cof',
            'type': 'allopathic',
            'slug': 'a-cofsyrup10-mg30-mg125-mg5-ml',
            'dosage_form': 'Syrup',
            'generic': 'Dextromethorphan + Pseudoephedrine + Triprolidine',
            'strength': '(10 mg+30 mg+1.25 mg)/5 ml',
            'manufacturer': 'ACME Laboratories Ltd.',
            'package_container': '100 ml bottle: ৳ 100.00',
            'package_size': '100 ml',
            'price': 100.00
        },
        {
            'brand_id': 6174,
            'brand_name': 'A-Clox',
            'type': 'allopathic',
            'slug': 'a-cloxinjection500-mgvial',
            'dosage_form': 'Injection',
            'generic': 'Cloxacillin Sodium',
            'strength': '500 mg/vial',
            'manufacturer': 'ACME Laboratories Ltd.',
            'package_container': '500 mg vial: ৳ 28.43',
            'package_size': '500 mg',
            'price': 28.43
        },
        {
            'brand_id': 6173,
            'brand_name': 'A-Clox',
            'type': 'allopathic',
            'slug': 'a-cloxinjection250-mgvial',
            'dosage_form': 'Injection',
            'generic': 'Cloxacillin Sodium',
            'strength': '250 mg/vial',
            'manufacturer': 'ACME Laboratories Ltd.',
            'package_container': '250 mg vial: ৳ 20.00',
            'package_size': '250 mg',
            'price': 20.00
        },
        {
            'brand_id': 6172,
            'brand_name': 'A-Clox',
            'type': 'allopathic',
            'slug': 'a-cloxpowder-for-suspension125-mg5-ml',
            'dosage_form': 'Powder for Suspension',
            'generic': 'Cloxacillin Sodium',
            'strength': '125 mg/5 ml',
            'manufacturer': 'ACME Laboratories Ltd.',
            'package_container': '100 ml bottle: ৳ 45.00',
            'package_size': '100 ml',
            'price': 45.00
        }
    ]
    
    # Clear existing data
    db.query(Medicine).delete()
    
    # Add sample data
    for medicine_data in sample_medicines:
        medicine = Medicine(**medicine_data)
        db.add(medicine)
    
    db.commit()
    db.close()
    
    print(f"Created {len(sample_medicines)} sample medicines")
    return len(sample_medicines)

def main():
    """Main import function"""
    print("Medicine Inventory System - Data Import")
    print("=" * 50)
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    print("Database tables created/verified")
    
    # Try to import from existing database
    imported_count = import_from_existing_db()
    
    # If no data was imported, create sample data
    if imported_count == 0:
        print("No existing data found, creating sample data...")
        imported_count = create_sample_data()
    
    print(f"\nImport completed. Total medicines: {imported_count}")
    print("\nYou can now start the FastAPI server with:")
    print("uvicorn main:app --reload")

if __name__ == "__main__":
    main()