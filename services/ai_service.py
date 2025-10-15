from langchain_google_genai import ChatGoogleGenerativeAI
from services.output_format import ExtractInfo
from services.web_search import find_best_medicine_match
from config.load_env import GEMINI_MODEL, GOOGLE_API_KEY

model = ChatGoogleGenerativeAI(model=GEMINI_MODEL, 
                             api_key = GOOGLE_API_KEY,
                             temperature=0.0,)

def ExtractMedicineInfo(image_base64: str):

    llm = model.with_structured_output(ExtractInfo)
    llm_response = llm.invoke([
            {"role": "user", "content": [
                {"type": "text", "text": "Explain what is happening in this image in simple terms."},
                {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_base64}"}
            ]}
        ])
    print(llm_response)
    response = {}
    for index, extracted_medicine_name in enumerate(llm_response.name):
        medicine_name = find_best_medicine_match(llm_response.fullname[index], extracted_medicine_name)
        strength_value = llm_response.strength[index] if index < len(llm_response.strength) else "N/A"
        dosage_type_value = llm_response.dosage_type[index] if index < len(llm_response.dosage_type) else "N/A"
        response[f"medicine_{index+1}"] = {
            "name": medicine_name,
            "strength": strength_value,
            "dosage_type": dosage_type_value,
        }

    return response

