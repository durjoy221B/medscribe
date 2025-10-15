from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Medicine(Base):
    """Medicine model for the inventory system"""
    __tablename__ = "medicines"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, index=True)
    brand_name = Column(String, index=True)
    type = Column(String, index=True)
    slug = Column(String)
    dosage_form = Column(String, index=True)
    generic = Column(String, index=True)
    strength = Column(String)
    manufacturer = Column(String, index=True)
    package_container = Column(String)
    package_size = Column(String)
    price = Column(Float)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'brand_id': self.brand_id,
            'brand_name': self.brand_name,
            'type': self.type,
            'slug': self.slug,
            'dosage_form': self.dosage_form,
            'generic': self.generic,
            'strength': self.strength,
            'manufacturer': self.manufacturer,
            'package_container': self.package_container,
            'package_size': self.package_size,
            'price': self.price
        }

# Create tables (if needed)
engine = create_engine("sqlite:///./medicines.db", connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)