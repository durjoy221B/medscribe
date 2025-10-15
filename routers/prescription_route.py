from fastapi import APIRouter, UploadFile
import base64
from services.ai_service import ExtractMedicineInfo


prescription_router = APIRouter()


@prescription_router.post("/explain-image/")
async def explain_image(file: UploadFile):
    """
    Takes an image file and returns an AI-generated explanation.
    """
    # Read the uploaded image
    image_bytes = await file.read()

    # Convert image to base64 for LangChain
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    # Create input for multimodal model
    response = ExtractMedicineInfo(image_base64)

    return response
