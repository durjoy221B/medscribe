from pydantic import BaseModel, Field
from typing import List

class ExtractInfo(BaseModel):
    fullname: List[str] = Field(..., description="Full medicine names with dosage")
    name: List[str] = Field(..., description="Extracted medicine names only")
    dosage_type: List[str] = Field(..., description="Dosage types (e.g., tablet, capsule)")
    strength: List[str] = Field(..., description="Strengths of the medicines (e.g., 500 mg, 20 mg)")
